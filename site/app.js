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
const btnForm = el("btn-form");

let DATA = null;
// "current" | "projected" | "form14".
// ⚠ form14 is NOT a third value — it is the SECOND WINDOW on current value (CLAUDE.md
// rule 32). Season-to-date and last-14-days both answer "what has he done"; projected
// is the only forward number. The caption says so on screen so the distinction does not
// quietly collapse the way it does when people talk about "his last two weeks" as a rank.
let mode = "current";
const FORM_DAYS = 14;
let selected = null;    // name of the clicked player

const fmt1 = (n) => (n === null || n === undefined ? "—" : n.toFixed(1));

/* The form window the current mode reads. Everything downstream — table, left rail,
   trade flags — goes through this, so the signal can never describe one window while
   the number beside it describes another. */
function win(p) {
  return (mode === "form14" ? p.form14 : p.form7) || null;
}
function sigOf(p) {
  const w = win(p);
  return (w && w.signal) || p.signal || "—";
}
function sigWhyOf(p) {
  const w = win(p);
  return (w && w.sigWhy) || null;
}

function signed(n) {
  if (n === null || n === undefined || Number.isNaN(n)) return "—";
  const s = n >= 0 ? "+" : "−";
  return s + Math.abs(n).toFixed(1);
}

function injuryTag(status, rested) {
  // A rested player carries ESPN's OUT flag but is not hurt — showing the chip would
  // contradict the panel, which says the opposite.
  if (rested) return "";
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
  const isForm = mode === "form14";

  // The 14-day rank lives inside the window object, not at the top level, so every
  // column goes through an accessor rather than a key name.
  const rankOf  = (p) => isForm ? (p.form14 && p.form14.rank)
                                : p[isProj ? "projectedRank" : "currentRank"];
  const mainOf  = (p) => isForm ? (p.form14 && p.form14.avg)
                                : p[isProj ? "projected" : "current"];
  const otherOf = (p) => isForm ? p.projected : p[isProj ? "current" : "projected"];
  // ⚠ In the 14-day view "over expected" is the WINDOW minus projection, which is the
  // "vs his proj" column rankings.md prints — not the season gap. Showing the season
  // gap next to a 14-day average would put two different windows in one row.
  const overOf  = (p) => isForm ? (p.form14 && p.form14.vsProj) : (p.current - p.projected);
  const gamesOf = (p) => isForm ? (p.form14 && p.form14.games) : p.gp;
  const mpgOf   = (p) => isForm ? (p.form14 && p.form14.mpg) : p.mpg;

  // Plain words, not abbreviations: the main column is whichever list is showing.
  el("th-main").textContent = isForm ? `${FORM_DAYS} days` : isProj ? "Projected" : "Average";
  el("th-other").textContent = isForm ? "Projected" : isProj ? "Average" : "Projected";
  el("th-games").title = isForm ? `Games played inside the last-${FORM_DAYS}-day window.` : "";
  el("th-mins").title = isForm ? `Minutes per game inside the last-${FORM_DAYS}-day window.` : "";
  el("th-over").title = isForm
    ? `Fantasy points over expected — his last-${FORM_DAYS}-day average minus his projection.`
    : "Fantasy points over expected — season average minus projection. Positive means he is outperforming the projection.";

  capEl.innerHTML = isForm
    ? `Last ${FORM_DAYS} days<span>Fantasy points per game over the last ${FORM_DAYS} days.
       A <em>window</em> on current value, not a third list. Games and minutes are the window's.</span>`
    : isProj
    ? `Projected value<span>Rest of season, fantasy points per game. Ranked best to worst.</span>`
    : `Current value<span>Season to date, actual fantasy points per game. Ranked best to worst.</span>`;

  // A player with fewer than 2 games in the window has no readable average, so he is
  // absent from this list rather than shown as a blank row.
  let list = DATA.players.filter((p) => rankOf(p));
  if (mineOnly) list = list.filter((p) => p.mine);
  if (q) {
    list = list.filter(
      (p) => p.name.toLowerCase().includes(q) || p.team.toLowerCase().includes(q)
    );
  }
  list.sort((a, b) => rankOf(a) - rankOf(b));

  rowsEl.innerHTML = list
    .map((p) => {
      // FANTASY POINTS OVER EXPECTED: season average minus projection, i.e. how far
      // he is running ABOVE the number projected for him. Positive = outperforming.
      // ⚠ This is the opposite sign to the old "Change" column, which was projected
      // minus average. The name sets the direction: "over expected" has to mean actual
      // above expectation, or the label lies about the sign.
      const move = overOf(p);
      const moveCls = move > 0.05 ? "up" : move < -0.05 ? "down" : "";
      const sel = p.name === selected ? ' class="is-selected"' : "";
      return `<tr${sel} data-id="${p.id}" data-name="${p.name}">
        <td class="l rank">${rankOf(p)}</td>
        <td class="l"><span class="player">${p.name}</span>${injuryTag(p.injury, p.rested)}</td>
        <td class="l owner hide-sm">${p.team}</td>
        <td class="val">${fmt1(mainOf(p))}</td>
        <td class="sub">${fmt1(otherOf(p))}</td>
        <td class="sub hide-sm ${moveCls}">${signed(move)}</td>
        <td class="sub hide-sm">${gamesOf(p)}</td>
        <td class="sub hide-sm">${fmt1(mpgOf(p))}</td>
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
  btnForm.setAttribute("aria-pressed", String(next === "form14"));
  render();
  // ⚠ The trade flags are built from the ACTIVE window's signal, but renderTrade() only
  // ran when a chip changed — so switching window left LaMelo showing BUY LOW (14-day)
  // while the table beside it had flipped to the 7-day FADE (minutes). Same class of bug
  // as the panel/table rank mismatch above: one control, two things to refresh.
  // (Hoisted function declaration, so calling it from here is fine.)
  if (!el("trade").hidden) renderTrade();
}

btnProj.addEventListener("click", () => setMode("projected"));
btnCur.addEventListener("click", () => setMode("current"));
btnForm.addEventListener("click", () => setMode("form14"));
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

/* The form screen. Each label carries a MEASURED persistence rate from a
   1,104-player-week backtest — that number is the whole point of the label, so it is
   shown rather than just the verdict. Rates and definitions: CLAUDE.md rule 32. */
const SIGNALS = {
  "BUY LOW": ["buy", "Under projection with minutes and touches intact — this shape reverses."],
  "RIDE": ["good", "Beating projection on minutes that are holding. ~67% stayed real."],
  "SELL HIGH": ["warn", "Beating projection on FEWER minutes. Only ~52% survived."],
  "FADE (usage)": ["bad", "The touches went, not just the shots. 90% persisted — the strongest signal."],
  "FADE (minutes)": ["bad", "Minutes cut. ~65% persisted, and coach decisions do not revert."],
  "FADE (washed)": ["bad", "35+, under projection, touches unchanged. Age-driven decline does not revert."],
  "SLUMP (no edge)": ["warn", "Well under projection with role intact. Roughly a coin flip."],
  "HOLD": ["neutral", "Tracking his projection. Nothing to act on."],
  "INJURED (void)": ["void", "Out or on IR — no role to read, so no claim made."],
  "MISSING GAMES (void)": ["void", "Missing games despite reading active. The window shows an absence, not a role."],
  "THIN DATA (void)": ["void", "Too few graded games — usually a recent pickup. Withholding."],
};

function showPlayer(p) {
  const isProj = mode === "projected";
  const isForm = mode === "form14";
  const w = win(p);
  // Rank comes from whichever list is on screen, so the panel never contradicts the table.
  el("d-rank-label").textContent = isForm ? `Last ${FORM_DAYS} days rank`
                                 : isProj ? "Projected rank" : "Current rank";
  const rk = isForm ? (p.form14 && p.form14.rank) : isProj ? p.projectedRank : p.currentRank;
  el("d-rank").textContent = rk ? "#" + rk : "—";

  // Over/under is measured against the projection. In the 14-day view that is the
  // WINDOW minus projection, matching the table beside it.
  const over = isForm ? (p.form14 && p.form14.vsProj) : (p.current - p.projected);
  const word = over >= 0 ? "Overperforming by" : "Underperforming by";
  el("d-perf-word").textContent = word;
  el("d-perf-num").textContent = over === null || over === undefined
    ? "—" : Math.abs(over).toFixed(1);
  el("d-perf").className = "detail-perf " + (over >= 0 ? "is-over" : "is-under");

  el("d-name").textContent = p.name;
  el("d-team").textContent = p.team + (!p.rested && p.injury && p.injury !== "ACTIVE"
    ? " · " + (p.injury === "DAY_TO_DAY" ? "DTD" : p.injury === "INJURY_RESERVE" ? "IR" : p.injury)
    : "");
  const label = sigOf(p);
  const why = sigWhyOf(p);
  const sig = SIGNALS[label];
  const sigBox = el("d-signal");
  if (sig) {
    el("d-sig-badge").textContent = label.replace(" (void)", "");
    el("d-sig-badge").className = "sig-badge is-" + sig[0];
    // A hand-set signal shows ONLY the reason it was overridden. Printing the override
    // reason AND the generic blurb made the card taller than the viewport.
    const days = isForm ? FORM_DAYS : 7;
    el("d-sig-note").textContent =
      (why ? "Set by hand: " + why : sig[1])
      + (w && w.avg !== null ? ` Last ${days} days: ${fmt1(w.avg)} over ${w.games}.` : "");
    sigBox.hidden = false;
  } else {
    sigBox.hidden = true;
  }

  el("d-proj").textContent = fmt1(p.projected);
  // In the window view the three measured stats describe the WINDOW, and their labels
  // say so — a "14-day" card showing season games and season minutes reads as the
  // season card with one number swapped, which is exactly the mixing rule 32 forbids.
  el("d-avg").previousElementSibling.textContent = isForm ? `${FORM_DAYS}-day average` : "Average";
  el("d-gp").previousElementSibling.textContent = isForm ? "Games in window" : "Games";
  el("d-mpg").previousElementSibling.textContent = isForm ? "Minutes in window" : "Minutes";
  el("d-avg").textContent = isForm ? fmt1(w && w.avg) : fmt1(p.current);
  el("d-gp").textContent = isForm ? ((w && w.games) ?? "—")
                                  : p.gp + (p.smallSample ? " ⚠" : "");
  el("d-mpg").textContent = isForm ? fmt1(w && w.mpg) : fmt1(p.mpg);
  el("d-age").textContent = p.age ?? "—";
  el("d-missed").textContent = p.missed ?? "—";

  // A hand-set projection can put a player on the board below the games-played floor,
  // so his CURRENT rank rests on a tiny sample. Say so rather than let it pass.
  const sample = p.smallSample
    ? `Only ${p.gp} games played — his current average and rank are a small sample. `
    : "";

  const prone = el("d-prone");
  if (sample || p.rested || p.prone) {
    prone.textContent = (sample ? "⚠ " + sample : "")
      + (p.rested ? (sample ? "" : "⚠ ") + p.rested + " " : "")
      + (p.prone ? (sample || p.rested ? "Injury prone — " : "⚠ Injury prone — ") + p.prone : "");
    prone.hidden = false;
  } else {
    prone.hidden = true;
  }


  if (p.id) {
    dImg.style.visibility = "";
    dImg.src = `https://a.espncdn.com/i/headshots/nba/players/full/${p.id}.png`;
  } else {
    dImg.style.visibility = "hidden";
  }

  dEmpty.hidden = true;
  dCard.hidden = false;
}

function clearPlayer() {
  selected = null;
  dCard.hidden = true;
  dEmpty.hidden = false;
  render();
}

rowsEl.addEventListener("click", (e) => {
  const tr = e.target.closest("tr");
  if (!tr || !tr.dataset.name) return;
  // With the trade panel open, a row click builds the trade instead of pinning a card.
  if (!el("trade").hidden) {
    const p = DATA.players.find((x) => x.name === tr.dataset.name);
    if (p) addToTrade(p);
    return;
  }
  // Clicking the already-selected row toggles it back off.
  if (tr.dataset.name === selected) {
    clearPlayer();
    return;
  }
  const p = DATA.players.find((x) => x.name === tr.dataset.name);
  if (!p) return;
  selected = p.name;
  render();
  showPlayer(p);
});

// Escape also clears, since the panel is pinned and a stale player is easy to forget.
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && selected) clearPlayer();
});

