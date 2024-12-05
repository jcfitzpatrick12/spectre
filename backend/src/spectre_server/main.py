from flask import Flask
from spectre_core.logging import configure_root_logger

from spectre_server.routes.configs import configs_blueprint

app = Flask(__name__)

# Register blueprints for modularity 
# app.register_blueprint(start_blueprint, url_prefix="/start")
# app.register_blueprint(create_blueprint, url_prefix="/create")
# app.register_blueprint(delete_blueprint, url_prefix="/delete")
# app.register_blueprint(get_blueprint, url_prefix="/get")
# app.register_blueprint(test_blueprint, url_prefix="/test")
# app.register_blueprint(update_blueprint, url_prefix="/update")
# app.register_blueprint(web_fetch_blueprint, url_prefix="/web-fetch")


if __name__ == "__main__":
    configure_root_logger("USER")
    app.run(host="0.0.0.0", 
            port=5000, 
            debug=True)
