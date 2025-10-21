from flask import Flask
from flask_cors import CORS
from app.routes import api_bp

app = Flask(__name__)

CORS(app, resources={r"/api/*": {"origins": "http://localhost:8080"}})

app.register_blueprint(api_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5000)