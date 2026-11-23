# Campus Property Lost & Found Log

Sistema para sa OSAS: nagpo-post ng found items ang OSAS, at ang mga estudyante ay naghahanap at nagsusumite ng claim, walang account na kailangan. Ang OSAS ang nagve-verify sa ID at nagre-record ng handover.

```
lost-found-system/
  frontend/   React (Vite) PWA
  backend/    Django REST API
```

## Pinakamabilis na paraan para patakbuhin
Dalawang terminal.

**Terminal 1: backend** (kailangan ng Python)
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

**Terminal 2: frontend** (kailangan ng Node.js)
```bash
cd frontend
npm install
npm run dev
```

Buksan ang http://localhost:5173. OSAS staff sign in: `osas` / `osas123`.

Ang detalye ay nasa `backend/README.md` at `frontend/README.md`.
