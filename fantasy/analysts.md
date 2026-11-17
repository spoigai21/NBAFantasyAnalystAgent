# The analyst roster

Who to read for **this** league: ESPN, 9 teams, points — ESPN default **plus** GP +1,
OREB +1, DD +3, TD +5, QD +25, TW +1, EJ −2, FF −1.

**ESPN's own analysts are excluded by the user's instruction, 26 Oct 2026** — Snellings,
Moody, Karabell, McCormick, Alexander, Florio. Do not cite their ranks. Noted in
CLAUDE.md rule 25.

## The calibration problem — read this first

"Points league" does not mean one thing, and the difference lands exactly on our roster.

| Format | STL | BLK | AST | TOV |
|---|---|---|---|---|
| **ESPN default (our base)** | **+4** | **+4** | +2 | −2 |
| Yahoo-style points | +2 | +2 | +1.5 | −1 |

Our base pays the **highest steal/block rate of any mainstream points format.** A ranking
written for generic points scoring therefore undervalues shot-blockers for us. RotoWire,
16 Sep 2026, on Wembanyama: *"The blocks that make him a category-league cheat code are
worth less here."* **True of their format, false of ours.** Wemby's 4.0 blocks are 16
fpts a night in our scoring.

And **nobody's list contains our bonuses** — DD +3, TD +5, OREB +1, GP +1, TW +1. That is
roughly +4.8/g for Wemby and +8.7/g for Jokic, which is most of the gap between them.

**So: we out-rank every public list already.** `fantasy/league.db` holds real ESPN applied
points for all 126 rostered players in our exact scoring. Use analysts for **mechanism** —
role, minutes, usage, rotation, injury, coaching — and never for ranks. Always state which
scoring a borrowed rank was built in. CLAUDE.md rules 24-25.

## The weighting scheme

User's instruction, 26 Oct 2026: *"if lloyd explcitiy says something follow that. if its
left vague use these analysts and rank em based on the best or more accurate in general."*

**Resolution order. Stop at the first tier that gives a clear answer.**

| # | Source | When it governs |
|---|---|---|
| **0** | **Hard data** — `league.db`, `game_log`, ESPN applied points | Always first. Nobody's opinion overrides a measured per-minute rate or a minutes count. Data sets the *size*, opinion sets the *direction*. |
| **1** | **Josh Lloyd, EXPLICIT — ON MECHANISM ONLY** | A verbatim, on-point, dated quote that greps clean in `fantasy/transcripts/`, about a **role, minutes, injury, usage or rotation move**. **Follow it.** ⚠ **NOT about a rank or a value — see "Lloyd is out of the rank business" below (16 Nov 2026).** Must be about the actual question — "I like Brandon Miller a lot in round three" is explicit about draft value, *vague* about whether to start him in week 2. |
| **2** | **Josh Lloyd, implicit** | He addressed the situation but not the question — a minutes comment, a trigger date, a team-context read. Use as a strong prior, say it is inference. |
| **3** | **Weighted analyst consensus** (below) | Lloyd silent or vague. Agreement across independent analysts beats any single voice. |
| **4** | **My own calc, stated as mine** | Nobody has addressed it. Never dress this as someone else's opinion (rule 14). |

**Lloyd does not get tier 1 on:** our bonus scoring (he does not know our settings), anything
he has since retracted (he reversed his own CMB call), or a single-game reaction — his own
rule is *"don't overreact"* at this time of year.

### Analyst weights for tier 3

Ranked on **observed track record in this project plus methodological quality.** I have no
audited accuracy data on any of these people and have not back-tested them — this is a
judgement, and it should get revised as we catch people being right and wrong.

