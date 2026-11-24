# Pag-deploy: Supabase (database at larawan) + Render (app)

Isang web service ang Django: ito ang API at ito rin ang nagse-serve ng na-build na React app. Kaya iisang address lang ito at walang CORS na aayusin.

```
Browser ──► Render (Django + React) ──► Supabase Postgres   (data)
                                   └──► Supabase Storage    (mga larawan)
```

> Hindi ko pa nasusubukan ang mga hakbang na ito sa totoong Supabase at Render account. Nasubukan ko ang code laban sa lokal na S3 simulator at sa gunicorn. Maaaring magkaiba nang kaunti ang pangalan ng mga menu sa dashboard nila.

## 1. Supabase

1. Gumawa ng project sa https://supabase.com. Piliin ang region na pinakamalapit (Singapore). Itala ang **database password**.
2. **Database**: pindutin ang **Connect** at kopyahin ang **Session pooler** na connection string (port `5432`). Ganito ang hitsura:
   ```
   postgresql://postgres.PROJECTREF:PASSWORD@aws-0-REGION.pooler.supabase.com:5432/postgres
   ```
   Idagdag sa dulo ang `?sslmode=require`. Kapag may espesyal na character ang password (`@`, `#`, `/`, `:`), i-URL-encode ito (`@` → `%40`).
   Huwag gamitin ang *transaction* pooler (port `6543`).
3. **Storage**: gumawa ng dalawang bucket.
   - `lf-items`: **Public** (mga larawan ng found items)
   - `lf-handover`: **Private** (mga handover photo)
4. **Storage → Settings → S3 connection**: i-enable, at gumawa ng **access key**. Itala ang Access Key ID, Secret Access Key, at **Region**. Ang project reference ay ang bahagi ng project URL bago ang `.supabase.co`. Ang key na ito ay may buong access sa lahat ng bucket, kaya sa server lang ito ilalagay, hindi sa frontend.

## 2. Render

1. I-push ang buong folder na ito (may `frontend/`, `backend/`, `build.sh`, `render.yaml`) sa isang GitHub repo. Gawing **private** ito. Ang `.env` ay wala sa repo.
2. Sa Render: **New → Blueprint**, piliin ang repo. Babasahin nito ang `render.yaml`.
3. Ilagay ang mga value na hinihingi:

   | Variable | Halimbawa |
   | --- | --- |
   | `DJANGO_ALLOWED_HOSTS` | `lost-found-log.onrender.com` |
   | `CSRF_TRUSTED_ORIGINS` | `https://lost-found-log.onrender.com` |
   | `DATABASE_URL` | ang session pooler string sa itaas |
   | `SUPABASE_PROJECT_REF` | `abcdefghijklmnop` |
   | `SUPABASE_S3_ACCESS_KEY` / `SUPABASE_S3_SECRET_KEY` | galing sa Supabase |
   | `SUPABASE_S3_REGION` | `ap-southeast-1` |
   | `OSAS_USERNAME` / `OSAS_PASSWORD` | ang unang OSAS account (hindi bababa sa 8 character) |

   Ang `DJANGO_SECRET_KEY` ay awtomatikong ginagawa ng Render.
4. I-deploy. Ang `build.sh` ang nagbi-build ng React, nagpapatakbo ng `migrate` (ginagawa ang mga table sa Supabase), at gumagawa ng OSAS account.
5. Buksan ang `https://<pangalan>.onrender.com` at mag-sign in sa `/admin/login`.

Kapag walang Node.js ang build environment ng Render, i-build ang frontend sa laptop (`cd frontend && npm run build`), kopyahin ang `dist` bilang `backend/frontend_dist`, at i-commit ito. Gagamitin iyon ng `build.sh`.

## 3. Dapat alam sa libreng plan

- **Natutulog ang Render** pagkalipas ng 15 minutong walang bisita. Ang unang bukas pagkatapos noon ay inaabot ng halos isang minuto. Buksan ang site ilang minuto bago ang UAT.
- **Napo-pause ang Supabase project** kapag isang linggong halos walang gamit. Hindi nabubura ang data. Pindutin ang **Restore** sa dashboard.
- **Walang automatic backup** ang libreng Supabase. Gumawa ng sarili (sa ibaba) bago ang UAT at bago ang Week 4.
- Dahil nasa Supabase ang data at mga larawan, hindi nawawala ang laman kapag nag-redeploy o natulog ang Render.

## 4. Backup at restore

**Database** (kailangan ng PostgreSQL client tools sa laptop; dapat kapareho o mas bago ang bersyon ng Supabase):
```bash
pg_dump "$DATABASE_URL" --no-owner --format=custom --file=backup-2026-11-23.dump
# ibalik:
pg_restore --no-owner --clean --if-exists --dbname "$DATABASE_URL" backup-2026-11-23.dump
```
Tanggalin ang `?sslmode=require` sa `$DATABASE_URL` kung magreklamo ang `pg_dump`, at ilagay na lang ito bilang `PGSSLMODE=require`.

**Mga larawan**: sa Supabase dashboard, buksan ang bawat bucket at i-download ang mga file. Kapag marami na, gamitin ang AWS CLI gamit ang S3 endpoint at keys:
```bash
aws s3 sync s3://lf-items ./backup/lf-items --endpoint-url https://PROJECTREF.storage.supabase.co/storage/v1/s3 --region ap-southeast-1
```

## 5. Subukan sa laptop gamit ang Supabase

Sa `backend/`, i-set ang parehong environment variable (tingnan ang `.env.example`) bago patakbuhin ang `python manage.py migrate` at `runserver`. Kapag walang `DATABASE_URL` at `SUPABASE_S3_ACCESS_KEY`, SQLite at lokal na folder ang gamit gaya ng dati.

## 6. Privacy

Ang handover photo ay makikita na ng lahat ng estudyante sa detalye ng naibalik na item, bilang proof. Walang pangalan o student number sa pampublikong sagot. Pero ang larawan mismo ay maaaring magpakita ng mukha o ID. Magandang gawin ito ng OSAS: kunan ang item sa kamay ng may-ari, huwag ang mukha o ang ID, at ipaalam sa estudyante na ilalagay ang larawan sa sistema. Mahalaga ito sa Data Privacy Act. Kapag gusto mong bawiin ang pagiging pampubliko, `get_handoverPhoto` sa `lostfound/serializers.py` lang ang babaguhin.
