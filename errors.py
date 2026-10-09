from flask import jsonify
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException

def register_error_handlers(app, jwt=None):
    @app.errorhandler(ValidationError)
    def handle_validation_error(err):
        return jsonify({
            "error": "Validation Error",
            "message": "Invalid input data.",
            "details": err.messages
        }), 400

    @app.errorhandler(HTTPException)
    def handle_http_exception(err):
        return jsonify({"error": err.name, "message": err.description}), err.code

    @app.errorhandler(Exception)
    def handle_unexpected_exception(err):
        return jsonify({
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please try again later."
        }), 500

    if jwt:
        @jwt.unauthorized_loader
        def missing_token_callback(error):
            return jsonify({
                "error": "Authorization Required",
                "message": "Authorization token is missing."
            }), 401

        @jwt.invalid_token_loader
        def invalid_token_callback(error):
            return jsonify({
                "error": "Invalid Token",
                "message": "The provided token is invalid."
            }), 401

        @jwt.expired_token_loader
        def expired_token_callback(jwt_header, jwt_payload):
            return jsonify({
                "error": "Token Expired",
                "message": "The provided token has expired."
            }), 401