const NOW=new Date();
const pad=n=>String(n).padStart(2,"0");
const ymd=d=>d.getFullYear()+"-"+pad(d.getMonth()+1)+"-"+pad(d.getDate());
const pd=s=>{const[a,b,c]=s.split("-").map(Number);return new Date(a,b-1,c)};
const TODAY=ymd(NOW);
const addD=(s,n)=>{const d=pd(s);d.setDate(d.getDate()+n);return ymd(d)};
const esc=s=>String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const uid=()=>Math.random().toString(36).slice(2,9);
const BLN=["Januari","Februari","Maret","April","Mei","Juni","Juli","Agustus","September","Oktober","November","Desember"];
const short=s=>pd(s).getDate()+" "+BLN[pd(s).getMonth()].slice(0,3);
const fmtD=s=>pd(s).toLocaleDateString("id-ID",{weekday:"long",day:"numeric",month:"long",year:"numeric"});
const rp=n=>"Rp "+Math.round(n).toLocaleString("id-ID");
const ini=s=>"MSSRKJS"[pd(s).getDay()];
const lastN=n=>Array.from({length:n},(_,i)=>addD(TODAY,i-n+1));
const hrs=s=>Array.from({length:19},(_,i)=>i+5).map(h=>`<option value="${h}" ${h===s?"selected":""}>${pad(h)}.00</option>`).join("");
let HOLERR=false;const HOL={},SRC={},YRS=[];
function loadHol(j){const t=[];Object.keys(j.libur).forEach(y=>{SRC[y]=j.sumber[y]||{};j.libur[y].forEach(h=>t.push([h.tanggal,{n:h.nama,k:h.jenis}]));YRS.push(+y)});t.forEach(([s,v])=>{HOL[s]=v});YRS.sort()}
const hl=s=>[short(s),HOL[s].n,HOL[s].k==="N"?"Nasional":"Cuti bersama"];
const nextH=n=>Object.keys(HOL).filter(s=>s>TODAY).sort().slice(0,n);
const def=()=>({name:"",tasks:[],events:[],goals:[],habits:[],mood:{},sleep:{},journal:[],fin:[],bud:{},proj:[],dl:[]});
const KEY="planner-os-2027";let D=def();
try{Object.assign(D,JSON.parse(localStorage.getItem(KEY))||{})}catch(e){}
let saveFail=false;
const save=()=>{try{localStorage.setItem(KEY,JSON.stringify(D))}catch(e){if(!saveFail){saveFail=true;alert("Data tidak bisa disimpan di perangkat ini (mode privat atau penyimpanan penuh). Gunakan Ekspor data di menu Downloads agar tidak hilang.")}}};
const sane=o=>{const b=def(),r={};if(!o||typeof o!=="object"||Array.isArray(o))return null;for(const k in b){if(!(k in o))continue;const ok=Array.isArray(b[k])?Array.isArray(o[k]):typeof b[k]==="object"?(o[k]&&typeof o[k]==="object"&&!Array.isArray(o[k])):typeof o[k]==="string";if(ok)r[k]=o[k]}return r};
const ic=p=>`<svg class="ico" viewBox="0 0 24 24" aria-hidden="true">${p}</svg>`;
const I={home:'<path d="M3 11l9-8 9 8v10H3z"/><path d="M10 21v-6h4v6"/>',plan:'<rect x="5" y="3" width="14" height="18" rx="2"/><path d="M9 3v18M12.5 8h4"/>',goal:'<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3.5"/>',well:'<path d="M12 20s-7-4.5-7-10a4 4 0 017-2.5A4 4 0 0119 10c0 5.5-7 10-7 10z"/>',jour:'<path d="M5 19l1-4L16 5l3 3L9 18zM14 7l3 3"/>',prod:'<path d="M4 12l5 5L20 6"/>',fin:'<path d="M3 7h16a2 2 0 012 2v9H5a2 2 0 01-2-2zM3 7l12-3v3M16 13h3"/>',cal:'<path d="M4 6h16v14H4zM4 10h16M8 3v4M16 3v4"/>',cat:'<path d="M4 4h12a4 4 0 014 4v12H8a4 4 0 01-4-4z"/><path d="M4 16a4 4 0 014-4h12"/>',dl:'<path d="M12 4v11M7 10l5 5 5-5M5 20h14"/>',adm:'<path d="M4 20V11M10 20V4M16 20v-6M2 20h20"/>',srch:'<circle cx="11" cy="11" r="6"/><path d="M20 20l-4-4"/>',bell:'<path d="M6 16v-5a6 6 0 0112 0v5l2 2H4zM10 20h4"/>',gear:'<circle cx="12" cy="12" r="3"/><path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M18.4 5.6l-2.1 2.1M7.7 16.3l-2.1 2.1"/>',menu:'<path d="M4 7h16M4 12h16M4 17h16"/>'};
const MODS=[
{id:"dashboard",t:"Dashboard",g:"Utama",i:"home",d:"Pusat kendali semua modul"},
{id:"planner",t:"Planner",g:"Personal",i:"plan",d:"Daily, weekly, monthly, yearly"},
{id:"goals",t:"Goals",g:"Personal",i:"goal",d:"Target, milestone, progres"},
{id:"wellness",t:"Wellness",g:"Personal",i:"well",d:"Mood, tidur, kebiasaan"},
{id:"journal",t:"Journal",g:"Personal",i:"jour",d:"Diary, notes, refleksi"},
{id:"productivity",t:"Productivity",g:"Kerja",i:"prod",d:"Proyek, tugas, deadline"},
{id:"finance",t:"Finance",g:"Kerja",i:"fin",d:"Anggaran, pemasukan, pengeluaran"},
{id:"calendar",t:"Calendar",g:"Kerja",i:"cal",d:"Kalender, hari libur, cuti"},
{id:"katalog",t:"Katalog",g:"Sistem",i:"cat",d:"Tema, template, preview"},
{id:"downloads",t:"Downloads",g:"Sistem",i:"dl",d:"PDF, ekspor, riwayat"}];
const S={cm:0,plan:"daily",date:TODAY,cy:NOW.getFullYear(),start:"monday",theme:"sage",adm:"Pengguna"};
const R={},A={},F={};
const pn=(t,b,c="c12",s="")=>`<section class="pn ${c}"><header><h3>${t}</h3>${s?`<span>${s}</span>`:""}</header>${b}</section>`;
const pg=(t,d,b)=>`<div class="ph"><h1>${t}</h1><p>${d}</p></div><div class="gd">${b}</div>`;
const prog=r=>r.map(x=>`<div class="pg"><div><b>${x[0]}</b><span>${x[2]||x[1]+"%"}</span></div><u><i style="width:${x[1]}%"></i></u></div>`).join("");
const list=r=>r.map(x=>`<div class="li"><b>${x[0]}</b><span>${x[1]}</span><span class="m">${x[2]||""}</span></div>`).join("");
const seg=(k,o)=>`<div class="seg" role="group">${o.map(([v,l])=>`<button data-set="${k}:${v}" aria-pressed="${S[k]===v}">${l}</button>`).join("")}</div>`;
const bars=(ser,lb,col=[])=>{const mx=Math.max(...ser.flat(),0)||1;return `<div class="bars">${lb.map((l,i)=>`<div><b>${ser.map((s,j)=>`<i title="${s[i]}" style="height:${s[i]/mx*100}%;${col[j]?"background:"+col[j]:""}"></i>`).join("")}</b><span>${l}</span></div>`).join("")}</div>`};
const empty=(t,p)=>`<div class="empty"><h3>${t}</h3><p>${p}</p></div>`;
const fm=(n,inner,btn="Tambah",c="")=>`<form class="fm ${c}" data-form="${n}">${inner}<button class="btn pri" type="submit">${btn}</button></form>`;
const inp=(n,ph,o="")=>`<input name="${n}" placeholder="${ph}" aria-label="${ph}" ${o}>`;
function grid(y,m,mon,ck){
  const f=new Date(y,m,1).getDay(),off=mon?(f+6)%7:f,n=new Date(y,m+1,0).getDate();
  let c=(mon?"SSRKJSM":"MSSRKJS").split("").map(x=>`<i>${x}</i>`).join("");
  for(let k=0;k<off;k++)c+="<i></i>";
  for(let d=1;d<=n;d++){
    const s=y+"-"+pad(m+1)+"-"+pad(d),h=HOL[s],w=new Date(y,m,d).getDay(),ev=D.events.some(e=>e.d===s);
    const cl=(h?(h.k==="N"?"n":"c"):w===0?"u":"")+(s===TODAY?" t":"")+(ev?" e":""),tt=h?esc(h.n):"";
    c+=ck?`<button class="${cl}" data-act="pick:${s}" title="${tt}">${d}</button>`:`<span class="${cl}" title="${tt}">${d}</span>`}
  return `<div class="g">${c}</div>`}
