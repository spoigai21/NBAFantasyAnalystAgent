#!/usr/bin/env python3
"""Two rankings, kept strictly apart: CURRENT value and PROJECTED value.

Why this exists -- user, 11 Nov 2026:

    "theres 2 types of values: 1. current value 2. projected value. Your not usin
    either of these your switching between 2 whenever convenient and random."

He was right. Across one session I priced Paul George at 44.6 ("producing"), ~33.5
("minutes-adjusted fair value") and 36.9 ("projection") and picked whichever suited the
argument. That is not a valuation, it is rhetoric. This file replaces all of it with two
numbers, one formula each, applied to every player, and re-runnable nightly.

    CURRENT   = ESPN applied fantasy points per game, actual, this season. Nothing else.
                No injury adjustment, no minutes adjustment, no projection blended in.
                It answers: what has this player ACTUALLY DONE.

    PROJECTED = rest-of-season per-game estimate. It answers: what WILL he do.
                No injury adjustment at all (user: "dont look at injuries at all
                just what are the values projected to be").

Injuries enter ONLY in trade mode, ONLY on the current list -- user: "if theres an
injury concern discount 10-15 spots of value mean drop the player down 5 reankings ONLY
in the case of trade evalutations." He gave two numbers (10-15, and 5), so this reads it
as severity-tiered and both are command-line flags:
    day-to-day / questionable -> -5 spots      (--dtd-penalty)
    out / IR / suspended      -> -12 spots     (--out-penalty)

------------------------------------------------------------------------------------
THE PROJECTED FORMULA, AND THE TWO MEASUREMENTS BEHIND IT (both run 11 Nov 2026)
------------------------------------------------------------------------------------
    proj_adj   = K_PROJ * proj_full            # rule 8 bonus-corrected, rule 28 bias fix
    projected  = (gp * actual_pg + W_PRIOR * proj_adj) / (gp + W_PRIOR)

1. K_PROJ = 0.905 SURVIVED RE-MEASUREMENT. Rule 28 warned the multiplier shrinks as the
   season goes on and quoted a re-derived 0.939. On a clean temporal holdout today (fit
   periods 1-18 = 960 games, test 19-22 = 199 games, zero overlap) the fitted value is
   **0.903**, out-of-sample MAE 11.956 against 11.962 for the stored 0.905 and 12.627 for
   the raw projection. Mean signed error at 0.905 is +0.128, i.e. unbiased. So 0.939 does
   NOT replicate and the stored constant is right. Keep it.

2. SHRINKING THE PROJECTION TOWARD ACTUALS NOW HELPS -- WHICH REVERSES RULE 28.
   Rule 28 says "Per-player corrections FAIL -- do not rebuild them", measured when
   players had ~5 games. At ~11 games the sample carries real signal. Same holdout,
   out-of-sample MAE against a 9.857 baseline:

       prior weight W   2      3      4      5      6      8     10     14
       fit<=16        +3.1%  +3.9%  +4.4%  +4.8%  +4.9%  +4.9%  +4.6%  +4.0%
       fit<=18        +5.7%  +6.1%  +6.3%  +6.5%  +6.5%  +6.3%  +6.0%  +5.4%

   W = 6 is optimal in both windows, so that is the default. Rule 28's finding was a
   sample-size effect, not a permanent truth. **Re-run --validate monthly**: as GP grows
   the optimum W should keep falling, and if it ever goes flat the shrinkage is done.

3. ⚠ THE MINUTES ADJUSTMENT I USED ALL SESSION DOES NOT WORK. MEASURED AND DROPPED.
   Multiplying the projection by realized-mpg / projected-mpg -- the "minutes-adjusted
   fair value" I quoted for Paul George (~33.5), LaMelo (~37.8), Coward (~29.6) and
   Garland (~36.0) -- buys **+0.3%** MAE (9.857 -> 9.824) and *adds* +0.80 of bias.
   Down-only is worse (+1.63 bias). Half-weighted on top of the shrinkage it LOSES 1.6pp.
   Individual cases show why: Josh Giddey at a 0.77 minutes ratio went on to score 59.0
   a game while the adjustment predicted 35.8. **Minutes are diagnostic context (rule 22,
   rule 31) and are printed as a column, but they are never multiplied into a value.**

------------------------------------------------------------------------------------
LLOYD AND OUTSIDE ANALYSTS
------------------------------------------------------------------------------------
Lloyd anchors are hand-verified only, and the automated pass is why: a regex over 1,376
segmented notes produced ~16 candidate ranks for my own players and **4 were
misattributions** -- "top 150" tagged to Ryan Rollins is Kel'el Ware, "top 50" tagged to
Murray-Boyles is Miles Bridges, "top 10" tagged to VanVleet is Alperen Sengun, and
"top 60" tagged to Wembanyama is a guard with three point guards ahead of him. Rule 19:
a clean grep licenses the words, never the subject. Every entry below was read in full.

⚠ SCALE: Lloyd and the outside lists rank the whole NBA (~200 players); this ranks the
128 players rostered in a 9-team league. The scales track closely at the top and drift
apart lower down -- validated below -- so they are compared, never substituted.

Usage:
    . ~/.espn-fantasy.env && python3 fantasy/rankings.py             # both lists
    python3 fantasy/rankings.py --trade                              # injury discount on
    python3 fantasy/rankings.py --player "Paul George"               # one player, both
    python3 fantasy/rankings.py --mine                               # my roster only
    python3 fantasy/rankings.py --validate                           # refit W and K
"""
import argparse, json, os, sqlite3, subprocess, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "league.db")
MD_OUT = os.path.join(HERE, "rankings.md")
LEAGUE, SEASON = "1858125890", "2027"
BASE = (f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/fba/seasons/{SEASON}"
        f"/segments/0/leagues/{LEAGUE}")

K_PROJ = 0.905   # rule 28, re-verified 11 Nov 2026 at 0.903 on a clean holdout
W_PRIOR = 6      # games of projection-as-prior; fitted, optimal in both holdout windows
MIN_GP = 5       # below this a per-game average is not a performance read (rules 12, 27)

