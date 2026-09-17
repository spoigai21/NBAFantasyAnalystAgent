# ---------------------------------------------------------------------------
# 02_features.R -- pre-game features, with no look-ahead
# ---------------------------------------------------------------------------
# The single rule of this script: a feature for game N may only use information
# from games 1..N-1. Every rolling statistic is computed on LAGGED values, so a
# team's "points per game" attached to a game never includes that game.
#
# Getting this wrong is the classic way a backtest produces a fake 60% win rate.
#
# Output: data/processed/model_data.rds
# ---------------------------------------------------------------------------

if (!exists("CFG")) source("R/00_setup.R")
if (!exists("games")) games <- readRDS(CFG$paths$games_rds)

# ===========================================================================
# Rolling helpers
# ===========================================================================
# roll_mean_prior() and games_in_prior_days() -- the two functions that enforce
# "game N may only see games 1..N-1" -- now live in R/utils.R. They were moved
# there so tests/run_tests.R can check them WITHOUT sourcing this file, which
# rebuilds the whole feature set as a side effect. The no-look-ahead property
# is the one thing in this project most worth having a test for, so it should
# not require running a pipeline to check.

# ===========================================================================
# 1. One row per team per game
# ===========================================================================
# Team form is naturally a per-team quantity, so flip the schedule into long
# form, compute everything there, then fold it back onto the game rows.

# Playoff games are a different population -- shortened rotations, no
# back-to-backs, a market that prices them separately. Dropping them is a
# config decision (CFG$model$include_playoffs), applied HERE, once, before form
# is built: a filter applied later would leave playoff results inside the
# rolling averages that feed regular-season games.
#
# Rows whose type the loader could not determine are kept either way. "Unknown"
# is not "playoff", and silently dropping a file that simply lacks the column
# would throw away the whole dataset.
filter_game_types <- function(g) {
  if (isTRUE(CFG$model$include_playoffs) || !"is_playoff" %in% names(g)) return(g)
  drop <- !is.na(g$is_playoff) & g$is_playoff
  if (!any(drop)) return(g)
  info("dropping ", sum(drop), " playoff game(s) (CFG$model$include_playoffs = FALSE)")
  g[!drop, ]
}

build_team_games <- function(g) {
  played <- g %>% filter(.data$completed)
  home <- played %>%
    transmute(.data$game_id, .data$date, .data$season,
              team = .data$home_team, opp = .data$away_team, is_home = 1L,
              pts_for = .data$home_score, pts_against = .data$away_score)
  away <- played %>%
    transmute(.data$game_id, .data$date, .data$season,
              team = .data$away_team, opp = .data$home_team, is_home = 0L,
              pts_for = .data$away_score, pts_against = .data$home_score)

  bind_rows(home, away) %>%
    mutate(margin = .data$pts_for - .data$pts_against,
           game_total = .data$pts_for + .data$pts_against,
           win = as.integer(.data$margin > 0)) %>%
    arrange(.data$team, .data$date, .data$game_id)
}

# ===========================================================================
# 2. Team-level pre-game state
# ===========================================================================

