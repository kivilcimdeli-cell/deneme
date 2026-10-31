// BOYDE Atölye arayüzü: ürün seç → müşteri bilgileri → katalog (yenilenebilir) → seçilen kod → baskı dosyaları.
"use strict";
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}[c]));
const sayfa = $("#sayfa");
let URUNLER = [], DURUM = {}, zamanlayici = null;

// çizgi simgeler (24 × 24); ürünlerinki ürün koduna göre (emoji Windows'ta her yerde düzgün çıkmıyor)
const YOL = {
  arti: "M12 5v14M5 12h14",
  kisiler: "M9 11.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7ZM2.5 20c0-3.6 2.9-6 6.5-6s6.5 2.4 6.5 6M16 4.8a3.2 3.2 0 0 1 0 6.2M18.5 14.4c1.9.6 3 2.3 3 4.6",
  isler: "M3 12h4l3-8 4 16 3-8h4",
  klasor: "M3 7.5A2.5 2.5 0 0 1 5.5 5H9l2 2h7.5A2.5 2.5 0 0 1 21 9.5v7a2.5 2.5 0 0 1-2.5 2.5h-13A2.5 2.5 0 0 1 3 16.5Z",
  kalem: "M4 20h4L19 9a2.8 2.8 0 0 0-4-4L4 16v4Z",
  cop: "M4 7h16M9.5 7V4.5h5V7M6.5 7l1 13h9l1-13",
  indir: "M12 4v11M7 10l5 5 5-5M5 20h14",
  ac: "M14 4h6v6M20 4l-9 9M18 14v4.5a1.5 1.5 0 0 1-1.5 1.5h-11A1.5 1.5 0 0 1 4 18.5v-11A1.5 1.5 0 0 1 5.5 6H10",
  ara: "M11 18a7 7 0 1 0 0-14 7 7 0 0 0 0 14ZM20 20l-4-4",
  yildiz: "M12 3l1.9 5.6L19.5 10l-5.6 1.9L12 17.5l-1.9-5.6L4.5 10l5.6-1.4Z",
  tik: "M5 12.5l4.5 4.5L19 7.5",
  ok: "M5 12h14M13 6l6 6-6 6",
  sag: "M9 6l6 6-6 6",
  yenile: "M20 11a8 8 0 1 0-2.4 5.7M20 4.5V11h-6.5",
  kapat: "M6 6l12 12M18 6 6 18",
  uyari: "M12 4 21 20H3ZM12 10v4.5M12 17.2v.3",
  katalog: "M4 5h7v7H4ZM13 5h7v7h-7ZM4 14h7v5H4ZM13 14h7v5h-7Z",
  kup: "M12 3l8 4.5v9L12 21l-8-4.5v-9ZM12 12l8-4.5M12 12v9M12 12 4 7.5",
  saat: "M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18ZM12 7v5l3 2",
  qr: "M4 4h6v6H4ZM14 4h6v6h-6ZM4 14h6v6H4ZM14 14h2.5v2.5H14ZM17.5 17.5H20V20h-2.5ZM14 19h1.5M19 14v1.5",
  kart: "M3 6.5A1.5 1.5 0 0 1 4.5 5h15A1.5 1.5 0 0 1 21 6.5v11a1.5 1.5 0 0 1-1.5 1.5h-15A1.5 1.5 0 0 1 3 17.5ZM8.5 12.5a2 2 0 1 0 0-4 2 2 0 0 0 0 4ZM5.8 16.2c.5-1.4 1.6-2.2 2.7-2.2s2.2.8 2.7 2.2M14 10h4.5M14 13.5h3",
  bayrak: "M5 21V4M5 4h13l-2.5 4.5L18 13H5",
  anahtar: "M8.5 19.5a4.5 4.5 0 1 0 0-9 4.5 4.5 0 0 0 0 9ZM11.7 11.8 20 3.5M16.5 7l3 3M14.5 9l2 2",
};
const URUN_IKON = {isimlik_9x12: "qr", kurumsal_10x20: "kart", bayrakli: "bayrak", anahtarlik: "anahtar"};
const ikon = (ad, cls = "") => `<span class="ikon ${cls}"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
  stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="${YOL[ad] || YOL.kup}"/></svg></span>`;

async function api(yol, govde) {
  const r = await fetch("/api/" + yol, govde === undefined ? {} :
    {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(govde)});
  const v = await r.json();
  if (!r.ok) throw new Error(v.hata || r.statusText);
  return v;
}

function bildir(mesaj, hata) {
  const b = $("#bildirim");
  b.innerHTML = ikon(hata ? "uyari" : "tik") + `<span>${esc(mesaj)}</span>`;
  b.className = "bildirim" + (hata ? " hata" : ""); b.hidden = false;
  clearTimeout(b._t); b._t = setTimeout(() => (b.hidden = true), hata ? 7000 : 3500);
}

