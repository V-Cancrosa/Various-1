# OBS Game Overlay

Nakładka „Teraz gram” do OBS na nagrania i streamy na YouTube i Twitchu. Nazwę gry możesz wpisać sam albo pozwolić, żeby wykrył ją Discord. Nakładka sama dobiera kolor do gry.

- `overlay.html` – sama nakładka; w OBS dodajesz ją jako **źródło przeglądarki** (Browser Source)
- `panel.html` – panel sterowania; w OBS dodajesz go jako **dock przeglądarki** (Custom Browser Dock)

Nie trzeba niczego instalować ani uruchamiać serwera. Wystarczą dwa pliki HTML.

## Motywy

`neon` · `glass` · `minimal` · `retro` (pixel art) · `esport` (pasek)

Kolor akcentu jest liczony z nazwy gry, więc każda gra ma swój stały kolor. Możesz też ustawić własny kolor w panelu.
Jeśli nie ma okładki, nakładka pokazuje monogram, np. **ER** dla Elden Ring. Jeśli grę wykrył Discord, pokazuje ikonę gry z Discorda.

## Instalacja w OBS

1. Pobierz folder `obs-game-overlay` na dysk, np. do `C:\OBS\obs-game-overlay\`.
2. **Nakładka:** *Źródła → + → Przeglądarka*
   - **Nie** zaznaczaj „Plik lokalny”. W polu URL wpisz:
     `file:///C:/OBS/obs-game-overlay/overlay.html`
   - Szerokość `1920`, wysokość `1080` (albo rozdzielczość Twojej sceny).
3. **Panel:** *Doki → Własne doki przeglądarki…*
   - Nazwa: `Gra`
   - URL: `file:///C:/OBS/obs-game-overlay/panel.html`

> Oba adresy muszą zaczynać się od `file:///`, czyli tak samo. Tylko wtedy panel i nakładka „widzą się” nawzajem. Opcja „Plik lokalny” zmienia adres na `http://absolute/…` i synchronizacja przestaje działać.

Gotowe. W docku wpisujesz nazwę gry i wciskasz Enter, a nakładka zmienia się z animacją. Ostatnie gry zostają w panelu jako przyciski do szybkiego wyboru.

## Automatyczne wykrywanie gry przez Discord

Działa przez [Lanyard](https://github.com/Phineas/lanyard), darmową usługę, która udostępnia Twój status z Discorda (to samo „Gra w …”, które widzą znajomi).

1. Dołącz do serwera Lanyard: <https://discord.gg/lanyard>. Wystarczy być na serwerze; nie musisz tam nic pisać.
2. W Discordzie: *Ustawienia → Prywatność aktywności → Udostępniaj wykrytą aktywność innym* musi być **włączone**.
   Jeśli Discord nie wykrywa jakiejś gry, dodaj ją w *Ustawienia → Zarejestrowane gry*.
3. Skopiuj swoje **User ID**:
   *Ustawienia → Zaawansowane → Tryb dewelopera: włącz*, potem kliknij prawym na swój avatar → *Kopiuj ID użytkownika*.
4. Wklej ID w panelu, w sekcji **Discord**.

Tryby źródła gry:

| Tryb | Co pokazuje |
|---|---|
| **Auto** (domyślny) | grę z Discorda, a gdy nic nie jest uruchomione, nazwę wpisaną ręcznie |
| **Tylko ręcznie** | tylko to, co wpiszesz |
| **Tylko Discord** | tylko wykrytą grę; gdy nic nie jest uruchomione, nakładka się chowa |

W polu **Ignoruj** wpisz programy, które Discord bierze za gry (np. `Visual Studio Code, Wallpaper Engine`).
Jeśli wpiszesz ręcznie tę samą nazwę co wykryta gra, to Twój podtytuł i okładka mają pierwszeństwo.

Licznik czasu przy grze z Discorda liczy od chwili uruchomienia gry. Przy grze wpisanej ręcznie liczy od chwili jej ustawienia. Przycisk „Zeruj licznik” zaczyna liczenie od nowa.

> Prywatność: po dołączeniu do serwera Lanyard Twój status Discorda (gra, Spotify itp.) jest dostępny publicznie przez API dla każdego, kto zna Twoje ID. Jeśli chcesz to wyłączyć, wyjdź z serwera Lanyard.

## Bez panelu – wszystko w adresie URL

Nakładka działa też sama, z ustawieniami w adresie. W panelu, w sekcji *Link bez panelu*, jest gotowy adres z obecnymi ustawieniami. Przykład:

```
file:///C:/OBS/obs-game-overlay/overlay.html?panel=0&game=Elden%20Ring&theme=esport&pos=br
```

| Parametr | Wartości | Domyślnie |
|---|---|---|
| `game` | nazwa gry | – |
| `sub` | podtytuł | – |
| `cover` | URL obrazka | – |
| `discord` | Discord User ID | – |
| `mode` | `auto`, `manual`, `discord` | `auto` |
| `ignore` | lista po przecinku | – |
| `theme` | `neon`, `glass`, `minimal`, `retro`, `esport` | `neon` |
| `pos` | `tl`, `tc`, `tr`, `bl`, `bc`, `br` | `bl` |
| `label` | napis nad nazwą | `Teraz gram` |
| `accent`, `accent2` | kolor hex bez `#`, np. `ff3366` | auto |
| `scale` | np. `1.5` | `1` |
| `margin` | odstęp od krawędzi w px | `40` |
| `timer`, `icon`, `showLabel` | `0` wyłącza | `1` |
| `panel` | `0` = ignoruj ustawienia z panelu | – |

Z `panel=0` możesz zrobić kilka źródeł z różnymi stałymi ustawieniami. Bez `panel=0` ustawienia z panelu nadpisują te z adresu.

## Wskazówki

- Nakładka ma przezroczyste tło, więc nie trzeba dodawać żadnego CSS w ustawieniach źródła.
- Odśwież źródło w OBS (*Właściwości → Odśwież pamięć podręczną bieżącej strony*), jeśli podmienisz pliki na nowszą wersję.
- Czcionki są pobierane z Google Fonts. Bez internetu nakładka użyje czcionek systemowych.
