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
    if request.method == 'POST':
        query = request.form.get('query', '')
        if query:
            result = call_api(query)
    return render_template('index.html', result=result)

if __name__ == "__main__":
    app.run(debug=True) 