const CATS=["Kebutuhan pokok","Operasional usaha","Transportasi","Tagihan","Tabungan","Lainnya"];
const PR=["Apa satu hal yang berjalan baik hari ini, dan apa yang ingin kamu ulangi besok?","Apa yang paling menguras energimu minggu ini, dan bisakah dikurangi?","Apa satu keputusan kecil hari ini yang membuatmu lebih dekat ke targetmu?","Siapa yang ingin kamu hubungi atau ucapkan terima kasih?"];
const T=(a,id)=>a.find(x=>x.id===id);

/* Goals */
F.goal=f=>{const t=f.get("t").trim();if(t)D.goals.push({id:uid(),t,ms:[]})};
F.ms=f=>{const g=T(D.goals,f.get("g")),t=f.get("t").trim();if(g&&t)g.ms.push({t,done:0})};
A.gms=a=>{const[id,i]=a.split(":"),g=T(D.goals,id);if(g)g.ms[i].done=g.ms[i].done?0:1};
A.gdel=id=>{D.goals=D.goals.filter(x=>x.id!==id)};
R.goals=()=>{
  const gs=D.goals.map(g=>{const dn=g.ms.filter(m=>m.done).length,tot=g.ms.length;
    return `<div class="gl">${prog([[esc(g.t),tot?Math.round(dn/tot*100):0,tot?`${dn} dari ${tot} tonggak`:"Belum ada tonggak"]])}${g.ms.map((m,i)=>`<div class="tk ${m.done?"d":""}"><label><input type="checkbox" data-act="gms:${g.id}:${i}" ${m.done?"checked":""}><span>${esc(m.t)}</span></label></div>`).join("")}${fm("ms",`<input type="hidden" name="g" value="${g.id}">${inp("t","Tambah tonggak","required")}`,"Tambah","in")}<button class="lk" data-act="gdel:${g.id}">Hapus target</button></div>`}).join("");
  return pg("Goals","Target, tonggak, dan progresnya.",pn("Target",gs||empty("Belum ada target","Buat target pertamamu di sebelah, lalu pecah jadi tonggak kecil."),"c7")+pn("Target baru",fm("goal",inp("t","Contoh: Rilis planner 2027","required"),"Buat"),"c5"))};

/* Wellness */
F.sleep=f=>{D.sleep[TODAY]=+f.get("h")};
F.habit=f=>{const n=f.get("n").trim();if(n)D.habits.push({id:uid(),n,log:{}})};
A.mood=v=>{D.mood[TODAY]=+v};
A.hab=a=>{const[id,s]=a.split(":"),h=T(D.habits,id);if(h){if(h.log[s])delete h.log[s];else h.log[s]=1}};
A.habdel=id=>{D.habits=D.habits.filter(x=>x.id!==id)};
R.wellness=()=>{
  const L=lastN(7),ML=["Buruk","Kurang","Biasa","Baik","Sangat baik"],L14=lastN(14);
  const mood=`<div class="mood">${ML.map((l,i)=>`<button class="btn" data-act="mood:${i+1}" aria-pressed="${D.mood[TODAY]===i+1}">${l}</button>`).join("")}</div><div class="dots">${L14.map(s=>D.mood[s]?`<i style="opacity:${.2+D.mood[s]*.16}" title="${short(s)}: ${D.mood[s]} dari 5"></i>`:`<i class="o" title="${short(s)}: belum diisi"></i>`).join("")}</div><p class="mute" style="margin:8px 0 0">14 hari terakhir. Makin pekat, makin baik.</p>`;
  const sl=fm("sleep",`<input name="h" type="number" step="0.5" min="0" max="24" placeholder="Jam tidur semalam" aria-label="Jam tidur semalam" required>`,"Simpan")+bars([L.map(s=>D.sleep[s]||0)],L.map(ini));
  const hb=`<div class="hb"><span></span>${L.map(s=>`<i>${ini(s)}</i>`).join("")}<span></span></div>`+D.habits.map(h=>`<div class="hb"><span>${esc(h.n)} <small>${L.filter(s=>h.log[s]).length}/7</small></span>${L.map(s=>`<button class="${h.log[s]?"on":""}" data-act="hab:${h.id}:${s}" aria-pressed="${!!h.log[s]}" aria-label="${esc(h.n)} ${short(s)}"></button>`).join("")}<button class="x" data-act="habdel:${h.id}" aria-label="Hapus kebiasaan">×</button></div>`).join("")+fm("habit",inp("n","Kebiasaan baru, misal Olahraga","required"),"Tambah","in");
  return pg("Wellness","Mood, tidur, dan kebiasaan harian.",pn("Mood hari ini",mood,"c5")+pn("Tidur, jam per malam",sl,"c7")+pn("Kebiasaan minggu ini",hb,"c12"))};

