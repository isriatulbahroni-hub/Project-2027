// Tes asap web Planner OS: buka semua modul, ketuk semua tombol aman, kirim semua form, pastikan 0 error.
// Pakai: cd tests && npm install && node smoke_web.js
const { JSDOM, VirtualConsole } = require("jsdom");
const fs = require("fs");
const path = require("path");
const P = path.join(__dirname, "..", "public") + path.sep;
const errs = [];
const vc = new VirtualConsole();
vc.on("jsdomError", e => errs.push("ERR " + ((e.detail && e.detail.stack) || e.message).split("\n").slice(0, 3).join(" | ")));
vc.on("error", e => errs.push("console.error " + e));
const html = fs.readFileSync(P + "index.html", "utf8").replace(/<script src="[^"]+"><\/script>/g, "");
const w = new JSDOM(html, { url: "https://x.test/", runScripts: "outside-only", pretendToBeVisual: true, virtualConsole: vc }).window;
w.matchMedia = () => ({ matches: false });
w.fetch = u => String(u).includes("holidays")
  ? Promise.resolve({ ok: true, json: () => Promise.resolve(JSON.parse(fs.readFileSync(P + "holidays.json", "utf8"))) })
  : Promise.resolve({ ok: true, headers: { get: () => "1000" } });
w.alert = m => errs.push("alert " + m);
w.confirm = () => false;
const src = ["core.js", "mods1.js", "mods2.js", "katalog.js"].map(f => fs.readFileSync(P + f, "utf8")).join("\n;\n");
try { w.eval(src); } catch (e) { errs.push("LOAD " + e.stack.split("\n").slice(0, 3).join(" | ")); }
const sleep = ms => new Promise(r => setTimeout(r, ms));
const SKIP = /^(gdel|pdel|reset|jdel|habdel|fdel|evdel|taskdel|export|dl|pidel)/;
(async () => {
  await sleep(300);
  const d = w.document;
  const ids = [...d.querySelectorAll(".nv")].map(b => b.dataset.go);
  if (ids.length !== 10) errs.push("modul: " + ids.length + ", seharusnya 10");
  let clicked = 0;
  for (const id of ids) {
    d.querySelector(`.nv[data-go="${id}"]`).click();
    await sleep(30);
    if (d.getElementById("view").innerHTML.length < 200) errs.push("modul kosong: " + id);
    for (const b of [...d.querySelectorAll("#view [data-act],#view [data-set]")]) {
      if (SKIP.test(b.dataset.act || "")) continue;
      try { b.click(); clicked++; } catch (e) { errs.push(id + " klik " + (b.dataset.act || b.dataset.set) + ": " + e.message); }
    }
  }
  const sub = async (hash, name, vals) => {
    w.location.hash = hash; await sleep(40);
    const f = d.querySelector(`[data-form="${name}"]`);
    if (!f) { errs.push("form tidak ada: " + name); return; }
    for (const k in vals) { const e = f.querySelector(`[name="${k}"]`); if (e) e.value = vals[k]; }
    f.dispatchEvent(new w.Event("submit", { bubbles: true, cancelable: true })); await sleep(40);
  };
  await sub("goals", "goal", { t: "Tes" }); await sub("goals", "ms", { t: "M1" });
  await sub("productivity", "proj", { t: "P" }); await sub("productivity", "pitem", { t: "T", due: "2027-01-05" });
  await sub("wellness", "habit", { n: "Olahraga" }); await sub("wellness", "sleep", { h: "7" });
  await sub("journal", "journal", { t: "a", b: "b" });
  await sub("finance", "fin", { d: "2026-11-18", ty: "out", c: "Tagihan", a: "5000", n: "x" });
  await sub("finance", "bud", { c: "Tagihan", l: "10000" });
  await sub("dashboard", "ev", { h: "9", t: "Rapat" });
  await sub("downloads", "name", { n: "Roney" });
  const S = JSON.parse(w.localStorage.getItem("planner-os-2027") || "{}");
  const want = { goals: 1, proj: 1, habits: 1, journal: 1, fin: 1, events: 1 };
  for (const k in want) if ((S[k] || []).length !== want[k]) errs.push("tidak tersimpan: " + k);
  if (S.name !== "Roney") errs.push("nama tidak tersimpan");
  d.getElementById("menu").click();
  if (!d.body.classList.contains("open")) errs.push("menu tidak terbuka");
  d.body.click();
  if (d.body.classList.contains("open")) errs.push("menu tidak menutup");
  console.log(`${ids.length} modul, ${clicked} ketukan, ${errs.length} masalah`);
  errs.forEach(e => console.log(" - " + e));
  process.exit(errs.length ? 1 : 0);
})();
