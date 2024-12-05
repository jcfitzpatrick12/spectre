from flask import Flask
from spectre_core.logging import configure_root_logger

from spectre_server.routes.chunks import chunks_blueprint
from spectre_server.routes.configs import configs_blueprint
from spectre_server.routes.receivers import receivers_blueprint
from spectre_server.routes.jobs import jobs_blueprint
from spectre_server.routes.logs import logs_blueprint
from spectre_server.routes.callisto import callisto_blueprint

app = Flask(__name__)

# Register blueprints
app.register_blueprint(chunks_blueprint, 
                       url_prefix = "/spectre-data/chunks")
app.register_blueprint(configs_blueprint, 
                       url_prefix = "/spectre-data/configs")
app.register_blueprint(logs_blueprint, 
                       url_prefix="/spectre-data/logs")
app.register_blueprint(receivers_blueprint, 
                       url_prefix="/receivers")
app.register_blueprint(jobs_blueprint, 
                       url_prefix="/jobs")
app.register_blueprint(callisto_blueprint, 
                       url_prefix="/callisto")

if __name__ == "__main__":
    configure_root_logger("user")
    app.run(host="0.0.0.0", 
            port=5000, 
            debug=True)
