// BOYDE Atölye arayüzü: ürün seç → müşteri bilgileri → katalog (yenilenebilir) → seçilen kod → baskı dosyaları.
"use strict";
const $ = (s, el = document) => el.querySelector(s);
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}[c]));
const sayfa = $("#sayfa");
let URUNLER = [], zamanlayici = null;

async function api(yol, govde) {
  const r = await fetch("/api/" + yol, govde === undefined ? {} :
    {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(govde)});
  const v = await r.json();
  if (!r.ok) throw new Error(v.hata || r.statusText);
  return v;
}

function bildir(mesaj, hata) {
  const b = $("#bildirim");
  b.textContent = mesaj; b.className = "bildirim" + (hata ? " hata" : ""); b.hidden = false;
  clearTimeout(b._t); b._t = setTimeout(() => (b.hidden = true), hata ? 7000 : 3500);
}

const tarih = s => s ? new Date(s).toLocaleString("tr-TR", {dateStyle: "short", timeStyle: "short"}) : "";
const urunAdi = kod => (URUNLER.find(u => u.kod === kod) || {}).ad || kod;
const dosyaUrl = (k, yol, indir) => `/dosya/${encodeURIComponent(k)}/${yol.split("/").map(encodeURIComponent).join("/")}${indir ? "?indir=1" : ""}`;

// ------------------------------------------------------------------ yönlendirme
async function git() {
  clearTimeout(zamanlayici);
  const [, yol = "", arg = ""] = location.hash.split("/");
  document.querySelectorAll("nav a").forEach(a => a.classList.toggle("etkin",
    a.getAttribute("href") === "#/" + (yol === "yeni" ? "" : yol)));
  try {
    if (!URUNLER.length) {
      sayfa.innerHTML = `<p class="soluk">Yükleniyor… (ilk açılışta birkaç saniye sürer)</p>`;
      URUNLER = await api("urunler");
    }
    if (yol === "yeni") return yeniSiparis(decodeURIComponent(arg));
    if (yol === "musteri") return musteriSayfasi(decodeURIComponent(arg));
    if (yol === "musteriler") return musteriler();
    if (yol === "isler") return isler();
    return anaSayfa();
  } catch (e) {
    sayfa.innerHTML = `<div class="kart uyari">${esc(e.message)}</div>`;
  }
}
addEventListener("hashchange", git);

// ------------------------------------------------------------------ ana sayfa
async function anaSayfa() {
  const son = (await api("musteriler")).slice(0, 8);
  sayfa.innerHTML = `
    <p class="k">Yeni sipariş</p><h1>Hangi ürün?</h1>
    <div class="izgara bolum">${URUNLER.map(u => `
      <a class="kart urun" href="#/yeni/${u.kod}">
        <span class="simge">${esc(u.simge || "▣")}</span><h2>${esc(u.ad)}</h2>
        <p class="soluk">${esc(u.aciklama)}</p>
        <span class="etiket">${u.katalog_adet ? `${u.katalog_adet} örnekli katalog` : "Doğrudan 3MF"}</span>
      </a>`).join("")}</div>
    <div class="bolum"><div class="satir ara"><h2>Son müşteriler</h2><a href="#/musteriler">Hepsi →</a></div>
      ${tablo(son)}</div>`;
}

function tablo(rows) {
  if (!rows.length) return `<p class="soluk">Henüz müşteri yok.</p>`;
  return `<div class="kart" style="padding:6px 14px"><table><tr><th>Müşteri</th><th>Ürün</th><th>Katalog</th>
    <th>Seçim</th><th>Güncelleme</th></tr>${rows.map(r => `
    <tr class="tik" onclick="location.hash='#/musteri/${encodeURIComponent(r.kimlik)}'">
      <td><b>${esc(r.ad)}</b></td><td>${esc(urunAdi(r.urun))}</td><td>${r.katalog || "–"}</td>
      <td>${esc(r.secim || "–")}</td><td>${tarih(r.guncelleme)}</td></tr>`).join("")}</table></div>`;
}

async function musteriler() {
  const rows = await api("musteriler");
  sayfa.innerHTML = `<p class="k">Kayıtlar</p><h1>Müşteriler</h1>
    <div class="bolum"><input id="ara" placeholder="Ad ya da ürün ara…" style="max-width:360px"></div>
    <div class="bolum" id="liste">${tablo(rows)}</div>`;
  $("#ara").oninput = e => {
    const q = e.target.value.toLocaleLowerCase("tr");
    $("#liste").innerHTML = tablo(rows.filter(r => (r.ad + " " + urunAdi(r.urun)).toLocaleLowerCase("tr").includes(q)));
  };
}

