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

Ang Django admin ay nasa http://127.0.0.1:8000/django-admin/. Doon pwedeng gumawa ng iba pang OSAS staff account: mag-add ng user at lagyan ng tsek ang **Staff status**. Pwede ring `python manage.py createsuperuser`.

## Mga patakaran ng sistema
Unclaimed → (may nag-claim) → **Pending** → (inaprubahan) → **Claimed**
Kapag ni-reject ang claim, babalik sa **Unclaimed**.

- Kapag Claimed na ang item, makikita ng lahat sa detalye nito ang handover photo bilang proof na naibalik na (walang pangalan o student number).
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
- Ang handover photos ay nasa `private_media/` (o sa private na bucket ng Supabase), kaya walang public na URL. Ang `GET /api/claims/` (kasama ang pangalan at student number) ay para sa staff lang. Ang larawan lang ang ipinapakita sa publiko, sa `GET /api/items/:id/` ng Claimed na item.
- Limitado ang pagsusumite ng claim (30 kada oras kada IP) at ang login (10 kada minuto kada IP). Mababago sa `THROTTLE_CLAIMS` at `THROTTLE_LOGIN`.
- Sinusuri kung totoong larawan ang ina-upload (JPG, PNG, o WebP, hanggang 5 MB).

## Tests
```bash
python manage.py test lostfound
```
29 tests: login, mga pahintulot, buong daloy ng claim, validation, throttle, privacy ng mga larawan, at proof photo ng naibalik na item.

## Database at larawan
- Walang `DATABASE_URL`: SQLite (`db.sqlite3`) at mga folder na `media/` at `private_media/`.
- May `DATABASE_URL` (hal. Supabase Postgres): iyon ang gagamitin.
- May `SUPABASE_S3_ACCESS_KEY` at kasama: sa Supabase Storage na ise-save ang mga larawan (`lf-items` public, `lf-handover` private).
- Tingnan ang `.env.example` at ang `DEPLOY.md` sa ugat ng project.

Para gumawa ng OSAS account nang walang shell: i-set ang `OSAS_USERNAME` at `OSAS_PASSWORD` at patakbuhin ang `python manage.py ensure_admin`. Ligtas ito patakbuhin nang paulit-ulit.

## Bago i-deploy (production)
1. I-set ang environment variables (tingnan ang `.env.example`): `DJANGO_DEBUG=0`, mahabang random na `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, at `CSRF_TRUSTED_ORIGINS`.
2. **Huwag patakbuhin ang `seed_demo` sa production.** Gumamit ng `ensure_admin` o `createsuperuser`.
3. Gumamit ng HTTPS. Kailangan din ito ng PWA.
4. Patakbuhin gamit ang `gunicorn config.wsgi`, hindi `runserver`. Ang WhiteNoise ang nagse-serve ng static files at ng na-build na React app (`backend/frontend_dist`).
5. Mag-backup nang regular (database at mga larawan). Walang automatic backup ang libreng plan ng Supabase; tingnan ang `DEPLOY.md`.
6. Kapag nasa likod ng proxy (Render), i-set ang `DRF_NUM_PROXIES=1` para tamang IP ang binibilang ng throttle.

## Mga limitasyon na alam na
- Ang token ng staff ay hindi nag-e-expire hangga't hindi nagsa-sign out.
- Kasama sa `GET /api/claims/` ang lahat ng handover photo (base64), kaya bibigat ito kapag libu-libo na ang claim. Kapag dumating ang puntong iyon, lagyan ng pagination at hiwalay na endpoint para sa larawan.
- Walang notification sa estudyante (sinadya, ayon sa Week 1).
