import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import numpy as np
from sklearn.neighbors import NearestNeighbors
import json

app = Flask(__name__)
CORS(app)

# 🔑 PASTE YOUR KEY HERE
GOOGLE_API_KEY = "AIzaSyDJZ--Ndof7rELsqmBtfx4K9CO5gY1ZQ5Q"
genai.configure(api_key=GOOGLE_API_KEY)

# --- THE 10 ARCHETYPES ---
ARCHETYPES = {
    0: "swiss", 1: "cyber", 2: "brutal", 3: "ethereal", 4: "midnight",
    5: "paper", 6: "bauhaus", 7: "y2k", 8: "botanical", 9: "obsidian"
}

# Training Data
X_train = np.array([
    [100, 0, 0], [100, 100, 0], [0, 100, 0], [10, 10, 100], [50, 50, 30],
    [30, 20, 90], [80, 60, 80], [40, 90, 50], [20, 10, 70], [90, 10, 20]
])

model = NearestNeighbors(n_neighbors=1).fit(X_train)

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        s = int(data.get('structure', 50))
        e = int(data.get('energy', 50))
        w = int(data.get('warmth', 50))
        
        distances, indices = model.kneighbors([[s, e, w]])
        archetype_id = ARCHETYPES[indices[0][0]]
        
        print(f"Matched: {archetype_id.upper()}")

        try:
            gemini = genai.GenerativeModel('gemini-pro')
            prompt = f"""
            Generate a JSON portfolio for a designer with the '{archetype_id}' aesthetic.
            Traits: Structure {s}%, Energy {e}%, Warmth {w}%.
            
            Generate unique 'stats' relevant to this specific personality (e.g., Cyber has 'Uptime', Botanical has 'Growth Rate').
            
            Output valid JSON only:
            {{
                "tagline": "Short Header",
                "bio": "Two sentence bio.",
                "manual": "A 1-sentence 'User Manual' or generalized fact about this style.",
                "stats": [
                    {{"label": "Unique Stat 1", "value": 85}}, 
                    {{"label": "Unique Stat 2", "value": 90}}, 
                    {{"label": "Unique Stat 3", "value": 40}}
                ],
                "projects": [
                    {{"title": "Project A", "desc": "Desc"}},
                    {{"title": "Project B", "desc": "Desc"}},
                    {{"title": "Project C", "desc": "Desc"}}
                ]
            }}
            """
            response = gemini.generate_content(prompt)
            clean_json = response.text.replace("```json", "").replace("```", "")
            content = json.loads(clean_json)
        except Exception as err:
            print(f"AI Error: {err}")
            content = {
                "tagline": "Offline Mode", "bio": "AI unavailable.",
                "manual": "System requires manual reboot.",
                "stats": [{"label": "Error", "value": 0}],
                "projects": []
            }

        return jsonify({"archetype": archetype_id, "content": content})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)