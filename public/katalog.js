/* Katalog lengkap. Dimuat setelah mods2.js dan menimpa R.katalog dan R.downloads.
   Dibungkus IIFE supaya tidak bentrok dengan nama global di core.js, mods1.js, mods2.js. */
(function(){
  const VER=[["full","Lengkap"],["lite","Ringkas"]];
  /* [id, nama, warna utama, warna lembut, warna aksen, latar]. Harus sama dengan THEMES di generate_planner.py */
  const TH=[["sage","Sage","#5F7F6E","#E3EBE5","#E8D9C5","#FBFAF7"],["rose","Rose","#B5707D","#F6E4E7","#EBD7C3","#FFFBFA"],["slate","Slate","#4A5D78","#E2E8F0","#F0DFC8","#F9FAFB"],["lavender","Lavender","#7B6BA8","#E9E5F4","#EADFC9","#FBFAFE"],["ocean","Ocean","#3F7F95","#DDEEF2","#F1E2C8","#F7FBFC"],["peach","Peach","#D98560","#FBE6DA","#E6E3C8","#FFFAF6"],["mocha","Mocha","#8B6B52","#EDE3D9","#D9E0CF","#FAF7F3"],["mint","Mint","#3E9C86","#DDF1EA","#F3E5D0","#F7FCFA"],["midnight","Midnight (gelap)","#9DB4E6","#2A3040","#3A4157","#1B1F2A"]];
  const THEMES=TH.map(x=>[x[0],x[1]]);
  const swatch=id=>{const t=TH.find(x=>x[0]===id)||TH[0];return `<div style="display:flex;gap:6px;align-items:center;margin:10px 0 0">${[t[5],t[3],t[2],t[4]].map(c=>`<i style="width:26px;height:26px;border-radius:50%;background:${c};border:1px solid rgba(128,128,128,.45);display:inline-block" aria-hidden="true"></i>`).join("")}<span class="mute" style="margin-left:6px">Palet ${esc(t[1])}</span></div>`};
  const STARTS=[["monday","Senin"],["sunday","Minggu"]];
  /* Isi tautan toko di sini (harus diawali https://). Tombol hanya tampil kalau terisi. */
  const SHOP={shopee:"",tiktok:"",etsy:""};
  const SHOPN={shopee:"Shopee",tiktok:"TikTok Shop",etsy:"Etsy"};
  /* [kategori, nama, deskripsi, jumlah halaman, hanya versi lengkap] */
  const SEC=[
    ["Dasar","Cover, Index, Year overview","Sampul, indeks yang semua itemnya bisa diklik, dan ringkasan setahun.",3],
    ["Kalender","Holidays","18 libur nasional dan 8 cuti bersama 2027, bisa diklik ke harinya.",1],
    ["Kalender","Monthly","Januari sampai Desember, dengan link ke minggu dan hari.",12],
    ["Kalender","Weekly","53 minggu.",53],
    ["Harian","Daily","365 hari: jadwal per jam, to-do, top 3, water, mood, notes.",365,true],
    ["Tracker","Habit tracker","Satu halaman per bulan.",12],
    ["Tracker","Mood tracker","Satu halaman per bulan.",12],
    ["Perencanaan","Budget, Expense log, Meal planner, Grocery, Goal, Project, Reading tracker, Brain dump","Delapan halaman perencanaan untuk keuangan, makan, target, dan ide.",8],
    ["Wellness","Wellness","Hub, daily log 12 bulan, period tracker, symptom log, medication log, doctor visit.",17],
    ["Produktivitas","Productivity","Hub, quarterly, SMART goal, appointments, meeting minutes, pomodoro, contacts, password tracker, order tracker.",9],
    ["Lifestyle","Lifestyle","Hub, birthdays, chore chart, cleaning checklist, outfit planner, bucket list.",6],
    ["Catatan","Notes","Lined, dotted, dan grid.",3]
  ];
  const CATS=[["all","Semua"]].concat(SEC.map(x=>x[0]).filter((c,i,a)=>a.indexOf(c)===i).map(c=>[c,c]));
  const pagesOf=v=>SEC.filter(x=>v==="full"||!x[4]).reduce((a,x)=>a+x[3],0);
  const fname=(s,t,v)=>`Planner-2027-${s}-${t}${v==="lite"?"-lite":""}.pdf`;
  const cur=()=>fname(S.start,S.theme,S.ver);
  const badge=t=>`<span style="display:inline-block;border:1px solid rgba(128,128,128,.4);border-radius:999px;padding:2px 10px;font-size:.82em;margin:0 6px 6px 0">${t}</span>`;
  const stat=(n,l)=>`<div><b style="display:block;font-size:1.5em">${n}</b><span class="mute">${l}</span></div>`;
  const lbl=t=>`<div class="mute" style="margin:10px 0 4px">${t}</div>`;

  Object.assign(S,{ver:"full",kc:"all",kq:""});
  F.kq=f=>{S.kq=String(f.get("q")||"").trim().toLowerCase()};

  /* Cek file ke server: tampilkan ukuran kalau ada, pesan jelas kalau belum ada atau offline. */
  const check=f=>{
    fetch("planners/"+f,{method:"HEAD",cache:"no-store"}).then(r=>{
      if(!r.ok)throw 0;
      const st=document.getElementById("pdfst");
      if(!st||cur()!==f)return;
      const n=+r.headers.get("content-length");
      st.textContent=n?`File siap. Ukuran sekitar ${(n/1048576).toFixed(1)} MB.`:"File siap.";
    }).catch(()=>{
      const st=document.getElementById("pdfst"),box=document.getElementById("pdfbox");
      if(!st||cur()!==f)return;
      st.textContent=navigator.onLine?"File planner ini belum tersedia di server. Coba varian lain atau muat ulang nanti.":"Kamu sedang offline. Pratinjau dan unduhan PDF butuh koneksi internet.";
      st.className="out";st.setAttribute("role","alert");
      if(box)box.innerHTML="";
    });
  };

  R.katalog=()=>{
    const f=cur(),u="planners/"+f,tot=pagesOf(S.ver),small=matchMedia("(max-width:700px)").matches;
    const rows=SEC.filter(x=>(S.kc==="all"||x[0]===S.kc)&&(!S.kq||(x[0]+" "+x[1]+" "+x[2]).toLowerCase().includes(S.kq)))
      .map(x=>[esc(x[1]),esc(x[2]),x[4]&&S.ver==="lite"?"Hanya Lengkap":x[3]+" hal"]);
    const shop=Object.keys(SHOP).filter(k=>/^https:\/\//.test(SHOP[k]))
      .map(k=>`<a class="btn pri" href="${esc(SHOP[k])}" target="_blank" rel="noopener noreferrer">Beli di ${SHOPN[k]}</a>`).join("");
    const info=pn("Planner Digital 2027",
      `<p style="margin:0 0 10px">Planner PDF dengan navigasi hyperlink (ketuk untuk pindah halaman), siap dipakai di GoodNotes, Notability, dan Noteshelf. Tanggal merah dan cuti bersama Indonesia 2027 sudah ditandai di kalender, mingguan, dan harian.</p>`
      +badge("Bahasa Indonesia")+badge("PDF berlink")+badge(THEMES.length+" tema")+badge("Mulai Senin atau Minggu")
      +`<div style="display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(110px,1fr));margin-top:6px">${stat(pagesOf("full"),"halaman, versi Lengkap")}${stat(pagesOf("lite"),"halaman, versi Ringkas")}${stat(26,"tanggal merah 2027")}${stat(VER.length*STARTS.length*THEMES.length,"file PDF")}</div>`
      +(shop?`<div class="fm" style="margin-top:12px">${shop}</div>`:""),"c12");
    const pick=pn("Pilih varian",
      lbl("Versi")+seg("ver",VER)+lbl("Tema")+seg("theme",THEMES)+swatch(S.theme)+lbl("Awal minggu")+seg("start",STARTS)
      +`<p class="mute" style="margin:10px 0">${tot} halaman. ${S.ver==="lite"?"Tanpa halaman harian, file lebih kecil.":"Termasuk 365 halaman harian."}</p>`
      +`<div class="fm"><a class="btn" href="${u}" target="_blank" rel="noopener">Buka di tab baru</a><a class="btn pri" href="${u}" download data-act="dl:${f}">Download PDF</a></div>`
      +`<p class="mute" style="margin:10px 0">Di HP, buka PDF dengan GoodNotes, Notability, Adobe Acrobat, atau Xodo agar link bisa diketuk. Pratinjau bawaan browser dan Google Drive sering mengabaikan link di dalam PDF.</p>`
      +`<p class="mute" id="pdfst" role="status" style="margin:10px 0">Memeriksa file...</p>`
      +`<div id="pdfbox">${small?`<p class="mute">Pratinjau tidak ditampilkan di layar kecil. Pakai Buka di tab baru.</p>`:`<iframe class="pdf" title="Pratinjau planner" src="${u}"></iframe>`}</div>`,"c7");
    const how=pn("Cara pakai",
      `<ol style="margin:0;padding-left:18px;line-height:1.6"><li>Pilih versi, tema, dan awal minggu, lalu Download PDF.</li><li>Impor atau buka file di GoodNotes, Notability, atau Noteshelf.</li><li>Ketuk tab di bagian atas halaman untuk pindah antar bagian.</li><li>Tanggal merah sudah ditandai otomatis.</li></ol><p class="mute" style="margin:10px 0 0">Halaman kesehatan memuat catatan bahwa isinya bukan nasihat medis.</p>`,"c5");
    const sec=pn("Isi planner",
      fm("kq",`<input name="q" value="${esc(S.kq)}" placeholder="Cari bagian, misal Habit" aria-label="Cari bagian planner" maxlength="40">`,"Cari","in")
      +seg("kc",CATS)
      +`<div style="margin-top:10px">${rows.length?list(rows):empty("Tidak ada bagian yang cocok","Ubah kata kunci atau pilih kategori Semua.")}</div>`,"c12",tot+" halaman");
    setTimeout(()=>check(f),0);
    return pg("Katalog","Pilih tema, versi, dan awal minggu, lihat isi dan pratinjau.",info+pick+how+sec);
  };

  R.downloads=()=>{
    const fs=VER.flatMap(([v])=>STARTS.flatMap(([s])=>THEMES.map(([t])=>fname(s,t,v))));
    return pg("Downloads","PDF, ekspor, dan riwayat.",
      pn("File planner",fs.map(f=>`<div class="fl">${ic(I.dl)}${f}<a class="btn" href="planners/${f}" download data-act="dl:${f}">Unduh</a></div>`).join(""),"c7")
      +pn("Riwayat unduhan",D.dl.length?list(D.dl.slice(0,8).map(x=>[x.at.slice(5,10),esc(x.f),x.at.slice(11)])):empty("Belum ada riwayat","Unduhan dari perangkat ini tercatat di sini."),"c5")
      +pn("Data saya",`${fm("name",`<input name="n" value="${esc(D.name)}" placeholder="Nama panggilan" aria-label="Nama panggilan" maxlength="40">`,"Simpan nama","in")}<p style="margin:10px 0">Semua data tersimpan di perangkat ini. Ekspor untuk cadangan atau pindah perangkat.</p><div class="fm"><button class="btn pri" data-act="export:">Ekspor data (JSON)</button><label class="btn">Pulihkan dari file<input id="imp" type="file" accept=".json,application/json" hidden></label><button class="btn" data-act="reset:">Hapus semua data</button></div>`,"c12"));
  };
})();