| Weight | Analyst | Basis for the weight |
|---|---|---|
| **1.0** | **Raphielle Johnson** (Rotoworld) | Twice gave a *mechanism* that our own numbers then confirmed: Buzelis's FG% ceiling and his two defensive-stat levers. Writes causes, not reactions. |
| **0.9** | **Noah Rubin** (Rotoworld) | Found the Brandon Miller free-throw-rate swing nobody else wrote up, and it held. Same mechanism-first style. |
| **0.7** | **Jacob Dunne** (FantraxHQ) | Points-format-native. His AD "Round 3 trap" call was independently reached and agrees with ours. Small sample on him. |
| **0.6** | **Dan Titus** (Yahoo / NBA.com) | Points-specific and non-ESPN, but publishes ranks without a stated formula. Directional only. |
| **0.5** | **Barutha / Sprecher / Whalen** (RotoWire) | Good role notes, but **Yahoo-calibrated** — mechanically wrong on blocks for us. Discount anything resting on STL/BLK value. |
| **0.4** | **Team beat writers** (Pounding the Rock, Bulls On SI, ClutchPoints) | Best and earliest on minutes, rotations and coach intent. No fantasy translation. |
| **0.3** | **CBS / FantraxHQ weekly** (Matt Garrett) | Fast and directional. Thin reasoning. |
| **0.0** | **ESPN's analysts** | Excluded by the user (rule 25). |

**Tie-breaks:** (1) the one citing a *mechanism* beats the one citing a result; (2) the more
recent wins — roles change weekly; (3) **two independent sources on the same lever outrank
one louder voice.** Always print the date.

## ⚠ Lloyd is out of the rank business — 16 Nov 2026

User: *"i found lloyd to be a bit iffy... so lets not use josh lloyd for rankings, but more
for giving info and flagging players."* CLAUDE.md rule 3 carries the full version.

**Take from him:** who left a game and why, who started, whose minutes moved and whether a
blowout explains it, who is getting the touches, injury news ahead of ESPN's flag, and
"go look at this player" pointers.
**Do not take:** any rank, any value, any "round N", any "X fantasy points player".

**Why — Jalen Johnson, 9 Nov buy-low show, one episode.** *"I was down on Jaylen Johnson
heading into this season. I was dumbfounded that people were viewing him as a first round
**category league** player"* — he names the format — against, minutes later, *"He should be
over 40 easy in fantasy points"*, *"on the fringes of first round in that middle of the
second round area"*, *"I think he's a 45 minimum fantasy point player."* The user reports
he drafted Johnson **top 10 in an ESPN points league**; that part is **unverified** — not
in the transcripts on disk — and the verified quotes carry the point without it.
**A rank whose meaning depends on a format stated once and then dropped is not a rank.**
This is the calibration problem at the top of this file, except it cannot be corrected for,
because the format is usually unstated.

## Tier 1 — the one that's format-correct

| Analyst | Where | Why |
|---|---|---|
| **Josh Lloyd** | Basketball Monster lead analyst ($9.95/mo); Locked On Fantasy Basketball (free, daily, YouTube); `joshlloyd48.substack.com` | The only one who treats **points-league tiers as a first-class product** and talks through the reasoning daily rather than publishing a list. Melbourne-based; ex-Yahoo, RotoWire, Betfair. Our primary source — transcripts in `fantasy/transcripts/`, searchable via `./fantasy/lloyd.sh`. Still opinion, not truth (rule 2), and he retracts (see his CMB reversal). |

Nobody else is in this tier **for mechanism**, which since 16 Nov 2026 is the only thing
this tier governs. For ranks and values nobody is in tier 1, including him — our own two
lists are the answer (CLAUDE.md rule 32).

## Added 16 Nov 2026 — Bleav

User: *"i think another fantasy analyst who is good is BLEAV."*

