# ---------------------------------------------------------------------------
# 10_player_projection.R -- a team forecast built from players, not team form
# ---------------------------------------------------------------------------
# WHY THIS EXISTS
#
# The project's headline finding is not "the model loses money" -- it is *why*
# it loses: the encompassing regression in 08 showed the model is 88-95%
# collinear with the closing line. Every feature in 02 is team-level history
# (net rating, pace, rest, opponent-adjusted strength), which is precisely what
# a betting line is made of. A more accurate version of the same information
# cannot beat the market, and Phase 3 demonstrated exactly that: better ratings
# improved RMSE, moved the correlation with the line from 0.948 to 0.961, and
# changed nothing.
#
# So the question this file asks is not "can we predict better?" but "can we
# predict from somewhere else?" It builds the same two numbers -- a total and a
# margin -- from the bottom up:
#
#     team points  =  sum over expected-available players of
#                     (expected minutes) x (expected points per minute)
#
# That is a different input to the same output. Whether it is a *better*
# forecast is not the point and is unlikely; whether it carries information the
# closing line lacks is testable, and the test already exists in
# 08_diagnostics.R.
#
# NO LOOK-AHEAD, and it matters more here than anywhere else in the project,
# because the temptation is enormous:
#
#   * per-player minutes and points-per-minute use games strictly BEFORE the
#     one being predicted (roll_mean_prior, the same helper 02 uses).
#   * availability is taken from the team's PREVIOUS game, never from tonight's
#     box score. Using who actually played tonight would be reading the answer:
#     "team X's starting centre sat" is only knowable afterwards for historical
#     games, and it is worth several points.
#   * the calibration from raw projection to points is fitted on PRIOR seasons
#     only and applied forward.
#
# The last one is the honest ceiling on what this can claim: a live forecast
# would know tonight's inactives hours before tip-off, and this backtest never
# does. If a signal shows up here it should be *stronger* live; if none shows up
# here, the live version is the only place left to look, which is what 06/09
# and the forward test are for.
#
# Run:
#   source("R/10_player_projection.R")
#   pp <- player_projection_report()     # builds, tests, prints
# ---------------------------------------------------------------------------

if (!exists("CFG")) source("R/00_setup.R")
if (!exists("encompassing_report")) source("R/08_diagnostics.R")

PROJ <- list(
  # Rolling window for a player's minutes and scoring rate. Ten games is about
  # three weeks -- long enough to be stable, short enough to follow a role
  # change. The same window 02 uses for team form, deliberately.
  window = 10,

  # A player must have this many prior games before his rate is believed at
  # all. Below it he is treated as not in the rotation: a rookie's first night
  # is unpredictable by construction and there is nothing to average.
  min_prior_games = 3,

  # Minutes in a regulation NBA game: 5 positions x 48 minutes. Every team's
  # projected minutes are rescaled to this, which is what stops a projection
  # from inheriting roster size or overtime from the sample.
  team_minutes = 240,

  # Seasons the calibration needs before it will predict one. Season S is
  # predicted from seasons < S, so the first season in the file is unusable.
  min_train_games = 400
)

# ===========================================================================
# 1. Player rates, from strictly prior games
# ===========================================================================

player_rates <- function(pg, window = PROJ$window) {
  pg %>%
    arrange(.data$athlete_id, .data$date) %>%
    group_by(.data$athlete_id) %>%
    mutate(
      gp_prior   = dplyr::row_number() - 1L,
      # Minutes are averaged over ALL prior games including DNPs (a zero is
      # information: it is how a bench player differs from a starter who
      # missed a night). The scoring rate is averaged over minutes actually
      # played, so a run of DNPs cannot drag a starter's rate to zero.
      min_prior  = roll_mean_prior(.data$minutes, window),
      ppm_prior  = roll_mean_prior(ifelse(.data$minutes > 0,
                                          .data$points / .data$minutes, NA_real_), window),
      played_prev = dplyr::lag(.data$played, default = FALSE)
    ) %>%
    ungroup()
}

# ===========================================================================
# 2. Team projection
# ===========================================================================
# Availability is the hard part, and the honest answer for a backtest is: use
# the previous game. Anything richer -- tonight's inactive list, the injury
# report -- is not recoverable for historical games, and reaching for it is how
# a bottom-up projection quietly becomes a description of the result.

project_team_points <- function(rates) {
  rates %>%
    filter(.data$gp_prior >= PROJ$min_prior_games,
           .data$played_prev,
           !is.na(.data$min_prior), !is.na(.data$ppm_prior)) %>%
    group_by(.data$game_id, .data$date, .data$season, .data$team) %>%
    summarise(
      rotation = dplyr::n(),
      min_sum  = sum(.data$min_prior),
      # Rescale the expected rotation to a full game, then score it. Without
      # this a night when nine players are listed and a night when fourteen are
      # would produce different totals for the same team.
      raw_pts  = if (sum(.data$min_prior) > 0)
        PROJ$team_minutes * stats::weighted.mean(.data$ppm_prior, .data$min_prior)
        else NA_real_,
      .groups = "drop"
    ) %>%
    filter(.data$rotation >= 7, !is.na(.data$raw_pts))
}

