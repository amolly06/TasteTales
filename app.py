from flask import Flask, render_template, jsonify, request, abort, session, redirect, url_for
import json
import os
import tempfile
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET') or 'dev-secret-change-me'

# Path to recipes file (absolute)
def recipes_file_path():
    # Using TasteTales directory
    tastetales_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(tastetales_dir, 'static', 'recipes.json')


def users_file_path():
    # Using TasteTales directory
    tastetales_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(tastetales_dir, 'static', 'users.json')


# Load recipes from JSON file
def load_recipes():
    path = recipes_file_path()
    print(f"Loading recipes from: {path}")  # Debug print
    if not os.path.exists(path):
        print(f"File not found at: {path}")  # Debug print
        return []
    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        print(f"Loaded {len(data)} recipes")  # Debug print
        return data


def load_users():
    path = users_file_path()
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_users(users):
    path = users_file_path()
    dirpath = os.path.dirname(path)
    os.makedirs(dirpath, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=dirpath, prefix='users_', suffix='.json')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as tmp:
            json.dump(users, tmp, indent=4, ensure_ascii=False)
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.remove(tmp_path)
        except Exception:
            pass
        raise


# Save recipes to JSON file (atomic write)
def save_recipes(recipes):
    path = recipes_file_path()
    dirpath = os.path.dirname(path)
    os.makedirs(dirpath, exist_ok=True)
    # write to a temp file then replace to avoid corruption
    fd, tmp_path = tempfile.mkstemp(dir=dirpath, prefix='recipes_', suffix='.json')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as tmp:
            json.dump(recipes, tmp, indent=4, ensure_ascii=False)
        os.replace(tmp_path, path)
    except Exception:
        # clean up tmp file on error
        try:
            os.remove(tmp_path)
        except Exception:
            pass
        raise

@app.route('/')
def index():
    return render_template('index.html', username=session.get('username'), display_name=session.get('display_name'))

@app.route('/api/recipes', methods=['GET'])
def get_recipes():
    query = request.args.get('search', '').lower()
    category = request.args.get('category', '').strip().lower()
    recipes = load_recipes()

    filtered = recipes

    if category:
        filtered = [r for r in filtered if category == str(r.get('category', '')).strip().lower()]

    if query:
        def matches(recipe):
            low = lambda v: str(v).lower()
            if query in low(recipe.get('title', '')):
                return True
            if query in low(recipe.get('description', '')):
                return True
            if query in low(recipe.get('category', '')):
                return True
            for ing in recipe.get('ingredients', []) or []:
                if query in low(ing):
                    return True
            if query in low(recipe.get('tips', '')):
                return True
            if query in low(recipe.get('instructions', '')):
                return True
            return False

        filtered = [r for r in filtered if matches(r)]

    return jsonify(filtered)


@app.route('/recipe/<int:recipe_id>')
def recipe_detail(recipe_id):
    recipes = load_recipes()
    recipe = None
    for r in recipes:
        try:
            if int(r.get('id')) == int(recipe_id):
                recipe = r
                break
        except Exception:
            continue

    if recipe is None:
        return render_template('recipe.html', recipe=None, username=session.get('username'), display_name=session.get('display_name')), 404

    # add favorited flag if user logged in
    username = session.get('username')
    user_fav = False
    if username:
        users = load_users()
        u = users.get(username, {})
        if 'favorites' in u and any(int(fid) == int(recipe.get('id')) for fid in u.get('favorites', [])):
            user_fav = True

    return render_template('recipe.html', recipe=recipe, username=username, display_name=session.get('display_name'), favorited=user_fav)


