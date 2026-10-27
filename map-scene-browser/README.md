# Map & Scene Browser (Foundry VTT v14)

A GM-only window that lists map and scene modules from a remote CSV file: search by name, filter by type
(All / Scene / Map), and Install / Uninstall buttons on each card.

## Install
In Foundry: *Setup → Add-on Modules → Install Module*, paste this into **Manifest URL** and click Install:

```
https://raw.githubusercontent.com/V-Cancrosa/Various-1/main/map-scene-browser/module.json
```

Then enable **Map & Scene Browser** in the world's *Manage Modules*.

**PL:** W Foundry: *Setup → Add-on Modules → Install Module*, wklej powyższy link w pole **Manifest URL** i kliknij
Install. Potem włącz moduł w świecie (*Manage Modules*) i wpisz link do CSV w *Configure Settings → Map & Scene Browser*.

## Use it
1. *Configure Settings → Map & Scene Browser → CSV source URL*: paste a public link to the CSV.
2. Open the browser with the map icon in the **Token** controls on the left (GMs only), or from a macro:
   `game.modules.get("map-scene-browser").api.open()`.

CSV columns (header row required, any order): `source` (Scene, Map, …), `name`, `json_link` (module manifest URL),
`zip_link`, `version`. Only `name` and `json_link` are required; `zip_link` isn't used.

The browser downloads the CSV and the manifests itself, so their host has to allow cross-origin requests (CORS):
raw.githubusercontent.com, a Google Sheets "Publish to web" CSV link, and Dropbox links work. Dropbox links are read
through `dl.dropboxusercontent.com`.

## Install and Uninstall
Foundry v14 has no API for installing or removing packages from inside a running world. The buttons send the same
request that the Setup screen sends (`POST /setup` with `installPackage` / `uninstallPackage`). If the server refuses it,
for example because a world is running or because this browser isn't logged in as the server administrator, the
module shows the reason. Install also copies the manifest URL, so you can paste it into *Setup → Add-on Modules →
Install Module*.

- **Install** reads the module ID from the manifest (to show the status), asks first if the module is already installed,
  then sends the install request. A newly installed module shows up in *Manage Modules* after the world reloads.
- **Uninstall** finds the module ID (from an installed module with the same manifest URL, or from the manifest),
  checks that the module is installed and not enabled in this world, asks for confirmation, then sends the uninstall request.
- The status line shows the installed version, whether the CSV has a newer one, and whether the module is enabled.

## Releases
In `module.json`, raise `version` and change the tag in `download` to match
(`…/releases/download/map-scene-browser-vX.Y.Z/module.zip`), then push to `main`. The workflow
`.github/workflows/map-scene-browser.yml` creates the `map-scene-browser-vX.Y.Z` release with `module.zip`, and Foundry
offers the update through the manifest URL. The workflow fails if `download` doesn't match the version.
