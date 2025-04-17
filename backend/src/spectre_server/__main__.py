from flask import Flask
from spectre_core.logs import configure_root_logger
from spectre_core.logs import ProcessType

from .config import SPECTRE_SERVICE_HOST, SPECTRE_SERVICE_PORT
from .routes.batches import batches_blueprint
from .routes.capture_configs import capture_configs_blueprint
from .routes.receivers import receivers_blueprint
from .routes.jobs import jobs_blueprint
from .routes.logs import logs_blueprint
from .routes.callisto import callisto_blueprint

app = Flask(__name__)

# Register blueprints
app.register_blueprint(batches_blueprint)
app.register_blueprint(callisto_blueprint)
app.register_blueprint(capture_configs_blueprint)
# app.register_blueprint(logs_blueprint) 
# app.register_blueprint(receivers_blueprint) 
# app.register_blueprint(jobs_blueprint)


if __name__ == "__main__":
    configure_root_logger(ProcessType.USER)
    app.run(host=SPECTRE_SERVICE_HOST, 
            port=SPECTRE_SERVICE_PORT,
            debug=True)
