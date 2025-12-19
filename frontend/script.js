const dom = {
    quiz: document.getElementById('quiz-view'),
    portfolio: document.getElementById('portfolio-view'),
    loader: document.getElementById('loader'),
    btn: document.getElementById('generate-btn'),
    tagline: document.getElementById('tagline'),
    bio: document.getElementById('bio'),
    grid: document.getElementById('projects'),
    reset: document.getElementById('reset-btn')
};

lucide.createIcons();

dom.btn.addEventListener('click', async () => {
    dom.loader.classList.remove('hidden');

    const data = {
        structure: document.getElementById('structure').value,
        energy: document.getElementById('energy').value,
        warmth: document.getElementById('warmth').value
    };

    try {
        const res = await fetch('http://127.0.0.1:5000/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await res.json();
        applyTheme(result.archetype, result.content);

    } catch (e) {
        alert("Server Error. Check Python Console.");
        dom.loader.classList.add('hidden');
    }
});

function applyTheme(archetype, content) {
    // 1. Set The Visual Theme
    document.body.setAttribute('data-theme', archetype);

    // 2. Inject Content (Typewriter Effect)
    setTimeout(() => {
        dom.loader.classList.add('hidden');
        dom.quiz.classList.add('hidden');
        dom.portfolio.classList.remove('hidden');
        
        dom.tagline.innerHTML = content.tagline;
        dom.bio.innerHTML = content.bio;
        
        dom.grid.innerHTML = '';
        content.projects.forEach(p => {
            dom.grid.innerHTML += `
                <div class="card">
                    <h3>${p.title}</h3>
                    <p>${p.desc}</p>
                </div>
            `;
        });
        lucide.createIcons();
    }, 1000);
}

dom.reset.addEventListener('click', () => location.reload());