// ------------------------------------------------------------------ form
function alanHtml(a, deger) {
  const d = esc(deger ?? a.varsayilan ?? "");
  const z = a.zorunlu ? " required" : "";
  let giris;
  if (a.tur === "textarea") giris = `<textarea name="${a.ad}"${z}>${d}</textarea>`;
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

function formHtml(u, bilgiler = {}) {
  let grup = null, h = "";
  for (const a of u.alanlar) {
    if (a.grup && a.grup !== grup) { grup = a.grup; h += `<h3 class="grup-baslik">${esc(grup)}</h3>`; }
    h += alanHtml(a, bilgiler[a.ad]);
  }
  return `<div class="alanlar">${h}</div>`;
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
  sayfa.innerHTML = `<p class="k">Yeni sipariş · ${esc(u.ad)}</p><h1>Müşteri bilgileri</h1>
    <p class="soluk">${esc(u.aciklama)}</p>
    <form class="kart bolum" id="form">${formHtml(u)}
      <div class="satir bolum"><button class="vurgu" type="submit">${u.katalog_adet ? "Kaydet ve katalog üret" : "Kaydet ve 3MF üret"}</button>
      <a class="dugme ince" href="#/">Vazgeç</a></div></form>`;
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

// ------------------------------------------------------------------ müşteri sayfası
let SECILEN = {};
let RENKSEC = {};                                         // üretimde renk değişikliği (müşteri başına)
const RENK_ALANI = {govde: ["zemin", "Gövde"], metin: ["yazi_renk", "Yazı"], vurgu: ["renk", "Vurgu"]};

async function musteriSayfasi(k, sessiz) {
  const m = await api("musteri/" + encodeURIComponent(k));
  const u = URUNLER.find(x => x.kod === m.urun);
  const aktif = m.isler.find(j => j.durum === "bekliyor" || j.durum === "calisiyor");
  const sonHata = [...m.isler].reverse().find(j => j.durum === "hata");
  const uretilen = new Set(m.secimler.map(s => s.kod));
  const kE = encodeURIComponent(k);
  if (!SECILEN[k]) SECILEN[k] = (m.secimler.at(-1) || {}).kod || "";
  const sec = SECILEN[k];
  const rs = RENKSEC[k] = RENKSEC[k] || {};
  // "A07 olsun ama kırmızı": seçilen tasarım katalogdaki renkleriyle ya da burada seçilen renklerle üretilir
  const renkSec = Object.entries(RENK_ALANI).map(([rol, [alan, ad]]) => {
    const a = u.alanlar.find(x => x.ad === alan);
    return a ? `<label class="renksec">${ad}<select data-renk="${rol}"><option value="">katalogdaki</option>
      ${a.secenekler.filter(([v]) => v !== "otomatik").map(([v, t]) =>
        `<option value="${esc(v)}"${rs[rol] === v ? " selected" : ""}>${esc(t)}</option>`).join("")}</select></label>` : "";
  }).join("");

  const kataloglar = [...m.kataloglar].reverse().map((c, i) => `
    <details class="bolum katalog"${i === 0 ? " open" : ""}><summary class="satir ara"><h3>${c.no}. katalog
      <span class="soluk">· ${tarih(c.tarih)} · ${c.tasarimlar[0] ? esc(c.tasarimlar[0].kod) + "–" + esc(c.tasarimlar.at(-1).kod) : ""}</span></h3>
      <div class="satir">${c.pdf ? `<a class="dugme ince" href="${dosyaUrl(k, c.pdf)}" target="_blank">PDF'i aç</a>
        <a class="dugme ince" href="${dosyaUrl(k, c.pdf, 1)}">PDF indir</a>` : ""}
        ${(c.sayfalar || []).map((y, j) => `<a class="dugme ince" href="${dosyaUrl(k, y)}" target="_blank">Sayfa ${j + 1}</a>`).join("")}</div></summary>
      <div class="tasarimlar bolum">${c.tasarimlar.map(t => `
        <div class="tasarim${t.kod === sec ? " secili" : ""}${uretilen.has(t.kod) ? " uretildi" : ""}" data-kod="${esc(t.kod)}">
          <span class="kod">${esc(t.kod)}</span><img loading="lazy" src="${dosyaUrl(k, t.onizleme)}" alt="">
          <p>${esc(t.ad || "")}</p></div>`).join("")}</div></details>`).join("");

  // en yeni üretim üstte; aynı üretimde eklentinin sırası (3MF önce)
  const ciktilar = m.ciktilar.map((c, i) => [c, i]).sort((a, b) => (b[0].tarih || "").localeCompare(a[0].tarih || "")
    || a[1] - b[1]).map(([c]) => `
    <div class="cikti">${c.tur === "resim" ? `<img src="${dosyaUrl(k, c.yol)}" alt="">` : `<span class="tur">${esc(c.tur)}</span>`}
      <div class="ad"><b>${esc(c.ad)}</b><br><span class="soluk">${esc(c.yol)} · ${tarih(c.tarih)}</span></div>
      <a class="dugme ince" href="${dosyaUrl(k, c.yol)}" target="_blank">Aç</a>
      <a class="dugme" href="${dosyaUrl(k, c.yol, 1)}">İndir</a></div>`).join("");

  sayfa.innerHTML = `
    <div class="satir ara"><div><p class="k">${esc(u.ad)}</p><h1>${esc(m.ad)}</h1>
      <p class="soluk">${esc(m.kimlik)} · ${tarih(m.olusturma)}</p></div>
      <div class="satir"><button class="ince" id="klasor">Klasörü aç</button>
        <button class="ince" id="duzenle">Bilgileri düzenle</button>
        <button class="ince" id="sil" title="Klasörü silinenler/ altına taşınır">Sil</button></div></div>
    <form class="kart bolum" id="form" hidden>${formHtml(u, m.bilgiler)}
      <div class="satir bolum"><button type="submit">Kaydet</button></div></form>
    ${aktif ? `<div class="kart bolum ilerleme"><div class="satir ara"><b>${esc(aktif.baslik)}</b><span>%${aktif.yuzde}</span></div>
      <div class="cubuk"><i style="width:${aktif.yuzde}%"></i></div><p class="soluk">${esc(aktif.mesaj)}</p>
      ${aktif.gunluk.length ? `<div class="gunluk">${esc(aktif.gunluk.slice(-12).join("\n"))}</div>` : ""}</div>` : ""}
    ${!aktif && sonHata && (!m.ciktilar.length || sonHata.bitti * 1000 > Date.parse(m.guncelleme)) ?
      `<div class="kart bolum uyari"><b>Son iş hata verdi:</b> ${esc(sonHata.mesaj)}
       <div class="gunluk">${esc(sonHata.gunluk.slice(-15).join("\n"))}</div></div>` : ""}
    ${uyarilar(m)}
    <div class="iki bolum"><div>
      ${m.ciktilar.length ? `<div class="kart" style="margin-bottom:20px"><h2>Çıktılar</h2><div class="ciktilar bolum">${ciktilar}</div></div>` : ""}
      ${u.katalog_adet ? `<div class="kart"><div class="satir ara"><h2>Katalog</h2>
          <button class="${m.kataloglar.length ? "ince" : "vurgu"}" id="katalog" ${aktif ? "disabled" : ""}>
            ${m.kataloglar.length ? "Yeni katalog üret (beğenmedi)" : "Katalog üret"}</button></div>
          <p class="soluk">Her katalogda ${u.katalog_adet} örnek. Yeni katalog öncekilerde gösterilenleri tekrar etmez.
            Müşterinin beğendiği koda tıklayın, sonra baskı dosyalarını üretin.</p>
          ${kataloglar || ""}</div>
        <div class="kart bolum" style="position:sticky;bottom:12px"><div class="satir ara">
          <div class="satir"><b>Seçilen: <span id="secilen">${esc(sec || "—")}</span></b>
            <input id="kodgir" placeholder="Kodu yaz (ör. M03)" style="width:170px"></div>
          <button class="vurgu" id="uret" ${!sec || aktif ? "disabled" : ""}>Seçilen tasarımın baskı dosyalarını üret</button></div>
          ${renkSec ? `<div class="satir renkler"><span class="soluk">Renkleri değiştir (isteğe bağlı):</span>${renkSec}</div>` : ""}
        </div>`
      : `<div class="kart satir ara"><h2>Baskı dosyası</h2>
          <button class="vurgu" id="uret" ${aktif ? "disabled" : ""}>${m.ciktilar.length ? "Yeniden üret" : "3MF üret"}</button></div>`}
    </div><div>
      <div class="kart"><h2>Özel istek (Claude)</h2>
        <p class="soluk">Algoritmanın yapamadığı bir şey mi var? ("logo daha büyük olsun", "arka yüze adres ekle")
          Bu müşterinin dosyalarıyla birlikte Claude'a iletilir; sonucu çıktılara eklenir.</p>
        <textarea id="istek" placeholder="İsteği yazın…"></textarea>
        <div class="satir" style="margin-top:10px"><button id="claude" ${aktif ? "disabled" : ""}>Claude'a ilet</button></div></div>
      <div class="kart bolum"><h2>Geçmiş</h2><ul class="notlar bolum">${m.notlar.slice().reverse().map(n =>
        `<li><time>${tarih(n.tarih)}</time>${esc(n.metin)}</li>`).join("")}</ul></div>
    </div></div>`;

  $("#klasor").onclick = () => api(`musteri/${kE}/klasor`, {}).catch(e => bildir(e.message, true));
  $("#duzenle").onclick = () => { $("#form").hidden = !$("#form").hidden; };
  $("#sil").onclick = async () => {
    if (!confirm(`${m.ad} silinsin mi? (Klasörü veri klasöründe silinenler/ altına taşınır.)`)) return;
    try { await api(`musteri/${kE}/sil`, {}); bildir("Müşteri silindi"); location.hash = "#/musteriler"; }
    catch (e) { bildir(e.message, true); }
  };
  $("#form").onsubmit = async e => {
    e.preventDefault();
    try {
      const {b, dosyalar} = formOku(e.target, u);
      await api(`musteri/${kE}/bilgi`, {bilgiler: b});
      await dosyalariYukle(k, dosyalar);
      bildir("Bilgiler kaydedildi"); musteriSayfasi(k);
    } catch (err) { bildir(err.message, true); }
  };
  const sec_ = el => {
    SECILEN[k] = el.dataset.kod;
    document.querySelectorAll(".tasarim").forEach(x => x.classList.toggle("secili", x === el));
    $("#secilen").textContent = el.dataset.kod;
    if (!aktif) $("#uret").disabled = false;
  };
  document.querySelectorAll(".tasarim").forEach(el => el.onclick = () => sec_(el));
  if ($("#kodgir")) $("#kodgir").oninput = e => {        // müşterinin söylediği kodu yazınca seçilir
    const kod = e.target.value.trim().toLocaleUpperCase("tr").replace(/\s/g, "");
    const el = [...document.querySelectorAll(".tasarim")].find(x => x.dataset.kod === kod);
    if (el) { sec_(el); const d = el.closest("details"); if (d) d.open = true; el.scrollIntoView({block: "center"}); }
  };
  const is_ = (yol, govde, mesaj) => api(`musteri/${kE}/${yol}`, govde).then(() => { bildir(mesaj); musteriSayfasi(k); })
    .catch(e => bildir(e.message, true));
  if ($("#katalog")) $("#katalog").onclick = () => is_("katalog", {}, "Katalog sıraya alındı");
  document.querySelectorAll("[data-renk]").forEach(el => el.onchange = () => { rs[el.dataset.renk] = el.value; });
  $("#uret").onclick = () => is_("uret", {kod: SECILEN[k] || "", renkler: rs}, "Baskı dosyaları sıraya alındı");
  $("#claude").onclick = () => is_("claude", {istek: $("#istek").value}, "Claude'a iletildi");
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
  return u.length ? `<div class="bolum uyari">${u.map(x => esc(x.metin.replace(/^Uyarı: /, "⚠ "))).join("<br>")}</div>` : "";
}

// ------------------------------------------------------------------ işler
async function isler() {
  const rows = await api("isler");
  sayfa.innerHTML = `<p class="k">Arka planda</p><h1>İşler</h1><div class="kart bolum" style="padding:6px 14px">
    ${rows.length ? `<table><tr><th>#</th><th>Müşteri</th><th>İş</th><th>Durum</th><th>Mesaj</th></tr>${rows.map(j => `
      <tr class="tik" onclick="location.hash='#/musteri/${encodeURIComponent(j.kimlik)}'"><td>${j.no}</td>
      <td>${esc(j.kimlik)}</td><td>${esc(j.baslik)}</td><td><span class="durum ${j.durum}">${j.durum}</span></td>
      <td>${esc(j.mesaj)} ${j.durum === "calisiyor" ? `(%${j.yuzde})` : ""}</td></tr>`).join("")}</table>`
      : `<p class="soluk">Bu oturumda iş yok.</p>`}</div>`;
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
