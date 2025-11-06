# TasteTales

TasteTales is a lightweight Flask web app for browsing, adding, and managing recipes. It serves a responsive website and exposes a small JSON API for recipe listing, searching, and management.

## Features

- Browse recipes with details (ingredients, instructions, tips, health benefits)
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
