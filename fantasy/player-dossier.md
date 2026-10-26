# League player dossier — LeFantasy 2027

_Rendered from `fantasy/league.db` on 2026-10-25. 126 rostered players, 9 teams._

**This file is a VIEW. The database is the source of truth.** Rebuild:
`python3 fantasy/build_db.py && python3 fantasy/load_research.py && python3 fantasy/index_lloyd.py && python3 fantasy/aliases.py`

`proj full/g` = ESPN 2027 projection (base + GP — carries **no** OREB/DD/TD/TW, CLAUDE.md
rule 8) **plus** the measured bonus from last season's actual. `Δ` = this season's per-game
minus that. `/min` = applied points per minute, the fairest early read because minutes settle
long before efficiency. **Never quote Lloyd from a summary — run `./fantasy/lloyd.sh`.**


## The Freaky Alien

_14 players · 1410 fantasy points produced_

| player | NBA | | GP | total | /g | mpg | /min | **proj full/g** | Δ |
|---|---|---|---|---|---|---|---|---|---|
| Victor Wembanyama | SAS |  | 3 | 147 | 49.0 | 31.7 | 1.55 | **66.4** | -17.4 |
| Giannis Antetokounmpo | MIA |  | 3 | 144 | 48.0 | 29.3 | 1.64 | **63.3** | -15.3 |
| Anthony Davis | WAS |  | 3 | 112 | 37.3 | 32.3 | 1.16 | **56.1** | -18.8 |
| Amen Thompson | HOU |  | 3 | 153 | 51.0 | 36.0 | 1.42 | **45.3** | +5.7 |
| Dejounte Murray | NOP |  | 3 | 148 | 49.3 | 33.0 | 1.50 | **40.9** | +8.4 |
| Paul George | BOS |  | 2 | 107 | 53.5 | 32.5 | 1.65 | **40.8** | +12.7 |
| Brandon Miller | CHA |  | 3 | 69 | 23.0 | 31.7 | 0.73 | **40.2** | -17.2 |
| Zach Edey | MEM | **OUT** | 2 | 72 | 36.0 | 21.5 | 1.67 | **40.1** | -4.1 |
| Matas Buzelis | CHI |  | 3 | 67 | 22.3 | 25.7 | 0.87 | **35.1** | -12.7 |
| Zach LaVine | SAC |  | 3 | 127 | 42.3 | 37.7 | 1.12 | **33.5** | +8.9 |
| Cedric Coward | MEM |  | 2 | 67 | 33.5 | 30.0 | 1.12 | **32.7** | +0.8 |
| Keegan Murray | SAC | **OUT** | 2 | 26 | 13.0 | 27.0 | 0.48 | **32.2** | -19.2 |
| Collin Murray-Boyles | TOR |  | 3 | 71 | 23.7 | 19.0 | 1.25 | **28.9** | -5.3 |
| Paul Reed | DET |  | 3 | 100 | 33.3 | 22.0 | 1.51 | **24.2** | +9.1 |

**Research:**

