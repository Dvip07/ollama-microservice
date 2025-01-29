from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/llm', methods=['POST'])
def query_llm():
    # Get input text from the request
    input_text = request.json.get('text', '')

    # Run the Ollama model with the input text
    try:
        result = subprocess.run(
            ['ollama', 'run', 'llama'],
            input=input_text,
            text=True,
            capture_output=True
        )
        response = result.stdout.strip()
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000)
