A.task=id=>{const t=D.tasks.find(x=>x.id===id);if(t)t.done=t.done?"":TODAY};
A.taskdel=id=>{D.tasks=D.tasks.filter(x=>x.id!==id)};
A.evdel=id=>{D.events=D.events.filter(x=>x.id!==id)};
A.cm=n=>{S.cm+=+n};
A.cy=n=>{S.cy+=+n};
A.today=()=>{S.date=TODAY};
A.pick=s=>{S.date=s;S.plan="daily";if(location.hash!=="#planner")location.hash="planner"};
A.mon=ym=>{S.date=ym+"-01";S.plan="monthly";if(location.hash!=="#planner")location.hash="planner"};
A.shift=n=>{n=+n;const d=pd(S.date);
  if(S.plan==="daily")d.setDate(d.getDate()+n);
  else if(S.plan==="weekly")d.setDate(d.getDate()+7*n);
  else if(S.plan==="monthly"){d.setDate(1);d.setMonth(d.getMonth()+n)}
  else{d.setDate(1);d.setFullYear(d.getFullYear()+n)}
  S.date=ymd(d)};
F.name=f=>{D.name=f.get("n").trim().slice(0,40)};
F.task=f=>{const t=f.get("t").trim();if(t)D.tasks.push({id:uid(),t,p:+f.get("p"),done:""})};
F.ev=f=>{const t=f.get("t").trim();if(t&&f.get("d"))D.events.push({id:uid(),d:f.get("d"),h:+f.get("h"),t})};

R.dashboard=()=>{
  const hr=NOW.getHours(),gr=hr<11?"pagi":hr<15?"siang":hr<18?"sore":"malam";
  const nx=nextH(1)[0],days=nx?Math.ceil((pd(nx)-pd(TODAY))/864e5):0;
  const yd=Math.round((pd(TODAY)-new Date(NOW.getFullYear(),0,0))/864e5),yl=Math.round((new Date(NOW.getFullYear()+1,0,1)-new Date(NOW.getFullYear(),0,1))/864e5);
  const evT=D.events.filter(e=>e.d===TODAY).sort((a,b)=>a.h-b.h),ni=evT.findIndex(e=>e.h>=hr);
  const open=D.tasks.filter(t=>!t.done).length,hp=D.habits.filter(h=>!h.log[TODAY]).length;
  const cm=new Date(NOW.getFullYear(),NOW.getMonth()+S.cm,1),cy=cm.getFullYear(),cmo=cm.getMonth();
  const ag=[...D.events.filter(e=>e.d>=TODAY).map(e=>[e.d,short(e.d),esc(e.t),pad(e.h)+".00"]),...Object.keys(HOL).filter(s=>s>=TODAY).map(s=>[s,...hl(s)])].sort((a,b)=>a[0]<b[0]?-1:1).slice(0,4).map(x=>x.slice(1));
  const tod=(evT.length?evT.map((e,i)=>`<div class="tl ${i===ni?"nx":""}"><b>${pad(e.h)}.00</b><span>${esc(e.t)}</span><button class="x" data-act="evdel:${e.id}" aria-label="Hapus jadwal">×</button></div>`).join(""):`<p class="mute">Belum ada jadwal hari ini.</p>`)
   +`<p class="mute" style="margin:10px 0 0">${open} tugas terbuka${D.habits.length?`, ${hp} kebiasaan belum dicentang`:""}.</p>`
   +fm("ev",`<input type="hidden" name="d" value="${TODAY}"><select name="h" aria-label="Jam">${hrs(Math.max(hr,5))}</select>${inp("t","Jadwal baru","required")}`,"Tambah","in");
  const ts=[...D.tasks].sort((a,b)=>(!!a.done-!!b.done)||b.p-a.p),dn=D.tasks.length-open;
  const task=(D.tasks.length?prog([[`${dn} dari ${D.tasks.length} selesai`,Math.round(dn/D.tasks.length*100)]]):"")
   +fm("task",`${inp("t","Tugas baru","required")}<select name="p" aria-label="Prioritas"><option value="2">Tinggi</option><option value="1" selected>Sedang</option><option value="0">Rendah</option></select>`,"Tambah")
   +(ts.map(t=>`<div class="tk p${t.p} ${t.done?"d":""}"><label><input type="checkbox" data-act="task:${t.id}" ${t.done?"checked":""}><span>${esc(t.t)}</span></label><button class="x" data-act="taskdel:${t.id}" aria-label="Hapus tugas">×</button></div>`).join("")||`<p class="mute">Belum ada tugas. Tambahkan yang pertama di atas.</p>`);
  const L=lastN(7),a1=L.map(s=>D.tasks.filter(t=>t.done===s).length),a2=L.map(s=>D.habits.filter(h=>h.log[s]).length);
  const act=bars([a1,a2],L.map(ini),["var(--sage)","var(--brass)"])+`<div class="lg"><span><b style="background:var(--sage)"></b>Tugas selesai</span><span><b style="background:var(--brass)"></b>Kebiasaan dicentang</span><span>7 hari terakhir, hari ini di kanan</span></div>`;
  return `<div class="gd">
  <section class="hero c8"><div><p>Selamat ${gr}${D.name?", "+esc(D.name):""}</p><h1>${fmtD(TODAY)}</h1></div>
  <div><div class="yr"><i style="width:${yd/yl*100}%"></i></div><p>Hari ke-${yd} dari ${yl}.${nx?` Tanggal merah berikutnya: ${HOL[nx].n}, ${days} hari lagi.`:""}</p></div></section>
  ${D.name?"":pn("Siapa namamu?",fm("name",inp("n","Nama panggilan","required maxlength=40"),"Simpan"),"c4")}
  ${pn("Hari ini",tod,"c4")}
  ${pn(BLN[cmo]+" "+cy,grid(cy,cmo,true,true)+`<div class="ag">${list(ag)}</div>`,"c5").replace("</header>",`<span class="r"><button class="ib" data-act="cm:-1" aria-label="Bulan sebelumnya">‹</button><button class="ib" data-act="cm:1" aria-label="Bulan berikutnya">›</button></span></header>`)}
  ${pn("Task center",task,"c7")}
  ${pn("Aktivitas",act,"c7")}
  ${pn("Quick launch",`<div class="ql">${MODS.slice(1).map(m=>`<button data-go="${m.id}">${ic(I[m.i])}<span>${m.t}</span></button>`).join("")}</div>`,"c5")}
  </div>`};

