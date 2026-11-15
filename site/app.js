// Rankings site — frontend only. Reads the static rankings.json written by
// fantasy/build_site_data.py. No API, no build step, no framework.

const el = (id) => document.getElementById(id);
const rowsEl = el("rows");
const capEl = el("cap");
const countEl = el("count");
const emptyEl = el("empty");
const qEl = el("q");
const mineEl = el("mine");
const btnProj = el("btn-proj");
const btnCur = el("btn-cur");

let DATA = null;
let mode = "current";   // or "projected" — Current leads, per the toggle order
let selected = null;    // name of the clicked player

const fmt1 = (n) => (n === null || n === undefined ? "—" : n.toFixed(1));

function signed(n) {
  if (n === null || n === undefined || Number.isNaN(n)) return "—";
  const s = n >= 0 ? "+" : "−";
  return s + Math.abs(n).toFixed(1);
}

function injuryTag(status) {
  if (!status || status === "ACTIVE") return "";
  const label =
    status === "DAY_TO_DAY" ? "DTD" :
    status === "INJURY_RESERVE" ? "IR" :
    status === "OUT" ? "OUT" : status;
  return ` <span class="tag">${label}</span>`;
}

function render() {
  const q = qEl.value.trim().toLowerCase();
  const mineOnly = mineEl.checked;
  const isProj = mode === "projected";

  const rankKey = isProj ? "projectedRank" : "currentRank";
  const mainKey = isProj ? "projected" : "current";
  const otherKey = isProj ? "current" : "projected";

  // Plain words, not abbreviations: the main column is whichever list is showing.
  el("th-main").textContent = isProj ? "Projected" : "Average";
  el("th-other").textContent = isProj ? "Average" : "Projected";

  capEl.innerHTML = isProj
    ? `Projected value<span>Rest of season, fantasy points per game. Ranked best to worst.</span>`
    : `Current value<span>Season to date, actual fantasy points per game. Ranked best to worst.</span>`;

  let list = DATA.players.filter((p) => p[rankKey]);
  if (mineOnly) list = list.filter((p) => p.mine);
  if (q) {
    list = list.filter(
      (p) => p.name.toLowerCase().includes(q) || p.team.toLowerCase().includes(q)
    );
  }
  list.sort((a, b) => a[rankKey] - b[rankKey]);

  rowsEl.innerHTML = list
    .map((p) => {
      // FANTASY POINTS OVER EXPECTED: season average minus projection, i.e. how far
      // he is running ABOVE the number projected for him. Positive = outperforming.
      // ⚠ This is the opposite sign to the old "Change" column, which was projected
      // minus average. The name sets the direction: "over expected" has to mean actual
      // above expectation, or the label lies about the sign.
      const move = p.current - p.projected;
      const moveCls = move > 0.05 ? "up" : move < -0.05 ? "down" : "";
      const sel = p.name === selected ? ' class="is-selected"' : "";
      return `<tr${sel} data-id="${p.id}" data-name="${p.name}">
        <td class="l rank">${p[rankKey]}</td>
        <td class="l"><span class="player">${p.name}</span>${injuryTag(p.injury)}</td>
        <td class="l owner hide-sm">${p.team}</td>
        <td class="val">${fmt1(p[mainKey])}</td>
        <td class="sub">${fmt1(p[otherKey])}</td>
        <td class="sub hide-sm ${moveCls}">${signed(move)}</td>
        <td class="sub hide-sm">${p.gp}</td>
        <td class="sub hide-sm">${fmt1(p.mpg)}</td>
      </tr>`;
    })
    .join("");

  emptyEl.hidden = list.length > 0;
  const mineCount = list.filter((p) => p.mine).length;
  countEl.textContent =
    `${list.length} player${list.length === 1 ? "" : "s"}` +
    (mineOnly ? "" : ` · ${mineCount} mine`);
}

function setMode(next) {
  mode = next;
  // The panel shows the rank of whichever list is active, so refresh it on a toggle.
  if (selected && DATA) {
    const p = DATA.players.find((x) => x.name === selected);
    if (p) setTimeout(() => showPlayer(p), 0);
  }
  btnProj.setAttribute("aria-pressed", String(next === "projected"));
  btnCur.setAttribute("aria-pressed", String(next === "current"));
  render();
}

btnProj.addEventListener("click", () => setMode("projected"));
btnCur.addEventListener("click", () => setMode("current"));
qEl.addEventListener("input", render);
mineEl.addEventListener("change", render);