const tarih = s => s ? new Date(s).toLocaleString("tr-TR", {dateStyle: "short", timeStyle: "short"}) : "";
function once(s) {                                        // "5 dk önce"; bir haftadan eskiyse tarih
  const d = (Date.now() - Date.parse(s)) / 1000;
  if (!s || isNaN(d)) return "";
  if (d < 60) return "az önce";
  if (d < 3600) return `${Math.floor(d / 60)} dk önce`;
  if (d < 86400) return `${Math.floor(d / 3600)} sa önce`;
  if (d < 7 * 86400) return `${Math.floor(d / 86400)} gün önce`;
  return tarih(s);
}
const urunAdi = kod => (URUNLER.find(u => u.kod === kod) || {}).ad || kod;
const basHarf = ad => String(ad).split(/\s+/).filter(Boolean).slice(0, 2).map(w => w[0].toLocaleUpperCase("tr")).join("");
const dosyaUrl = (k, yol, indir) => `/dosya/${encodeURIComponent(k)}/${yol.split("/").map(encodeURIComponent).join("/")}${indir ? "?indir=1" : ""}`;
const yukleniyor = (s = "Yükleniyor…") => `<div class="yukleniyor"><span class="donen"></span>${esc(s)}</div>`;
const iz = (...p) => `<div class="iz">${p.map(([a, h]) => h ? `<a href="${h}">${esc(a)}</a>` : `<span>${esc(a)}</span>`).join(ikon("sag"))}</div>`;
const baslik = (h1, alt = "", sag = "") => `<header class="baslik"><div><h1>${h1}</h1>${alt ? `<p class="alt">${alt}</p>` : ""}</div>${sag}</header>`;

// ------------------------------------------------------------------ yönlendirme ve menü
async function git() {
  clearTimeout(zamanlayici);
  cekmeceKapat();
  const [, yol = "", arg = ""] = location.hash.split("/");
  const menu = yol === "musteri" ? "musteriler" : yol === "yeni" ? "" : yol;
  $$("#menu a").forEach(a => a.classList.toggle("etkin", a.dataset.yol === menu));
  try {
    if (!URUNLER.length) {
      sayfa.innerHTML = yukleniyor("Yükleniyor… (ilk açılışta birkaç saniye sürer)");
      [URUNLER, DURUM] = await Promise.all([api("urunler"), api("durum").catch(() => ({}))]);
      $$("[data-ikon]").forEach(el => (el.outerHTML = ikon(el.dataset.ikon)));
      yanAlt();
    }
    yanSon(yol === "musteri" ? decodeURIComponent(arg) : "");
    if (yol === "yeni") return yeniSiparis(decodeURIComponent(arg));
    if (yol === "musteri") return musteriSayfasi(decodeURIComponent(arg));
    if (yol === "musteriler") return musteriler();
    if (yol === "isler") return isler();
    return anaSayfa();
  } catch (e) {
    sayfa.innerHTML = `<div class="uyari hata-kutu">${esc(e.message)}</div>`;
  }
}
addEventListener("hashchange", git);

async function yanSon(aktif) {
  const rows = (await api("musteriler").catch(() => [])).slice(0, 6);
  $("#son-musteriler").innerHTML = rows.length ? rows.map(r => `
    <a href="#/musteri/${encodeURIComponent(r.kimlik)}" class="${r.kimlik === aktif ? "etkin" : ""}">
      <b>${esc(r.ad)}</b><span>${esc(urunAdi(r.urun))}</span></a>`).join("")
    : `<p class="yan-baslik" style="letter-spacing:0;text-transform:none;font-weight:400">Henüz yok</p>`;
}

function yanAlt() {
  $("#yan-alt").innerHTML = `
    <div class="durum-nokta ${DURUM.claude ? "acik" : ""}" title="Özel istekler için Claude Code"><i></i>
      ${DURUM.claude ? "Claude hazır" : "Claude kurulu değil"}</div>
    <div>Sürüm ${esc(DURUM.surum || "–")}</div>`;
}

// ------------------------------------------------------------------ ana sayfa ve müşteriler
function durumCipi(r) {
  if (r.cikti) return `<span class="cip yesil">${ikon("tik")}Üretildi${r.secim ? " · " + esc(r.secim) : ""}</span>`;
  if (r.katalog) return `<span class="cip turuncu">${r.katalog}. katalog · seçim bekliyor</span>`;
  return `<span class="cip">Yeni</span>`;
}

