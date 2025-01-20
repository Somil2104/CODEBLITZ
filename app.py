from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    # Mock code evaluation response
    return jsonify({'status': 'success', 'output': 'Hello, World!'})

if __name__ == '__main__':
    app.run(debug=True)