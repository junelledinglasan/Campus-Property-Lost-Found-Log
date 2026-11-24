#!/usr/bin/env bash
# Build para sa deployment (hal. Render). Patakbuhin mula sa ugat ng project.
set -euo pipefail

# 1. Frontend -> backend/frontend_dist
if command -v npm >/dev/null 2>&1; then
  (cd frontend && npm ci && npm run build)
  rm -rf backend/frontend_dist
  cp -r frontend/dist backend/frontend_dist
elif [ -f backend/frontend_dist/index.html ]; then
  echo "Walang npm; gagamitin ang naka-commit na backend/frontend_dist."
else
  echo "Walang npm at walang backend/frontend_dist. I-build muna ang frontend (npm run build) at kopyahin ang dist." >&2
  exit 1
fi

# 2. Backend
cd backend
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate --noinput
python manage.py ensure_admin
