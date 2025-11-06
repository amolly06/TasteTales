// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// Fetch and display recipes
async function loadRecipes(query = '') {
    try {
        const response = await fetch(`/api/recipes${query ? `?search=${encodeURIComponent(query)}` : ''}`);
        const recipes = await response.json();
        const recipeGrid = document.getElementById('recipeGrid');
        recipeGrid.innerHTML = '';

        recipes.forEach(recipe => {
            const card = document.createElement('div');
            card.className = 'recipe-card';
            card.innerHTML = `
                <img src="${recipe.image}" alt="${recipe.title}">
                <h3>${recipe.title}</h3>
                <p>${recipe.description}</p>
                <a href="#" class="view-recipe" data-id="${recipe.id}">View Recipe</a>
            `;
            recipeGrid.appendChild(card);
        });

        // Add click event for recipe details: navigate to recipe detail page
        document.querySelectorAll('.view-recipe').forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const recipeId = e.target.getAttribute('data-id');
                if (recipeId) {
                    window.location.href = `/recipe/${encodeURIComponent(recipeId)}`;
                }
            });
        });
    } catch (error) {
        console.error('Error loading recipes:', error);
    }
}

// Search functionality: navigate to search page on Enter or small debounce
const searchInput = document.getElementById('searchInput');
let searchTimeout = null;
if (searchInput) {
    searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        const q = e.target.value.trim();
        searchTimeout = setTimeout(() => {
            if (q.length === 0) return; // do nothing for empty
            window.location.href = `/search?q=${encodeURIComponent(q)}`;
        }, 600);
    });
    searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            const q = searchInput.value.trim();
            window.location.href = `/search?q=${encodeURIComponent(q)}`;
        }
    });
}

// category cards are links to /category/<name>, no JS needed

// Newsletter form submission
document.getElementById('newsletterForm').addEventListener('submit', (e) => {
    e.preventDefault();
    const email = e.target.querySelector('input').value;
    alert(`Thank you for subscribing with ${email}!`);
    e.target.reset();
});

// No featured recipes loaded on home page; category pages render server-side

// Add recipe form toggle and submission
const addRecipeBtn = document.getElementById('addRecipeBtn');
const addRecipeSection = document.getElementById('add-recipe');
const addRecipeForm = document.getElementById('addRecipeForm');
const cancelAddRecipe = document.getElementById('cancelAddRecipe');

if (addRecipeBtn && addRecipeSection) {
    addRecipeBtn.addEventListener('click', (e) => {
        e.preventDefault();
        // toggle visibility
        addRecipeSection.classList.toggle('hidden');
        // scroll into view when shown
        if (!addRecipeSection.classList.contains('hidden')) {
            addRecipeSection.scrollIntoView({ behavior: 'smooth' });
        }
    });
}

if (cancelAddRecipe && addRecipeSection) {
    cancelAddRecipe.addEventListener('click', () => {
        addRecipeSection.classList.add('hidden');
        addRecipeForm.reset();
    });
}

if (addRecipeForm) {
    addRecipeForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const title = document.getElementById('recipeTitle').value.trim();
        const category = document.getElementById('recipeCategory').value.trim();
        const imageUrl = document.getElementById('recipeImage').value.trim();
        const imageFile = document.getElementById('recipeImageFile').files[0];
        const description = document.getElementById('recipeDescription').value.trim();
        const ingredients = document.getElementById('recipeIngredients').value.trim();
        const instructions = document.getElementById('recipeInstructions').value.trim();
        const health = document.getElementById('recipeHealth').value.trim();
        const tips = document.getElementById('recipeTips').value.trim();

        if (!title || !category || !description) {
            alert('Please fill title, category and description.');
            return;
        }

        try {
            let resp;
            if (imageFile) {
                const form = new FormData();
                form.append('title', title);
                form.append('category', category);
                form.append('description', description);
                form.append('ingredients', ingredients);
                form.append('instructions', instructions);
                form.append('health', health);
                form.append('tips', tips);
                form.append('image', imageFile);
                resp = await fetch('/api/recipes', { method: 'POST', body: form });
            } else {
                const payload = { title, category, image: imageUrl, description, ingredients, instructions, health, tips };
                resp = await fetch('/api/recipes', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
            }

            if (!resp.ok) {
                const err = await resp.json().catch(() => ({}));
                throw new Error(err.error || 'Failed to save recipe');
            }

            const created = await resp.json();
            addRecipeForm.reset();
            addRecipeSection.classList.add('hidden');
            // redirect to the new recipe page
            if (created && created.id) {
                window.location.href = `/recipe/${created.id}`;
            } else {
                alert('Recipe added successfully!');
            }
        } catch (error) {
            console.error('Error adding recipe:', error);
            alert('Error adding recipe: ' + (error.message || error));
        }
    });
}