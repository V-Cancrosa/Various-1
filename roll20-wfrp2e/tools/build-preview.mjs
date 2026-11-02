// Składa jednoplikowy podgląd karty (sheet.html + sheet.css + roll20-mock.js) z przykładową postacią.
// Użycie: node tools/build-preview.mjs [plik-wyjściowy]   (domyślnie: preview.html obok karty)
import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const dir = join(dirname(fileURLToPath(import.meta.url)), '..');
const out = process.argv[2] || join(dir, 'preview.html');
const sheet = readFileSync(join(dir, 'sheet.html'), 'utf8');
const css = readFileSync(join(dir, 'sheet.css'), 'utf8');
const mock = readFileSync(join(dir, 'tools', 'roll20-mock.js'), 'utf8');

const rt = sheet.match(/<rolltemplate class="sheet-rolltemplate-wfrp2e">([\s\S]*?)<\/rolltemplate>/)[1];
const worker = sheet.match(/<script type="text\/worker">([\s\S]*?)<\/script>/)[1];
const body = sheet
  .replace(/<rolltemplate[\s\S]*?<\/rolltemplate>/, '')
  .replace(/<script type="text\/worker">[\s\S]*?<\/script>/, '');

// Ciemne zmienne z .sheet-darkmode -> motyw ciemny podglądu.
const dark = css.match(/\.sheet-darkmode \.charsheet \{([\s\S]*?)\}/)[1];
const sheetCss = css.replace(/@import url\('[^']+'\);/, '');
const fontImport = css.match(/@import url\('([^']+)'\);/)[1];

const preset = {
  attrs: {
    character_name: 'Ottilia Brenner', rasa: 'Człowiek', profesja: 'Czeladnik czarodzieja',
    profesje_poprz: 'Uczeń czarodzieja, Najemniczka', gracz: 'Przykład', wiek: '27', plec: 'Kobieta',
    oczy: 'Szare', wlosy: 'Kasztanowe', znak: 'Mammit Mądry', wzrost: '5 stóp 7 cali', waga: '130 funtów',
    rodzenstwo: '2', urodzenie: 'Altdorf', znaki: 'Blizna po oparzeniu na lewej dłoni',
    ww_pocz: 31, us_pocz: 33, k_pocz: 29, odp_pocz: 34, zr_pocz: 37, int_pocz: 41, sw_pocz: 39, ogd_pocz: 30,
    ww_schemat: 5, us_schemat: 5, k_schemat: 0, odp_schemat: 5, zr_schemat: 10, int_schemat: 25, sw_schemat: 25, ogd_schemat: 15,
    ww_rozw: 5, int_rozw: 15, sw_rozw: 15, zr_rozw: 5, ogd_rozw: 5, k_rozw: 5,
    a_pocz: 1, zyw_pocz: 12, sz_pocz: 4, mag_pocz: 1, po_pocz: 2, pp_pocz: 2,
    zyw_schemat: 3, mag_schemat: 2, zyw_rozw: 2, mag_rozw: 1,
    zyw_akt: 11, ps_akt: 2, mod_staly: 0, pytaj: '1',
    um_spostrzegawczosc_poz: 10, um_przeszukiwanie_poz: 0, um_plotkowanie_poz: 0, um_mocnaglowa_poz: 0, um_wycena_poz: 0,
    pz_korpus: 1, pz_reka_p: 1, pz_reka_l: 1, pz_glowa: 0,
    pancerz_opis: 'Skórzana kurta (korpus, ręce)',
    krytyki: '',
    tradycja: 'Tradycja Ognia (Kolegium Jasności)', magia_prosta: 'Magia prosta (tajemna)',
    zk: 4, szylingi: 13, pensy: 7, pd_akt: 150, pd_wydane: 700,
    notatki: 'Wydalona z Kolegium Jasności za „nadmierny entuzjazm wobec ognia”. Dług u pasera Gerharda: 15 zk.',
  },
  rows: {
    umiej: [
      { nazwa: 'Splatanie magii', cecha: 'sw', poz: 0, mod: 0 },
      { nazwa: 'Czytanie i pisanie', cecha: 'int', poz: 0, mod: 0 },
      { nazwa: 'Język tajemny (magiczny)', cecha: 'int', poz: 10, mod: 0 },
      { nazwa: 'Wykrywanie magii', cecha: 'sw', poz: 0, mod: 0 },
    ],
    zdol: [
      { nazwa: 'Magia prosta (tajemna)', opis: 'Zna zaklęcia magii prostej tajemnej.' },
      { nazwa: 'Tradycja magiczna (Ogień)', opis: 'Zaklęcia ognia; po rzuceniu każdego zaklęcia ogień buzuje wokół czarodziejki.' },
      { nazwa: 'Bystry wzrok', opis: '+20% do testów Spostrzegawczości opartych na wzroku.' },
    ],
    bron: [
      { nazwa: 'Kostur', rodzaj: 'wr', plus_s: '1', obr: 0, cechy: 'Ogłuszająca, Parujący' },
      { nazwa: 'Sztylet', rodzaj: 'wr', plus_s: '1', obr: -3, cechy: '—' },
      { nazwa: 'Proca', rodzaj: 'dyst', plus_s: '0', obr: 3, zasieg: '16/32', przeladowanie: 'Pół akcji', cechy: '—' },
    ],
    czary: [
      { nazwa: 'Ognisty pocisk', pm: 6, czas: 'Pół akcji', skladnik: 'Węgielek', premia: 1, opis: 'Pocisk o Sile 4 trafia cel w zasięgu 24 yardów.' },
      { nazwa: 'Płonące serce', pm: 11, czas: 'Pełna akcja', skladnik: 'Pióro feniksa', premia: 2, opis: 'Sojusznicy w promieniu 12 yardów stają się odporni na Strach.' },
    ],
    ekw: [
      { nazwa: 'Kostur', ilosc: 1, obc: 50 },
      { nazwa: 'Skórzana kurta', ilosc: 1, obc: 40 },
      { nazwa: 'Księga zaklęć', ilosc: 1, obc: 20 },
      { nazwa: 'Racje żywnościowe (dzień)', ilosc: 3, obc: 2 },
      { nazwa: 'Węgielki (składnik)', ilosc: 6, obc: 0 },
    ],
    obled: [],
  },
};

const html = `<title>Karta WFRP 2e</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="${fontImport}">
<style>
/* Podgląd: karta po lewej, czat Roll20 po prawej; na telefonie jedno pod drugim. */
:root {
  --tlo: #cfcbc0;
  --tlo-czat: #dcd8ce;
  --tekst: #1f1c19;
  --tekst-2: #5b554c;
  --obramowanie: #a9a292;
  --akcent: #7d1b1b;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) { --tlo: #0f1011; --tlo-czat: #141517; --tekst: #e4dfd4; --tekst-2: #a49d90; --obramowanie: #333336; --akcent: #d4564b; color-scheme: dark; }
  :root:not([data-theme="light"]) .charsheet {${dark}}
}
:root[data-theme="dark"] { --tlo: #0f1011; --tlo-czat: #141517; --tekst: #e4dfd4; --tekst-2: #a49d90; --obramowanie: #333336; --akcent: #d4564b; color-scheme: dark; }
:root[data-theme="dark"] .charsheet {${dark}}
body { background: var(--tlo); color: var(--tekst); font-family: 'Alegreya Sans', 'Segoe UI', Helvetica, Arial, sans-serif; }
.r20-strona { display: grid; grid-template-columns: minmax(0, 1fr) 300px; gap: 16px; padding-block: 16px; padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); max-width: 1260px; margin: 0 auto; align-items: start; }
.r20-pasek { grid-column: 1 / -1; display: flex; flex-wrap: wrap; align-items: baseline; gap: 4px 14px; }
.r20-pasek h1 { font-family: 'Pirata One', Georgia, serif; font-weight: 400; font-size: 30px; margin: 0; color: var(--akcent); text-wrap: balance; }
.r20-pasek p { margin: 0; color: var(--tekst-2); font-size: 13px; max-width: 70ch; }
.r20-okno { min-width: 0; border: 1px solid var(--obramowanie); box-shadow: 0 2px 10px rgb(0 0 0 / 0.18); }
.r20-czat { position: sticky; top: max(12px, env(safe-area-inset-top, 0px)); display: flex; flex-direction: column; border: 1px solid var(--obramowanie); background: var(--tlo-czat); height: min(78vh, 760px); min-width: 0; }
.r20-czat h2 { margin: 0; padding: 8px 10px; font-size: 11px; text-transform: uppercase; letter-spacing: 0.1em; color: var(--tekst-2); border-bottom: 1px solid var(--obramowanie); }
.r20-wiadomosci { flex: 1; overflow-y: auto; padding: 10px 10px 10px 17px; display: flex; flex-direction: column; gap: 10px; }
.r20-wiad .sheet-rt { box-shadow: 0 1px 3px rgb(0 0 0 / 0.2); }
.r20-wiad a[data-akcja] { cursor: pointer; text-decoration: none; }
.r20-pusto { color: var(--tekst-2); font-size: 12px; font-style: italic; }
.inlinerollresult { cursor: help; }
#r20-pytanie { position: fixed; inset: 0; background: rgb(0 0 0 / 0.45); display: grid; place-items: center; z-index: 20; padding: 16px; }
#r20-pytanie[hidden] { display: none; }
.r20-pyt { background: var(--tlo-czat); color: var(--tekst); border: 1px solid var(--obramowanie); padding: 14px; width: min(340px, 100%); display: grid; gap: 10px; }
.r20-pyt-label { font-weight: 700; }
.r20-pyt select, .r20-pyt input { width: 100%; padding: 6px; font: inherit; background: var(--tlo); color: var(--tekst); border: 1px solid var(--obramowanie); }
.r20-pyt-btns { display: flex; justify-content: flex-end; gap: 8px; }
.r20-pyt button { font: inherit; padding: 5px 12px; cursor: pointer; border: 1px solid var(--obramowanie); background: transparent; color: var(--tekst); }
.r20-pyt button.r20-pyt-ok { background: var(--akcent); color: #fff; border-color: var(--akcent); }
/* Imitacja kontrolek sekcji powtarzalnych Roll20 */
.charsheet .repitem { position: relative; }
.charsheet .itemcontrol { display: none; position: absolute; inset: 0; background: rgb(125 27 27 / 0.1); z-index: 2; justify-content: flex-end; align-items: center; padding-right: 4px; }
.charsheet .editmode .itemcontrol { display: flex; }
.charsheet .repcontrol_del { background: var(--akcent); color: #fff; border: none; padding: 2px 8px; cursor: pointer; font-size: 11px; }
.charsheet .repcontrol_del::before { content: 'Usuń'; }
.charsheet .repcontrol_del { font-size: 0; }
.charsheet .repcontrol_del::before { font-size: 11px; }
.charsheet .repcontrol { display: flex; justify-content: flex-end; gap: 6px; }
.charsheet .repcontrol_add, .charsheet .repcontrol_edit { cursor: pointer; padding: 2px 8px; font-size: 11px; }
@media (max-width: 900px) {
  .r20-strona { grid-template-columns: minmax(0, 1fr); }
  .r20-czat { position: static; height: 420px; }
}
${sheetCss}
</style>

<div class="r20-strona">
  <div class="r20-pasek">
    <h1>Warhammer Fantasy 2e: karta Roll20</h1>
    <p>Podgląd z symulacją Roll20: sheet workery, zapytania o trudność i szablon rzutu działają tak jak w grze. Kości są losowane w przeglądarce, a dane postaci to przykład. Zmień cechę, a karta przeliczy umiejętności, pancerz i ruch.</p>
  </div>
  <div class="r20-okno"><div class="charsheet" id="karta">${body}</div></div>
  <aside class="r20-czat" aria-label="Czat">
    <h2>Czat</h2>
    <div class="r20-wiadomosci" id="czat"><p class="r20-pusto">Wyniki rzutów pojawią się tutaj. Kliknij „k100” przy cesze, „Atak” przy broni albo „Rzuć” przy zaklęciu.</p></div>
  </aside>
</div>

<div id="r20-pytanie" hidden role="dialog" aria-modal="true">
  <div class="r20-pyt">
    <div class="r20-pyt-label"></div>
    <div class="r20-pyt-pole"></div>
    <div class="r20-pyt-btns"><button type="button" class="r20-pyt-anuluj">Anuluj</button><button type="button" class="r20-pyt-ok">Rzuć</button></div>
  </div>
</div>

<script>
${mock}
</script>
<script>
Roll20Mock.init({
  sheetRoot: document.getElementById('karta'),
  chatEl: document.getElementById('czat'),
  rolltemplate: ${JSON.stringify(rt)},
  worker: ${JSON.stringify(worker)},
  preset: ${JSON.stringify(preset)},
});
</script>
`;
writeFileSync(out, html);
console.log(`Zapisano ${out} (${html.length} B)`);