add_team_features <- function(tg, form_window = CFG$model$form_window) {
  # --- previous season's strength, carried forward -------------------------
  # Early-season form is noise; last year's net rating is the best cheap prior.
  season_net <- tg %>%
    group_by(.data$team, .data$season) %>%
    summarise(net = mean(.data$margin), n = n(), .groups = "drop") %>%
    filter(.data$n >= 20) %>%
    mutate(season = .data$season + 1L) %>%          # available for the NEXT season
    select("team", "season", prev_season_net = "net")

  tg %>%
    left_join(season_net, by = c("team", "season")) %>%
    mutate(prev_season_net = coalesce(.data$prev_season_net, 0)) %>%
    group_by(.data$team, .data$season) %>%
    arrange(.data$date, .data$game_id, .by_group = TRUE) %>%
    mutate(
      gp_prior      = row_number() - 1L,

      # season-to-date (expanding), strictly prior games
      win_pct_prior = roll_mean_prior(.data$win),
      pf_prior      = roll_mean_prior(.data$pts_for),
      pa_prior      = roll_mean_prior(.data$pts_against),
      net_prior     = .data$pf_prior - .data$pa_prior,
      pace_prior    = roll_mean_prior(.data$game_total),   # points-per-game proxy

      # recent form
      form_margin   = roll_mean_prior(.data$margin, form_window),
      form_total    = roll_mean_prior(.data$game_total, form_window),

      # schedule
      rest_days     = as.numeric(.data$date - lag(.data$date)),
      games_last_7  = games_in_prior_days(.data$date, 7)
    ) %>%
    ungroup() %>%
    mutate(
      # First game of a season: treat as fully rested rather than unknown.
      rest_days = ifelse(is.na(.data$rest_days), 7, pmin(.data$rest_days, 7)),
      b2b       = as.integer(.data$rest_days <= 1),

      # Before a team has played enough, fall back to last season's strength.
      net_prior   = ifelse(is.na(.data$net_prior), .data$prev_season_net, .data$net_prior),
      form_margin = ifelse(is.na(.data$form_margin), .data$prev_season_net, .data$form_margin),
      pace_prior  = ifelse(is.na(.data$pace_prior), mean(.data$pace_prior, na.rm = TRUE),
                           .data$pace_prior),
      form_total  = ifelse(is.na(.data$form_total), .data$pace_prior, .data$form_total),
      win_pct_prior = coalesce(.data$win_pct_prior, 0.5),
      pf_prior      = coalesce(.data$pf_prior, .data$pace_prior / 2),
      pa_prior      = coalesce(.data$pa_prior, .data$pace_prior / 2)
    )
}

TEAM_FEATURE_COLS <- c("gp_prior", "win_pct_prior", "pf_prior", "pa_prior",
                       "net_prior", "pace_prior", "form_margin", "form_total",
                       "rest_days", "b2b", "games_last_7", "prev_season_net")

# ===========================================================================
# 2b. Opponent-adjusted team ratings
# ===========================================================================
# net_prior is raw point differential, which credits a team for the schedule it
# happened to draw. A team that has played the league's worst opponents looks
# better than it is, and the market corrects for that as a matter of course.
#
# For every game date in a season, ratings are fitted on the games played
# STRICTLY BEFORE that date:
#
#     margin_ij = rating_i - rating_j + home_advantage
#
# solved as ridge regression. The penalty does the early-season work: two games
# in, a team's rating stays near league average instead of exploding. The
# home-advantage term is estimated alongside and left unpenalised.
#
# The identical design fitted on total points instead of margin gives a pace
# rating per team:  total_ij = pace_i + pace_j + base.
#
# Cost is kept down by accumulating X'X and X'y one game at a time as the
# season advances, rather than rebuilding the design matrix at every date.

solve_ridge <- function(XtX, Xty, lambda, p) {
  # The intercept (home advantage / base scoring level) is never penalised --
  # shrinking it toward zero would be shrinking toward "no home court".
  P <- diag(c(rep(lambda, p - 1L), 0))
  out <- tryCatch(solve(XtX + P, Xty), error = function(e) NULL)
  if (is.null(out)) NULL else as.numeric(out)
}

opponent_adjusted_ratings <- function(g,
                                      lambda    = CFG$model$rating_lambda,
                                      min_games = CFG$model$rating_min_games) {
  teams <- sort(unique(c(g$home_team, g$away_team)))
  ti <- setNames(seq_along(teams), teams)
  n_teams <- length(teams)
  p <- n_teams + 1L

  played <- g %>% filter(.data$completed) %>% arrange(.data$date, .data$game_id)

  res <- map_dfr(sort(unique(played$season)), function(s) {
    gs <- played %>% filter(.data$season == s)
    if (!nrow(gs)) return(NULL)
    hi <- ti[gs$home_team]; ai <- ti[gs$away_team]

    XtX_m <- matrix(0, p, p); Xty_m <- numeric(p)   # margin design
    XtX_t <- matrix(0, p, p); Xty_t <- numeric(p)   # total design
    n_seen <- 0L

    h_rat <- a_rat <- h_pac <- a_pac <- rep(NA_real_, nrow(gs))

    for (d in sort(unique(gs$date))) {
      cur <- which(gs$date == d)

      # Fit on everything strictly before this date, then read off today's
      # teams. No game contributes to its own rating.
      if (n_seen >= min_games) {
        bm <- solve_ridge(XtX_m, Xty_m, lambda, p)
        bt <- solve_ridge(XtX_t, Xty_t, lambda, p)
        if (!is.null(bm)) { h_rat[cur] <- bm[hi[cur]]; a_rat[cur] <- bm[ai[cur]] }
        if (!is.null(bt)) { h_pac[cur] <- bt[hi[cur]]; a_pac[cur] <- bt[ai[cur]] }
      }

      # Only now fold today's results into the accumulator.
      for (k in cur) {
        xm <- numeric(p); xm[hi[k]] <-  1; xm[ai[k]] <- -1; xm[p] <- 1
        xt <- numeric(p); xt[hi[k]] <-  1; xt[ai[k]] <-  1; xt[p] <- 1
        XtX_m <- XtX_m + tcrossprod(xm); Xty_m <- Xty_m + xm * gs$margin[k]
        XtX_t <- XtX_t + tcrossprod(xt); Xty_t <- Xty_t + xt * gs$total_points[k]
      }
      n_seen <- n_seen + length(cur)
    }

    tibble(game_id = gs$game_id, h_rating = h_rat, a_rating = a_rat,
           h_pace_rtg = h_pac, a_pace_rtg = a_pac)
  })

  info("opponent-adjusted ratings: ", sum(!is.na(res$h_rating)), " of ",
       nrow(res), " games rated (lambda ", lambda, ")")
  res
}