# Hand-verified Lloyd rank statements. Each was read in full with the sentences on both
# sides to confirm the subject (rule 19). kind: "curr" = where he says the player IS,
# "proj" = where he says the player is GOING. Anything ambiguous was left out.
LLOYD = {
    "Anthony Davis":        [("2026-11-09", "curr", 10,
        "Do you know he's the 10th ranked player per game this season?"),
                             ("2026-11-05", "proj", 22,
        "I thought Anthony Davis could be a top 25 per game player... certainly top 20, top 25")],
    "Paul George":          [("2026-11-10", "curr", 25,
        "He's a top 25 player this season. He's top 15 over the last two weeks."),
                             ("2026-11-10", "proj", 28,
        "I said I thought he could beat top 30 per game this season... I just take what I get")],
    "Damian Lillard":       [("2026-11-10", "curr", 90,
        "He's top 90 on the season."),
                             ("2026-11-10", "proj", 30,
        "I feel like he's going to get to top 30 this year.")],
    "Zach LaVine":          [("2026-10-30", "proj", 65,
        "I had him in the 80s heading into the season. I've adjusted that to top 65.")],
    # ⚠ The 9 Nov Edey line reads like a current rank and is NOT one. "we've seen him BE"
    # plus "at the moment is not moving in that direction" is the level he could return
    # to, i.e. a projection. Filed as curr on the first pass, it showed a 47-spot gap to
    # my #107 and the gap was my labelling, not a disagreement.
    "Zach Edey":            [("2026-11-09", "proj", 60,
        "we've seen him be a top 60ish sort of player, but at the moment is not moving in "
        "that direction anywhere near fast enough for me"),
                             ("2026-10-29", "proj", 60,
        "Edy could be a top 30 player if he played 30 minutes a night but I don't think "
        "he's going to get there"),
    # 11 Nov is the FIRST actual current rank he has given Edey, and it is the floor of
    # the roster: 167th, named as "unquestionably bad", with the mechanism being usage
    # ("11 usage only for Edy... as guys like Boozer, Jerome, and Coward get most of the
    # stuff"). He still says hold, on replacement-level grounds, not on upside.
                             ("2026-11-11", "curr", 167,
        "In all of this, in all of the suck... he's 167th. If your league has two IL "
        "slots, that's still a 12 team league guy."),
    # 12 Nov mailbag: he puts a DEADLINE on it, which no earlier Edey note does. Not a
    # rank -- stored as proj 60 to keep the band, but the load-bearing part is the clock:
    # ~3 Dec 2026. The mechanism he names is the same one our grader prints (minutes and
    # usage, both coach-controlled, neither reverting on its own -- rule 27).
                             ("2026-12-03", "proj", 60,
        "I'm giving him patience to see if the minutes and usage increase in the next 3 "
        "weeks. Simple as that. And if it doesn't happen, we take the L and move on... "
        "it's confusing how low the minutes in usage are")],
    "LaMelo Ball":          [("2026-11-08", "curr", 54,
        "He's now up to 54th on the season after a dreadful start.")],
    "Karl-Anthony Towns":   [("2026-11-11", "curr", 13,
        "another big one from Towns, who's the 13th ranked player, 21-11, eight assists. "
        "I think that's 11 consecutive double doubles for him."),
                             ("2026-10-28", "curr", 12,
        "Towns is now up to 12th on the season.")],
    "Darius Garland":       [("2026-11-02", "curr", 84,
        "He's 84th for the year. That's not great.")],
    "Cedric Coward":        [("2026-11-11", "curr", 70,
        "the chicken Cedric Coward. Kacha 70th ranked player over the course of the "
        "season. A bit of a bargain on where he was drafted."),
                             ("2026-11-04", "curr", 60,
        "the chicken Cedric Coward he's now top 60, 23 and N and four steals")],
    "Fred VanVleet":        [("2026-10-29", "curr", 75,
        "He's been incredibly up and down, but top 75 so far.")],
    # ⚠ THE 29 OCT ANCHOR IS NO LONGER THE STALE ONE RULE 32 CALLED IT. 12 Nov mailbag
    # re-asked and he went HIGHER, and he gave it knowing Miller is hurt -- in the same
    # episode he says "Allen is dependent on the absence of Canipple and and Miller at
    # the moment". So the injury is priced in, not overlooked. It is a ROS projection,
    # not a current rank, hence kind "proj" (rule 32's labelling trap).
    "Brandon Miller":       [("2026-11-12", "proj", 25,
        "where do I have Brandon Miller projected rest of season? I also talked about "
        "this on the B low show earlier in the week. Uh, pretty high. Like top 25, I "
        "think. Yeah, pretty high."),
                             ("2026-10-29", "curr", 30,
        "his first couple of games were bad, but he is now inside the top 30")],
    # ⚠ "over the last two weeks" is a RECENT-FORM window, not a season rank. Compared
    # against my season-to-date #71 it looked like a 34-spot disagreement; it is a
    # different measurement. kind "curr2w" prints but is excluded from the season check.
    # 11 Nov got WORSE, not better -- the 9 Nov read was already outside 100, this is
    # outside 140, and Lloyd names the mechanism: he is not being given the ball.
    "Dejounte Murray":      [("2026-11-09", "curr2w", 105,
        "He's outside the top 100 over the last two weeks."),
                             ("2026-11-11", "curr2w", 145,
        "Murray is now outside the top 140 over the last two weeks despite playing over "
        "30 minutes a night because he's just never getting the ball.")],

    # ------------------------------------------------------------------------------
    # 2026-11-11 Wednesday recap (10 games). 26 explicit ranks, every one verified with
    # verify.py against fantasy/transcripts/2026-11-11_recap-wednesday.txt.
    #
    # ⚠ FORMAT WARNING, and it is visible right at the top of the board. Lloyd flags
    # Jokic as "the second ranked player overall IN CATEGORY LEAGUES" and puts Wembanyama
    # 3rd. Our points list has Wembanyama clearly 1st (74.2/g against Jokic's 66.8) --
    # because STL/BLK +4 and our DD/OREB/GP bonuses pay Wembanyama far more than 8-cat
    # does. So his season ranks in a daily recap are CATEGORY-FLAVOURED unless he says
    # otherwise, which is rule 24: use them for direction and for mechanism, never as a
    # points rank. Jokic's is deliberately NOT stored, because it is explicitly a
    # category rank and would corrupt the validation it is supposed to check.
    # ------------------------------------------------------------------------------
    "Victor Wembanyama":    [("2026-11-11", "curr", 3,
        "He's the number three ranked player over the course of the season.")],
    "Jamal Murray":         [("2026-11-11", "curr", 10,
        "he is now 10th for the season, sixth over the last two weeks"),
                             ("2026-11-11", "curr2w", 6,
        "he is now 10th for the season, sixth over the last two weeks")],
    "Shai Gilgeous-Alexander": [("2026-11-11", "curr", 18,
        "the struggles of Shay Gudis Alexander continue. Is he a buy low? Like he "
        "probably is... he's 18th which is still great but it's not top four")],
    "Zion Williamson":      [("2026-11-11", "curr", 25,
        "I do think that he is a sell high, but he is like a top 25 player this season.")],
    # ⚠ RULE 19 CAUGHT ONE BEFORE IT SHIPPED. I first filed this under Jonathan Kuminga
    # because the captioner writes "Yakel" and the passage is the Warriors recap. Kuminga
    # plays for MINNESOTA this season. "Yakel" is Yaxel Lendeborg (GSW rookie), which the
    # rest of the passage confirms -- "I was very in on drafting him after seeing like one
    # preseason game... we're taking him in the 90s". The numbers settle it: Lendeborg is
    # 43.1/g and my #26, which IS a top-25 player; Kuminga is 30.8/g and my #91, which is
    # not. Mis-filed it would have printed a phantom 66-spot disagreement.
    "Yaxel Lendeborg":      [("2026-11-11", "curr", 25,
        "I'm still massively wrong because this is a top 25 player... if you're selling "
        "high, if I don't get a top 15 player back, I'm not doing it")],
    "Franz Wagner":         [("2026-11-11", "curr2w", 20,
        "France Vagner, who is doing everything... Top 20 player over the last two "
        "weeks.")],
    "Pascal Siakam":        [("2026-11-11", "curr2w", 30,
        "he is flying at the moment. Top 30 player over the last two weeks, putting up "
        "really monster numbers.")],
    "Brandin Podziemski":   [("2026-11-11", "curr", 50,
        "He's been pretty good as well. Very good. In fact, top 50 player on the "
        "season.")],
    "Stephen Curry":        [("2026-11-11", "curr", 4,
        "Steph was a top four fantasy player and Melton's not going to do that sort of "
        "stuff")],
    "James Harden":         [("2026-11-11", "curr", 57,
        "He had 44 fantasy points. He's now up to 57th for the year. I don't expect a "
        "top 30 finish from him")],
    "Jalen Brunson":        [("2026-11-11", "proj", 50,
        "He's not going to get to be a top 30 player. That's not going to happen. But "
        "back inside the top 50 is probable.")],
    "OG Anunoby":           [("2026-11-11", "curr", 62,
        "He's still like just doing enough. two steals, a block, 62nd ranked player.")],
    "De'Aaron Fox":         [("2026-11-11", "curr", 70,
        "Darren Fox also has turned into a bit of a draft day bargain. He is a top 70 "
        "player on the year.")],
    "Dylan Harper":         [("2026-11-11", "curr", 60,
        "He looks completely solid as a starter. Almost a top 60 player so far. Minutes "
        "were pushing way up.")],
    "Jalen Smith":          [("2026-11-11", "curr", 82,
        "He's 82nd for the season, 50th over the last two weeks. He is a must roster "
        "player."),
                             ("2026-11-11", "curr2w", 50,
        "He's 82nd for the season, 50th over the last two weeks.")],
    "Isaiah Hartenstein":   [("2026-11-11", "curr2w", 80,
        "a big offensive game from Isaiah Hartenstein, who'd been missing every shot "
        "possible... He's inside the top 80 over the last two weeks.")],
    "Jeremiah Fears":       [("2026-11-11", "curr2w", 50,
        "he's the 50th best player over the last two weeks. Like you'll take it. "
        "Absolutely a must roster player.")],
    "Derik Queen":          [("2026-11-11", "curr", 100,
        "he's still like a top 100 player for the season in limited minutes")],
    "Stephon Castle":       [("2026-11-11", "curr", 105,
        "He's outside the top 100 now for fantasy... I will tell you that I think it is "
        "a buy low on Castle, but a lot of the concerns that I had with him as a player "
        "are showing up")],
    "Toumani Camara":       [("2026-11-11", "curr", 130,
        "he probably is a 12 team league guy, although not really a top 130 player so "
        "far this season")],
    "AJ Dybantsa":          [("2026-11-11", "curr", 145,
        "He's now back outside the top 140, 13 and five... I don't think he's going to "
        "be a top 100 player this season.")],
    "Payton Pritchard":     [("2026-11-11", "curr", 145,
        "Pritchard remains outside the top 140 for the season."),
                             ("2026-11-11", "proj", 120,
        "He probably gets inside the top 120, but I'm not going to guarantee that.")],
    "Matas Buzelis":        [("2026-11-11", "curr", 153,
        "Gizales is now 153rd for the season. So again, still beholding him. The minutes "
        "looked a bit better here, but it's still not great.")],
    "Mikal Bridges":        [("2026-11-11", "curr", 205,
        "He's outside the top 200 for this season.")],
}