/* Journal */
F.journal=f=>{const t=f.get("t").trim(),b=f.get("b").trim();if(t||b)D.journal.push({id:uid(),d:TODAY,t:t||"Tanpa judul",b})};
A.jdel=id=>{D.journal=D.journal.filter(x=>x.id!==id)};
R.journal=()=>{
  const pr=PR[Math.round(pd(TODAY)/864e5)%PR.length];
  const en=[...D.journal].reverse().map(j=>`<article class="en"><header><b>${esc(j.t)}</b><span>${fmtD(j.d)}</span></header><p>${esc(j.b)}</p><button class="lk" data-act="jdel:${j.id}">Hapus</button></article>`).join("");
  return pg("Journal","Diary, catatan, dan refleksi.",pn("Tulis entri",`<p class="mute" style="margin:0 0 8px">${pr}</p>`+fm("journal",`${inp("t","Judul")}<textarea name="b" placeholder="Tulis di sini" aria-label="Isi entri"></textarea>`,"Simpan entri"),"c5")+pn("Entri",en||empty("Belum ada entri","Tulis entri pertamamu. Semua tersimpan di perangkat ini."),"c7",D.journal.length+" entri"))};

/* Productivity */
F.proj=f=>{const t=f.get("t").trim();if(t)D.proj.push({id:uid(),t,items:[]})};
F.pitem=f=>{const p=T(D.proj,f.get("p")),t=f.get("t").trim();if(p&&t)p.items.push({id:uid(),t,due:f.get("due")||"",done:0})};
A.pit=a=>{const[p,i]=a.split(":"),it=T((T(D.proj,p)||{items:[]}).items,i);if(it)it.done=it.done?0:1};
A.pidel=a=>{const[p,i]=a.split(":"),pj=T(D.proj,p);if(pj)pj.items=pj.items.filter(x=>x.id!==i)};
A.pdel=id=>{D.proj=D.proj.filter(x=>x.id!==id)};
R.productivity=()=>{
  const pj=D.proj.map(p=>{const dn=p.items.filter(i=>i.done).length,tot=p.items.length;
    return `<div class="pj">${prog([[esc(p.t),tot?Math.round(dn/tot*100):0,tot?`${dn} dari ${tot} tugas`:"Belum ada tugas"]])}${p.items.map(i=>`<div class="tk ${i.done?"d":""}"><label><input type="checkbox" data-act="pit:${p.id}:${i.id}" ${i.done?"checked":""}><span>${esc(i.t)}</span></label>${i.due?`<small class="mute">${short(i.due)}</small>`:""}<button class="x" data-act="pidel:${p.id}:${i.id}" aria-label="Hapus tugas">×</button></div>`).join("")}${fm("pitem",`<input type="hidden" name="p" value="${p.id}">${inp("t","Tugas baru","required")}<input type="date" name="due" aria-label="Tenggat">`,"Tambah","in")}<button class="lk" data-act="pdel:${p.id}">Hapus proyek</button></div>`}).join("");
  const dl=D.proj.flatMap(p=>p.items.filter(i=>i.due&&!i.done).map(i=>({d:i.due,t:i.t,p:p.t}))).sort((a,b)=>a.d<b.d?-1:1).slice(0,8);
  return pg("Productivity","Proyek, tugas, dan tenggat.",pn("Proyek",pj||empty("Belum ada proyek","Buat proyek pertama, lalu tambahkan tugas dan tenggatnya."),"c7")+pn("Proyek baru",fm("proj",inp("t","Nama proyek","required"),"Buat"),"c5")+pn("Deadline",dl.length?list(dl.map(x=>[short(x.d),esc(x.t),x.d<TODAY?"Terlambat":esc(x.p)])):`<p class="mute">Belum ada tugas bertenggat.</p>`,"c5"))};

