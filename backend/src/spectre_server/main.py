from flask import Flask
from spectre_core.logging import configure_root_logger

from spectre_server.routes.capture import capture_blueprint

app = Flask(__name__)

# Register blueprints for modularity 
app.register_blueprint(capture_blueprint, url_prefix="/capture")


if __name__ == "__main__":
    configure_root_logger("USER")
    app.run(host="0.0.0.0", 
            port=5000, 
            debug=True)
