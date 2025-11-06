Recipe-Website
===============

Simple Flask app that serves a recipes website. Includes an API to list recipes and an "Add Recipe" UI to create and persist new recipes to `static/recipes.json`.

Quick start (Windows PowerShell):

```powershell
# create and activate venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# install deps
pip install -r requirements.txt

# run the app
python .\app.py

# visit
# http://127.0.0.1:5000
```

Notes:
- New recipes are saved to `static/recipes.json` using an atomic write. Provide image URLs when adding recipes; a placeholder image will be used if omitted.
- If PowerShell blocks activation scripts, run:
  Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force

If you'd like, I can also add basic server-side validation tests or a small HTML modal instead of the inline form.
 
Authentication:
- Register and login from the web UI before creating or deleting recipes. Only the owner of a recipe may delete it.

Uploading images:
- You can upload an image file in the Add Recipe form. Uploaded files are stored under `static/uploads/` and served by the app.

Endpoints of interest:
- GET /api/recipes?search=...&category=...  — search/filter recipes
- POST /api/recipes  — create (requires login); supports multipart/form-data (image file) or JSON
- DELETE /api/recipes/<id>  — delete (owner only)
- POST /api/recipes/<id>/favorite — toggle favorite for current user

If you'd like, I can also add basic server-side validation tests or a small HTML modal instead of the inline form.
