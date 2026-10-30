# Watchlist — open questions with a dated trigger

## Monday 26 October — one night answers four questions

| game | my players | what to watch |
|---|---|---|
| **WSH @ CHA 7:00** | **Anthony Davis + Brandon Miller** | Davis: rebounds and FG% (41.5% on 17.7 attempts; his six boards on 24 Oct were a season low). Miller: **free throw attempts** — Rubin's point, 3 FTA in two games then 12 on 24 Oct, and a made FT is +2 net here |
| **CHI @ BOS 7:30** | **Matas Buzelis + Paul George** | Buzelis: **three-point rate and stocks** — 0.33 stl / 1.00 blk vs 0.70 / 1.51 last season, the two levers Rotoworld named. George: whether the 73 was real |
| DAL @ MIA 7:30 | Giannis | **minutes** — 29.3 mpg vs 33.6 projected, the quiet problem nobody is tracking |
| ATL @ HOU 8:30 | Amen Thompson | running 26% above projection per minute; just confirm it holds |
| **MEM @ UTAH 9:00** | **Zach Edey** + Coward | **Does he clear 25 minutes?** Sat the FIRST leg of the back-to-back, which is the tell he plays the second. **Verify the injury report before lock.** |

Idle Monday: Wemby, LaVine, Dejounte, Paul Reed, Murray-Boyles, Keegan (OUT).
Seven or eight startable for ten slots — three go empty regardless.

**Lloyd's Monday recap covers all four questions in one show.** Pull it as soon as it posts,
then `./fantasy/lloyd.sh` each name.

## ~12 November — Edey's hard trigger

Lloyd's exact words, 23 Oct: *"If he's still playing minutes in the low 20s in two or three
weeks, then I would start to kind of wonder if this is a bit of a trend."* He is at 21.5 mpg
on 1.651 fp/min — **the highest rate on my roster.** Purely a minutes and availability
question. He also ranks Edey over Poeltl outright: *"I'd prefer Edy over Purle."*

## Standing

- **Brandon Miller — Knueppel and Coby White returning** is the real trigger, not a hot
  night. Rubin: *"Miller is going to continue to get as many shots as he wants until Kon
  Knueppel returns."* No timeline on either as of 21 Oct. Separately, his **left shoulder**
  (surgery May 2026, not cleared for basketball until after 28 Aug) is the one flag.
- **Paul George — do not plan around 53.5/g.** That is 73 and 34. The 73 had seven threes
  and five steals. True level is likely 42-48; Lloyd's "top 30 possible" is the bull case.
- **Dejounte is still the only PG-eligible player.** If he sits, the slot is forfeited.
- **Start LaVine over Murray-Boyles.** 42.3/g on 37.7 mpg vs 23.7/g on 19.0. CMB's blocker
  is fouls — 10 in 57 minutes, 6.3 per 36.
- **Keegan Murray** remains the drop when a spot is needed.
- **Anthony Davis** — the question is games played, not production. Break-even on the
  LaMelo trade is ~36-38 games.

## Method — run these before claiming anything

```
python3 fantasy/verify.py quote "<words>"   # zero hits = do not attribute to Lloyd
python3 fantasy/verify.py score             # LIVE score; totalPoints lags a full day
python3 fantasy/verify.py slate             # are games still running?
./fantasy/lloyd.sh <player>                 # newest first, expands caption manglings
./fantasy/q.sh "SELECT ..."                 # the database
```

## AD right hand + Markkanen hand — opened 26 Oct 2026

**Two separate hand events the same night, one on each side of a proposed trade.**

- **Anthony Davis (WAS), right/shooting hand.** User watched it get hit **at the end** of
  WSH @ CHA (Final, CHA 110-103). He had already banked 36 min / 50.0 applied fpts
  (29/10/0, 11-22 FG, 4-4 FT) — the hit does not show in the line. **Nothing reported**
  as of this writing; he was absent from the game's injury node entirely.
  Note his *other* hand carries history: left (non-shooting) hand ligament damage, hurt
  8 Jan 2026 vs Utah as a Maverick, **surgery declined** in favour of ~6-week rehab after
  a second opinion with Dr. Steven Shin, never fully resolved — shut down for the season
  with hand + groin at **20 GP**, debuted for Washington 21 Oct 2026.