/* Finance */
F.fin=f=>{const a=+f.get("a");if(a>0&&f.get("d"))D.fin.push({id:uid(),d:f.get("d"),ty:f.get("ty"),c:f.get("c"),a,n:f.get("n").trim()})};
F.bud=f=>{const l=+f.get("l");if(l>0)D.bud[f.get("c")]=l;else delete D.bud[f.get("c")]};
A.fdel=id=>{D.fin=D.fin.filter(x=>x.id!==id)};
R.finance=()=>{
  const mo=TODAY.slice(0,7),sum=(m,ty)=>D.fin.filter(x=>x.d.startsWith(m)&&x.ty===ty).reduce((a,x)=>a+x.a,0),inc=sum(mo,"in"),out=sum(mo,"out");
  const ms=Array.from({length:6},(_,i)=>{const d=new Date(NOW.getFullYear(),NOW.getMonth()-5+i,1);return d.getFullYear()+"-"+pad(d.getMonth()+1)});
  const chart=bars([ms.map(m=>sum(m,"in")/1e6),ms.map(m=>sum(m,"out")/1e6)],ms.map(m=>BLN[+m.slice(5)-1].slice(0,3)),["var(--sage)","var(--brass)"])+`<div class="lg"><span><b style="background:var(--sage)"></b>Pemasukan</span><span><b style="background:var(--brass)"></b>Pengeluaran</span><span>Juta rupiah</span></div>`;
  const spent=c=>D.fin.filter(x=>x.d.startsWith(mo)&&x.ty==="out"&&x.c===c).reduce((a,x)=>a+x.a,0);
  const bud=CATS.filter(c=>D.bud[c]).map(c=>{const s=spent(c),l=D.bud[c],pc=Math.round(s/l*100);return `<div class="${pc>100?"over":""}">${prog([[c,Math.min(pc,100),`${rp(s)} dari ${rp(l)}`]])}</div>`}).join("")||`<p class="mute">Belum ada anggaran. Atur batas per kategori di bawah.</p>`;
  const opt=CATS.map(c=>`<option>${c}</option>`).join("");
  const tx=[...D.fin].sort((a,b)=>a.d<b.d?1:-1).slice(0,15).map(x=>`<div class="li"><b>${short(x.d)}</b><span>${esc(x.n||x.c)}</span><span class="${x.ty==="in"?"inc":"out"}">${x.ty==="in"?"+":"−"}${rp(x.a)} <button class="x" data-act="fdel:${x.id}" aria-label="Hapus transaksi">×</button></span></div>`).join("");
  return pg("Finance","Pemasukan, pengeluaran, dan anggaran.",
   pn("Bulan ini",list([["Pemasukan","",rp(inc)],["Pengeluaran","",rp(out)],["Selisih","",rp(inc-out)]])+`<div style="margin-top:14px">${chart}</div>`,"c7",BLN[NOW.getMonth()])
   +pn("Anggaran",bud+fm("bud",`<select name="c" aria-label="Kategori">${opt}</select><input name="l" type="number" min="0" placeholder="Batas (Rp), 0 untuk hapus" aria-label="Batas anggaran" required>`,"Atur","in"),"c5")
   +pn("Catat transaksi",fm("fin",`<input type="date" name="d" value="${TODAY}" required aria-label="Tanggal"><select name="ty" aria-label="Jenis"><option value="out">Pengeluaran</option><option value="in">Pemasukan</option></select><select name="c" aria-label="Kategori">${opt}</select><input name="a" type="number" min="1" placeholder="Jumlah (Rp)" aria-label="Jumlah" required>${inp("n","Catatan (opsional)")}`,"Simpan")+(tx||`<p class="mute">Belum ada transaksi.</p>`),"c12"))};