R.planner=()=>{
  const P=[["daily","Daily"],["weekly","Weekly"],["monthly","Monthly"],["yearly","Yearly"]],d=pd(S.date),y=d.getFullYear(),mo=d.getMonth();
  const w0=addD(S.date,-((d.getDay()+6)%7));
  const lab=S.plan==="daily"?fmtD(S.date):S.plan==="weekly"?short(w0)+" – "+short(addD(w0,6)):S.plan==="monthly"?BLN[mo]+" "+y:String(y);
  const nav=`<div class="nvb"><button class="btn" data-act="shift:-1" aria-label="Sebelumnya">‹</button><strong>${lab}</strong><button class="btn" data-act="shift:1" aria-label="Berikutnya">›</button><button class="btn" data-act="today:">Hari ini</button></div>`;
  let b;
  if(S.plan==="daily"){
    const ev=D.events.filter(e=>e.d===S.date),h=HOL[S.date];
    const rows=Array.from({length:19},(_,i)=>i+5).map(hh=>`<div class="tl"><b>${pad(hh)}.00</b><span>${ev.filter(e=>e.h===hh).map(e=>`<em>${esc(e.t)} <button class="x" data-act="evdel:${e.id}" aria-label="Hapus">×</button></em>`).join("")}</span><span></span></div>`).join("");
    b=pn("Jadwal per jam",(h?`<p class="out" style="margin:0 0 10px">${esc(h.n)} (${h.k==="N"?"libur nasional":"cuti bersama"})</p>`:"")+fm("ev",`<input type="hidden" name="d" value="${S.date}"><select name="h" aria-label="Jam">${hrs(9)}</select>${inp("t","Jadwal baru","required")}`)+rows);
  }else if(S.plan==="weekly"){
    b=`<div class="wk c12">${Array.from({length:7},(_,i)=>addD(w0,i)).map(s=>{const h=HOL[s];return `<div class="${s===TODAY?"t":""}"><button class="lk" data-act="pick:${s}">${["Sen","Sel","Rab","Kam","Jum","Sab","Min"][(pd(s).getDay()+6)%7]} ${pd(s).getDate()}</button>${h?`<p class="h">${esc(h.n)}</p>`:""}${D.events.filter(e=>e.d===s).sort((a,c)=>a.h-c.h).map(e=>`<p>${pad(e.h)}.00 ${esc(e.t)}</p>`).join("")}</div>`}).join("")}</div>`;
  }else if(S.plan==="monthly"){
    b=`<div class="big c12">${pn(BLN[mo]+" "+y,grid(y,mo,true,true)+legend)}</div>`;
  }else b=pn("Tahun "+y,year(y));
  return pg("Planner","Satu planner, empat tampilan waktu. Pilih tanggal untuk membuka harinya.",`<div class="c12">${seg("plan",P)}${nav}</div>${b}`)};

R.calendar=()=>{
  const y=S.cy,up=D.events.filter(e=>e.d>=TODAY).sort((a,b)=>a.d<b.d?-1:a.d>b.d?1:a.h-b.h).slice(0,8);
  const ks=Object.keys(HOL).filter(s=>s.startsWith(y+"-")).sort(),sc=SRC[y]||{},nn=ks.filter(s=>HOL[s].k==="N").length,cc=ks.length-nn;
  const hol=ks.length?`<div class="cols">${list(ks.map(hl))}</div><p class="mute" style="margin:10px 0 0">Sumber: ${esc(sc.dokumen||"data libur")}${sc.ditetapkan?", "+fmtD(sc.ditetapkan):""}. ${esc(sc.catatan||"")}</p>`:`<p class="mute">Data libur untuk ${y} belum tersedia. Tambahkan ke holidays.json.</p>`;
  return pg("Calendar","Kalender, hari libur, cuti bersama, dan jadwal pribadi.",
   `<div class="c12 nvb"><button class="btn" data-act="cy:-1" aria-label="Tahun sebelumnya">‹</button><strong style="min-width:60px">${y}</strong><button class="btn" data-act="cy:1" aria-label="Tahun berikutnya">›</button></div>`
   +pn("Kalender "+y,year(y))
   +pn("Tambah jadwal",fm("ev",`<input type="date" name="d" value="${TODAY}" required aria-label="Tanggal"><select name="h" aria-label="Jam">${hrs(9)}</select>${inp("t","Nama jadwal","required")}`),"c5")
   +pn("Jadwal mendatang",up.length?up.map(e=>`<div class="li"><b>${short(e.d)}</b><span>${esc(e.t)}</span><span class="m">${pad(e.h)}.00 <button class="x" data-act="evdel:${e.id}" aria-label="Hapus">×</button></span></div>`).join(""):`<p class="mute">Belum ada jadwal mendatang.</p>`,"c7")
   +pn("Libur dan cuti bersama",hol,"c12",ks.length?nn+" nasional, "+cc+" cuti bersama":""))};