- **Lauri Markkanen (UTA), hand.** Left MEM @ UTAH early — hand caught between Cameron
  Boozer and Jaren Jackson Jr. **6 minutes, did not return**, ESPN flag Day-To-Day / GTD
  type "Hand". Game was still in the 2nd quarter when checked; **post-game X-rays pending.**

**Trigger — before accepting or sending LaMelo Ball + Markkanen for AD:**
1. Markkanen's X-ray result. Contusion/sprain → deal is live. Fracture or ligament → swap
   the second piece (see below).
2. Washington's next injury report, for "Davis" with a hand or finger designation.
3. If AD plays: watch **FG% and FT%, not minutes.** A bad shooting hand suppresses rate
   while the role holds — the *identical* signature to his current `BUY LOW` flag
   (form_z -1.18, min_ratio 1.004), but it does **not** regress upward. Treat that
   buy-low signal as unreliable until the hand is clarified.

**Second piece matters more than the deal.** Gain to the starting ten vs AD out:
Towns **+10.9**/g, Haliburton **+9.4**, Garland +2.6, Markkanen +2.2, JJJ +0.3.
Everything below Haliburton is inside the method's error (rule 10) — the Markkanen
version is a wash on points and rests entirely on the PG fix and the 20-GP durability swap.

## Zach Edey's left ankle — opened 27 Oct 2026

**New information that was not in any of our notes.** Rotoworld, 24 Oct 2026: *"Zach Edey
(ankle) ruled out vs. Sacramento"* — **left ankle, injury management.** That is why he sat
the first leg of the back-to-back, and it is a better explanation of the 21 minutes / **two
shot attempts** than Iisalo's "very conservative" line alone. RotoWire's preseason note
flags *"recurring ankle injuries."* **ESPN reads ACTIVE** — rule 27's blind spot again.

Lloyd is **explicitly** a buy-low here (*"It is a clear by low to me, but it's painful"*) and
**does not mention the ankle**, so his call is priced without it.

**Trigger:**
1. Memphis's next injury report for "Edey" with an ankle designation. Clean → Lloyd's buy-low
   is live at full size.
2. If he plays: watch **FGA, not minutes.** Two attempts in 21 minutes is the whole problem
   (usg 14.3%, ratio 0.77 USG-DOWN). A ramp shows up as attempts before it shows as points.
3. Lloyd's own earlier date, **~12 Nov**, stands as the point at which a still-suppressed role
   stops being a ramp and becomes the role.
4. Note the per-minute rate is **the best on my roster at 1.674** — this is purely a
   usage-and-availability question, not an ability question.

### Amendment — the minutes themselves, from play-by-play (27 Oct 2026)

**21 / 22 / 21 is a fixed script, not variance.** All three games: pulled at Q1 7:07 / 7:33 /
7:41, back at **Q2 12:00 every game**, **Q3 12:00 every game**, **Q4 12:00** both games he was
needed. Four stints of ~5 minutes = the first ~4:30-5:00 of each quarter.

**And he CLOSES.** 23 Oct: in at Q4 4:17, finished a **3-point game**. 26 Oct: in at Q4 5:40,
finished a **5-point game carrying five fouls**. 21 Oct: in at 3:36, out at 1:32 — a 20-point
blowout, pure rest. **Two of three, both the close ones.** A coach who caps a man at 21 and plays
him in the last five minutes of a one-possession game is managing load, not demoting him.

**26 Oct was fouls.** Five in ~15 minutes of floor time, one ending each stint (Q1 10:14,
Q2 11:29, Q2 8:54 → pulled, Q3 11:25 offensive foul, Q3 9:18 → pulled instantly). He fouled five
times, turned it over three times, shot 0-for-2 — **and still got 21 minutes and closed.** The 21
is behaving like a **floor**, not a performance ceiling.

**Q4 is his biggest quarter in every game, and it is growing.** Stint reconstruction:

| | Q1 | Q2 | Q3 | **Q4** | Total |
|---|---|---|---|---|---|
| 21 Oct | 4:53 | 4:16 | 4:15 | **7:41** | 21 |
| 23 Oct | 4:27 | 4:30 | 5:23 | **8:06** | 22 |
| 26 Oct | 4:19 | 3:26 | 2:42 | **10:08** | 21 |