/* Katalog, Downloads, Admin */
A.dl=f=>{D.dl.unshift({f,at:TODAY+" "+pad(new Date().getHours())+"."+pad(new Date().getMinutes())});D.dl=D.dl.slice(0,30);return false};
A.export=()=>{const b=new Blob([JSON.stringify(D,null,1)],{type:"application/json"}),a=document.createElement("a");a.href=URL.createObjectURL(b);a.download="planner-os-"+TODAY+".json";a.click();return false};
A.reset=()=>{if(confirm("Hapus semua data Planner OS di perangkat ini? Tindakan ini tidak bisa dibatalkan.")){D=def();save();return true}return false};
R.katalog=()=>{const f=`Planner-2027-${S.start}-${S.theme}.pdf`,u="planners/"+f;
  return pg("Katalog","Pilih tema dan awal minggu, lihat pratinjau.",pn("Pilih varian",`<div class="fm">${seg("start",[["monday","Senin"],["sunday","Minggu"]])}${seg("theme",[["sage","Sage"],["rose","Rose"],["slate","Slate"]])}<a class="btn" href="${u}" target="_blank" rel="noopener">Buka di tab baru</a><a class="btn pri" href="${u}" download data-act="dl:${f}">Download PDF</a></div><iframe class="pdf" title="Pratinjau planner" src="${u}"></iframe><p class="mute">Di HP, jika pratinjau tidak muncul, pakai tombol Buka di tab baru.</p>`))};
R.downloads=()=>{const fs=["monday","sunday"].flatMap(s=>["sage","rose","slate"].map(t=>`Planner-2027-${s}-${t}.pdf`));
  return pg("Downloads","PDF, ekspor, dan riwayat.",
   pn("File planner",fs.map(f=>`<div class="fl">${ic(I.dl)}${f}<a class="btn" href="planners/${f}" download data-act="dl:${f}">Unduh</a></div>`).join(""),"c7")
   +pn("Riwayat unduhan",D.dl.length?list(D.dl.slice(0,8).map(x=>[x.at.slice(5,10),esc(x.f),x.at.slice(11)])):empty("Belum ada riwayat","Unduhan dari perangkat ini tercatat di sini."),"c5")
   +pn("Data saya",`${fm("name",`<input name="n" value="${esc(D.name)}" placeholder="Nama panggilan" aria-label="Nama panggilan" maxlength="40">`,"Simpan nama","in")}<p style="margin:10px 0">Semua data tersimpan di perangkat ini. Ekspor untuk cadangan atau pindah perangkat.</p><div class="fm"><button class="btn pri" data-act="export:">Ekspor data (JSON)</button><label class="btn">Pulihkan dari file<input id="imp" type="file" accept=".json,application/json" hidden></label><button class="btn" data-act="reset:">Hapus semua data</button></div>`,"c12"))};
R.admin=()=>{const X={Pengguna:["Belum ada pengguna","Daftar pengguna dan status akun muncul di sini setelah login aktif."],Pesanan:["Belum ada pesanan","Pesanan dari marketplace dan checkout muncul di sini."],Penjualan:["Belum ada penjualan","Rekap penjualan per varian, tema, dan periode."],Analitik:["Belum ada data analitik","Kunjungan, unduhan, dan konversi muncul di sini setelah akun dan pelacakan aktif."],Laporan:["Belum ada laporan","Laporan bulanan yang bisa diekspor ke PDF atau CSV."]};
  return pg("Admin","Pengguna, pesanan, penjualan, analitik, dan laporan.",`<div class="c12">${seg("adm",Object.keys(X).map(x=>[x,x]))}</div>`+pn(X[S.adm][0],empty(...X[S.adm]),"c12"))};