const legend=`<div class="lg"><span><b style="background:var(--red)"></b>Libur nasional</span><span><b style="box-shadow:inset 0 0 0 1px var(--red)"></b>Cuti bersama</span><span><b style="background:var(--brass);border-radius:50%"></b>Ada jadwal</span></div>`;
const year=y=>`<div class="yg">${BLN.map((b,m)=>`<div><h4><button class="lk" data-act="mon:${y}-${pad(m+1)}">${b}</button></h4>${grid(y,m,true,true)}</div>`).join("")}</div>${legend}`;
function go(){
  const ae=document.activeElement,ak=ae&&ae.dataset&&ae.dataset.act;
  const id=(location.hash||"#dashboard").slice(1),m=MODS.find(x=>x.id===id)||MODS[0];
  const vw=document.getElementById("view");vw.innerHTML=R[m.id]();
  if(HOLERR)vw.insertAdjacentHTML("afterbegin",'<p class="out" role="alert">Data tanggal merah gagal dimuat. Kalender tampil tanpa tanda libur. Muat ulang halaman saat online.</p>');
  const av=document.querySelector(".av");if(av)av.textContent=(D.name||"?").trim().charAt(0).toUpperCase()||"?";
  if(ak){const n=document.querySelector('[data-act="'+ak.replace(/"/g,'\\"')+'"]');if(n)n.focus()}
  document.querySelectorAll(".nv").forEach(b=>b.dataset.go===m.id?b.setAttribute("aria-current","page"):b.removeAttribute("aria-current"));
  document.title=m.t+" · Planner OS 2027";document.body.classList.remove("open");
  const d=document.querySelector("#bell .dot");if(d)d.hidden=!D.events.some(e=>e.d===TODAY)}
