import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def call_api(text_query):
    url = "https://srch-main.api.eduki.info/api/v3/query-intent/predict"
    headers = {"Content-Type": "application/json"}
    payload = {"text": text_query}

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        print("API Response:", result)  # Debug print
        return result
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

@app.route('/', methods=['GET', 'POST'])
def home():
    result = None
    category_intents = []
    grade_intents = []
    if request.method == 'POST':
        query = request.form.get('query', '')
        if query:
            result = call_api(query)
            # Extract category and grade intents with confidence
            tags = result.get('tags', {}) if isinstance(result, dict) else {}
            category_intents = tags.get('category', [])
            grade_intents = tags.get('grade', [])
    return render_template('index.html', result=result, category_intents=category_intents, grade_intents=grade_intents)

if __name__ == "__main__":
    app.run(debug=True) 