- **Anthony Davis — analyst — Rotowire/CBS 24 Oct.** On the 19-pt game: "bounced back from a nine-point effort... but Davis' six boards were still his lowest mark on the young season." Season line 20.7p/9.0r/2.7a/1.3s/1.0b, and the key number — "he hasn't even found his rhythm on offense yet: he's shooting just 41.5 percent from the floor on 17.7 FG attempts a contest." Read: volume and role intact, efficiency is the whole gap. Matches my own finding (1.144/min vs 1.602 last season). _(CBS Sports / Rotowire, 24 Oct 2026)_
- **Anthony Davis — context.** AJ Dybantsa (#1 overall pick) has missed every game — his return adds spacing and unloads Kyshawn George (8 TOV vs TOR). Trae Young is also cold (4-of-16 from three). Offence not yet synced. Lloyd: "a walking injury where we're just crossing our fingers every time he steps on the court." _(Wiz of Awes / Lloyd 23 Oct)_
- **Anthony Davis — durability.** Lloyd/Locked On Wizards: in his Dallas spell "he failed to even play five games in a row before he found himself on the shelf." He is 33. Ayton was signed because "you have absolutely no depth behind Alex Sarr and Anthony Davis, two players that have been injured pretty often recently." _(transcripts 2026-09-20_previews_HOU-WAS)_
- **Anthony Davis — matchup.** The 3-12 game: Toronto FRONTED him in the post with Scottie Barnes and Kawhi Leonard. Beat writers' complaint is delivery, not decline — "He needs more than 12 shots, and the Wizards have to get him easier looks." _(Wiz of Awes)_
- **Anthony Davis — verdict.** Two bad games in three: 68, 16, 28. 37.3/g vs a 56.1 projection; 1.144/min vs 1.602 last season, down 29%. The 24 Oct "bounce-back" was 19 pts on 8-21 with 6 reb and no double-double = 28 fp. Minutes are fine (32.3 vs 32.2 projected) — this is shooting and bonus loss, not role. _(own calc)_
- **Brandon Miller — analyst — Noah Rubin NBC/Rotoworld 24 Oct.** THE most useful outside read on Miller. "Miller has been the focal point of the offense... which gives him a green light to shoot often. He is averaging 21.3 shot attempts per game." The mechanism he identifies: FREE THROW RATE. "He shot three total free throws in their first two games, far less than his 12 attempts in this one." And the trigger: "Miller is going to continue to get as many shots as he wants UNTIL KON KNUEPPEL (hamstring) RETURNS. He should be in for more big scoring nights, especially when his shot starts falling." _(NBC Sports/Rotoworld, Noah Rubin, 24 Oct 2026)_
- **Brandon Miller — cause.** No supporting cast: Kon Knueppel (hamstring), Coby White (calf) and Grant Williams (hamstring) have missed every game, so he is the only scoring threat and defences load up. Charlotte shot 11-of-51 from three with 25 turnovers. Charles Lee as of 21 Oct: "there's still no timeline on those guys." _(Yahoo/HEAVY, Roundtable)_
- **Brandon Miller — free throws — format impact.** Rubin's FT point matters more in this league than a normal one. FTA is -1 here, but FTM is +1 AND the point counts, so a made FT is +2 net and a miss is -1. Miller went 11-of-12 on 24 Oct (+21 net from the line) after 3 total FTAs in two games. That single change is most of the jump from 9 and 18 fantasy points to 40. _(own calc + Rubin)_
- **Brandon Miller — injury flag.** Surgery May 2026 for LEFT SHOULDER INSTABILITY, after missing 13 straight games the prior season with a subluxation and playing out the year in a wrap. Still NOT cleared for basketball activities on 28 Aug 2026 — a very compressed ramp. It is his guide hand (shoots right-handed) and no reporting links it to his mechanics, so this is a flag, not a diagnosis. _(NBA.com, NBC Sports 28 Aug)_
- **Brandon Miller — positive.** Volume intact and that matters here: 29 FGA on 24 Oct produced +17 from field goals alone (4xFGM + 2x3PM - FGA). Format break-even is 25% shooting, so high volume is fine as long as he clears it. 31.7 mpg, career-best 38.3% from three last year, Lee publicly backing him. _(own calc)_
- **Brandon Miller — shooting.** 9-of-35, 4-of-25 from three through two games; opened 7-of-12 for 17 points then went 2-of-23. 23 Oct: 2-14, 1-11 from three, -37, booed at home. 0.705 fp/min is the worst on my roster. _(Yahoo/HEAVY + own calc)_
- **Collin Murray-Boyles — coach intent.** Darko Rajakovic plans him at BOTH power forward and centre and wants him on the floor WITH Poeltl — "they need to play CMB more than last year and get him on the court with Jakob Poeltl." Poeltl is taking 22/27/19 min and producing 3, 6, 0 points. Lloyd is confused too: "why has he not even hit 20 minutes in one game yet?" _(RotoWire/SI, Lloyd 25 Oct)_
- **Collin Murray-Boyles — minutes.** Three different causes, none a demotion: 21 Oct rested in the closing minutes of a 43-point blowout win (20 min, +28); 23 Oct FOUL TROUBLE, 5 fouls in 18 min (+21); 25 Oct a 23-point loss (19 min). Fouls are the real constraint — 10 in 57 minutes is 6.3 per 36. _(own calc from box scores)_
- **Giannis Antetokounmpo — minutes.** The quiet problem. Rate is nearly fine (1.636/min vs 1.743 projected) but he is at 29.3 mpg against 33.6 projected — a 4.3 minute shortfall that a hot night does not fix. Worth tracking separately from the shooting stories. _(own calc)_
- **Matas Buzelis — analyst — Raphielle Johnson NBC/Rotoworld 24 Oct.** "Buzelis had a difficult start to the season, totaling 24 points on 4-of-17 shooting... He was considerably better against the Wizards, shooting over 50 percent and finishing a blocked shot shy of a complete stat line." The caution, which agrees with my per-minute read: "GIVEN WHAT HE'S BEING ASKED TO DO as one of the Bulls' young building blocks, Buzelis' FIELD-GOAL PERCENTAGE MAY STRUGGLE. That said, he's still someone who should be rostered in all fantasy leagues." Note the verdict is ROSTER, not start with confidence. _(NBC Sports/Rotoworld, Raphielle Johnson, 24 Oct 2026)_
- **Matas Buzelis — analyst — the swing factor.** Johnson, 14 Oct: "He attempted 6.4 three-pointers per game last season but made just 34.9 percent. IF BUZELIS BECOMES A RELIABLE PERIMETER SHOOTER, HIS FANTASY CEILING WILL RISE CONSIDERABLY." And 7 Oct: last season 0.7 steals and 1.5 blocks — "if Buzelis can build on that defensive output, he becomes an even more appealing option." He has NOT: 0.33 stl / 1.00 blk so far. Two independent sources now point at the same two levers. _(NBC Sports/Rotoworld, 14 and 7 Oct 2026)_
- **Matas Buzelis — coaching change.** Chicago has a NEW head coach, Tiago Splitter, not Billy Donovan. The new offence wants Buzelis taking MORE mid-range, "something he didn't do often under Billy Donovan" — a mechanical reason for the cold start. He is relearning shot locations. _(ClutchPoints)_
- **Matas Buzelis — minutes.** The 17-minute game on 23 Oct was a real 4th-quarter benching — Splitter rode the second unit to the end; Giddey sat too. Not a role change: Splitter — "We're making this a bigger deal than we should be. It's just basketball. You're not having a great night; you play a little bit less. Not a big deal." He answered with 35 min on 24 Oct. _(ClutchPoints / Bulls On SI)_
- **Matas Buzelis — threat.** Caleb Wilson (rookie) is behind only Michael Jordan for total points by a Bulls rookie through 3 games — 30 pts / 14 reb on 24 Oct. Leonard Miller and Okoro took the 4th-quarter minutes in the benching game. _(Bulls On SI)_
- **Matas Buzelis — verdict.** NOT fixed. Per-minute 0.800 / 0.882 / 0.914 vs 1.167 last season — even his best game is 22% below his own rate. The loss is in the +4 cats: steals 0.70 -> 0.33, blocks 1.51 -> 1.00, assists 2.05 -> 1.67, about 4.3 fp/g gone. He had ZERO blocks in the 21-point game. Realistic now 25-27/g, not 35.1. _(own calc from game_log)_
- **Paul George — Lloyd — strongly bullish.** One of his five universal ADP targets: "Paul George is still really good. Last season wasn't a great year. Still top 50 in category leagues... I'll happily take him in the 50s and 60s. I think a TOP 30 FINISH IS DEFINITELY POSSIBLE for Paul George. He's the number two offensive option in Boston. He generates steals. He hits threes. He gets assists. Yes, he does have some injury concerns... but that is priced in to this draft spot and PRICED IN TOO MUCH. 80 is his Yahoo ADP. 104 on ESPN. That is LITERALLY JUST FREE REAL ESTATE. You are not wasting anything by taking him. Just do it. Just easy easy win." _(transcripts 2026-10-23 draft-guide)_
- **Paul George — Lloyd — the injury caveat, resolved.** "He's not currently hurt. HALF HIS GAMES MISSED LAST SEASON WERE A SUSPENSION. He doesn't have the ongoing persistent problems like Kawhi and Embiid. So, I'm not that worried about him." Separately he still says "Paul George I wouldn't take inside the top 40" — so the read is: huge value at his ADP, not a top-40 pick. Both are his. _(transcripts 2026-10-23 draft-guide)_
- **Paul George — analyst consensus.** Outside projections are more modest than Lloyd: ~31-33 mpg as the clear SECOND option behind Tatum, ADP 86.5, Yahoo projecting 19.6p/5.7r/4.2a/1.4s in 31.4 mpg. Fantasy Alarm flags that Tatum, Derrick White and Pritchard all absorb shots, helping them more than George. He is at 32.5 mpg so far, right in that band. Lloyd's "top 30 possible" is the bull case, not the consensus. _(Fantasy Alarm, Yahoo Sports)_
- **Paul George — ⚠️ the +12.7 is ONE game.** His 53.5/g is the most misleading number on my roster. 20 Oct: 31 min, 12-21, SEVEN threes, FIVE STEALS, 38 pts = 73.0 fp at 2.355/min — an enormous outlier (5 steals alone is 20 fantasy points). 23 Oct: 34 min, 6-15, 2 stl, 15 pts = 34.0 fp at 1.000/min, BELOW his 40.8 valuation. Two games, 73 and 34. Do not plan around 53.5 — CLAUDE.md rule 12. True level is likely 42-48. _(own calc from game_log)_
- **Victor Wembanyama — trend.** Rate recovering fast: 1.294 -> 1.562 -> 1.828 fp/min, against a 1.893 projection. The opener was 1-of-13 and he still scored 44 on six blocks. 4.0 blocks per game = 16 fantasy points a night from blocks alone — the mechanism behind Lloyd rating him over Jokic in points leagues. Minutes fine at 31.7. _(own calc)_
- **Victor Wembanyama — vs Jokic.** ESPN projection in full league scoring has JOKIC ahead 76.9 to 66.4, because Jokic's measured bonus is +8.74 (triple-doubles) vs Wemby's +4.84. But Wemby is the one projected to IMPROVE on last season (+5.1/g vs Jokic +0.9). User states Lloyd has Wemby over Jokic in points leagues this year; my notes file contained a contradicting quote that greps clean in ZERO transcripts, now flagged as unverified. Opinion and projection genuinely split. _(own calc + user)_
- **Zach Edey — Monday 26 Oct expectation.** Expected back but NOT yet confirmed. He was ruled OUT for Sunday at Sacramento as "LT Ankle — Return From Injury Management", explicitly the FIRST leg of a back-to-back; teams normally rest the second leg, so sitting the first signals he plays the second. Lloyd said on the Sunday show: "Edy will be back tomorrow." No Monday injury report had posted as of this check — VERIFY before locking the lineup. _(Grizzlies PR, Lloyd 25 Oct)_
- **Zach Edey — availability.** OUT on 25 Oct — left ankle, officially "Return From Injury Management". Played only 11 regular-season games in 2025-26 after ankle surgery. Beat (Damichael Cole): "Grizzlies are still ramping Edey up and want to be careful." Was in "ramp-up phase two" at camp under Tuomas Iisalo, not cleared for two-a-days. NO stated numeric cap. Precedent from his last return: ~25 min for five games, then up. _(Grizzlies PR, Damichael Cole, Yahoo)_
- **Zach Edey — caveat.** His measured bonus of +5.91 is derived from an 11-game, 284-minute sample. Thin — treat the 40.1 projection as wide. _(own calc)_
- **Zach Edey — efficiency.** The most efficient player on my roster: 1.651 fp/min (1.333 and 1.955), above Wemby and Giannis. Backed by last season at 1.592/min, so not a fluke. 2.0 blocks/g at +4, double-digit rebounds in 21-22 min, ZERO turnovers in both games. _(own calc)_
- **Zach LaVine — correction.** ⚠️ I told the user to bench him citing Lloyd as having him "correctly OFF the board, keep him there." THAT QUOTE IS FABRICATED — it appears in no transcript. Lloyd is a LaVine BULL: bounce-back segment, "I expect more usage and more importantly, more ball handling opportunities", Sacramento's "second best player", "I started to warm to LaVine towards the end of draft season", and 25 Oct "one of the two guys I was actually high on... absolutely dominant." _(transcripts, verified by grep)_
- **Zach LaVine — status.** 42.3/g on 37.7 mpg — the most minutes on my roster and +8.9 over his projection. Put up 56 on 25 Oct. The -15 rank penalty is MY format adjustment for high-FGA scorers, not Lloyd's opinion, and it is not binding so far. START HIM over Murray-Boyles. _(own calc)_

## Skywalking Like I'm Luka

_15 players · 1686 fantasy points produced_

| player | NBA | | GP | total | /g | mpg | /min | **proj full/g** | Δ |
|---|---|---|---|---|---|---|---|---|---|
| Luka Doncic | LAL |  | 3 | 172 | 57.3 | 35.0 | 1.64 | **65.2** | -7.8 |
| Joel Embiid | PHI | **OUT** | 3 | 144 | 48.0 | 34.3 | 1.40 | **49.9** | -1.9 |
| Jalen Duren | DET | **OUT** | 2 | 71 | 35.5 | 19.0 | 1.87 | **49.4** | -13.9 |
| Kevin Durant | HOU |  | 3 | 120 | 40.0 | 37.0 | 1.08 | **45.3** | -5.3 |
| Jaylen Brown | PHI |  | 4 | 155 | 38.8 | 37.0 | 1.05 | **42.2** | -3.4 |
| Franz Wagner | ORL |  | 3 | 112 | 37.3 | 33.0 | 1.13 | **41.5** | -4.2 |
| Julius Randle | BKN |  | 3 | 116 | 38.7 | 32.3 | 1.20 | **41.0** | -2.4 |
| Rudy Gobert | MIN |  | 3 | 75 | 25.0 | 31.3 | 0.80 | **41.0** | -16.0 |
| Derrick White | BOS |  | 2 | 70 | 35.0 | 34.5 | 1.01 | **39.8** | -4.8 |
| VJ Edgecombe | PHI | **OUT** | 3 | 113 | 37.7 | 32.7 | 1.15 | **37.2** | +0.5 |
| Nickeil Alexander-Walker | ATL |  | 3 | 131 | 43.7 | 29.7 | 1.47 | **36.3** | +7.3 |
| Dylan Harper | SAS |  | 3 | 102 | 34.0 | 32.0 | 1.06 | **34.8** | -0.8 |
| Darryn Peterson | UTA |  | 3 | 69 | 23.0 | 30.3 | 0.76 | **30.1** | -7.1 |
| Brook Lopez | LAC |  | 3 | 116 | 38.7 | 23.3 | 1.66 | **28.4** | +10.2 |
| Wendell Carter Jr. | ORL |  | 3 | 120 | 40.0 | 31.0 | 1.29 | **27.1** | +12.9 |

## I Finish Quickley

_14 players · 1497 fantasy points produced_

| player | NBA | | GP | total | /g | mpg | /min | **proj full/g** | Δ |
|---|---|---|---|---|---|---|---|---|---|
| Shai Gilgeous-Alexander | OKC |  | 3 | 158 | 52.7 | 35.7 | 1.48 | **59.6** | -6.9 |
| Alperen Sengun | HOU |  | 3 | 144 | 48.0 | 33.0 | 1.46 | **49.3** | -1.3 |
| Scottie Barnes | TOR |  | 3 | 113 | 37.7 | 30.3 | 1.24 | **48.4** | -10.8 |
| Cooper Flagg | DAL | **OUT** | 2 | 99 | 49.5 | 25.0 | 1.98 | **48.4** | +1.1 |
| Walker Kessler | LAL |  | 3 | 148 | 49.3 | 31.0 | 1.59 | **45.8** | +3.5 |
| Chet Holmgren | OKC |  | 3 | 126 | 42.0 | 30.0 | 1.40 | **42.7** | -0.7 |
| Ivica Zubac | IND | **DAY_TO_DAY** | 3 | 81 | 27.0 | 21.7 | 1.25 | **41.7** | -14.7 |
| Trey Murphy III | NOP |  | 3 | 87 | 29.0 | 33.3 | 0.87 | **39.2** | -10.2 |
| Immanuel Quickley | TOR |  | 3 | 104 | 34.7 | 28.3 | 1.22 | **37.4** | -2.7 |
| OG Anunoby | NYK |  | 3 | 92 | 30.7 | 33.7 | 0.91 | **36.3** | -5.6 |
| Jaden McDaniels | MIN |  | 3 | 120 | 40.0 | 30.0 | 1.33 | **32.4** | +7.6 |
| Jalen Suggs | ORL | **DAY_TO_DAY** | 3 | 83 | 27.7 | 33.3 | 0.83 | **31.6** | -3.9 |
| Andrew Nembhard | IND |  | 3 | 99 | 33.0 | 32.0 | 1.03 | **30.5** | +2.5 |
| Jake LaRavia | LAL |  | 2 | 43 | 21.5 | 16.5 | 1.30 | **26.8** | -5.3 |

## Top G

_15 players · 1419 fantasy points produced_

| player | NBA | | GP | total | /g | mpg | /min | **proj full/g** | Δ |
|---|---|---|---|---|---|---|---|---|---|
| Karl-Anthony Towns | NYK |  | 3 | 143 | 47.7 | 31.3 | 1.52 | **51.1** | -3.5 |
| Tyrese Haliburton | IND |  | 3 | 164 | 54.7 | 32.3 | 1.69 | **49.6** | +5.0 |
| LaMelo Ball | MIN |  | 3 | 118 | 39.3 | 23.0 | 1.71 | **49.4** | -10.0 |
| Devin Booker | PHX |  | 2 | 111 | 55.5 | 32.5 | 1.71 | **45.8** | +9.7 |
| Kyrie Irving | DAL |  | 2 | 68 | 34.0 | 24.5 | 1.39 | **45.2** | -11.2 |
| Jimmy Butler III | GSW | **OUT** | 0 | 0 | 0.0 | 0.0 | 0.00 | **42.9** | — |
| Darius Garland | LAC |  | 3 | 102 | 34.0 | 35.0 | 0.97 | **42.8** | -8.8 |
| Lauri Markkanen | UTA |  | 3 | 106 | 35.3 | 36.0 | 0.98 | **42.4** | -7.1 |
| Jaren Jackson Jr. | UTA |  | 3 | 101 | 33.7 | 31.3 | 1.07 | **40.5** | -6.9 |
| Damian Lillard | POR |  | 2 | 85 | 42.5 | 28.5 | 1.49 | **38.6** | +3.9 |
| Fred VanVleet | HOU |  | 2 | 87 | 43.5 | 31.0 | 1.40 | **34.4** | +9.1 |
| Aaron Gordon | DEN |  | 2 | 69 | 34.5 | 33.0 | 1.04 | **32.4** | +2.1 |
| Darius Acuff Jr. | SAC |  | 3 | 82 | 27.3 | 36.0 | 0.76 | **31.4** | -4.1 |
| Jonathan Kuminga | MIN |  | 3 | 107 | 35.7 | 27.7 | 1.29 | **29.3** | +6.4 |
| Toumani Camara | POR |  | 2 | 76 | 38.0 | 25.0 | 1.52 | **27.0** | +11.0 |

**Research:**

- **Darius Acuff Jr. — usage.** Coach Doug Christie is NOT reining him in — "He's special." His shot-selection note was generic and team-wide: do not settle late, "the last seven seconds, which we call butter or fire." The pushback comes from SABONIS: "we took a lot of one-pass shots, pick-and-roll shots without passing the ball," asking for the ball more. Acuff 5-of-24, then 10-of-26 for 33. Implication: the touches are coming out of Sabonis's share, not LaVine's. _(SacTown Sports, SI Kings)_

## The Big Chin

_13 players · 1411 fantasy points produced_

| player | NBA | | GP | total | /g | mpg | /min | **proj full/g** | Δ |
|---|---|---|---|---|---|---|---|---|---|
| Cade Cunningham | DET |  | 3 | 141 | 47.0 | 32.7 | 1.44 | **55.1** | -8.1 |
| Domantas Sabonis | SAC |  | 3 | 183 | 61.0 | 36.0 | 1.69 | **53.1** | +7.9 |
| Trae Young | WAS |  | 3 | 140 | 46.7 | 36.3 | 1.28 | **46.4** | +0.3 |
| Austin Reaves | LAL |  | 3 | 153 | 51.0 | 35.3 | 1.44 | **46.0** | +5.0 |
| Ty Jerome | MEM |  | 3 | 176 | 58.7 | 32.0 | 1.83 | **41.6** | +17.1 |
| Stephon Castle | SAS |  | 3 | 116 | 38.7 | 29.7 | 1.30 | **41.2** | -2.5 |
| Alex Sarr | WAS |  | 3 | 84 | 28.0 | 24.0 | 1.17 | **40.7** | -12.7 |
| Keyonte George | UTA |  | 3 | 128 | 42.7 | 31.3 | 1.36 | **38.7** | +4.0 |
| Naz Reid | CHA |  | 3 | 119 | 39.7 | 31.7 | 1.25 | **38.4** | +1.2 |
| Kevin Porter Jr. | ? |  | 0 | 0 | 0.0 | 0.0 | 0.00 | **36.4** | — |
| Mikal Bridges | NYK |  | 3 | 33 | 11.0 | 30.0 | 0.37 | **35.5** | -24.5 |
| Derik Queen | NOP |  | 3 | 103 | 34.3 | 24.0 | 1.43 | **34.1** | +0.2 |
| Brandin Podziemski | GSW |  | 1 | 35 | 35.0 | 33.0 | 1.06 | **33.3** | +1.7 |

## TanTheMan’s TerrifyingTeam

_13 players · 1271 fantasy points produced_

| player | NBA | | GP | total | /g | mpg | /min | **proj full/g** | Δ |
|---|---|---|---|---|---|---|---|---|---|
| Jalen Johnson | ATL |  | 3 | 174 | 58.0 | 31.7 | 1.83 | **55.9** | +2.1 |
| Tyrese Maxey | PHI |  | 4 | 210 | 52.5 | 38.0 | 1.38 | **47.3** | +5.2 |
| Jamal Murray | DEN |  | 2 | 79 | 39.5 | 40.0 | 0.99 | **46.7** | -7.2 |
| Stephen Curry | GSW |  | 2 | 67 | 33.5 | 25.5 | 1.31 | **45.2** | -11.7 |
| Zion Williamson | NOP |  | 3 | 119 | 39.7 | 32.7 | 1.21 | **43.6** | -3.9 |
| Donovan Clingan | POR |  | 2 | 67 | 33.5 | 21.0 | 1.59 | **41.3** | -7.8 |
| Desmond Bane | ORL |  | 3 | 71 | 23.7 | 31.7 | 0.75 | **40.9** | -17.3 |
| Dyson Daniels | ATL |  | 3 | 159 | 53.0 | 29.0 | 1.83 | **40.4** | +12.6 |
| Kel'el Ware | MIL |  | 3 | 81 | 27.0 | 19.3 | 1.40 | **39.0** | -12.0 |
| Caleb Wilson | CHI |  | 3 | 120 | 40.0 | 34.3 | 1.17 | **35.9** | +4.1 |
| Payton Pritchard | BOS |  | 2 | 34 | 17.0 | 29.0 | 0.59 | **34.3** | -17.3 |
| Reed Sheppard | HOU |  | 2 | 65 | 32.5 | 23.0 | 1.41 | **31.9** | +0.6 |
| DeMar DeRozan | DEN |  | 2 | 25 | 12.5 | 26.0 | 0.48 | **31.6** | -19.1 |

## Why so serious

_14 players · 1193 fantasy points produced_

| player | NBA | | GP | total | /g | mpg | /min | **proj full/g** | Δ |
|---|---|---|---|---|---|---|---|---|---|
| Nikola Jokic | DEN |  | 2 | 122 | 61.0 | 39.5 | 1.54 | **76.9** | -15.9 |
| Josh Giddey | CHI |  | 3 | 71 | 23.7 | 26.3 | 0.90 | **51.5** | -27.9 |
| Kawhi Leonard | TOR | **OUT** | 2 | 84 | 42.0 | 26.0 | 1.61 | **48.6** | -6.6 |
| Evan Mobley | CLE |  | 2 | 96 | 48.0 | 34.5 | 1.39 | **48.6** | -0.6 |
| Jalen Williams | OKC | **DAY_TO_DAY** | 3 | 85 | 28.3 | 31.7 | 0.90 | **43.6** | -15.3 |
| Tyler Herro | MIL |  | 3 | 118 | 39.3 | 31.7 | 1.24 | **40.6** | -1.3 |
| Onyeka Okongwu | ATL |  | 3 | 68 | 22.7 | 25.7 | 0.88 | **38.9** | -16.2 |
| Josh Hart | NYK |  | 3 | 111 | 37.0 | 33.7 | 1.10 | **36.8** | +0.2 |
| Cameron Boozer | MEM |  | 3 | 112 | 37.3 | 33.7 | 1.11 | **35.3** | +2.0 |
| RJ Barrett | TOR |  | 3 | 113 | 37.7 | 30.7 | 1.23 | **35.1** | +2.6 |
| Ryan Rollins | MIL |  | 3 | 80 | 26.7 | 27.7 | 0.96 | **34.2** | -7.5 |
| Tobias Harris | SAS | **OUT** | 0 | 0 | 0.0 | 0.0 | 0.00 | **32.8** | — |
| Dillon Brooks | PHX |  | 2 | 36 | 18.0 | 30.5 | 0.59 | **29.1** | -11.1 |
| Julian Champagnie | SAS |  | 3 | 97 | 32.3 | 27.7 | 1.17 | **26.3** | +6.1 |

**Research:**

- **Nikola Jokic — weakness.** Underperforming per minute worse than anyone on my roster: 2.182/min last season -> 1.916 projected -> 1.544 now, down 29%. He is only posting 61/g because Denver plays him 39.5 mpg against a 35.6 projection. If that load regresses he drops toward 55/g; if his RATE returns at that load he is a 75/g player. Biggest single swing factor in matchup 2. _(own calc)_

## Sparsh's Smart Team

_15 players · 1168 fantasy points produced_

| player | NBA | | GP | total | /g | mpg | /min | **proj full/g** | Δ |
|---|---|---|---|---|---|---|---|---|---|
| Jayson Tatum | BOS |  | 2 | 104 | 52.0 | 37.5 | 1.39 | **52.6** | -0.6 |
| Donovan Mitchell | CLE |  | 2 | 94 | 47.0 | 35.0 | 1.34 | **49.1** | -2.1 |
| James Harden | CLE |  | 2 | 51 | 25.5 | 33.0 | 0.77 | **45.2** | -19.7 |
| Deni Avdija | POR |  | 2 | 90 | 45.0 | 30.5 | 1.48 | **44.1** | +0.9 |
| Paolo Banchero | ORL | **OUT** | 2 | 96 | 48.0 | 33.5 | 1.43 | **43.0** | +5.0 |
| Brandon Ingram | LAC | **OUT** | 0 | 0 | 0.0 | 0.0 | 0.00 | **40.9** | — |
| De'Aaron Fox | SAS |  | 3 | 136 | 45.3 | 31.3 | 1.45 | **40.8** | +4.5 |
| Ja Morant | POR |  | 2 | 83 | 41.5 | 25.0 | 1.66 | **40.4** | +1.1 |
| Kon Knueppel | CHA | **OUT** | 0 | 0 | 0.0 | 0.0 | 0.00 | **38.2** | — |
| John Collins | DET |  | 3 | 105 | 35.0 | 29.3 | 1.19 | **35.0** | +0.0 |
| Ausar Thompson | DET | **OUT** | 2 | 58 | 29.0 | 26.0 | 1.11 | **34.6** | -5.6 |
| AJ Dybantsa | WAS | **OUT** | 0 | 0 | 0.0 | 0.0 | 0.00 | **33.9** | — |
| Jaime Jaquez Jr. | MIL |  | 3 | 109 | 36.3 | 31.0 | 1.17 | **31.3** | +5.1 |
| Jabari Smith Jr. | HOU |  | 3 | 114 | 38.0 | 34.3 | 1.11 | **31.2** | +6.8 |
| Yaxel Lendeborg | GSW |  | 3 | 128 | 42.7 | 34.0 | 1.25 | **24.5** | +18.2 |

## Yash's Hearty Team

_13 players · 1100 fantasy points produced_

| player | NBA | | GP | total | /g | mpg | /min | **proj full/g** | Δ |
|---|---|---|---|---|---|---|---|---|---|
| Anthony Edwards | MIN |  | 3 | 141 | 47.0 | 31.3 | 1.50 | **49.5** | -2.5 |
| Jalen Brunson | NYK |  | 3 | 91 | 30.3 | 34.3 | 0.88 | **46.4** | -16.1 |
| LeBron James | PHI |  | 3 | 116 | 38.7 | 33.3 | 1.16 | **45.9** | -7.3 |
| Bam Adebayo | MIA |  | 3 | 100 | 33.3 | 31.0 | 1.07 | **44.6** | -11.3 |
| Pascal Siakam | IND |  | 3 | 113 | 37.7 | 30.0 | 1.26 | **44.3** | -6.6 |
| Michael Porter Jr. | BKN |  | 3 | 117 | 39.0 | 29.3 | 1.33 | **42.2** | -3.2 |
| Jarrett Allen | CLE |  | 2 | 76 | 38.0 | 27.5 | 1.38 | **42.2** | -4.2 |
| Norman Powell | CHI |  | 3 | 88 | 29.3 | 29.3 | 1.00 | **37.9** | -8.5 |
| Miles Bridges | PHX |  | 2 | 54 | 27.0 | 31.0 | 0.87 | **36.7** | -9.7 |
| Coby White | CHA | **OUT** | 0 | 0 | 0.0 | 0.0 | 0.00 | **34.8** | — |
| CJ McCollum | ATL |  | 3 | 77 | 25.7 | 25.7 | 1.00 | **34.7** | -9.1 |
| Jalen Green | PHX |  | 2 | 30 | 15.0 | 25.5 | 0.59 | **34.5** | -19.5 |
| Ayo Dosunmu | MIN |  | 3 | 97 | 32.3 | 26.3 | 1.23 | **32.7** | -0.4 |


## General research

- **Lloyd Monday recap — what it will cover.** One show will update ALL FOUR open questions: Davis and Miller are in WSH @ CHA together, Buzelis and Paul George are in CHI @ BOS together, Edey is at UTAH. Pull it as soon as it posts and run ./fantasy/lloyd.sh on each name. _(scheduling)_
- **Monday 26 Oct slate — my players.** WSH @ CHA 7:00 (Anthony Davis + Brandon Miller, same game), CHI @ BOS 7:30 (Matas Buzelis + Paul George, same game), DAL @ MIA 7:30 (Giannis), ATL @ HOU 8:30 (Amen Thompson), MEM @ UTAH 9:00 (Zach Edey + Cedric Coward). Idle: Wemby, LaVine, Dejounte, Paul Reed, Murray-Boyles, Keegan Murray (OUT). Seven or eight startable for ten slots — three slots go empty regardless. _(ESPN scoreboard)_
- **analyst consensus — the three strugglers.** Outside analysts and my own per-minute work agree on causes and split on urgency. All three are EFFICIENCY problems with roles intact; none is a minutes problem (Buzelis aside, whose one benching resolved). Nobody credible is calling for a drop. The concrete triggers are: Kon Knueppel returning (Miller's load lightens), Buzelis's three-point rate and defensive counting stats, and AD's 41.5% FG normalising. Lloyd has NOT recapped any of the three since the slumps deepened — his Monday recap after WSH@CHA on 26 Oct covers Davis and Miller in the same game. _(NBC/Rotoworld, CBS/Rotowire, own calc)_
- **method — abbreviations.** The fantasy API uses WAS/SAS/NOP/GSW/UTA/NYK; the public scoreboard uses WSH/SA/NO/GS/UTAH/NY. Unnormalised, this silently drops players from "who plays today" — it hid Anthony Davis from a slate he was playing. _(session)_
- **method — live score.** ESPN matchup `totalPoints` LAGS BY A DAY and excludes the current scoring period. `totalPointsLive` is the real score; `winner` ("UNDECIDED" vs a team id) is the only reliable signal a matchup closed. I reported 1134-995 (+139) three times when the true live score was 1278-1273 (+5). _(ESPN API)_
- **method — partial slates.** Never report an in-progress slate as final. On 23 Oct I filed Edey at 28 fp when he finished at 43, and called the night a 100-point shortfall off partial box scores. Check every game status first. _(session)_
- **opponent — I Finish Quickley.** Has NEVER proposed a trade — five declines, zero proposals. Pure waiver operator: Ausar Thompson, Jrue Holiday, Rui Hachimura, Andrew Wiggins, Jake LaRavia, then added Jalen Suggs on 23 Oct two days before his knee injury, dropped him 25 Oct and took Davion Mitchell + Ajay Mitchell. _(transactions table)_
- **opponent — Why so serious.** Matchup 2 opponent. Kawhi Leonard OUT (knee swelling; Lloyd: "his knee is rooted"), Jalen Williams day-to-day with what Lloyd called a broken ankle/leg — "I don't think there's any chance that we are seeing him again this season." Tobias Harris out. BUT they still have Jokic 61/g and Mobley 48/g, and they REFUSED Kyrie + KAT + Haliburton from Top G for Jokic. They are not selling. _(Lloyd 25 Oct, transactions table)_