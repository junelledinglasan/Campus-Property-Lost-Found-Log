# Campus Property Lost & Found Log: Backend

Django + Django REST Framework. Ito ang API at database ng sistema.

## Kailangan
- Python 3.10 o mas bago (https://www.python.org). Sa Windows, lagyan ng tsek ang "Add Python to PATH" kapag nag-install.

## Patakbuhin (development)

**Windows (PowerShell o Command Prompt):**
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

**Mac o Linux:**
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Tumatakbo ito sa http://127.0.0.1:8000. Ang `seed_demo` ay gumagawa ng:
- OSAS staff account: `osas` / `osas123` (para sa development lang)
- 6 sample na found items

Tapos, sa ibang terminal, patakbuhin ang frontend (tingnan ang README ng frontend).

Ang Django admin ay nasa http://127.0.0.1:8000/admin/. Doon pwedeng gumawa ng iba pang OSAS staff account: mag-add ng user at lagyan ng tsek ang **Staff status**. Pwede ring `python manage.py createsuperuser`.

## Mga patakaran ng sistema
Unclaimed → (may nag-claim) → **Pending** → (inaprubahan) → **Claimed**
Kapag ni-reject ang claim, babalik sa **Unclaimed**.

- Isang Pending claim lang kada item. Ipinapatupad ito mismo ng database, kaya hindi nalulusutan kahit sabay na nag-claim ang dalawa.
- Ang estudyante ay hindi nangangailangan ng account. Full name at student number lang ang isinusumite.
- Para ma-approve, kailangan ang pangalan at student number na nakita ng OSAS sa ID, at ang handover photo.
- Hindi direktang mababago ang status ng item. Nagbabago lang ito sa pamamagitan ng mga claim.

## API
| Method at address | Sino | Ano ang ginagawa |
| --- | --- | --- |
| `POST /api/auth/login/` | Lahat | Login ng OSAS staff. Ibinabalik ang token |
| `POST /api/auth/logout/` | Staff | Binubura ang token |
| `GET /api/items/` at `GET /api/items/:id/` | Lahat | Listahan at detalye ng found items |
| `POST /api/items/` | Staff | Mag-post ng found item |
| `PUT` o `PATCH /api/items/:id/` | Staff | Mag-edit ng item |
| `DELETE /api/items/:id/` | Staff | Magbura ng item at ng mga claim nito |
| `POST /api/claims/` | Lahat | Magsumite ng claim. Walang personal na detalye sa sagot |
| `GET /api/claims/` | Staff | Lahat ng claim, kasama ang handover photo |
| `POST /api/claims/:id/decide/` | Staff | I-approve o i-reject ang claim |

Ang staff endpoints ay nangangailangan ng header na `Authorization: Token <token>`.
Lahat ng error ay may ganitong hugis: `{"detail": "isang malinaw na mensahe"}`.

## Seguridad
- Ang listahan ng claims (pangalan at student number) at ang handover photos ay para sa OSAS staff lang.
- Ang handover photos ay nasa `private_media/`, hindi sa `media/`, kaya walang public na URL. Ipinapadala lang ito ng API sa naka-sign in na staff.
- Limitado ang pagsusumite ng claim (30 kada oras kada IP) at ang login (10 kada minuto kada IP). Mababago sa `THROTTLE_CLAIMS` at `THROTTLE_LOGIN`.
- Sinusuri kung totoong larawan ang ina-upload (JPG, PNG, o WebP, hanggang 5 MB).

## Tests
```bash
python manage.py test lostfound
```
25 tests: login, mga pahintulot, buong daloy ng claim, validation, throttle, at privacy ng mga larawan.

## Bago i-deploy (production)
1. I-set ang environment variables (tingnan ang `.env.example`): `DJANGO_DEBUG=0`, mahabang random na `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, at `CSRF_TRUSTED_ORIGINS`.
2. **Palitan o burahin ang demo account** (`osas` / `osas123`). Huwag patakbuhin ang `seed_demo` sa production.
3. Gumamit ng HTTPS. Kailangan din ito ng PWA.
4. Ang Django ay hindi dapat patakbuhin gamit ang `runserver`. Gumamit ng `gunicorn config.wsgi` (o katumbas) sa likod ng web server tulad ng nginx. Ang web server ang magse-serve ng `/media/`. Huwag i-expose ang `private_media/`.
5. I-backup ang `db.sqlite3` at ang `private_media/` nang regular. Para sa mas maraming gumagamit, lumipat sa PostgreSQL sa `DATABASES` sa `config/settings.py`.

## Mga limitasyon na alam na
- Ang token ng staff ay hindi nag-e-expire hangga't hindi nagsa-sign out.
- Kasama sa `GET /api/claims/` ang lahat ng handover photo (base64), kaya bibigat ito kapag libu-libo na ang claim. Kapag dumating ang puntong iyon, lagyan ng pagination at hiwalay na endpoint para sa larawan.
- Walang notification sa estudyante (sinadya, ayon sa Week 1).