function listeHtml(rows, bos = "Henüz müşteri yok.") {
  if (!rows.length) return `<div class="kart bos">${ikon("kisiler")}<p>${esc(bos)}</p></div>`;
  return `<div class="kart liste">${rows.map(r => `
    <a class="liste-satir" href="#/musteri/${encodeURIComponent(r.kimlik)}">
      <span class="avatar">${esc(basHarf(r.ad))}</span>
      <span class="ad"><b>${esc(r.ad)}</b><span>${esc(urunAdi(r.urun))}</span></span>
      <span class="cipler">${durumCipi(r)}</span>
      <time title="${tarih(r.guncelleme)}">${once(r.guncelleme)}</time>${ikon("sag")}</a>`).join("")}</div>`;
}

async function anaSayfa() {
  const rows = await api("musteriler");
  const d = new Date(), ay = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
  const ozet = [["kisiler", rows.length, "müşteri"], ["saat", rows.filter(r => (r.guncelleme || "").startsWith(ay)).length,
    "bu ay çalışılan"], ["kup", rows.filter(r => r.cikti).length, "baskı dosyası hazır"]];
  sayfa.innerHTML = baslik("Yeni sipariş", "Ürünü seçin. Müşteri bilgilerinden sonra katalog ya da baskı dosyası hazırlanır.") + `
    <div class="ozet">${ozet.map(([i, n, t]) => `<div class="kart">${ikon(i)}<div><b>${n}</b><span>${t}</span></div></div>`).join("")}</div>
    <div class="bolum urunler">${URUNLER.map(u => `
      <a class="kart urun" href="#/yeni/${u.kod}">
        <span class="urun-ikon">${ikon(URUN_IKON[u.kod])}</span><h2>${esc(u.ad)}</h2>
        <p>${esc(u.aciklama)}</p>
        <span class="urun-alt"><span class="cip">${u.katalog_adet ? `${u.katalog_adet} tasarımlık katalog` : "Doğrudan 3MF"}</span>
          ${ikon("ok", "ok")}</span></a>`).join("")}</div>
    <div class="bolum"><div class="kart-baslik"><h2>Son müşteriler</h2>
      ${rows.length ? `<a class="dugme ince kucuk" href="#/musteriler">Hepsi ${ikon("ok")}</a>` : ""}</div>
      ${listeHtml(rows.slice(0, 5))}</div>`;
}

let SUZGEC = "";
async function musteriler() {
  const rows = await api("musteriler");
  sayfa.innerHTML = baslik("Müşteriler", `${rows.length} kayıt · ${esc(DURUM.veri || "")}`) + `
    <div class="arac-cubugu"><div class="arama">${ikon("ara")}<input id="ara" placeholder="Ad ya da ürün ara…"></div>
      <div class="suzgec">${[["", "Tümü"], ...URUNLER.map(u => [u.kod, u.ad])].map(([k, a]) =>
        `<button data-urun="${k}" class="${SUZGEC === k ? "etkin" : ""}">${esc(a)}</button>`).join("")}</div></div>
    <div id="liste"></div>`;
  const ciz = () => {
    const q = $("#ara").value.toLocaleLowerCase("tr");
    $("#liste").innerHTML = listeHtml(rows.filter(r => (!SUZGEC || r.urun === SUZGEC) &&
      (r.ad + " " + urunAdi(r.urun)).toLocaleLowerCase("tr").includes(q)), rows.length ? "Aramaya uyan müşteri yok." : "Henüz müşteri yok.");
  };
  $("#ara").oninput = ciz;
  $$("[data-urun]").forEach(b => b.onclick = () => {
    SUZGEC = b.dataset.urun; $$("[data-urun]").forEach(x => x.classList.toggle("etkin", x === b)); ciz();
  });
  ciz();
  $("#ara").focus();
}

// ------------------------------------------------------------------ form
function alanHtml(a, deger) {
  const d = esc(deger ?? a.varsayilan ?? "");
  const z = a.zorunlu ? " required" : "";
  let giris;
  if (a.tur === "textarea") giris = `<textarea name="${a.ad}"${z} placeholder="${esc(a.ornek || "")}">${d}</textarea>`;
  else if (a.tur === "select") giris = `<select name="${a.ad}"${z}>${a.secenekler.map(([v, t]) =>
      `<option value="${esc(v)}"${String(v) === String(deger ?? a.varsayilan ?? "") ? " selected" : ""}>${esc(t)}</option>`).join("")}</select>`;
  else if (a.tur === "dosya") giris = `<input type="file" name="${a.ad}" accept="${esc(a.kabul || "image/*")}">` +
      (deger ? `<span class="ipucu">Yüklü: ${esc(deger)}</span>` : "");
  else giris = `<input name="${a.ad}" type="${a.tur === "sayi" ? "number" : a.tur === "tel" ? "tel" : "text"}" value="${d}"${z}
      ${a.tur === "sayi" ? `min="${a.min ?? 1}" step="1"` : ""} placeholder="${esc(a.ornek || "")}">`;
  return `<label class="${a.tur === "textarea" || a.genis ? "genis" : ""}">
    <span class="${a.zorunlu ? "zorunlu" : ""}">${esc(a.etiket)}</span>${giris}
    ${a.ipucu ? `<span class="ipucu">${esc(a.ipucu)}</span>` : ""}</label>`;
}

