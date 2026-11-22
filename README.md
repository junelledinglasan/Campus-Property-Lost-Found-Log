# Campus Property Lost & Found Log: Frontend

React (Vite) frontend. Gumagamit ito ng mock API na nakasave sa browser (localStorage), kaya tumatakbo kahit wala pang Django.

## Kailangan
- Node.js 18 o mas bago (https://nodejs.org). Kasama na ang `npm`.

## Patakbuhin
```bash
npm install
npm run dev
```
Buksan ang http://localhost:5173

## Demo account (OSAS staff)
- Username: `osas`
- Password: `osas123`

## Mga page
| Address | Para kanino | Ano ang ginagawa |
| --- | --- | --- |
| `/` | Lahat | Listahan ng found items, search, at filter |
| `/items/:id` | Lahat | Detalye ng item at claim form (full name at student number) |
| `/admin/login` | OSAS | Sign in |
| `/admin/items` | OSAS | Mag-post, mag-edit, at mag-delete ng found item |
| `/admin/claims` | OSAS | Mag-check ng claim, i-verify ang ID, mag-upload ng handover photo, i-approve o i-reject |
| `/admin/history` | OSAS | Claim history, may handover photo |

## Status ng item
Unclaimed (may claim ang estudyante) → Pending (may claim na, ichecheck ng OSAS) → Claimed (na-approve). Kapag ni-reject ang claim, babalik sa Unclaimed.

## Pagkonekta sa Django mamaya
Lahat ng data access ay nasa `src/api/api.js`. Nakalista sa itaas ng file ang mga endpoint na kakailanganin. Palitan lang ang laman ng bawat function ng `fetch('/api/...')`. Naka-set na ang proxy sa `vite.config.js` papunta sa `http://localhost:8000`.

## Mga limitasyon ng mock
- Nawawala ang data kapag nilinis ang browser data. Bawat browser ay may sariling data.
- Nasa browser storage ang mga larawan (binabawasan ang laki bago i-save), kaya limitado ang dami.
- Hindi totoong seguridad ang demo login. Ang Django na ang mag-aalaga nito.
