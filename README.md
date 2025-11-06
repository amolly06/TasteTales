Recipe-Website
# TasteTales

TasteTales is a lightweight Flask web app for browsing, adding, and managing recipes. It serves a responsive website and exposes a small JSON API for recipe listing, searching, and management.

This README explains how to set up the project locally (Windows PowerShell), where recipe data is stored, available endpoints, and how to contribute.

## Features

- Browse recipes with details (ingredients, instructions, tips, health benefits)
- Search and filter by category or ingredient
- Create recipes via the web form or JSON API (requires authentication)
- Favorite recipes and manage your own recipes (delete if you are the owner)
- Image upload support (stored under `static/uploads/`)

## Tech stack

- Python 3.10+ (project currently runs on venv Python 3.12 in the workspace)
- Flask
- Simple JSON storage in `static/recipes.json` (no database by default)

## Prerequisites

- Git
- Python 3.10+ installed
- A GitHub account (optional, for pushing changes)

## Quick start (Windows PowerShell)

Run these commands from the repository root (the `TasteTales` folder):

```powershell
# create and activate venv (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# install dependencies
pip install -r requirements.txt

# start the app
python .\app.py

# visit in browser
# http://127.0.0.1:5000
```

If you encounter an execution policy error when activating the venv, run (as the current user):

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
```

## Environment & Config

- The app uses a simple `app.secret_key` derived from the `FLASK_SECRET` environment variable if set; otherwise it falls back to a development secret. For production, set `FLASK_SECRET` to a secure value.

Example (PowerShell):

```powershell
$env:FLASK_SECRET = 'a-strong-secret-value'
python .\app.py
```

## Data storage

- Recipes are stored in `static/recipes.json`. The app reads and writes this file using an atomic write routine (`save_recipes`) to reduce corruption risk.
- Uploaded images are saved to `static/uploads/` when using the web form's file upload.

Tip: If you prefer a database-backed approach later, a migration layer can be added to translate the JSON into a DB model (SQLite/Postgres).

## Useful endpoints

- `GET /api/recipes` — Returns JSON array of recipes. Supports query params `search` and `category`.
- `POST /api/recipes` — Create a recipe (requires login). Accepts JSON or `multipart/form-data` for file uploads.
- `GET /recipe/<id>` — Recipe detail page (HTML)
- `DELETE /api/recipes/<id>` — Delete a recipe (owner only)
- `POST /api/recipes/<id>/favorite` — Toggle favorite for authenticated user
- `GET /api/whoami` — Returns the logged-in username (if any)

## Development notes

- The app uses `app.root_path` and was updated to resolve paths relative to the `TasteTales` directory so the project can be separated from any previous repo name.
- When editing `static/recipes.json`, restart the server to ensure changes are picked up (the server auto-reloads in debug mode but explicit restarts help after path/structure changes).

## Contributing

1. Fork the repository on GitHub.
2. Create a feature branch: `git checkout -b feat/my-change`.
3. Make changes and run the app locally to verify.
4. Commit and push: `git push -u origin feat/my-change`.
5. Open a pull request against `main`.

If you'd like help converting this project to use a small SQLite DB, adding unit tests, or GitHub Actions for CI, I can add that in a follow-up.

## Troubleshooting

- Permission / locked files when deleting old directories (Windows + OneDrive): close editors/terminals that may use the folder and try again.
- `git push` rejected: if your remote has commits you don't have locally, run `git pull --rebase origin main` and resolve conflicts, or force push only if you intend to overwrite remote history: `git push --force`.
- Virtual environment activation blocked: see the execution policy section above.

## License & attribution

This project is available under the MIT License — update as needed for your project.

---

If you'd like, I can:
- add a minimal `requirements.txt` check, or
- add a tiny automated test that validates `load_recipes()` reads the JSON file correctly.

Enjoy building TasteTales!