# Lloyd anchors older than this many days are printed with a staleness marker. Brandon
# Miller's "inside the top 30" is 29 Oct and he has since left a game injured, which is
# why his anchor sits 53 spots above his production -- stale, not wrong.
STALE_DAYS = 7

# Jacob Dunne, Fantrax, "Rest of the Season Points League Rankings: November Edition",
# published 3 Nov 2026. In analysts.md's tier for points-specific reads. ⚠ RULE 24: this
# is GENERIC points scoring -- it does not carry our STL/BLK +4 premium or any of our
# DD/TD/OREB/GP/TW bonuses, so it is a cross-check on DIRECTION, never a rank to borrow.
DUNNE = {
    "Nikola Jokic": 1, "Victor Wembanyama": 2, "Luka Doncic": 3,
    "Giannis Antetokounmpo": 4, "Shai Gilgeous-Alexander": 5, "Tyrese Maxey": 6,
    "Jayson Tatum": 7, "Cooper Flagg": 8, "Cade Cunningham": 9, "Jalen Johnson": 10,
    "Scottie Barnes": 11, "Domantas Sabonis": 12, "Brandon Miller": 13,
    "Alperen Sengun": 14, "Karl-Anthony Towns": 15, "Amen Thompson": 16,
    "Jalen Brunson": 17, "Jamal Murray": 18, "Pascal Siakam": 19, "Trae Young": 20,
    "Kevin Durant": 21, "Walker Kessler": 22, "Austin Reaves": 23,
    "Donovan Mitchell": 24, "Cameron Boozer": 25, "Evan Mobley": 26,
    "Bam Adebayo": 27, "Anthony Davis": 28, "Zion Williamson": 29,
    "Lauri Markkanen": 30, "Jaylen Brown": 31, "Nickeil Alexander-Walker": 32,
    "Dejounte Murray": 33, "Franz Wagner": 34, "Julius Randle": 35, "Jalen Duren": 36,
    "Michael Porter Jr.": 37, "De'Aaron Fox": 38, "Devin Booker": 39,
    "Stephen Curry": 40, "Darius Acuff Jr.": 41, "Caleb Wilson": 42,
    "Yaxel Lendeborg": 43, "Dyson Daniels": 44, "Naz Reid": 45, "Paolo Banchero": 46,
    "Josh Giddey": 47, "Tyler Herro": 48, "Donovan Clingan": 49, "LaMelo Ball": 50,
    "Jarrett Allen": 51, "Kawhi Leonard": 52, "Deni Avdija": 53, "Keyonte George": 54,
    "Dylan Harper": 55, "Ty Jerome": 56, "Cedric Coward": 57, "Trey Murphy III": 58,
    "Immanuel Quickley": 59, "Jonathan Kuminga": 60, "Onyeka Okongwu": 61,
    "LeBron James": 62, "Joel Embiid": 63, "Anthony Edwards": 64, "James Harden": 65,
    "Miles Bridges": 66, "Ajay Mitchell": 67, "Tyrese Haliburton": 68,
    "Kon Knueppel": 69, "Ryan Rollins": 70, "Stephon Castle": 71, "Kyrie Irving": 72,
    "Ivica Zubac": 73, "Darius Garland": 74, "Desmond Bane": 75, "Coby White": 76,
    "Damian Lillard": 77, "Darryn Peterson": 78, "Davion Mitchell": 79,
    "Jaden McDaniels": 80, "Norman Powell": 81, "RJ Barrett": 82, "Derrick White": 83,
    "Paul George": 84, "Jabari Smith Jr.": 85, "Nic Claxton": 86, "Jalen Green": 87,
    "OG Anunoby": 88, "Andrew Nembhard": 89, "Derik Queen": 90, "Kris Dunn": 91,
    "Wendell Carter Jr.": 92, "Moussa Diabate": 93, "Ausar Thompson": 94,
    "Brandin Podziemski": 95, "Jaime Jaquez Jr.": 96, "Zach LaVine": 97,
    "Jusuf Nurkic": 98, "Payton Pritchard": 99, "Alex Sarr": 100, "Rudy Gobert": 101,
    "Isaiah Hartenstein": 102, "Duncan Robinson": 103, "VJ Edgecombe": 104,
    "Aaron Wiggins": 105, "Zach Edey": 106, "Anthony Black": 107,
    "Jeremiah Fears": 108, "Day'Ron Sharpe": 109, "Kel'el Ware": 110,
    "Matas Buzelis": 111, "Jalen Suggs": 112, "Rui Hachimura": 113,
    "Andrew Wiggins": 114, "Brandon Ingram": 115, "Jrue Holiday": 116,
    "Ayo Dosunmu": 117, "AJ Dybantsa": 118, "Myles Turner": 119, "CJ McCollum": 120,
    "Peyton Watson": 121, "Chet Holmgren": 122, "Fred VanVleet": 123,
    "Mikal Bridges": 124, "P.J. Washington": 125, "Devin Vassell": 126,
    "Christian Braun": 127, "Ace Bailey": 128, "Zaccharie Risacher": 129,
    "Kyshawn George": 130, "Daniel Gafford": 131, "Isaiah Jackson": 132,
    "Aaron Gordon": 133, "John Collins": 134, "Josh Hart": 135, "Grayson Allen": 136,
    "Keegan Murray": 137, "Tari Eason": 138, "Collin Murray-Boyles": 139,
    "Scoot Henderson": 140, "Alex Caruso": 142, "Jared McCain": 145,
    "Toumani Camara": 146, "Ja Morant": 147, "Jaren Jackson Jr.": 150,
    "Draymond Green": 151, "Dillon Brooks": 153, "Paul Reed": 157, "Jakob Poeltl": 160,
    "Saddiq Bey": 162, "Jalen Smith": 172, "Reed Sheppard": 173, "Jaylen Wells": 178,
    "Brook Lopez": 187, "Daniss Jenkins": 188, "Jimmy Butler III": 200,
}

