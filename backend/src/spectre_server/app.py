from flask import Flask
from spectre_server.api.capture import capture_blueprint

app = Flask(__name__)

# Register blueprints for modularity
app.register_blueprint(capture_blueprint, url_prefix="/capture")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