# ===========================================================================
# 3. Fold team state back onto game rows
# ===========================================================================


# Home/away team state -> matchup features. Lives in its own function because
# 05_forward.R calls it too: the live path and the backtest path must build
# features with byte-identical arithmetic or the backtest is meaningless.
derive_matchup_features <- function(md) {
  md %>% mutate(
    # --- margin/spread model inputs -----------------------------------------
    net_diff       = .data$h_net_prior       - .data$a_net_prior,
    form_diff      = .data$h_form_margin     - .data$a_form_margin,
    prev_net_diff  = .data$h_prev_season_net - .data$a_prev_season_net,
    win_pct_diff   = .data$h_win_pct_prior   - .data$a_win_pct_prior,
    rest_diff      = .data$h_rest_days       - .data$a_rest_days,
    b2b_diff       = .data$h_b2b             - .data$a_b2b,
    density_diff   = .data$h_games_last_7    - .data$a_games_last_7,

    # --- opponent-adjusted inputs -------------------------------------------
    # Present in both the backtest and the live path; NA only before a season
    # has enough games to fit ratings at all.
    rating_diff     = .data$h_rating   - .data$a_rating,
    pace_rating_sum = .data$h_pace_rtg + .data$a_pace_rtg,

    # --- total model inputs --------------------------------------------------
    pace_sum       = .data$h_pace_prior      + .data$a_pace_prior,
    form_total_sum = .data$h_form_total      + .data$a_form_total,
    off_sum        = .data$h_pf_prior        + .data$a_pf_prior,
    def_sum        = .data$h_pa_prior        + .data$a_pa_prior,
    rest_sum       = .data$h_rest_days       + .data$a_rest_days,
    b2b_any        = as.integer(.data$h_b2b + .data$a_b2b > 0)
  )
}

build_model_data <- function(g, tg) {
  side <- function(which_team, prefix) {
    tg %>%
      select("game_id", "team", all_of(TEAM_FEATURE_COLS)) %>%
      rename_with(~ paste0(prefix, .x), all_of(TEAM_FEATURE_COLS)) %>%
      rename(!!which_team := "team")
  }

  md <- g %>%
    filter(.data$completed) %>%
    inner_join(side("home_team", "h_"), by = c("game_id", "home_team")) %>%
    inner_join(side("away_team", "a_"), by = c("game_id", "away_team")) %>%
    left_join(opponent_adjusted_ratings(g), by = "game_id") %>%
    derive_matchup_features() %>%
    mutate(
      # --- market context (opening line only; the close is never an input) ---
      spread_move    = .data$spread_close - .data$spread_open,
      total_move     = .data$total_close  - .data$total_open
    )

  # Drop games where either team has too little history for its form numbers
  # to mean anything.
  keep <- md$h_gp_prior >= CFG$model$min_prior_games &
          md$a_gp_prior >= CFG$model$min_prior_games
  info("dropping ", sum(!keep), " early-season games (fewer than ",
       CFG$model$min_prior_games, " prior games for a team)")
  md[keep, ]
}

