import os
from errors import register_error_handlers
from flask import Flask
from flask_jwt_extended import JWTManager
from models import db
from routes import api_bp

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "postgresql+psycopg2://postgres:PASSWORD@localhost:5432/booking_db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "super_secret_booking_key_2026"

jwt = JWTManager(app)
db.init_app(app)

register_error_handlers(app, jwt=jwt)
app.register_blueprint(api_bp)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)