/* Boot */
(function(){
  let side=`<div class="brand">Planner OS<small>2027</small></div>`,g="";
  MODS.forEach(m=>{if(m.g!==g){g=m.g;side+=`<div class="grp">${g}</div>`}side+=`<button class="nv" data-go="${m.id}">${ic(I[m.i])}${m.t}</button>`});
  const $=id=>document.getElementById(id),pop=$("pop");
  $("side").innerHTML=side;
  $("mods").innerHTML=MODS.map(m=>`<option value="${m.t}">${m.d}</option>`).join("");
  $("sico").innerHTML=ic(I.srch);$("bell").insertAdjacentHTML("afterbegin",ic(I.bell));$("gear").innerHTML=ic(I.gear);$("menu").innerHTML=ic(I.menu);
  const popHTML=()=>{const ev=D.events.filter(e=>e.d>=TODAY).sort((a,b)=>a.d<b.d?-1:a.d>b.d?1:a.h-b.h).slice(0,3).map(e=>[short(e.d),esc(e.t),pad(e.h)+".00"]);
    return `<h3>Jadwal mendatang</h3>${ev.length?list(ev):`<p class="mute">Belum ada jadwal.</p>`}<h3 style="margin-top:10px">Tanggal merah</h3>${list(nextH(2).map(hl))}`};
  $("q").addEventListener("change",e=>{const v=e.target.value.toLowerCase(),m=MODS.find(x=>x.t.toLowerCase()===v)||MODS.find(x=>(x.t+x.d).toLowerCase().includes(v));if(m){location.hash=m.id;e.target.value=""}});
  document.addEventListener("click",e=>{
    const t=e.target;
    if(t===document.body){document.body.classList.remove("open");return}
    if(!t.closest("#pop,#bell"))pop.hidden=true;
    if(t.closest("#bell")){pop.innerHTML=popHTML();pop.hidden=!pop.hidden;return}
    if(t.closest("#menu")){document.body.classList.add("open");return}
    if(t.closest("#gear")){const r=document.documentElement,d=r.dataset.theme?r.dataset.theme==="dark":matchMedia("(prefers-color-scheme:dark)").matches;r.dataset.theme=d?"light":"dark";return}
    const o=t.closest("[data-go]");if(o){if(location.hash==="#"+o.dataset.go)go();else location.hash=o.dataset.go;return}
    const s=t.closest("[data-set]");if(s){const[k,v]=s.dataset.set.split(":");S[k]=v;go();return}
    const a=t.closest("[data-act]");if(a){const x=a.dataset.act,i=x.indexOf(":"),r=A[x.slice(0,i)](x.slice(i+1));save();if(r===true)location.reload();else if(r!==false)go()}});
  document.addEventListener("submit",e=>{const f=e.target.closest("[data-form]");if(!f)return;e.preventDefault();const n=f.dataset.form;F[n](new FormData(f));save();go();const el=document.querySelector(`[data-form="${n}"] input:not([type=hidden])`);if(el&&n!=="journal")el.focus()});
  document.addEventListener("change",e=>{if(e.target.id!=="imp")return;const fl=e.target.files[0];if(!fl)return;const r=new FileReader();r.onload=()=>{try{const o=JSON.parse(r.result);if(!o||typeof o!=="object")throw 0;const c=sane(o);if(!c)throw 0;D=Object.assign(def(),c);save();go();alert("Data dipulihkan.")}catch(x){alert("File tidak valid.")}};r.readAsText(fl)});
  addEventListener("hashchange",()=>{go();$("main").scrollTop=0});
  fetch("holidays.json").then(r=>{if(!r.ok)throw 0;return r.json()}).then(j=>{loadHol(j);if(YRS.length&&!YRS.includes(S.cy))S.cy=YRS[0]}).catch(()=>{HOLERR=true}).finally(go);
  if("serviceWorker" in navigator)navigator.serviceWorker.register("sw.js").catch(()=>{});
})();