function formHtml(u, bilgiler = {}) {                     // alan grupları ayrı kartlarda
  const bolumler = [];
  for (const a of u.alanlar) {
    if (!bolumler.length || (a.grup && a.grup !== bolumler.at(-1).ad)) bolumler.push({ad: a.grup || "Bilgiler", h: ""});
    bolumler.at(-1).h += alanHtml(a, bilgiler[a.ad]);
  }
  return bolumler.map(b => `<section class="kart form-bolum"><h3>${esc(b.ad)}</h3><div class="alanlar">${b.h}</div></section>`).join("");
}

function formOku(form, u) {
  const b = {}, dosyalar = [];
  for (const a of u.alanlar) {
    const el = form.elements[a.ad];
    if (!el) continue;
    if (a.tur === "dosya") { if (el.files[0]) dosyalar.push([a.ad, el.files[0]]); continue; }
    b[a.ad] = el.value.trim();
  }
  return {b, dosyalar};
}

const okuBase64 = f => new Promise((ok, red) => { const r = new FileReader();
  r.onload = () => ok(r.result); r.onerror = red; r.readAsDataURL(f); });

async function dosyalariYukle(k, dosyalar) {
  for (const [alan, f] of dosyalar) await api(`musteri/${encodeURIComponent(k)}/dosya`, {alan, ad: f.name, veri: await okuBase64(f)});
}

function yeniSiparis(kod) {
  const u = URUNLER.find(x => x.kod === kod);
  if (!u) return anaSayfa();
  sayfa.innerHTML = iz(["Yeni sipariş", "#/"], [u.ad]) +
    baslik("Müşteri bilgileri", esc(u.aciklama), `<span class="cip koyu">${ikon(URUN_IKON[u.kod])}${esc(u.ad)}</span>`) + `
    <form id="form" class="yigin">${formHtml(u)}
      <div class="eylem-cubugu"><button class="vurgu" type="submit">${ikon(u.katalog_adet ? "katalog" : "kup")}
        ${u.katalog_adet ? `Kaydet ve ${u.katalog_adet} tasarımlık katalog üret` : "Kaydet ve 3MF üret"}</button>
        <a class="dugme ince" href="#/">Vazgeç</a><span class="soluk"><span class="zorunlu"></span> zorunlu alan</span></div></form>`;
  $("#form").onsubmit = async e => {
    e.preventDefault();
    const btn = e.submitter; btn.disabled = true;
    try {
      const {b, dosyalar} = formOku(e.target, u);
      const m = await api("musteri", {urun: kod, bilgiler: b});
      await dosyalariYukle(m.kimlik, dosyalar);
      await api(`musteri/${encodeURIComponent(m.kimlik)}/${u.katalog_adet ? "katalog" : "uret"}`, {});
      location.hash = "#/musteri/" + encodeURIComponent(m.kimlik);
    } catch (err) { bildir(err.message, true); btn.disabled = false; }
  };
}

// ------------------------------------------------------------------ bilgileri düzenle (sağdan çekmece)
function cekmeceKapat() { const c = $("#cekmece"); c.hidden = true; c.innerHTML = ""; }
addEventListener("keydown", e => { if (e.key === "Escape") cekmeceKapat(); });

function cekmeceAc(k, m, u) {
  const c = $("#cekmece");
  c.innerHTML = `<div class="cekmece">
    <div class="cekmece-bas"><div><p class="soluk kucuk">${esc(m.ad)} · ${esc(u.ad)}</p><h2>Bilgileri düzenle</h2></div>
      <button class="ince simge-dugme" id="cekmece-kapat" title="Kapat (Esc)">${ikon("kapat")}</button></div>
    <form id="duzen-form">${formHtml(u, m.bilgiler)}</form>
    <div class="cekmece-alt"><button class="vurgu" type="submit" form="duzen-form">${ikon("tik")}Kaydet</button>
      <button class="ince" id="cekmece-vazgec">Vazgeç</button>
      <span class="soluk kucuk" style="margin-left:auto;align-self:center">Sonraki katalog ve üretimde kullanılır.</span></div></div>`;
  c.hidden = false;
  c.onclick = e => { if (e.target === c) cekmeceKapat(); };
  $("#cekmece-kapat").onclick = $("#cekmece-vazgec").onclick = cekmeceKapat;
  $("#duzen-form").onsubmit = async e => {
    e.preventDefault();
    try {
      const {b, dosyalar} = formOku(e.target, u);
      await api(`musteri/${encodeURIComponent(k)}/bilgi`, {bilgiler: b});
      await dosyalariYukle(k, dosyalar);
      cekmeceKapat(); bildir("Bilgiler kaydedildi"); musteriSayfasi(k);
    } catch (err) { bildir(err.message, true); }
  };
}