Memphis **rests him through the first three quarters and spends him at the end.** On the night he
committed five fouls he got his **longest fourth quarter of the season**, in a 5-point game. The
fouls cost ~2:48 across Q2+Q3 and the fourth quarter gave all of it back — which is why the total
still landed on 21. This reverses the natural reading of "MINS-DOWN every night."

**⚠ Correction to my own usage read.** `usg_ratio` climbed 0.51 → 0.62 → **0.77** and looked like
a clean ramp. Decomposed, it isn't: **FGA went 5 → 6 → 2.** The 26 Oct rise is 4 free throws and
3 turnovers, not shots. For a low-volume big the usage axis must be decomposed before it is read —
Lloyd was right on *attempts* and our headline metric flattered him.

**For him to reach his 26.4 projection, minutes must come off Quinten Post (19/20/12) or Isaiah
Stewart (0/16/15).** Memphis is splitting 48 centre minutes three ways. That is the thing to watch,
not his point totals.

**Data-quality note:** `players.status` reads `OUT` for Edey and is **stale** (captured during the
25 Oct DNP). Live ESPN returns `injured=False / ACTIVE`. Use `player_form.injury`.

## Amen Thompson's 28 minutes — REOPENED and re-diagnosed, 27 Oct 2026

**My first answer was wrong and the user caught it.** I offered Udoka's preseason *"10-man
rotation... keeping Kevin Durant and Amen Thompson's minutes down"* as the mechanism. The
play-by-play (ESPN event `401909874`) refutes it:

- Houston did **not** play a 10-man rotation — **seven** players cleared 13 minutes; Tate,
  Crawford and Thornton got 1 minute each in the final 1:22.
- I used Durant's drop to 30 as corroboration. It is **not independent** — Durant and Thompson
  came out in the *same substitution* at Q4 12:00, and Durant never returned. One fact, counted
  twice.
- The user's objection is simply correct: Thompson played **33 and 36** in the two games
  VanVleet was active, and his 39 came with VanVleet **out**. Neither VanVleet nor a season cap
  explains 28.

**What actually happened — the whole shortfall is the fourth quarter.** Pulled at **Q4 12:00**
with Houston up 91-85. Did **not return until 2:56 at 118-103**, out again at 1:22. By quarter:
10:05 / 6:52 / 9:01 / **1:34**. Through three quarters he was at 25:58 against 37:33 on 23 Oct —
and that night he came back at Q4 8:17 because the game stayed close (114-110) and **he closed
it**. Houston went **+9 in the nine minutes he sat** (91-85 → 118-103; 106-93 by 7:47) with
Sengun / Jabari / Eason / VanVleet / Sheppard-Bogdanovic.

**Not foul trouble — ONE personal foul in 28 minutes.** Not garbage time he rested in — a
6-point game at the quarter break. He was also the **only Houston starter with a negative
plus-minus (−3)** against Sengun +29, and had 5 of the team's turnovers.

**Best reading:** a routine quarter-break substitution that became a nine-minute absence because
the replacement unit broke the game open while he sat. **Score-dependent, not role-dependent** —
but he was on the bench for the decisive stretch, which is what the user said from the start.

**The pattern that IS real:** Udoka pulls him early in **every** fourth quarter; only the
re-entry varies, and it varies with the score. 21 Oct out 9:54 / back 7:00. 23 Oct out 12:00 /
back 8:17, closed. 24 Oct out 8:49 / back 6:51, closed. 26 Oct out 12:00 / back 2:56, did not
close. **He has closed two of four.** He is at 34.0 mpg against 37.39 last season and a 36.5
projection — down ~3.4.

**Trigger:** a **second competitive fourth quarter spent on the bench.** That, not a low point
total, is what would re-rate him. Also watch **Marcus Smart's return** — he was active 21/23
Oct and out 24/26, so the bench group that closed Monday changes when he is back.

## AD's hand — amendment, 27 Oct 2026

**Lloyd says wrist, not hand**, and he is the only outside voice who mentioned it at all:
*"he looked to be shaking his wrist a bit... I don't know how true that is. It probably isn't...
But of course, it's Anthony Davis, so we got to be a little bit concerned."* Noah Rubin's
Rotoworld recap of the same game **does not mention any injury.** Keefe said hand. Two
observers, two limbs, both skeptical of Davis's "cooling off" explanation.