/* ── Trade compare ────────────────────────────────────────────────────────────────────
   Compares two sets of players on PROJECTED value — a trade is a forward question, so
   the rest-of-season number is the one that matters, not what they have already banked.

   ⚠ THE UNEVEN-SIDES CORRECTION. Trading 3 players for 1 does not mean "three totals vs
   one total": the side receiving fewer bodies also frees two roster spots, and those
   spots get filled off the waiver wire rather than left empty. So each missing body on
   the short side is worth a WAIVER_FILL, not zero. Without it, every 3-for-1 looks like
   a landslide for whoever receives three — which is the single most common way a trade
   gets misjudged.  */
const WAIVER_FILL = 29.0;          // user's figure for a wire replacement, per game

const tradeEl = el("trade");
const chipsEl = { a: el("chips-a"), b: el("chips-b") };
const sides = { a: [], b: [] };
let activeSide = "a";

function fmtSigned(n) {
  return (n >= 0 ? "+" : "−") + Math.abs(n).toFixed(1);
}

/* The flags worth stopping a trade over: a role that is shrinking, a body that does not
   stay on the floor, and a value that is about to move. */
function playerFlags(p) {
  const out = [];
  // Lead with the SIGNAL LABEL, not just the prose — "BUY LOW" is the thing you act on,
  // and the sentence after it is the reason.
  const S = {
    "FADE (usage)": ["bad", "FADE", "losing touches — role shrinking"],
    "FADE (minutes)": ["bad", "FADE", "losing minutes — role shrinking"],
    "FADE (washed)": ["bad", "FADE", "age-driven decline, role intact"],
    "SELL HIGH": ["warn", "SELL HIGH", "value may not hold"],
    "BUY LOW": ["buy", "BUY LOW", "shortfall should revert"],
    "RIDE": ["good", "RIDE", "beating projection on real minutes"],
    "SLUMP (no edge)": ["warn", "SLUMP", "under projection, role intact — no edge"],
    "INJURED (void)": ["warn", "INJURED", "no role to read"],
    "MISSING GAMES (void)": ["warn", "MISSING GAMES", "not playing despite reading active"],
    "THIN DATA (void)": ["warn", "THIN DATA", "too few games to read"],
  };
  const sig = S[sigOf(p)];
  if (sig) out.push([sig[0], sig[1], sigWhyOf(p) || sig[2]]);

  if (p.prone) {
    // The generic hand-flag says nothing beyond "injury prone", so do not repeat it.
    const generic = p.prone.startsWith("User-flagged");
    out.push(["warn", "INJURY PRONE", generic ? "" : p.prone]);
  }
  if (p.rested) out.push(["warn", "NOT INJURED", p.rested]);
  if (p.smallSample) out.push(["warn", "SMALL SAMPLE", `only ${p.gp} games played`]);
  return out;
}

