import os
from flask import Flask, render_template, request, send_file
import json
import io
import zipfile
import requests
from dotenv import load_dotenv
import re

load_dotenv()

app = Flask(__name__)

# --- CONFIGURATION ---
API_KEY = os.getenv("GENAI_API_KEY")
print(f"🔑 KEY LOADED: {'YES' if API_KEY else 'NO'}")

# --- THEMES ---
THEMES = {
    "minimalist": { "name": "Modern Minimal", "layout_type": "grid", "aos_mode": "fade-up", "--bg": "#ffffff", "--text": "#121212", "--accent": "#000000", "--font-h": "'Inter', sans-serif", "--font-b": "'Inter', sans-serif", "--radius": "0px", "--card-bg": "#f9f9f9" },
    "cyberpunk": { "name": "Neon Future", "layout_type": "sidebar", "aos_mode": "flip-left", "--bg": "#050505", "--text": "#e0e0e0", "--accent": "#00ff9d", "--font-h": "'Orbitron', sans-serif", "--font-b": "'Rajdhani', sans-serif", "--radius": "4px", "--card-bg": "rgba(0, 255, 157, 0.05)" },
    "luxury": { "name": "Golden Luxury", "layout_type": "centered", "aos_mode": "zoom-in", "--bg": "#0f0f0f", "--text": "#f0f0f0", "--accent": "#d4af37", "--font-h": "'Playfair Display', serif", "--font-b": "'Lato', sans-serif", "--radius": "2px", "--card-bg": "#1a1a1a" },
    "nature": { "name": "Organic Earth", "layout_type": "grid", "aos_mode": "fade-right", "--bg": "#f4f1ea", "--text": "#2c3e2e", "--accent": "#4a6741", "--font-h": "'DM Serif Display', serif", "--font-b": "'Nunito', sans-serif", "--radius": "20px", "--card-bg": "#e9e5db" },
    "terminal": { "name": "Hacker Console", "layout_type": "terminal", "aos_mode": "slide-up", "--bg": "#000000", "--text": "#00ff00", "--accent": "#00aa00", "--font-h": "'Fira Code', monospace", "--font-b": "'Fira Code', monospace", "--radius": "0px", "--card-bg": "#111" },
    "retro": { "name": "Retro 90s", "layout_type": "centered", "aos_mode": "flip-up", "--bg": "#2b0f3a", "--text": "#ffe6f2", "--accent": "#ff00ff", "--font-h": "'Press Start 2P', cursive", "--font-b": "'VT323', monospace", "--radius": "0px", "--card-bg": "rgba(255, 0, 255, 0.1)" },
    "corporate": { "name": "Corporate Pro", "layout_type": "grid", "aos_mode": "fade-up", "--bg": "#ffffff", "--text": "#2d3436", "--accent": "#0984e3", "--font-h": "'Roboto', sans-serif", "--font-b": "'Open Sans', sans-serif", "--radius": "6px", "--card-bg": "#f1f2f6" },
    "brutalist": { "name": "Neo-Brutalist", "layout_type": "sidebar", "aos_mode": "zoom-out-right", "--bg": "#e0e0e0", "--text": "#000000", "--accent": "#ff4757", "--font-h": "'Archivo Black', sans-serif", "--font-b": "'Courier Prime', monospace", "--radius": "0px", "--card-bg": "#ffffff" },
    "pastel": { "name": "Soft Pastel", "layout_type": "grid", "aos_mode": "fade-down", "--bg": "#fff0f5", "--text": "#5e548e", "--accent": "#9f86c0", "--font-h": "'Quicksand', sans-serif", "--font-b": "'Mulish', sans-serif", "--radius": "30px", "--card-bg": "#ffffff" },
    "saas": { "name": "Dark SaaS", "layout_type": "grid", "aos_mode": "fade-up", "--bg": "#0b0c15", "--text": "#a0a0b0", "--accent": "#7c3aed", "--font-h": "'Inter', sans-serif", "--font-b": "'Inter', sans-serif", "--radius": "12px", "--card-bg": "#151621" }
}

# --- AUTO-DISCOVERY SYSTEM ---
def find_working_model():
    print("\n🔍 SYSTEM CHECK: Searching for available AI models...")
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
        response = requests.get(url)
        if response.status_code != 200: return None
        data = response.json()
        for model in data.get('models', []):
            if "generateContent" in model.get('supportedGenerationMethods', []) and 'gemini' in model['name']:
                print(f"✅ FOUND WORKING MODEL: {model['name']}")
                return model['name']
        return "models/gemini-pro"
    except: return None

ACTIVE_MODEL = find_working_model()

def clean_json_text(text):
    text = text.replace('```json', '').replace('```', '')
    return text.strip()

def generate_ai_content(name, role, skills, theme_key):
    target_model = ACTIVE_MODEL if ACTIVE_MODEL else "models/gemini-pro"
    print(f"\n🚀 ASKING AI ({target_model}): {name}...")
    
    # --- STRICT VISUAL PROMPT ---
    prompt = f"""
    Create a JSON portfolio for: Name: {name}, Role: {role}, Skills: {skills}.
    REQUIREMENTS:
    1. Output VALID JSON ONLY.
    2. Structure:
    {{
        "tagline": "Str", "bio": "Str", "stats": [{{"label":"Str","value":"Str"}}],
        "hard_skills": ["Str"], "timeline": [{{"year":"Str","company":"Str","role":"Str","achievements":["Str"]}}],
        "projects": [
            {{
                "title":"Str",
                "image_prompt": "A LITERAL, PHYSICAL description of the project for an image generator. Do NOT use abstract words like 'solution' or 'efficiency'. DESCRIBE THE OBJECTS. Example: 'A close up of a circuit board with glowing red lights', 'A laptop screen displaying a medical x-ray interface', 'A futuristic drone flying over a farm field'.",
                "tech":"Str", "desc":"Str", "impact":"Str"
            }}
        ],
        "education": [{{"degree":"Str","school":"Str","year":"Str"}}], "testimonials": [{{"quote":"Str","author":"Str"}}]
    }}
    """

    if not target_model.startswith("models/"): target_model = f"models/{target_model}"
    url = f"https://generativelanguage.googleapis.com/v1beta/{target_model}:generateContent?key={API_KEY}"
    
    try:
        response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
        if response.status_code == 200:
            data = response.json()
            if 'candidates' in data and data['candidates']:
                raw = data['candidates'][0]['content']['parts'][0]['text']
                print(f"✅ SUCCESS!")
                return json.loads(clean_json_text(raw))
        else:
            print(f"❌ API ERROR: {response.text}")
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")

    # Fallback
    return {
        "tagline": "Server Connection Failed", 
        "bio": "Check API Key.", 
        "stats": [], "hard_skills": [], "timeline": [], 
        "projects": [{"title": "Error", "image_prompt": "red warning sign 3d render", "tech": "Error", "desc": "Error", "impact": "0"}], 
        "education": [], "testimonials": []
    }

@app.route('/')
def index():
    return render_template('index.html', themes=THEMES)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.form
    theme_key = data.get('theme', 'minimalist')
    content = generate_ai_content(data['name'], data['role'], data['skills'], theme_key)
    styles = THEMES.get(theme_key, THEMES['minimalist'])
    return render_template('portfolio.html', name=data['name'], content=content, styles=styles)

@app.route('/download', methods=['POST'])
def download():
    html_content = request.form.get('html_source')
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        zf.writestr('index.html', html_content)
    memory_file.seek(0)
    return send_file(memory_file, download_name='portfolio.zip', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)