fetch("rankings.json", { cache: "no-cache" })
  .then((r) => {
    if (!r.ok) throw new Error(`rankings.json: HTTP ${r.status}`);
    return r.json();
  })
  .then((d) => {
    DATA = d;
    el("meta").textContent =
      `${d.players.length} rostered players with ${d.minGp}+ games played · ` +
      `data as of ${d.asof}. ` +
      `Built from the ESPN API; rebuilt after each slate goes final.`;
    render();
  })
  .catch((err) => {
    emptyEl.hidden = false;
    emptyEl.textContent = `Could not load rankings data (${err.message}).`;
    console.error(err);
  });

/* ── Clicked player → left rail ──────────────────────────────────────────────────────
   ESPN's CDN serves a headshot per athlete id, and the fantasy API's player id IS that
   athlete id, so this costs one <img> and no server — it works as a static file on
   Vercel exactly as it does locally. Verified 15 Nov 2026: all 116 rostered players
   return 200. The onerror still hides the IMAGE (not the card), because a player traded
   in later could arrive without one and a broken-image glyph is worse than a gap. */
const dEmpty = el("detail-empty");
const dCard = el("detail-card");
const dImg = el("d-img");

dImg.addEventListener("error", () => { dImg.style.visibility = "hidden"; });

/* The 14-day form screen. Each label carries a MEASURED persistence rate from a
   1,104-player-week backtest — that number is the whole point of the label, so it is
   shown rather than just the verdict. Rates and definitions: CLAUDE.md rule 32. */
const SIGNALS = {
  "BUY LOW": ["buy", "Moderately under projection with minutes AND touches intact. This shape reverses — it is the one real buy-low."],
  "RIDE": ["good", "Beating the projection on minutes that are holding. About 67% of these stayed real the following week."],
  "SELL HIGH": ["warn", "Beating the projection on FEWER minutes than projected. Only about half of these survived — the weakest signal here."],
  "FADE (usage)": ["bad", "Under projection and the touches have gone, not just the shots. 90% of these persisted — the strongest signal on the board."],
  "FADE (minutes)": ["bad", "Under projection with minutes cut. About 65% persisted. Coach-controlled, so it does not revert on its own."],
  "SLUMP (no edge)": ["warn", "Well under projection with role intact — no edge either way. Roughly a coin flip."],
  "HOLD": ["neutral", "Tracking his projection. Nothing to act on."],
  "INJURED (void)": ["void", "Out or on IR. There is no role to read, so no claim is made."],
  "MISSING GAMES (void)": ["void", "Has missed his team's recent games despite being listed active. The window describes an absence, not a role."],
  "THIN DATA (void)": ["void", "Too few graded games to read — usually a recent pickup. Withholding rather than guessing."],
};

function showPlayer(p) {
  const isProj = mode === "projected";
  // Rank comes from whichever list is on screen, so the panel never contradicts the table.
  el("d-rank-label").textContent = isProj ? "Projected rank" : "Current rank";
  el("d-rank").textContent = "#" + (isProj ? p.projectedRank : p.currentRank);

  // Over/under is measured against the projection: average minus projected.
  const over = p.current - p.projected;
  const word = over >= 0 ? "Overperforming by" : "Underperforming by";
  el("d-perf-word").textContent = word;
  el("d-perf-num").textContent = Math.abs(over).toFixed(1);
  el("d-perf").className = "detail-perf " + (over >= 0 ? "is-over" : "is-under");

  el("d-name").textContent = p.name;
  el("d-team").textContent = p.team + (p.injury && p.injury !== "ACTIVE"
    ? " · " + (p.injury === "DAY_TO_DAY" ? "DTD" : p.injury === "INJURY_RESERVE" ? "IR" : p.injury)
    : "");
  const sig = SIGNALS[p.signal];
  const sigBox = el("d-signal");
  if (sig) {
    el("d-sig-badge").textContent = p.signal.replace(" (void)", "");
    el("d-sig-badge").className = "sig-badge is-" + sig[0];
    el("d-sig-note").textContent = sig[1]
      + (p.form !== null ? ` Last 14 days: ${fmt1(p.form)} per game over ${p.formGames}.` : "");
    sigBox.hidden = false;
  } else {
    sigBox.hidden = true;
  }

  el("d-proj").textContent = fmt1(p.projected);
  el("d-avg").textContent = fmt1(p.current);
  el("d-gp").textContent = p.gp;
  el("d-mpg").textContent = fmt1(p.mpg);

  if (p.id) {
    dImg.style.visibility = "";
    dImg.src = `https://a.espncdn.com/i/headshots/nba/players/full/${p.id}.png`;
  } else {
    dImg.style.visibility = "hidden";
  }

  dEmpty.hidden = true;
  dCard.hidden = false;
}

rowsEl.addEventListener("click", (e) => {
  const tr = e.target.closest("tr");
  if (!tr || !tr.dataset.name) return;
  const p = DATA.players.find((x) => x.name === tr.dataset.name);
  if (!p) return;
  selected = p.name;
  render();
  showPlayer(p);
});
