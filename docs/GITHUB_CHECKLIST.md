# GitHub pre-push checklist

- [ ] `.env` is absent
- [ ] No JWT/bearer token export is present
- [ ] `node_modules/`, `dist/`, `.venv/`, caches and SQLite DB are absent
- [ ] `ml/artifacts/*.joblib` are present because local inference requires them
- [ ] `README.md` explains synthetic-data limitations
- [ ] Backend starts with `python -m uvicorn backend.app.main:app --reload`
- [ ] Frontend `npm run build` passes
- [ ] `/health` reports database `ok` and ML `ready`
- [ ] Production prediction returns 200
- [ ] Digital Twin simulation returns 200
- [ ] Optimization and recommendation approval return 200

Do not push or deploy until these checks are completed locally.