// ------------------------------------------------------------------ müşteri sayfası
let SECILEN = {}, RENKSEC = {}, KATSEC = {}, ISTEK = {}, GECMIS = {};   // müşteri başına arayüz durumu
const RENK_ALANI = {govde: ["zemin", "Gövde"], metin: ["yazi_renk", "Yazı"], vurgu: ["renk", "Vurgu"]};

function adimlar(m, u, sec) {                             // Bilgiler → Katalog → Seçim → Baskı dosyaları
  const a = u.katalog_adet ? [["Bilgiler", true], ["Katalog", m.kataloglar.length > 0],
    ["Seçim", !!(m.secimler.length || sec)], ["Baskı dosyaları", m.ciktilar.length > 0]]
    : [["Bilgiler", true], ["Baskı dosyası", m.ciktilar.length > 0]];
  const simdi = a.findIndex(([, t]) => !t);
  return `<div class="adimlar">${a.map(([ad, t], i) => `<span class="adim ${t ? "tamam" : i === simdi ? "simdi" : ""}">
    <i>${t ? ikon("tik") : i + 1}</i>${ad}</span>`).join(`<span class="adim-cizgi"></span>`)}</div>`;
}

function claudeKarti(k, aktif) {
  const ust = `<div class="kart-baslik"><h2>${ikon("yildiz")}Özel istek</h2>
    ${DURUM.claude ? `<span class="cip yesil">Claude hazır</span>` : ""}</div>
    <p class="soluk kucuk" style="margin-bottom:12px">Algoritmanın yapamadığı bir şey mi var? ("logo daha büyük olsun",
      "arka yüze adres ekle") İstek bu müşterinin dosyalarıyla Claude'a gider; sonucu çıktılara eklenir.</p>`;
  if (DURUM.claude) return `<div class="kart">${ust}<textarea id="istek" placeholder="İsteği yazın…">${esc(ISTEK[k] || "")}</textarea>
    <div class="satir" style="margin-top:10px"><button id="claude" ${aktif ? "disabled" : ""}>${ikon("yildiz")}Claude'a ilet</button></div></div>`;
  return `<div class="kart">${ust}<div class="uyari kurulum"><b>Claude Code bu bilgisayarda bulunamadı.</b> Bu özellik komut
    satırındaki Claude Code ile çalışır; Claude'un sohbet uygulaması yetmez. Bir kez kurulur:
    <ol><li>Başlat menüsünden <b>PowerShell</b>'i açın, şunu yapıştırıp Enter'a basın:
      <code>irm https://claude.ai/install.ps1 | iex</code></li>
    <li>Bitince <b>yeni</b> bir PowerShell penceresi açıp <code>claude</code> yazın, hesabınızla bir kez giriş yapın,
      sonra pencereyi kapatın. (<code>claude</code> tanınmazsa: <code>&amp; "$env:USERPROFILE\\.local\\bin\\claude.exe"</code>)</li>
    <li>Burada <b>Yeniden dene</b>'ye basın.</li></ol>
    <button class="ince kucuk" id="claude-yokla">${ikon("yenile")}Yeniden dene</button></div></div>`;
}