OUT_FLAGS = {"OUT", "INJURY_RESERVE", "SUSPENSION", "NOT_ACTIVE"}
DTD_FLAGS = {"DAY_TO_DAY", "QUESTIONABLE", "DOUBTFUL"}

# ---------------------------------------------------------------------------------
# FORM: the last-14-days window, and the buy-low screen built on it.
#
# User, 11 Nov 2026: "for the over the last 2 weeks he is ... this basicalyl should be
# done by you when understand buy lows as well. Over the last 2 weeks is this player
# blowing his projections out of the park."
#
# ⚠ THIS IS NOT A THIRD VALUE. Current value has two WINDOWS -- season-to-date and the
# last 14 days -- and both answer "what has he done". Projected value stays the single
# forward number. Two kinds of value, one of them available at two windows.
#
# MEASURED 11 Nov 2026 on 659 player-weeks (4+ games in the window, 2+ games forward),
# and it corrects the naive buy-low story:
#
#   1. A GAP PERSISTS, IT DOES NOT REVERT TO PROJECTION. Correlation between the 2-week
#      gap and the next week's gap is +0.272 absolute, +0.330 as a share of the player's
#      own projection. Relative is the better predictor and is scale-free, so the signals
#      below are cut on PERCENTAGE of projection -- a flat 4/g gate called Wembanyama a
#      sell-high off a 6% wobble.
#
#   2. MINUTES ARE THE GATE ON THE DOWNSIDE -- rule 31's split, measured. "Holds" = how
#      much of the gap was still there the following week, so LOW is good for a buy-low:
#
#        threshold          minutes intact (>=.90)      minutes down (<.90)
#        under by 4+/g      holds   1%  (n=84)          holds  45%  (n=80)
#        under by 6+/g      holds   8%  (n=53)          holds  47%  (n=62)
#        under by 10%+      holds  14%  (n=78)          holds  46%  (n=88)
#        under by 15%+      holds  41%  (n=48)          holds  42%  (n=73)
#        under by 20%+      holds  44%  (n=28)          holds  47%  (n=61)
#
#      ⚠ THE GATE WORKS ON MODERATE SHORTFALLS AND DIES ON EXTREME ONES. At 10% under,
#      minutes-intact shortfalls almost entirely wash out (14% persists) while
#      minutes-down ones stick (46%). At 20% under the two are identical (44% vs 47%) --
#      a player that far below his projection with "intact" minutes has something else
#      wrong, so it is NOT a buy. Hence the BAND in the signal: a buy-low is a moderate
#      shortfall with the minutes still there, never a collapse.
#
#   3. SELL HIGH IS THE STRONGEST AND MOST ROBUST SIGNAL HERE -- it holds at every
#      threshold tested, which the buy-low does not:
#
#        over by 4+/g       minutes >= proj: holds 57% (n=128)   minutes < proj: 39% (n=72)
#        over by 10%+                        holds 62% (n=137)                   36% (n=73)
#        over by 15%+                        holds 63% (n=117)                   11% (n=45)
#        over by 20%+                        holds 64% (n=85)                    23% (n=22)
#
#      An overperformance built on MORE minutes than projected is ~60% real and you keep
#      him. The same overperformance on FEWER minutes than projected almost completely
#      evaporates. That is the sell.
#
# ⚠⚠ HONEST LIMIT, 11 Nov 2026: the season is 21 days old, so at every date that leaves a
# forward window the 14-day span IS every game played. "Last two weeks" and "this season"
# are the same games today, and the window only becomes a distinct signal around late
# November. Recency weighting is therefore UNTESTABLE right now -- season-actuals and
# last-14 shrinkage returned byte-identical MAE (7.390). Re-run --validate then.
FORM_DAYS = 14
FORM_MIN_GAMES = 3      # below this the window is not a read (rules 12, 27)
FORM_REL = 0.10         # 10% of his own projection before the window says anything
FORM_DEEP = 0.20        # past this the buy-low gate stops working -- no edge, not a buy
MINS_INTACT = 0.90      # measured gate between "the shortfall washes out" and "it sticks"
# ⚠ ADDED 12 Nov 2026, and the user had to point it out: the screen tested MINUTES ONLY,
# so a player who kept his minutes and lost his TOUCHES was being filed as a reverting
# slump. Rule 27 has said since 26 Oct that usage is a separate coach-controlled axis that
# does NOT revert -- I built the form screen without it. Dejounte Murray was the case:
# 31.2 mpg (intact) on a usage ratio of 0.49, four FROZEN games in five, and the screen
# said "SLUMP (no edge)". User, 12 Nov: "dejounte is not even a slump itts reduce role?"
# Measured on 1,104 player-weeks (14-day window, 4+ games in it, 2+ games after):
#   10%+ under own projection WITH minutes intact, all of them ......  31% persists
#     of those, usage DOWN (<0.90) .................................  90% persists
#     of those, usage INTACT ........................................   4% persists
# That is a cleaner split than the minutes gate itself (65% vs 31%), i.e. USAGE IS THE
# STRONGER OF THE TWO COACH-CONTROLLED AXES. Threshold set to 0.90 for symmetry with
# MINS_INTACT, NOT fitted -- and the direction holds at every cut tested (0.80 +25pp,
# 0.85 +59pp, 0.90 +85pp, 0.95 +39pp), so the gate is robust even though the exact
# number is not pinned down at this n.
USG_INTACT = 0.90       # below this the touches went, not the touch -> FADE (usage)


