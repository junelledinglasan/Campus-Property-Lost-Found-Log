# Campus Property Lost & Found Log: Frontend

React (Vite) PWA. Kumakausap sa Django backend (tingnan ang README ng backend).

## Kailangan
- Node.js 18 o mas bago (https://nodejs.org). Kasama na ang `npm`.

## Patakbuhin
Una, patakbuhin ang backend (nasa `backend/README.md`). Pagkatapos, sa ibang terminal:
```bash
cd frontend
npm install
npm run dev
```
Buksan ang http://localhost:5173

Demo account ng OSAS staff (galing sa `seed_demo` ng backend): `osas` / `osas123`.

Ang `/api` at `/media` ay dumadaan sa proxy ng Vite papunta sa Django sa http://127.0.0.1:8000 (tingnan ang `vite.config.js`).

### Demo na walang backend
Kung gusto mong subukan ang app nang walang Django (ang data ay nasa browser lang):
```bash
# Windows PowerShell
$env:VITE_USE_MOCK="true"; npm run dev
# Mac o Linux
VITE_USE_MOCK=true npm run dev
```

## Mga page
| Address | Para kanino | Ano ang ginagawa |
| --- | --- | --- |
| `/` | Lahat | Listahan ng found items, search, at filter |
| `/items/:id` | Lahat | Detalye ng item at claim form (full name at student number). Kapag naibalik na, ipinapakita ang handover photo bilang proof |
| `/admin/login` | OSAS | Sign in |
| `/admin/items` | OSAS | Mag-post, mag-edit, at mag-delete ng found item |
| `/admin/claims` | OSAS | Mag-check ng claim, i-verify ang ID, mag-upload ng handover photo, i-approve o i-reject |
| `/admin/history` | OSAS | Claim history, may handover photo |

## PWA (installable web app)
Pwedeng i-install sa browser (laptop man o phone). Hindi tumatakbo ang PWA features sa `npm run dev`. Subukan sa production build:
```bash
npm run build
npm run preview
```
Buksan ang http://localhost:4173. Sa Chrome o Edge, lalabas ang **Install app** button sa header.

- Kailangan ng **HTTPS** kapag naka-host na online. Localhost lang ang exempted.
- Naka-cache ang app shell at mga larawan, pero ang data (items at claims) ay galing sa server. Kapag offline, magpapakita ang app ng mensaheng hindi maabot ang server.
- Ang `/api` ay hindi kailanman kine-cache, kaya laging bago ang data.

Mga file ng PWA: `public/manifest.webmanifest`, `public/sw.js`, at `public/icons/`.

## Logo
Ang seal ng OSAS ay nasa `public/logo.png` (transparent). Ginagamit ito sa header, hero, login page, at sa mga PWA icon sa `public/icons/`.

## Mga file na dapat alam
- `src/api/http.js`: lahat ng tawag sa Django. `src/api/mock.js`: demo na walang backend. `src/api/api.js`: pumipili kung alin.
- Ang listahan ng categories ay nasa `src/api/http.js` at sa `Category` ng backend (`lostfound/models.py`). Dapat magkapareho.