**Date-check trap for this thread:** a Rotoworld related-news item quoting Keefe that Davis
*"(hand) isn't expected to play again this season"* is from the **2025-26 shutdown**, not now.

## Markkanen's hand — CLOSED 28 Oct 2026

**He's fine.** Lloyd: *"Larry Markin looks to be okay. He's considered day today."* ESPN:
`injured=False`, `status=DAY_TO_DAY`. The 26 Oct scare (hand caught between Boozer and JJJ,
6 minutes, X-rays pending) resolved with no structural damage. No action — and note he's
owned by **Top G**, my matchup-period-3 opponent, so this is not in my favour.

## Murray-Boyles — Kawhi is out, opened 28 Oct 2026

**Kawhi Leonard is a Raptor and ESPN now reads him `OUT`** (26.0 mpg over 2 games, 48.6
projected in our scoring). That is the first genuine opening for CMB all season. It also
hurts **Why so serious — my current opponent** — who owns him.

Toronto's wing/forward minutes: **Kawhi OUT**, Barnes 30.3, Barrett 30.7, Quickley 28.3,
**CMB 19.0** (projected 22.9, `min_ratio` 0.83). So ~26 minutes are up for redistribution and
CMB is the one with headroom.

**But Lloyd hedges, and he prefers a player we don't roster:** *"we talked about Kawaz.
**Jacobe Walter is the guy that I like there. I hope we get more out of Colinary Boils, but I
don't know if we will.**"*

**Trigger — CMB's minutes in Toronto's next game.** 19 → 25+ makes him startable over Buzelis
or Edey. 19 → 20 means Walter took the minutes and CMB stays a bench body. Watch minutes, not
points; he's a 23.7/g player whose problem has only ever been floor time.

**✅ UPDATED 29 Oct — Lloyd has firmed from hedge to hold, and dropped the Walter preference.
Keeping CMB was the right call.** Three times in the mailbag: *"I think you just got to hold
him. Early fouls yesterday."* · *"Just just hold on it, man... **let's see where the minutes
go.**"* · and refusing Malik Thomas/Tyson over him: *"**Murray Boils is a guy that should be
closing games and playing 25 minutes a night.**"* Asked directly whether Walter or Achiuwa is
the better points-league pickup, he no longer picks Walter: *"I think I'd probably take
Precious."* The thesis is now simply **19 actual vs the 25 Lloyd says he should play.**

## Paul Reed — Lloyd explicit, 28 Oct 2026

*"he just has to be rostered while Duran is out. And then we figure it out later on. Has to
be."* ESPN confirms **Jalen Duren `OUT`**. Our grades agree — two straight `ROLE-UP` + `FED`
games. Same expiry on both reads: **Duren's return.** Keep him in the C slot until then.

**⚠ UPDATED 29 Oct — the window may be half what I logged.** Lloyd in the mailbag: *"you
absolutely keep a top 40 player in IIL **if he might be back in a week.**"* I had Duren at
**≥2 weeks** (hamstring). Lloyd is working from **one week**. Re-check Detroit's own injury
report rather than trusting my figure, and **do not plan the C slot past next week on Reed.**

## ⚠ LINEUP — three starters sitting on the bench, opened 29 Oct 2026

**Lineup lock is `INDIVIDUAL_GAME`** (confirmed in `mSettings`), so slots must be set *every
day*, per tipoff. Tonight nothing was lost — SAS, MIA and TOR were all off — but the slate
flips immediately.

| Date | My players who play | Currently benched among them |
|---|---|---|
| **30 Oct** | 8: Amen, B. Miller, Reed, Davis, George, Buzelis, **Giannis**, **CMB** | **Giannis 58.5/g, CMB 18.0/g** |
| **31 Oct** | 6–7: Amen, Miller, Coward, Edey, LaVine, **Wemby** (+Dejounte if cleared) | **Wembanyama 69.8/g** |
| **1 Nov** | 2: George, **CMB** | **CMB 18.0/g** |