def fetch(url):
    s2, swid = os.environ.get("ESPN_S2"), os.environ.get("ESPN_SWID")
    if not (s2 and swid):
        sys.exit("ESPN_S2 and ESPN_SWID are not set. . ~/.espn-fantasy.env first.")
    r = subprocess.run(["curl", "-s", "-H", f"cookie: espn_s2={s2}; SWID={swid}", url],
                       capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        sys.exit("Bad response (a 401 means the cookies expired -- ask the user to "
                 f"refresh them, never read them out of Chrome):\n{r.stdout[:300]}")


def live_roster():
    """Who is rostered RIGHT NOW, with injury flag. Never trust the players table for
    this -- CLAUDE.md's standing-weaknesses section went stale twice in 48 hours."""
    d = fetch(BASE + "?view=mRoster&view=mTeam")
    teams = {t["id"]: (t.get("name") or t.get("abbrev")) for t in d.get("teams", [])}
    out = {}
    for t in d.get("teams", []):
        for e in t["roster"]["entries"]:
            p = e["playerPoolEntry"]["player"]
            out[p["fullName"]] = {
                "team": teams.get(t["id"]), "team_id": t["id"],
                "injury": p.get("injuryStatus", "ACTIVE"),
                "slot": e.get("lineupSlotId"),
            }
    return out


def load(roster, min_gp=MIN_GP, w_prior=W_PRIOR):
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    rows = []
    for r in db.execute("SELECT name, gp, per_game, mpg, proj_mpg, proj_full FROM players"):
        if r["name"] not in roster or not r["proj_full"]:
            continue
        gp = r["gp"] or 0
        cur = r["per_game"] or 0.0
        proj_adj = K_PROJ * r["proj_full"]
        projected = ((gp * cur + w_prior * proj_adj) / (gp + w_prior)) if gp else proj_adj
        info = roster[r["name"]]
        rows.append({
            "name": r["name"], "fteam": info["team"], "injury": info["injury"],
            "gp": gp, "mpg": r["mpg"] or 0.0, "proj_mpg": r["proj_mpg"] or 0.0,
            "current": cur, "projected": projected, "proj_adj": proj_adj,
            "enough": gp >= min_gp,
        })
    return rows


def add_form(rows, days=FORM_DAYS):
    """Last-`days` window per player, plus the measured buy-low / sell-high screen."""
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    last = db.execute("SELECT MAX(date) d FROM game_grades").fetchone()["d"]
    lo = (datetime.date.fromisoformat(last) - datetime.timedelta(days=days - 1)).isoformat()
    agg = {r["player"]: r for r in db.execute(
        """SELECT player, COUNT(*) n, AVG(fpts) fpts, AVG(min_ratio) mr, AVG(min) mins,
                  AVG(usg_ratio) ur
           FROM game_grades WHERE date >= ? AND fpts IS NOT NULL
           GROUP BY player""", (lo,))}
    for r in rows:
        a = agg.get(r["name"])
        r["form_from"], r["form_to"] = lo, last
        if not a or a["n"] < FORM_MIN_GAMES:
            r.update(form=None, form_n=(a["n"] if a else 0), form_gap=None,
                     form_mr=None, form_ur=None, signal="—")
            continue
        gap = a["fpts"] - r["proj_adj"]
        rel = gap / r["proj_adj"] if r["proj_adj"] else 0.0
        mr = a["mr"] or 0.0
        ur = a["ur"]
        # ⚠ INJURY GATE -- rule 27's confounder, which this screen did not consult at all
        # until 12 Nov 2026. Rule 27 has said since 26 Oct that injury "is not a fourth
        # axis, it is the confounder" and that it "INVALIDATES the other three", and the
        # signal block below read only rate, minutes and usage. So a hurt player got a
        # coach-decision label for a medical absence.
        # Caught on Brandon Miller: he printed FADE (minutes) because his last-14 window
        # holds a 14-minute game he LEFT with a groin strain plus the games he then
        # missed. Nothing about his role changed -- Charlotte's own note says he "injured
        # his groin during the 119-80 loss to Boston". Same shape as the usage hole the
        # user found the day before: an axis the screen cannot see, mislabelled as one it
        # can. Rule 31's triage table puts INJURY in the top row for the same reason --
        # "triage stops here", before minutes are even read.
        # ⚠ HONEST LIMIT: this is a VALIDITY gate, not a fitted threshold, and it is
        # UNMEASURED. It cannot be backtested here because neither game_grades nor
        # player_form stores the injury flag per game -- `rankings.injury` only starts
        # 11 Nov 2026. It makes no prediction; it withholds one. Do not quote a
        # persistence number for it, and if per-game injury status ever gets stored,
        # measure whether OUT/DTD weeks really do behave unlike healthy ones.
        # ⚠ TWO TIERS, because the flag is CURRENT status and the window is the LAST 14
        # DAYS, and those are not the same question. First pass voided both OUT and DTD
        # and that was too blunt: it killed Paul George's reading on a DTD that arrived
        # the day AFTER the six games in his window were played. So:
        #   OUT / IR   -> void. He is not playing; there is no role to read.
        #   DTD        -> keep the signal, mark it provisional. He may yet play.
        # This still does not know whether the INJURY IS INSIDE THE WINDOW, which is the
        # question that actually matters -- Miller's is (he left a game in it and missed
        # two more), Curry's is not. Storing a per-game injury flag in game_grades would
        # fix it properly; until then the gate is coarse and errs toward withholding.
        if r["injury"] in OUT_FLAGS:
            r.update(form=a["fpts"], form_n=a["n"], form_gap=gap, form_rel=rel,
                     form_mr=mr, form_ur=ur, form_mins=a["mins"],
                     signal="INJURED (void)")
            continue
        dtd = r["injury"] in DTD_FLAGS
        if rel <= -FORM_REL:
            if mr < MINS_INTACT:
                sig = "FADE (minutes)"          # 65% of it sticks -- that part is the role
            elif ur is not None and ur < USG_INTACT:
                sig = "FADE (usage)"            # 90% sticks. The touches went, not the touch
            elif rel <= -FORM_DEEP:
                sig = "SLUMP (no edge)"         # 50% sticks even with role intact
            else:
                sig = "BUY LOW"                 # only 7% sticks -- it washes out
        elif rel >= FORM_REL:
            # minutes >= projection: ~62% is real, keep him. Below projection: it goes.
            sig = "RIDE" if mr >= 1.0 else "SELL HIGH"
        else:
            sig = "HOLD"
        r.update(form=a["fpts"], form_n=a["n"], form_gap=gap, form_rel=rel, form_mr=mr,
                 form_ur=ur, form_mins=a["mins"], signal=sig, form_dtd=dtd)
    pool = [r for r in rows if r.get("form") is not None]
    for i, r in enumerate(sorted(pool, key=lambda x: -x["form"]), 1):
        r["form_rank"] = i
    return pool


def rank(rows, key, only_enough=True):
    pool = [r for r in rows if r["enough"]] if only_enough else rows
    for i, r in enumerate(sorted(pool, key=lambda x: -x[key]), 1):
        r[key + "_rank"] = i
    return pool


def apply_trade_discount(rows, dtd, out_pen):
    """Injury discount -- TRADE MODE ONLY, CURRENT LIST ONLY. A spot penalty, not a
    points penalty, because that is how the user expressed it."""
    ranked = sorted([r for r in rows if r["enough"]], key=lambda x: -x["current"])
    n = len(ranked)
    for r in ranked:
        pen = out_pen if r["injury"] in OUT_FLAGS else dtd if r["injury"] in DTD_FLAGS else 0
        r["inj_penalty"] = pen
        r["trade_rank"] = min(n, r["current_rank"] + pen)
    # resolve collisions so the discounted order is a strict ranking
    for i, r in enumerate(sorted(ranked, key=lambda x: (x["trade_rank"], x["current_rank"])), 1):
        r["trade_rank"] = i
    return ranked


def validate():
    """Refit K_PROJ and W_PRIOR on a temporal holdout. Run monthly."""
    db = sqlite3.connect(DB); db.row_factory = sqlite3.Row
    games = db.execute("""SELECT g.player, g.period, g.fpts, p.proj_full
                          FROM game_grades g JOIN players p ON p.name = g.player
                          WHERE p.proj_full IS NOT NULL AND g.fpts IS NOT NULL""").fetchall()
    mx = max(g["period"] for g in games)
    for cut in (mx - 6, mx - 4):
        tr, te = {}, {}
        for g in games:
            (tr if g["period"] <= cut else te).setdefault(g["player"], []).append(g)
        k, best = None, 9e9
        x = 0.70
        while x <= 1.20:
            flat = [g for v in tr.values() for g in v]
            m = sum(abs(g["fpts"] - x * g["proj_full"]) for g in flat) / len(flat)
            if m < best:
                k, best = round(x, 3), m
            x += 0.001
        cases = []
        for name, gs in te.items():
            h = tr.get(name, [])
            if len(h) < 5:
                continue
            cases.append((sum(g["fpts"] for g in gs) / len(gs),
                          K_PROJ * h[0]["proj_full"],
                          sum(g["fpts"] for g in h) / len(h), len(h)))
        base = sum(abs(a - p) for a, p, _, _ in cases) / len(cases)
        print(f"\nholdout fit<={cut} test>{cut}: fitted K={k} (stored {K_PROJ}), "
              f"n={len(cases)}, baseline MAE {base:.3f}")
        for w in (2, 3, 4, 5, 6, 8, 10, 14):
            m = sum(abs(a - (n * h + w * p) / (n + w)) for a, p, h, n in cases) / len(cases)
            s = sum(a - (n * h + w * p) / (n + w) for a, p, h, n in cases) / len(cases)
            star = "  <== current default" if w == W_PRIOR else ""
            print(f"   W={w:>2}  MAE {m:6.3f} ({(base - m) / base * 100:+5.1f}%)  "
                  f"bias {s:+6.3f}{star}")


def lloyd_cell(r, want):
    """Lloyd's rank for one list, newest first, with a staleness marker. '2w' entries are
    a last-two-weeks window, not a season rank, and are labelled as such."""
    today = datetime.date.today()
    bits = []
    for d, kind, n, _ in sorted(r["lloyd"], reverse=True):
        if kind != want and not (want == "curr" and kind == "curr2w"):
            continue
        age = (today - datetime.date.fromisoformat(d)).days
        bits.append(f"#{n}" + ("*2w*" if kind == "curr2w" else "")
                    + (f" ⚠{age}d" if age > STALE_DAYS else ""))
    return bits[0] if bits else "—"


def fmt(rows, key, title, extra_cols, limit=None):
    rk = key + "_rank"
    body = [title, ""]
    body.append("| # | Player | Team | " + " | ".join(extra_cols[0]) + " |")
    body.append("|---|---|---|" + "---|" * len(extra_cols[0]))
    for r in sorted([x for x in rows if rk in x], key=lambda x: x[rk])[:limit]:
        body.append(f"| {r[rk]} | {r['name']} | {r['fteam']} | "
                    + " | ".join(c(r) for c in extra_cols[1]) + " |")
    return "\n".join(body)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trade", action="store_true", help="apply the injury discount")
    ap.add_argument("--player"); ap.add_argument("--mine", action="store_true")
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--min-gp", type=int, default=MIN_GP)
    ap.add_argument("--w-prior", type=int, default=W_PRIOR)
    ap.add_argument("--dtd-penalty", type=int, default=5)
    ap.add_argument("--out-penalty", type=int, default=12)
    ap.add_argument("--form-days", type=int, default=FORM_DAYS)
    ap.add_argument("--buylow", action="store_true",
                    help="only the players the form screen flags")
    ap.add_argument("--no-write", action="store_true")
    a = ap.parse_args()

    if a.validate:
        return validate()

    roster = live_roster()
    rows = load(roster, a.min_gp, a.w_prior)
    rank(rows, "current"); rank(rows, "projected"); add_form(rows, a.form_days)
    if a.trade:
        apply_trade_discount(rows, a.dtd_penalty, a.out_penalty)
    for r in rows:
        r["lloyd"] = LLOYD.get(r["name"], [])
        r["dunne"] = DUNNE.get(r["name"])

    by = {r["name"]: r for r in rows}

    if a.player:
        hit = [n for n in by if a.player.lower() in n.lower()]
        if not hit:
            sys.exit(f"no rostered player matching {a.player!r}")
        for n in hit:
            r = by[n]
            print(f"\n{'=' * 72}\n{n}  ({r['fteam']})   injury {r['injury']}")
            print(f"  CURRENT    {r['current']:6.1f}/g over {r['gp']} GP"
                  + (f"   rank {r.get('current_rank')}" if r.get("current_rank")
                     else f"   UNRANKED (under {a.min_gp} GP)"))
            if a.trade and r.get("trade_rank"):
                print(f"             trade-discounted rank {r['trade_rank']}"
                      f"   (injury penalty {r['inj_penalty']} spots)")
            print(f"  PROJECTED  {r['projected']:6.1f}/g"
                  + (f"   rank {r.get('projected_rank')}" if r.get("projected_rank") else ""))
            if r.get("form") is not None:
                print(f"  LAST {a.form_days}d   {r['form']:6.1f}/g over {r['form_n']} games"
                      f"   rank {r.get('form_rank')}"
                      f"   {r['form_gap']:+.1f} vs his projection   ->  {r['signal']}")
            else:
                print(f"  LAST {a.form_days}d   only {r['form_n']} games -- no read")
            print(f"  context    {r['mpg']:.1f} mpg now vs {r['proj_mpg']:.1f} projected"
                  f"   (context only -- never multiplied into a value)")
            if r["dunne"]:
                print(f"  Dunne ROS  #{r['dunne']}  (Fantrax, 3 Nov, GENERIC points "
                      f"scoring -- direction only, rule 24)")
            for d, kind, n_, q in r["lloyd"]:
                print(f"  Lloyd {d} {kind.upper():<4} #{n_}  \"{q}\"")
        return

    pool = [r for r in rows if r["enough"]]
    sel = [r for r in pool if r["fteam"] == "The Freaky Alien"] if a.mine else pool
    lim = a.limit or (None if a.mine else 60)

    cur_cols = (["Fpts/g", "GP", "mpg", "Lloyd now", "Dunne ROS"],
                [lambda r: f"**{r['current']:.1f}**", lambda r: str(r["gp"]),
                 lambda r: f"{r['mpg']:.1f}",
                 lambda r: lloyd_cell(r, "curr"),
                 lambda r: f"#{r['dunne']}" if r["dunne"] else "—"])
    if a.trade:
        cur_cols[0].insert(1, "Trade rank")
        cur_cols[1].insert(1, lambda r: (f"**{r['trade_rank']}**"
                                         + (f" (−{r['inj_penalty']})" if r["inj_penalty"] else ""))
                           if r.get("trade_rank") else "—")
    proj_cols = (["Proj/g", "Now/g", "Move", "Lloyd proj", "Dunne ROS"],
                 [lambda r: f"**{r['projected']:.1f}**", lambda r: f"{r['current']:.1f}",
                  lambda r: f"{r['projected'] - r['current']:+.1f}",
                  lambda r: lloyd_cell(r, "proj"),
                  lambda r: f"#{r['dunne']}" if r["dunne"] else "—"])

    form_cols = (["Last 14d/g", "Gms", "vs his proj", "mpg", "Signal"],
                 [lambda r: f"**{r['form']:.1f}**" if r.get("form") is not None else "—",
                  lambda r: str(r.get("form_n", 0)),
                  lambda r: (f"{r['form_gap']:+.1f}  ({r['form_rel'] * 100:+.0f}%)"
                             if r.get("form_gap") is not None else "—"),
                  lambda r: (f"{r['form_mins']:.1f}"
                             + ("" if r['form_mr'] >= MINS_INTACT else " ⚠down")
                             if r.get("form_mins") else "—"),
                  lambda r: f"**{r['signal']}**" if r.get("signal", "—") not in ("—", "HOLD")
                  else r.get("signal", "—")])

    if a.buylow:
        flagged = [r for r in rows if r.get("signal") in
                   ("BUY LOW", "SELL HIGH", "FADE (usage)", "FADE (minutes)",
                    "SLUMP (no edge)", "RIDE", "INJURED (void)")]
        if a.mine:
            flagged = [r for r in flagged if r["fteam"] == "The Freaky Alien"]
        print(f"## FORM SCREEN — last {a.form_days} days vs each player's own projection\n")
        print("All cuts are a share of the player's OWN projection. Every number below is\n"
              "measured on 1,104 player-weeks (14-day window, 4+ games in it, 2+ after),\n"
              "re-measured 12 Nov 2026 under these exact gates. 'Persists' = the share of\n"
              "the gap still there the following week.\n\n"
              "  BUY LOW    10-20% under, minutes AND touches intact -> -11%: it REVERSES\n"
              "  FADE usage 10%+ under, TOUCHES down (<0.90)         ->  90% sticks. Role.\n"
              "  FADE mins  10%+ under, MINUTES down (<0.90)         ->  65% sticks\n"
              "  SLUMP      20%+ under with minutes AND touches fine ->  46% sticks, no edge\n"
              "  SELL HIGH  10%+ over on FEWER minutes               ->  52% survives (weak)\n"
              "  RIDE       10%+ over, minutes >= projection         ->  67% is real\n"
              "  INJURED    OUT/IR only -- rule 27's confounder. NOT a persistence class:\n"
              "             the three axes do not measure role for a hurt player, so no\n"
              "             signal is claimed. Unmeasured by construction (no per-game\n"
              "             injury flag is stored); it withholds a read, never makes one.\n")
        for sig in ("BUY LOW", "SELL HIGH", "FADE (usage)", "FADE (minutes)",
                    "SLUMP (no edge)", "RIDE", "INJURED (void)"):
            grp = [r for r in flagged if r["signal"] == sig]
            if not grp:
                continue
            print(f"### {sig}  ({len(grp)})")
            for r in sorted(grp, key=lambda x: x["form_gap"]):
                print(f"  {r['name']:<26} {r['fteam'][:18]:<19} last14 {r['form']:5.1f}/g "
                      f"({r['form_n']}g)  {r['form_gap']:+6.1f} ({r['form_rel'] * 100:+4.0f}%) "
                      f"vs proj {r['proj_adj']:5.1f}  {r['form_mins']:4.1f} mpg"
                      + ("  ⚠injured — axes void" if r["signal"] == "INJURED (void)"
                         else ("" if r['form_mr'] >= MINS_INTACT else "  ⚠minutes down")
                             + ("  ⚠DTD — provisional" if r.get("form_dtd") else "")))
            print()
        return

    print(fmt(sel, "current", f"## CURRENT VALUE — actual fantasy points per game "
                              f"({len(pool)} rostered players with {a.min_gp}+ GP)",
              cur_cols, lim))
    print()
    print(fmt(sel, "projected", "## PROJECTED VALUE — rest-of-season per game, "
                                "no injury adjustment", proj_cols, lim))
    print()
    print(fmt(sel, "form", f"## FORM — last {a.form_days} days (a WINDOW on current "
                           f"value, not a third value)", form_cols, lim))
    low = [r for r in rows if not r["enough"]]
    if low:
        print(f"\n**Under {a.min_gp} GP — not ranked, sample too small to be a "
              f"performance read:** "
              + ", ".join(f"{r['name']} ({r['current']:.1f}/g on {r['gp']})"
                          for r in sorted(low, key=lambda x: -x["current"])))

    if not a.no_write and not a.mine:
        r0 = next((x for x in pool if x.get("form_from")), {"form_from": "?", "form_to": "?"})
        stamp = datetime.date.today().isoformat()
        db = sqlite3.connect(DB)
        db.execute("""CREATE TABLE IF NOT EXISTS rankings(
            asof TEXT, name TEXT, fantasy_team TEXT, gp INT, mpg REAL,
            current REAL, current_rank INT, projected REAL, projected_rank INT,
            trade_rank INT, injury TEXT, PRIMARY KEY(asof, name))""")
        db.executemany("""INSERT OR REPLACE INTO rankings VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                       [(stamp, r["name"], r["fteam"], r["gp"], r["mpg"], r["current"],
                         r.get("current_rank"), r["projected"], r.get("projected_rank"),
                         r.get("trade_rank"), r["injury"]) for r in pool])
        db.commit()
        with open(MD_OUT, "w") as f:
            f.write(f"# Rankings — {stamp}\n\n"
                    f"Generated by `fantasy/rankings.py`. Two lists, two formulas, no "
                    f"mixing.\n\n**CURRENT** = actual ESPN fantasy points per game, "
                    f"nothing adjusted.\n**PROJECTED** = "
                    f"`(GP x actual + {a.w_prior} x {K_PROJ} x ESPN projection) / "
                    f"(GP + {a.w_prior})`, no injury adjustment.\n\n"
                    + fmt(pool, "current", "## CURRENT VALUE", cur_cols) + "\n\n"
                    + fmt(pool, "projected", "## PROJECTED VALUE", proj_cols) + "\n\n"
                    + fmt(pool, "form", f"## FORM — last {a.form_days} days "
                          f"({r0['form_from']} to {r0['form_to']}). A WINDOW on current "
                          f"value, not a third value.", form_cols) + "\n")
        print(f"\nwrote {MD_OUT} and {len(pool)} rows to rankings (asof {stamp})")


if __name__ == "__main__":
    main()