function sideTotal(side) {
  const own = sides[side].reduce((t, p) => t + p.projected, 0);
  const other = side === "a" ? "b" : "a";
  const missing = Math.max(0, sides[other].length - sides[side].length);
  return { own, missing, fill: missing * WAIVER_FILL, total: own + missing * WAIVER_FILL };
}

function renderTrade() {
  for (const side of ["a", "b"]) {
    chipsEl[side].innerHTML = sides[side]
      .map((p) => `<li><button type="button" data-side="${side}" data-name="${p.name}"
          title="Remove ${p.name}">
        <span class="chip-name">${p.name}</span>
        <span class="chip-val">${fmt1(p.projected)}</span>
        <span class="chip-x" aria-hidden="true">×</span>
        <span class="sr">Remove</span></button></li>`)
      .join("");
    const t = sideTotal(side);
    el("total-" + side).innerHTML = sides[side].length === 0 && t.missing === 0
      ? "—"
      : `<strong>${t.total.toFixed(1)}</strong>` +
        (t.missing
          ? `<span class="fill-note"> incl. ${t.missing} waiver fill
             &times; ${WAIVER_FILL.toFixed(0)} = ${t.fill.toFixed(0)}</span>`
          : "");
  }

  const A = sideTotal("a"), B = sideTotal("b");
  const v = el("trade-verdict");
  if (!sides.a.length && !sides.b.length) {
    v.hidden = true;
    el("trade-flags").innerHTML = "";
    return;
  }
  const diff = B.total - A.total;
  const word = Math.abs(diff) < 1.5 ? "Close to even" : diff > 0 ? "You gain" : "You lose";
  v.hidden = false;
  v.className = "trade-verdict " + (Math.abs(diff) < 1.5 ? "is-even" : diff > 0 ? "is-good" : "is-bad");
  v.innerHTML = `<span class="verdict-word">${word}</span>
    <span class="verdict-num">${fmtSigned(diff)}</span>
    <span class="verdict-unit">projected fantasy points per game</span>`;

  const flags = [];
  for (const side of ["a", "b"]) {
    for (const p of sides[side]) {
      for (const [kind, label, text] of playerFlags(p)) {
        flags.push(`<li class="flag is-${kind}">
          <span class="flag-side">${side === "a" ? "give" : "get"}</span>
          <strong>${p.name}</strong>
          <span class="flag-tag">${label}</span>
          ${text ? `<span class="flag-why">${text}</span>` : ""}</li>`);
      }
    }
  }
  el("trade-flags").innerHTML = flags.length
    ? flags.join("")
    : `<li class="flag is-none">No flags — nobody in this trade is injury prone, fading,
       or carrying a buy-low or sell-high signal.</li>`;
}

