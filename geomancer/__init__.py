from flask import Flask, render_template
from geomancer.api import api
from geomancer.views import views
from geomancer.redis_session import RedisSessionInterface

def create_app():
    app = Flask(__name__)
    app.config.from_object('geomancer.app_config')
    app.session_interface = RedisSessionInterface()
    app.register_blueprint(api)
    app.register_blueprint(views)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def page_not_found(e):
        return render_template('error.html'), 500

    return app