# Feature sets handed to the models in 03. Kept short on purpose: with ~1000
# games per season, a dozen features is already enough to start overfitting.
FEATURES_MARGIN <- c("net_diff", "form_diff", "prev_net_diff", "win_pct_diff",
                     "rest_diff", "b2b_diff", "density_diff",
                     "rating_diff")
# def_sum is deliberately absent: pace_sum == off_sum + def_sum exactly, so
# including all three makes the design matrix singular and lm silently returns
# an NA coefficient. Any two of them carry the same information.
FEATURES_TOTAL  <- c("pace_sum", "form_total_sum", "off_sum",
                     "rest_sum", "b2b_any",
                     "pace_rating_sum")

# Optional market anchors -- see CFG$model$use_market_features.
FEATURES_MARGIN_MARKET <- c(FEATURES_MARGIN, "spread_open")
FEATURES_TOTAL_MARKET  <- c(FEATURES_TOTAL,  "total_open")

# ===========================================================================
# 4. No-look-ahead audit
# ===========================================================================
# A cheap but effective guard: if any feature is suspiciously correlated with
# the outcome it is meant to predict, something leaked.

# Correlation measured WITHIN each season, then averaged across seasons
# weighted by games.
#
# This exists because the pooled version raised two false alarms. League scoring
# moved from ~190 points a game in 2008 to ~230 in 2026, so any feature built
# from recent scoring (pace_sum, form_total_sum) tracks total_points across
# eighteen seasons at r ~ 0.61 -- entirely through a shared era trend, with no
# look-ahead anywhere. Inside a single season that same correlation is about
# half as large, which is the number the threshold was always meant to judge.
#
# A real leak does not care about era: a feature carrying the outcome of the
# game it is predicting correlates just as hard within a season as across all
# of them, so nothing is lost by de-trending this way.
within_season_cor <- function(md, f, target) {
  by_season <- split(md[, c(f, target)], md$season)
  rs <- vapply(by_season, function(d) {
    x <- d[[f]]; y <- d[[target]]
    keep <- is.finite(x) & is.finite(y)
    if (sum(keep) < 30 || sd(x[keep]) == 0 || sd(y[keep]) == 0) return(NA_real_)
    suppressWarnings(cor(x[keep], y[keep]))
  }, numeric(1))
  ns <- vapply(by_season, nrow, numeric(1))
  keep <- is.finite(rs)
  if (!any(keep)) return(NA_real_)
  sum(rs[keep] * ns[keep]) / sum(ns[keep])
}

audit_leakage <- function(md, threshold = 0.6) {
  step("Look-ahead audit")
  checks <- list(margin = FEATURES_MARGIN, total_points = FEATURES_TOTAL)
  worst <- 0; worst_f <- NA_character_; worst_pooled <- 0
  for (target in names(checks)) {
    for (f in checks[[target]]) {
      if (!f %in% names(md)) next
      if (sd(md[[f]], na.rm = TRUE) == 0) next
      r <- within_season_cor(md, f, target)
      if (is.na(r)) next
      pooled <- suppressWarnings(cor(md[[f]], md[[target]], use = "complete.obs"))
      if (abs(r) > abs(worst)) { worst <- r; worst_f <- f; worst_pooled <- pooled }
      if (abs(r) > threshold)
        warn("feature '", f, "' correlates ", round(r, 2), " with ", target,
             " within a season -- suspiciously strong for a pre-game signal, ",
             "check for leakage")
    }
  }
  info("strongest feature/outcome correlation: ", round(worst, 3),
       if (!is.na(worst_f)) paste0(" (", worst_f, "; pooled across seasons ",
                                   round(worst_pooled, 3), ")") else "",
       "  (pre-game NBA signals are weak; |r| under ~0.35 is expected)")
  invisible(md)
}

# ===========================================================================
# 5. Run
# ===========================================================================

step("Building features")
games_modelled <- filter_game_types(games)
team_games <- build_team_games(games_modelled) %>% add_team_features()
model_data <- build_model_data(games_modelled, team_games) %>% audit_leakage()

saveRDS(team_games, file.path(CFG$paths$processed_dir, "team_games.rds"))
saveRDS(model_data, CFG$paths$model_data_rds)
info("model_data: ", nrow(model_data), " games x ", ncol(model_data), " columns")
step("Saved ", CFG$paths$model_data_rds)