@app.route('/api/recipes', methods=['POST'])
def create_recipe():
    # Only logged-in users can create recipes
    if 'username' not in session:
        return jsonify({'error': 'Authentication required'}), 401

    # Accept multipart/form-data (for file upload) or JSON
    if request.content_type and request.content_type.startswith('multipart/form-data'):
        form = request.form
        title = (form.get('title') or '').strip()
        description = (form.get('description') or '').strip()
        category = (form.get('category') or '').strip()
        ingredients_raw = form.get('ingredients', '')
        tips = (form.get('tips') or '').strip()
        instructions = (form.get('instructions') or '').strip()
        health = (form.get('health') or '').strip()

        image_url = ''
        file = request.files.get('image')
        if file and file.filename and allowed_file(file.filename):
            uploads_dir = os.path.join(app.root_path, 'static', 'uploads')
            os.makedirs(uploads_dir, exist_ok=True)
            filename = secure_filename(file.filename)
            save_path = os.path.join(uploads_dir, filename)
            file.save(save_path)
            image_url = url_for('static', filename=f'uploads/{filename}')
        else:
            image_url = form.get('image') or ''
    else:
        data = request.get_json() or {}
        title = (data.get('title') or '').strip()
        description = (data.get('description') or '').strip()
        category = (data.get('category') or '').strip()
        ingredients_raw = data.get('ingredients', '')
        tips = (data.get('tips') or '').strip()
        instructions = (data.get('instructions') or '').strip()
        health = (data.get('health') or '').strip()
        image_url = (data.get('image') or '').strip()

    if not title or not description or not category:
        return jsonify({'error': 'title, description and category are required'}), 400

    # normalize ingredients into list
    if isinstance(ingredients_raw, list):
        ingredients = [str(i).strip() for i in ingredients_raw if str(i).strip()]
    else:
        ingredients = [i.strip() for i in str(ingredients_raw).split('\n') if i.strip()]

    recipes = load_recipes()
    next_id = 1
    if recipes:
        try:
            next_id = max(int(r.get('id', 0)) for r in recipes) + 1
        except Exception:
            next_id = len(recipes) + 1

    new_recipe = {
        'id': next_id,
        'title': title,
        'description': description,
        'category': category,
        'image': image_url or 'https://via.placeholder.com/600x400?text=No+Image',
        'ingredients': ingredients,
        'tips': tips,
        'instructions': instructions,
        'health': health,
        'owner': session.get('username')
    }

    recipes.append(new_recipe)
    try:
        save_recipes(recipes)
    except Exception as e:
        return jsonify({'error': 'Failed to save recipe', 'details': str(e)}), 500

    return jsonify(new_recipe), 201


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    username = (request.form.get('username') or '').strip()
    display_name = (request.form.get('display_name') or '').strip()
    password = (request.form.get('password') or '').strip()
    if not username or not password:
        return render_template('register.html', error='Username and password required')

    users = load_users()
    if username in users:
        return render_template('register.html', error='Username already exists')

    users[username] = {
        'password': generate_password_hash(password),
        'favorites': [],
        'display_name': display_name
    }
    save_users(users)
    session['username'] = username
    session['display_name'] = display_name
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username = (request.form.get('username') or '').strip()
    password = (request.form.get('password') or '').strip()
    users = load_users()
    u = users.get(username)
    if not u or not check_password_hash(u.get('password', ''), password):
        return render_template('login.html', error='Invalid credentials')

    session['username'] = username
    # set display name in session if available
    session['display_name'] = u.get('display_name') if u else None
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('display_name', None)
    return redirect(url_for('index'))


@app.route('/api/recipes/<int:recipe_id>', methods=['DELETE'])
def delete_recipe(recipe_id):
    if 'username' not in session:
        return jsonify({'error': 'Authentication required'}), 401

    recipes = load_recipes()
    for i, r in enumerate(recipes):
        try:
            if int(r.get('id')) == int(recipe_id):
                # check owner
                if r.get('owner') != session.get('username'):
                    return jsonify({'error': 'Permission denied'}), 403
                recipes.pop(i)
                save_recipes(recipes)
                return jsonify({'status': 'deleted'})
        except Exception:
            continue

    return jsonify({'error': 'Not found'}), 404


@app.route('/api/recipes/<int:recipe_id>/favorite', methods=['POST'])
def toggle_favorite(recipe_id):
    if 'username' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    username = session.get('username')
    users = load_users()
    if username not in users:
        return jsonify({'error': 'User record missing'}), 400

    favs = users[username].get('favorites', [])
    # toggle
    if any(int(fid) == int(recipe_id) for fid in favs):
        favs = [fid for fid in favs if int(fid) != int(recipe_id)]
        users[username]['favorites'] = favs
        save_users(users)
        return jsonify({'favorited': False})
    else:
        favs.append(recipe_id)
        users[username]['favorites'] = favs
        save_users(users)
        return jsonify({'favorited': True})


@app.route('/category/<string:category_name>')
def category_page(category_name):
    recipes = load_recipes()
    filtered = [r for r in recipes if str(r.get('category', '')).strip().lower() == category_name.strip().lower()]
    return render_template('category.html', category=category_name, recipes=filtered, username=session.get('username'), display_name=session.get('display_name'))


@app.route('/search')
def search_page():
    q = request.args.get('q', '')
    # reuse get_recipes filtering
    # client-side will fetch via API for details; render results server-side here
    recipes = load_recipes()
    query = q.lower()
    def matches(recipe):
        low = lambda v: str(v).lower()
        if query in low(recipe.get('title', '')):
            return True
        if query in low(recipe.get('description', '')):
            return True
        if query in low(recipe.get('category', '')):
            return True
        for ing in recipe.get('ingredients', []) or []:
            if query in low(ing):
                return True
        return False
    results = [r for r in recipes if matches(r)] if query else []
    return render_template('search.html', query=q, results=results, username=session.get('username'), display_name=session.get('display_name'))


@app.route('/api/whoami')
def whoami():
    return jsonify({'username': session.get('username')})

if __name__ == '__main__':
    app.run(debug=True)