| Weight | Analyst | Basis |
|---|---|---|
| **0.6 (provisional)** | **Robbin Marx** — *Bleav in Fantasy Basketball*, Apple Podcasts [id1592852703](https://podcasts.apple.com/us/podcast/bleav-in-fantasy-basketball---nba-points-leagues/id1592852703) | User-nominated. Points-league oriented, which is the scarce thing (see the calibration section). Former NBC Sports Rotoworld analyst; Hashtag Basketball Dynasty contributor. Active — 600 episodes, 2021–2026, new episodes daily as of 16 Nov 2026. |

⚠ **Provisional weight, and three honest caveats — do not treat this as a vetted source
yet.** (1) **Bleav is a NETWORK, not a person.** "Bleav said X" is not an attribution; name
the show and the host. The same feed carries team-specific shows (a Dallas Mavericks daily
was the top episode on 16 Nov), so the feed alone does not identify the fantasy analyst.
(2) The directory listing titles the show *"NBA Points Leagues & Category Leagues"* but the
show's own description does **not** state which format a given rank is built in — which is
the exact failure that just cost Lloyd his rank privileges. **Make him state the format or
treat the number as unusable.** (3) I have **no observed track record** on Marx in this
project and have back-tested nothing. The 0.6 is a placeholder matching Dan Titus
(points-specific, no stated formula), not a measurement.
⚠ Also note: **Bleav Basketball also carries *Fantasy NBA Today*, whose hosts include Steve
"Dr. A" Alexander.** The user's ESPN exclusion (rule 25) names an "Alexander"; I have not
established whether that refers to this Steve Alexander (Rotoworld/SportsEthos) or a
different one, so **ask before citing him** rather than guessing in either direction.

## Tier 2 — read for mechanism, not ranks

| Analyst | Where | Note |
|---|---|---|
| **Raphielle Johnson** | NBC Sports / Rotoworld | **Best daily per-player notes in the industry.** Explains role and usage, not just box scores. Already the source on Buzelis's FG% ceiling and his defensive-stat levers. |
| **Noah Rubin** | NBC Sports / Rotoworld | Strongest on *why* a line moved — found the Brandon Miller free-throw-rate swing nobody else wrote up. |
| **Dan Titus** | Yahoo; also writes **NBA.com's** Top 150/250 points rankings | Non-ESPN and genuinely points-specific. 29 Sep 2026: Jokic 1, **Wemby 3**, Giannis 4, **AD 15**. Scoring formula unstated — treat as directional. |
| **Jacob Dunne** | FantraxHQ | Points-league round-by-round steals and traps, 6 Oct 2026. Called **AD a Round 3 trap** — *"Drafting him this high is playing with fire"* — which independently agrees with our own games-played read. |
| **Alex Barutha**, Kirien Sprecher, Nick Whalen | RotoWire | Points top 150 with per-player role notes. **Yahoo-calibrated — discount their block discount.** |
| **Matt Garrett** | FantraxHQ | Weekly buy-low / sell-high. Early and directional, not rigorous. Had Wemby as a Week 1 buy-low. |
| **RotoBaller** | rotoballer.com points tiers | Non-ESPN points rankings and tiers. Dan Besbris writes their late-round values. |

## Tools, not analysts

| Tool | Why it matters |
|---|---|
| **Hashtag Basketball** — points-league rankings + projections | The **only public tool whose stat list includes our bonus categories**: PTS, TREB, OREB, DREB, AST, STL, BLK, TO, 3PM, 3PA, MPG, FGM, FGA, FGMI, FTM, FTA, FTMI, **DD, TD**, PF. Also a rest-of-season vs 7/14/30-day blend and a GP penalty. ⚠️ **Unverified:** I could not confirm from the public page that you can type custom per-stat point values — that looks Patreon-gated (~$2.50/mo). Worth $2.50 to find out; closest thing to our scoring that exists off our own disk. |
| **Parlae.io** points rankings | Ranks on **actual fantasy points per game from real box scores** — methodologically the closest to what we compute. Good cross-check on our own numbers. |
| **Basketball Monster** | Lloyd's shop. Settings reportedly accommodate points as well as categories; mainly a category tool. |

## Tier 3 — news, which moves value before any analyst writes it up

Shams Charania, Jake Fischer, Chris Haynes. Team-local beats are usually first and best on
minutes and rotations: Pounding the Rock (SAS), Bulls On SI (CHI), ClutchPoints.

## Standing cautions

- **Date-check every hit.** On 26 Oct 2026 the first six results for Wembanyama's slow
  start included a **July 2026** column, a **Nov 2024** scout quote and a **2024** Bleacher
  Report item — all reading as current in the result list.
- **Category rankings are not points rankings.** Most fantasy basketball content is 9-cat.
  FG%/FT% damage and three-point volume are category problems that mostly vanish for us;
  FGA and FTA are *real costs* for us that categories ignore entirely.
- Never use the draft board's FP column (rule 4).
