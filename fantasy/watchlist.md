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