function addToTrade(p) {
  const other = activeSide === "a" ? "b" : "a";
  if (sides[other].some((x) => x.name === p.name)) return;   // never on both sides
  if (sides[activeSide].some((x) => x.name === p.name)) return;
  sides[activeSide].push(p);
  renderTrade();
}

el("trade-toggle").addEventListener("click", (e) => {
  const open = tradeEl.hidden;
  tradeEl.hidden = !open;
  e.currentTarget.setAttribute("aria-pressed", String(open));
  document.body.classList.toggle("trade-open", open);
});

function setSide(side) {
  activeSide = side;
  document.querySelectorAll(".side-tab").forEach((b) =>
    b.setAttribute("aria-pressed", String(b.dataset.side === activeSide)));
  document.querySelectorAll(".trade-side").forEach((d) =>
    d.classList.toggle("is-active", d.dataset.side === activeSide));
}

// The whole side box is the target, not just the little heading — that heading read as
// a label rather than a control, so switching to "You get" looked broken.
document.querySelectorAll(".trade-side").forEach((box) => {
  box.addEventListener("click", (e) => {
    if (e.target.closest(".chips button")) return;   // chip clicks remove, not switch
    setSide(box.dataset.side);
  });
});
setSide("a");

[chipsEl.a, chipsEl.b].forEach((ul) => {
  ul.addEventListener("click", (e) => {
    const btn = e.target.closest("button");
    if (!btn) return;
    sides[btn.dataset.side] = sides[btn.dataset.side].filter((p) => p.name !== btn.dataset.name);
    renderTrade();
  });
});

el("trade-clear").addEventListener("click", () => {
  sides.a = []; sides.b = [];
  renderTrade();
});