# Fold the two sides onto one row per game, matched to the betting table by
# date and teams -- hoopR's game ids and the Kaggle file's do not agree, and
# inventing a crosswalk would be a silent source of mismatches.
join_projection_to_games <- function(team_proj, g) {
  side <- function(prefix, team_col) {
    team_proj %>%
      transmute(date = .data$date, !!team_col := .data$team,
                !!paste0(prefix, "_raw") := .data$raw_pts,
                !!paste0(prefix, "_rotation") := .data$rotation)
  }

  g %>%
    filter(.data$completed) %>%
    inner_join(side("h", "home_team"), by = c("date", "home_team")) %>%
    inner_join(side("a", "away_team"), by = c("date", "away_team"))
}

# ===========================================================================
# 3. Calibration -- walk-forward, never on the season being predicted
# ===========================================================================
# The raw projection is a sum of averages: systematically flat (it cannot know
# tonight's blowout) and biased low or high depending on how the rotation
# filter lands. Two regressions fix the level, fitted on earlier seasons only:
#
#     total_points ~ (h_raw + a_raw)
#     margin       ~ (h_raw - a_raw)
#
# The margin fit absorbs home-court advantage in its intercept, which is why no
# home-court constant is hard-coded anywhere in this file.

calibrate_projection <- function(d) {
  d <- d %>% mutate(raw_total = .data$h_raw + .data$a_raw,
                    raw_margin = .data$h_raw - .data$a_raw)
  seasons <- sort(unique(d$season))
  out <- list()

  for (s in seasons) {
    train <- d %>% filter(.data$season < s)
    test  <- d %>% filter(.data$season == s)
    if (nrow(train) < PROJ$min_train_games || !nrow(test)) next

    ft <- lm(total_points ~ raw_total,  data = train)
    fm <- lm(margin       ~ raw_margin, data = train)
    test$pred_total  <- as.numeric(predict(ft, newdata = test))
    test$pred_margin <- as.numeric(predict(fm, newdata = test))
    out[[as.character(s)]] <- test
  }

  if (!length(out)) {
    warn("not enough prior seasons of player data to calibrate -- ",
         "need two seasons of box scores, have ", length(seasons))
    return(NULL)
  }
  bind_rows(out)
}

# ===========================================================================
# 4. Run it
# ===========================================================================

build_player_projection <- function(pg = NULL, g = NULL) {
  step("Player-level projection")
  # Prefer the deep file. One season of box scores leaves a single testable
  # season after calibration, and a single-season encompassing result is not
  # worth reporting -- the per-season sign check has nothing to check.
  pg <- pg %||% {
    deep <- file.path(CFG$paths$processed_dir, "player_games_multi.rds")
    p <- if (file.exists(deep)) deep else file.path(CFG$paths$processed_dir, "player_games.rds")
    if (!file.exists(p))
      stop("no player box scores. Run:\n",
           '  pg <- load_player_games(seasons = 2017:', season_of(Sys.Date()), ')\n',
           '  saveRDS(pg, "', deep, '")', call. = FALSE)
    readRDS(p)
  }
  g <- g %||% readRDS(CFG$paths$games_rds)

  info(nrow(pg), " player-games over seasons ",
       paste(range(pg$season), collapse = "-"))

  team_proj <- project_team_points(player_rates(pg))
  info(nrow(team_proj), " team-games projected from prior-game rates")

  joined <- join_projection_to_games(team_proj, g)
  info(nrow(joined), " of those matched a game with a closing line")
  if (!nrow(joined)) { warn("no overlap between box scores and the betting file"); return(NULL) }

  calibrate_projection(joined)
}

player_projection_report <- function(d = build_player_projection()) {
  if (is.null(d) || !nrow(d)) return(invisible(NULL))

  step("Player projection vs the closing line")
  info("testing on ", nrow(d), " games, seasons ",
       paste(sort(unique(d$season)), collapse = ", "))
  info("accuracy first -- the projection is expected to be WORSE than the line; ",
       "the encompassing test below is the one that matters")

  for (tg in c("total", "margin")) {
    actual <- if (tg == "total") d$total_points else d$margin
    model  <- if (tg == "total") d$pred_total else d$pred_margin
    market <- if (tg == "total") d$total_close else -d$spread_close
    keep <- is.finite(actual) & is.finite(model) & is.finite(market)
    info(sprintf("%-7s RMSE  market %6.2f   player projection %6.2f   corr %.3f",
                 tg, rmse(actual[keep], market[keep]),
                 rmse(actual[keep], model[keep]),
                 cor(model[keep], market[keep])))
  }

  # The comparison that decides whether this was worth building: 02's team-form
  # model sits at 0.88-0.95 correlation with the line. A bottom-up projection
  # that lands materially below that is at least a different view of the game,
  # whatever its accuracy.
  enc <- encompassing_report(d)
  invisible(list(data = d, encompassing = enc))
}

if (identical(environment(), globalenv()) &&
    !isTRUE(getOption("nba.schema_only", FALSE)) &&
    sys.nframe() == 0) {
  player_projection <- player_projection_report()
}