async function musteriSayfasi(k, sessiz) {
  if (!sessiz) sayfa.innerHTML = yukleniyor();
  const m = await api("musteri/" + encodeURIComponent(k));
  const u = URUNLER.find(x => x.kod === m.urun);
  const aktif = m.isler.find(j => j.durum === "bekliyor" || j.durum === "calisiyor");
  const sonHata = [...m.isler].reverse().find(j => j.durum === "hata");
  const uretilen = new Set(m.secimler.map(s => s.kod));
  const kE = encodeURIComponent(k);
  if (!SECILEN[k]) SECILEN[k] = (m.secimler.at(-1) || {}).kod || "";
  const sec = SECILEN[k];
  const rs = RENKSEC[k] = RENKSEC[k] || {};
  const ks = KATSEC[k] && m.kataloglar.some(c => c.no === KATSEC[k]) ? KATSEC[k] : (m.kataloglar.at(-1) || {}).no;
  // "A07 olsun ama kırmızı": seçilen tasarım katalogdaki renkleriyle ya da burada seçilen renklerle üretilir
  const renkSec = Object.entries(RENK_ALANI).map(([rol, [alan, ad]]) => {
    const a = u.alanlar.find(x => x.ad === alan);
    return a ? `<label class="renksec">${ad}<select data-renk="${rol}"><option value="">katalogdaki</option>
      ${a.secenekler.filter(([v]) => v !== "otomatik").map(([v, t]) =>
        `<option value="${esc(v)}"${rs[rol] === v ? " selected" : ""}>${esc(t)}</option>`).join("")}</select></label>` : "";
  }).join("");

  const panel = c => `<div data-panel="${c.no}"${c.no === ks ? "" : " hidden"}>
    <div class="satir" style="margin-bottom:14px">${c.pdf ? `
      <a class="dugme ince kucuk" href="${dosyaUrl(k, c.pdf)}" target="_blank">${ikon("ac")}PDF'i aç</a>
      <a class="dugme ince kucuk" href="${dosyaUrl(k, c.pdf, 1)}">${ikon("indir")}PDF indir</a>` : ""}
      ${(c.sayfalar || []).map((y, j) => `<a class="dugme ince kucuk" href="${dosyaUrl(k, y)}" target="_blank">Sayfa ${j + 1}</a>`).join("")}
      <span class="soluk kucuk" style="margin-left:auto">${tarih(c.tarih)} · ${c.tasarimlar.length} tasarım</span></div>
    <div class="tasarimlar">${c.tasarimlar.map(t => `
      <div class="tasarim${t.kod === sec ? " secili" : ""}${uretilen.has(t.kod) ? " uretildi" : ""}" data-kod="${esc(t.kod)}">
        <span class="kod">${esc(t.kod)}</span><img loading="lazy" src="${dosyaUrl(k, t.onizleme)}" alt="">
        <p>${esc(t.ad || "")}</p></div>`).join("")}</div></div>`;
  const katalogKarti = `<div class="kart">
    <div class="kart-baslik"><h2>${ikon("katalog")}Katalog</h2>
      <button class="${m.kataloglar.length ? "ince" : "vurgu"}" id="katalog" ${aktif ? "disabled" : ""}>
        ${ikon(m.kataloglar.length ? "yenile" : "katalog")}${m.kataloglar.length ? "Yeni katalog (beğenmedi)" : "Katalog üret"}</button></div>
    ${m.kataloglar.length ? `
      ${m.kataloglar.length > 1 ? `<div class="katalog-ust"><div class="sekmeler">${[...m.kataloglar].reverse().map(c =>
        `<button data-katalog="${c.no}" class="${c.no === ks ? "etkin" : ""}">${c.no}. katalog</button>`).join("")}</div></div>` : ""}
      ${m.kataloglar.map(panel).join("")}
      <p class="soluk kucuk" style="margin-top:14px">Müşterinin beğendiği tasarıma tıklayın ya da kodunu aşağıya yazın. Yeni
        katalog öncekilerde gösterilenleri tekrar etmez.</p>`
    : `<div class="bos">${ikon("katalog")}<p>Henüz katalog yok. <b>Katalog üret</b> ile ${u.katalog_adet} tasarım hazırlanır.</p></div>`}</div>`;
  const ornekKod = ((m.kataloglar.at(-1) || {}).tasarimlar || [])[2]?.kod || "M03";
  const uretimCubugu = `<div class="uretim"><div class="ust-satir">
      <span class="secilen">Seçilen <b id="secilen" class="${sec ? "var" : ""}">${esc(sec || "—")}</b></span>
      <input id="kodgir" placeholder="Kod yaz (ör. ${esc(ornekKod)})">
      <button class="vurgu" id="uret" ${!sec || aktif ? "disabled" : ""}>${ikon("kup")}Baskı dosyalarını üret</button></div>
    ${renkSec ? `<div class="renkler"><span>Renkleri değiştir (isteğe bağlı):</span>${renkSec}</div>` : ""}</div>`;

  // en yeni üretim üstte; aynı üretimde eklentinin sırası (3MF önce)
  const ciktilar = m.ciktilar.map((c, i) => [c, i]).sort((a, b) => (b[0].tarih || "").localeCompare(a[0].tarih || "")
    || a[1] - b[1]).map(([c]) => `
    <div class="cikti">${c.tur === "resim" ? `<img src="${dosyaUrl(k, c.yol)}" alt="">` : `<span class="tur t-${esc(c.tur)}">${esc(c.tur)}</span>`}
      <div class="ad"><b title="${esc(c.yol)}">${esc(c.ad)}</b><span>${once(c.tarih)}</span></div>
      <div class="satir"><a class="dugme ince kucuk simge-dugme" href="${dosyaUrl(k, c.yol)}" target="_blank" title="Aç">${ikon("ac")}</a>
        <a class="dugme kucuk simge-dugme" href="${dosyaUrl(k, c.yol, 1)}" title="İndir">${ikon("indir")}</a></div></div>`).join("");
  const notlar = m.notlar.slice().reverse();
  const gosterilen = GECMIS[k] ? notlar : notlar.slice(0, 6);

  sayfa.innerHTML = iz(["Müşteriler", "#/musteriler"], [m.ad]) + `
    <header class="baslik"><div class="musteri-bas"><span class="avatar buyuk">${esc(basHarf(m.ad))}</span>
      <div><h1>${esc(m.ad)}</h1><div class="alt"><span class="cip koyu">${ikon(URUN_IKON[u.kod])}${esc(u.ad)}</span>
        <span class="soluk kucuk">${tarih(m.olusturma)} · ${esc(m.kimlik)}</span></div></div></div>
      <div class="satir"><button class="ince" id="klasor">${ikon("klasor")}Klasörü aç</button>
        <button class="ince" id="duzenle">${ikon("kalem")}Bilgileri düzenle</button>
        <button class="tehlike simge-dugme" id="sil" title="Sil (klasörü silinenler/ altına taşınır)">${ikon("cop")}</button></div></header>
    ${adimlar(m, u, sec)}
    <div class="musteri-izgara"><div class="yigin">
      ${aktif ? `<div class="kart ilerleme"><div class="satir ara"><div class="satir"><span class="donen"></span>
          <b>${esc(aktif.baslik)}</b></div><span class="yuzde">%${aktif.yuzde}</span></div>
        <div class="cubuk"><i style="width:${aktif.yuzde}%"></i></div><p class="soluk kucuk">${esc(aktif.mesaj)}</p>
        ${aktif.gunluk.length ? `<div class="gunluk">${esc(aktif.gunluk.slice(-8).join("\n"))}</div>` : ""}</div>` : ""}
      ${!aktif && sonHata && (!m.ciktilar.length || sonHata.bitti * 1000 > Date.parse(m.guncelleme)) ?
        `<div class="uyari hata-kutu"><b>Son iş hata verdi:</b> ${esc(sonHata.mesaj)}
         <div class="gunluk">${esc(sonHata.gunluk.slice(-15).join("\n"))}</div></div>` : ""}
      ${uyarilar(m)}
      ${u.katalog_adet ? `<div>${katalogKarti}${uretimCubugu}</div>` : `<div class="kart">
        <div class="kart-baslik"><h2>${ikon("kup")}Baskı dosyası</h2>
          <button class="vurgu" id="uret" ${aktif ? "disabled" : ""}>${ikon("kup")}${m.ciktilar.length ? "Yeniden üret" : "3MF üret"}</button></div>
        <p class="soluk kucuk">Bu üründe katalog yok: bilgiler girilince X2D 3MF'i doğrudan hazırlanır.</p></div>`}
    </div><div class="yigin">
      <div class="kart"><div class="kart-baslik"><h2>${ikon("indir")}Çıktılar</h2>
        ${m.ciktilar.length ? `<span class="cip">${m.ciktilar.length}</span>` : ""}</div>
        ${m.ciktilar.length ? `<div class="ciktilar">${ciktilar}</div>`
          : `<div class="bos" style="padding:18px">${ikon("kup")}<p class="kucuk">Baskı dosyaları üretilince burada görünür.</p></div>`}</div>
      ${claudeKarti(k, aktif)}
      <div class="kart"><div class="kart-baslik"><h2>${ikon("saat")}Geçmiş</h2></div>
        <ul class="notlar">${gosterilen.map(n => `<li class="${n.metin.startsWith("Uyarı") ? "uyari-not" : ""}">
          <time>${tarih(n.tarih)}</time>${esc(n.metin)}</li>`).join("")}</ul>
        ${notlar.length > 6 ? `<button class="ince kucuk" id="gecmis" style="margin-top:12px">
          ${GECMIS[k] ? "Daha az göster" : `Tümünü göster (${notlar.length})`}</button>` : ""}</div>
    </div></div>`;

  $("#klasor").onclick = () => api(`musteri/${kE}/klasor`, {}).catch(e => bildir(e.message, true));
  $("#duzenle").onclick = () => cekmeceAc(k, m, u);
  $("#sil").onclick = async () => {
    if (!confirm(`${m.ad} silinsin mi? (Klasörü veri klasöründe silinenler/ altına taşınır.)`)) return;
    try { await api(`musteri/${kE}/sil`, {}); bildir("Müşteri silindi"); location.hash = "#/musteriler"; }
    catch (e) { bildir(e.message, true); }
  };
  const sec_ = el => {
    SECILEN[k] = el.dataset.kod;
    $$(".tasarim").forEach(x => x.classList.toggle("secili", x === el));
    $("#secilen").textContent = el.dataset.kod; $("#secilen").classList.add("var");
    if (!aktif) $("#uret").disabled = false;
  };
  const katalogGoster = no => {
    KATSEC[k] = no;
    $$("[data-panel]").forEach(p => (p.hidden = +p.dataset.panel !== no));
    $$("[data-katalog]").forEach(b => b.classList.toggle("etkin", +b.dataset.katalog === no));
  };
  $$(".tasarim").forEach(el => el.onclick = () => sec_(el));
  $$("[data-katalog]").forEach(b => b.onclick = () => katalogGoster(+b.dataset.katalog));
  if ($("#kodgir")) $("#kodgir").oninput = e => {        // müşterinin söylediği kodu yazınca seçilir
    const kod = e.target.value.trim().toLocaleUpperCase("tr").replace(/\s/g, "");
    const el = $$(".tasarim").find(x => x.dataset.kod === kod);
    if (el) { katalogGoster(+el.closest("[data-panel]").dataset.panel); sec_(el); el.scrollIntoView({block: "center"}); }
  };
  const is_ = (yol, govde, mesaj) => api(`musteri/${kE}/${yol}`, govde).then(() => { bildir(mesaj); musteriSayfasi(k, true); })
    .catch(e => bildir(e.message, true));
  if ($("#katalog")) $("#katalog").onclick = () => is_("katalog", {}, "Katalog sıraya alındı");
  $$("[data-renk]").forEach(el => el.onchange = () => { rs[el.dataset.renk] = el.value; });
  $("#uret").onclick = () => is_("uret", {kod: SECILEN[k] || "", renkler: rs}, "Baskı dosyaları sıraya alındı");
  if ($("#istek")) $("#istek").oninput = e => { ISTEK[k] = e.target.value; };
  if ($("#claude")) $("#claude").onclick = () => is_("claude", {istek: $("#istek").value}, "Claude'a iletildi")
    .then(() => { ISTEK[k] = ""; });
  if ($("#claude-yokla")) $("#claude-yokla").onclick = async () => {
    DURUM = await api("durum").catch(() => DURUM);
    bildir(DURUM.claude ? "Claude Code bulundu" : "Claude Code hâlâ bulunamadı", !DURUM.claude);
    yanAlt(); musteriSayfasi(k, true);
  };
  if ($("#gecmis")) $("#gecmis").onclick = () => { GECMIS[k] = !GECMIS[k]; musteriSayfasi(k, true); };
  if (aktif) zamanlayici = setTimeout(() => location.hash.includes(kE) && musteriSayfasi(k, true), 1500);
}

function uyarilar(m) {
  // son işin (katalog ya da baskı dosyaları) uyarıları: son "…üretildi" notundan önceki ardışık "Uyarı" notları
  const n = m.notlar;
  let son = -1;
  for (let i = n.length - 1; i >= 0; i--) if (/üretildi/.test(n[i].metin)) { son = i; break; }
  if (son < 0) return "";
  const u = [];
  for (let i = son - 1; i >= 0 && n[i].metin.startsWith("Uyarı"); i--) u.unshift(n[i]);
  return u.length ? `<div class="uyari">${u.map(x => esc(x.metin.replace(/^Uyarı: /, "⚠ "))).join("<br>")}</div>` : "";
}

// ------------------------------------------------------------------ işler
const DURUM_AD = {bekliyor: "Sırada", calisiyor: "Çalışıyor", bitti: "Bitti", hata: "Hata"};

async function isler() {
  const [rows, kisiler] = await Promise.all([api("isler"), api("musteriler").catch(() => [])]);
  const ad = Object.fromEntries(kisiler.map(r => [r.kimlik, r.ad]));
  sayfa.innerHTML = baslik("İşler", "Bu oturumda sıraya alınan katalog ve üretim işleri. Ağır işler sırayla, tek tek çalışır.") +
    (rows.length ? `<div class="kart liste">${rows.map(j => `
      <a class="is-satir" href="#/musteri/${encodeURIComponent(j.kimlik)}">
        <span class="durum ${j.durum}">${DURUM_AD[j.durum] || esc(j.durum)}</span>
        <span><b>${esc(j.baslik)}</b> <span class="soluk kucuk">· ${esc(ad[j.kimlik] || j.kimlik)}</span><br>
          <span class="soluk kucuk">${esc(j.mesaj)}${j.durum === "calisiyor" ? ` · %${j.yuzde}` : ""}</span>
          ${j.durum === "calisiyor" ? `<div class="cubuk"><i style="width:${j.yuzde}%"></i></div>` : ""}</span>
        ${ikon("sag")}</a>`).join("")}</div>`
    : `<div class="kart bos">${ikon("isler")}<p>Bu oturumda iş yok. Katalog ya da baskı dosyası üretince burada görünür.</p></div>`);
  if (rows.some(j => j.durum === "calisiyor" || j.durum === "bekliyor")) zamanlayici = setTimeout(isler, 2000);
}

async function rozet() {
  try {
    const n = (await api("isler")).filter(j => j.durum === "calisiyor" || j.durum === "bekliyor").length;
    const r = $("#is-rozet"); r.hidden = !n; r.textContent = n;
  } catch (e) { /* sunucu kapalı */ }
  setTimeout(rozet, 3000);
}

git(); rozet();
