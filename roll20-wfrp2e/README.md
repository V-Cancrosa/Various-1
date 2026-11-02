# Karta postaci WFRP 2e dla Roll20 (PL)

Karta do **Warhammer Fantasy Roleplay, 2. edycja** z polskim nazewnictwem. Pliki: `sheet.html` (karta, szablon
rzutu i sheet worker) oraz `sheet.css`.

## Instalacja w Roll20
Własne karty wymagają konta **Pro** u twórcy gry.

1. Wejdź na stronę gry i otwórz *Settings → Game Settings*.
2. W polu *Character Sheet Template* wybierz **Custom**.
3. Wklej zawartość `sheet.html` do zakładki **HTML Layout**, a `sheet.css` do **CSS Styling**.
4. **Odznacz „Legacy Sanitization”.** Karta używa trybu CSE (w `sheet.json`: `"legacy": false`).
   W trybie legacy część efektów (np. `:is()`, `mask`, `color-mix()`) może zostać wycięta.
5. Kliknij **Save Changes** i otwórz grę.

Do szybkiego testowania zmian użyj Roll20 **Sheet Sandbox**: zmiany widać bez przeładowania gry.

## Co jest na karcie
| Zakładka | Zawartość |
|---|---|
| Nagłówek | Imię, rasa, profesje, Żywotność i Punkty Szczęścia (aktualne / maks.), Punkty Obłędu, przycisk inicjatywy (k10 + Zr do trackera), przełącznik „Pytaj o trudność testu” i modyfikator stały |
| Cechy i umiejętności | Profil główny i drugorzędny (początkowa, schemat rozwoju, rozwinięcia, modyfikator, aktualna), 20 umiejętności podstawowych, umiejętności zaawansowane, zdolności |
| Walka | Broń (wręcz / dystansowa, +S, obrażenia, zasięg, przeładowanie, cechy oręża), pancerz na 6 lokacji z Wt, trafienia krytyczne, ruch / szarża / bieg |
| Magia | Magia (liczba k10), tradycja, zaklęcia z poziomem mocy, składnikiem i premią |
| Ekwipunek | Pieniądze (zk / s / p, suma w pensach), przedmioty z obciążeniem i udźwigiem K × 10 |
| Bohater | Opis, Punkty Doświadczenia, choroby psychiczne, notatki |

## Karta reaguje na stan postaci
Worker ustawia ukryte flagi (`stan_ran`, `stan_obled`, `zyw_proc`, `obc_proc`, `ps_flag`, `pp_flag`, `wiatr`),
a CSS zmienia wygląd selektorem `[value="…"] ~ …`. Nie ma tu żadnego JS w DOM, bo Roll20 na to nie pozwala.

| Stan | Efekt |
|---|---|
| Żywotność ≤ 3 (ciężko ranny) | rozbryzgi krwi w rogach, czerwona Żywotność, dopisek „ciężko ranny” |
| Żywotność 0 | pulsująca czerwona winieta w rytmie serca, migająca kropka na zakładce Walka |
| Punkty Obłędu 3+ / 6+ | fioletowe przebarwienia pergaminu; przy 6+ „oddychające” plamy i rozszczepione, drgające nagłówki |
| Przeciążenie (obciążenie > K × 10) | pasek obciążenia zakuty w przesuwający się łańcuch |
| Punkty Szczęścia | świece: tyle stoi, ile masz PP, a pali się tyle, ile zostało PS. Kliknięcie świecy zapala lub gasi |
| Wiatr magii | kolor kręgu runicznego, poświaty i przycisków w zakładce Magia (8 kolegiów) |
| Rasa | pieczęć lakowa w nagłówku: kolor wosku, wstęga i znak |

Pozostałe ozdobniki: pergamin i ramy z samych gradientów (bez obrazków), żelazne narożniki z nitami, kości k100
w kształcie ścianki k10, skórzane zakładki z animacją kartkowania. Szablon rzutu ma pieczęć wyniku, wstrząs
przy Furii Ulryka i mieniący się pasek przy Przekleństwie Tzeentcha. Przy `prefers-reduced-motion` ruch jest
wyłączony.

## Dopisek do rzutu (⚙)
Przy każdej broni i zaklęciu jest zębatka ⚙. Rozwija panel samym CSS-em (checkbox + `~`). W panelu wpisujesz
dopisek, który karta dokleja **na końcu** rzutu bez zmian. To wykorzystuje znaną sztuczkę z forum Roll20 („Overwriting
template fields in macros”): gdy pole szablonu powtarza się w rzucie, wygrywa ostatnie. Przykłady:

- `{{obr=[[2d10+3]]}}` podmienia rzut obrażeń, na przykład dla broni z homebrew.
- `{{info=Cel płonie}}` dopisuje notkę do wiadomości.
- `{{opis=…}}` podmienia opis zaklęcia w czacie.

Furia Ulryka nadal patrzy na pierwszą kość z pola `obr`, a Przekleństwo Tzeentcha na kości z pola `rzut`.

Pozostały tekst gracza (nazwy, cechy oręża, opisy, składniki) karta czyści z `{ } [ ] |`, zanim trafi do rzutu.
Dlatego nazwa broni typu `Sztylet}} {{sukces=[[1]]` nie nadpisze wyniku testu, tylko wyświetli się jako tekst.

## Zasady liczone automatycznie
- **Cecha aktualna** = początkowa + rozwinięcia + modyfikator. **S** = K ÷ 10, **Wt** = Odp ÷ 10 (w dół).
- Pole rozwinięć świeci na czerwono, gdy przekracza schemat rozwoju obecnej profesji.
- **Umiejętności**: nieznana podstawowa to ½ cechy, nabyta to pełna cecha, do tego +10% lub +20%.
- **Test**: k100 ≤ cel to sukces. Każde pełne 10 punktów różnicy to stopień sukcesu lub porażki.
  Trudność (od −30 do +30) wybierasz w okienku, a modyfikator stały dodaje się zawsze.
- **Atak**: test WW lub US. Przy trafieniu lokacja wynika z odwróconych cyfr rzutu (37 → 73 → korpus).
  W wiadomości jest przycisk „Rzuć obrażenia”.
- **Obrażenia**: k10 + S (jeśli zaznaczone +S) + modyfikator broni. Naturalne 10 to **Furia Ulryka**: karta sama
  rzuca test potwierdzający, a po sukcesie dorzuca k10, dopóki wypadają kolejne dziesiątki.
- **Zaklęcia**: Mag × k10 + premia za składnik + modyfikator kontra poziom mocy. Dublet, triplet lub kareta na
  kościach oznacza **Przekleństwo Tzeentcha** (pomniejszy, większy lub katastrofalny przejaw Chaosu).

Rzuty z logiką korzystają z *custom roll parsing* (`startRoll` / `finishRoll`), więc działają bez skryptów API.

## Podgląd poza Roll20
`tools/roll20-mock.js` symuluje API kart Roll20 (atrybuty, sekcje powtarzalne, sheet worker, zapytania i szablon
rzutu). Ten skrypt składa z niego podgląd w jednym pliku z przykładową postacią:

```
node tools/build-preview.mjs            # tworzy preview.html obok karty
```

Symulacja odtwarza tylko tyle Roll20, ile potrzebuje ta karta. Ostatecznie sprawdzaj kartę w Sheet Sandbox.
