# Karta postaci WFRP 2e dla Roll20 (PL)

Karta do **Warhammer Fantasy Roleplay, 2. edycja** z polskim nazewnictwem. Pliki: `sheet.html` (karta, szablon
rzutu i sheet worker) oraz `sheet.css`.

## Instalacja w Roll20
Własne karty wymagają konta **Pro** u twórcy gry.

1. Wejdź na stronę gry i otwórz *Settings → Game Settings*.
2. W polu *Character Sheet Template* wybierz **Custom**.
3. Wklej zawartość `sheet.html` do zakładki **HTML Layout**, a `sheet.css` do **CSS Styling**.
4. Kliknij **Save Changes** i otwórz grę.

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