Eight players for ten slots on the 30th, so **everyone who plays fits** — there is no tradeoff
to weigh. On the 31st **Wemby goes in the `C` slot**, which is free because Reed's Detroit is off.

**Trigger — before each day's first tipoff.** Leaving it alone costs **164.3 points** across the
three days and flips matchup period 2 from a projected **+119.6 win to a −44.7 loss**. Re-check
the day's slate against `proTeamId` each morning; this is now the highest-value recurring action
in the week.

## Dejounte Murray — out for PERSONAL reasons, opened 29 Oct 2026

**Not an injury**, despite ESPN reading `DAY_TO_DAY`. FantasyPros has him a **late scratch**,
ruled out Thursday; CBS lists the reason as **personal** and expects him out **through at least
31 Oct** — which is New Orleans' only remaining game this matchup period (ATL @ NO).

Two consequences: **(a)** rule 27's injury confounder does **not** apply, so do not read his form
as injury-suppressed — his weak 28 Oct (27.0 in 30 min, 0.90 fpts/min, usage down to 20.1 from
27.4/26.5) is just a bad game, and Lloyd agrees: *"Dejonte Murray not great 108 and five has
been pretty good though so I'm not particularly concerned about that."* **(b)** He is my **only
PG-eligible player**, so the slot is simply forfeited — there is no internal fix.

**Trigger — New Orleans' 31 Oct injury report.** If he is out again the PG slot is dead for the
week; the standing weakness is now a realised cost, not a hypothetical.

## Coward's usage — ARRIVED, closing the 26 Oct thread, 29 Oct 2026

Four games, monotonic on **both** axes: usage **8.5 → 18.6 → 20.1 → 24.0** (`FROZEN` → `USG+`)
and fpts/min **0.89 → 1.31 → 1.39 → 1.70**. Tonight **46.0 in 27 minutes**, z +1.28, on *flat*
minutes (28/32/31/27, `MINS-OK`). Every bit of the gain is touches and efficiency rather than
floor time — the configuration that actually holds.

**One thing still has not improved: zero FTA**, again. No free-throw floor means every miss is a
clean −1. That is the cap on him, not the role.

## Edey — the cap is real, but the role is growing inside it, 29 Oct 2026

Minutes **21/22/21/19**, `MINS-DOWN` in all four. Usage climbing anyway: **9.5 → 11.5 → 14.3 →
17.1**. Tonight 29.0 in 19 min, 13p/7r on 6-of-8, 1.53 fpts/min.

**This is a different finding from 26 Oct and a better one.** Then the usage rise was FTA + TOV
while FGA *fell* 5 → 6 → 2. Tonight it is **8 FGA, his highest** — the rise is now real shot
volume. Minutes caveat: MEM won by 21 at Portland, so the 4th was garbage time; 19 minutes in a
blowout is not a demotion. At 30 minutes his current rate is ~46/g.

**Web search found nothing current** — every ankle hit was 2025 or early 2026 (two surgeries, a
stress reaction). The management premise stands unrefuted but also unconfirmed.

**CORRECTED same night, from Lloyd's recap.** I said garbage time. Lloyd said *"He had foul
trouble again. He played 19 minutes."* The box score is **4 PF in 19 minutes** and a **−4** in
a 21-point win — he sat because he was in trouble, not because it was over.

**But the full foul series shows neither read was whole.** PF by game: **3, 2, 5, 4** in
21/22/21/19 minutes. Two and three fouls cannot explain the first two 21-minute games, so the
~21-minute baseline really is a **coaching cap** (my original read); the last two games at 5
and 4 fouls are why he can't even reach it (Lloyd's read). Correct synthesis: **the coach set a
21–22 minute ceiling and Edey's fouls have recently kept him under it.** Watch fouls per 36,
not just minutes — and note **Coward also had 5 fouls** in 27 minutes tonight.

**Lloyd's action call is explicit hold:** *"the answer to that is literally nothing... if
someone drops him, add immediately. And if you've got him, just suck it up, big boy."*

## Matchup period 1 — FINAL, a 3-POINT LOSS, and it was the lineup, opened 29 Oct 2026

**The Big Chin 1276.0 — The Freaky Alien 1273.0.** ESPN revised the opponent *down* from 1278
to 1276 after stat corrections and it still wasn't enough. **Record is 0-1, not 1-0** — I had
been reporting it wrong all week.

