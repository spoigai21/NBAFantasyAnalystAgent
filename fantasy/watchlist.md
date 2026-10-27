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