**The cause was leakage, not talent:**

| | |
|---|---|
| My roster **generated** (periods 1–6) | **1358.0** |
| What actually **counted** | **1273.0** |
| Forced by the 10-slot cap | ~31 (21 Oct: 11 played, drop Keegan 7 · 23 Oct: 12 played, drop Buzelis 15 + Miller 9) |
| **Avoidable** | **~54** |
| **Margin of defeat** | **3** |

I checked slot eligibility on both crowded days — all ten fit, so the cap genuinely only forced
~31. *(Caveat: Naji Marshall's 24.0 on 24 Oct may not have been available if his 18:58 drop beat
tipoff; that makes it ~30 avoidable, still ten times the margin.)*

**And I lead the entire league in points scored — 2207.0**, ahead of Skywalking 2183 and
TanTheMan 2078. Best offence in the league, 0-1. **The roster is not the problem; the daily
lineup is.** This is the same failure as the Giannis/Wemby bench entry above, and it has now
cost a week.

## ⚠ 2 Nov / 4 Nov — the cap will bind hard, opened 29 Oct 2026

Lloyd: *"a 15 game Monday, a zero game Tuesday, and a 14 game Wednesday."* So **2 Nov = 15
games, 3 Nov = ZERO, 4 Nov = 14 games.** On a 15- and a 14-game day far more than ten of my
players are active, so for the first time the 10-slot cap forces real **choices** rather than
just "start whoever plays" — the exact condition that lost matchup period 1.

**Trigger — build the 2 Nov and 4 Nov lineups the night before**, not in the morning. The
zero-game Tuesday is dead for both teams, so no edge either way.

## Paul George — Lloyd prices him top 40, which changes a trade shape, 29 Oct 2026

Unprompted, in answer to someone else's *George-for-Buzelis* question: *"**It's pretty bloody
high**"* that George outperforms Buzelis, *"**Bzalis's value is in the toilet. You do not need
to give up a top 40 player to get him.**"* And: *"What do you do with Paul George? **You just
bloody love it.**"* I own **both** names in that question.

**Consequence for the open LaMelo work.** On 29 Oct I offered two acceptable shapes: *Coward
straight up* or *George straight up*. Lloyd's top-40 tag raises George's cost, and he separately
refuses to call LaMelo a drop (*"only if you're in a coma"*), so George-for-LaMelo is roughly
**top-40 for top-40** — exactly the trade he says to skip: *"if a trade doesn't work out in a
way where you feel confident in it, don't do it."* **The Coward shape is now the cleaner of the
two.** Still never send both.

## Dejounte — Lloyd turns negative on the situation, 29 Oct 2026

*"**Deonte Murray actually isn't playing well and he's hampering the other guys.**"* · *"**The
Pelicans fans hate him at the moment**... **It's not looking great.**"* Plus live trade
speculation, and **Herb Jones** back in the starting five at 32 minutes (after sub-20 all
season) with a team-best **+27**.

This does **not** contradict his *"not particularly concerned"* line from the Wednesday recap —
that was about one box score, this is about role, fit and trade risk. Both same day, both his.

**Why it hits me harder than anyone:** he is my **only PG-eligible player.** A trade to a worse
spot, or Jones/Fears eating his minutes, forfeits the slot with no internal fix. Our numbers
already show it: 28 Oct was 0.90 fpts/min on usage **down to 20.1** from 27.4/26.5 — that drop
now has an opinion attached to it.

**Trigger — whether he starts, and at what usage, in New Orleans' next two games.**

## ⚠ Lloyd's "don't panic" does NOT cover matchup 1, noted 29 Oct 2026

*"I don't really care that much if I take an L in week one or week two because I like to see
some things settle."* · *"Stop panicking. Stop making snap decisions off one game."*

**He is right, and it is about the wrong thing.** That is a sound argument against churning the
**roster** on early results — and I should apply it (don't drop Buzelis, don't chase Walter,
hold CMB and Edey). It is **not** a defence of the matchup-1 loss: that was **~54 points of
avoidable bench leakage**, not variance and not a bad roster, on a team that leads the league in
points scored. **Patience applies to who you hold. It says nothing about whether you set the
lineup.** Don't let one launder the other.
