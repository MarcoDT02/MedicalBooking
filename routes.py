from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from sqlalchemy.exc import IntegrityError
from models import User, Appointment, db
from schemas import UserRegisterSchema, UserLoginSchema, AppointmentSchema

api_bp = Blueprint("api", __name__, url_prefix="/api")

user_register_schema = UserRegisterSchema()
user_login_schema = UserLoginSchema()
appointment_schema = AppointmentSchema()
appointments_list_schema = AppointmentSchema(many=True)


@api_bp.route("/register", methods=["POST"])
def register():
    data = user_register_schema.load(request.get_json() or {})
    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "Conflict", "message": "Username already exists."}), 409

    new_user = User(username=data["username"])
    new_user.set_password(data["password"])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully!", "user_id": new_user.id}), 201


@api_bp.route("/login", methods=["POST"])
def login():
    data = user_login_schema.load(request.get_json() or {})
    user = User.query.filter_by(username=data["username"]).first()
    if not user or not user.check_password(data["password"]):
        return jsonify({"error": "Unauthorized", "message": "Invalid credentials."}), 401

    access_token = create_access_token(identity=str(user.id))
    return jsonify({"message": "Login successful!", "access_token": access_token}), 200


@api_bp.route("/appointments", methods=["POST"])
@jwt_required()
def book_appointment():
    current_user_id = get_jwt_identity()
    data = appointment_schema.load(request.get_json() or {})

    new_app = Appointment(
        patient_id=int(current_user_id),
        date=data["date"],
        time=data["time"],
        notes=data.get("notes", "")
    )
    db.session.add(new_app)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "error": "Conflict",
            "message": f"The time {data['time']} on {data['date']} is already booked by someone else."
        }), 409

    return jsonify({
        "message": "Appointment booked successfully!",
        "appointment": appointment_schema.dump(new_app)
    }), 201


@api_bp.route("/appointments", methods=["GET"])
@jwt_required()
def get_my_appointments():
    current_user_id = get_jwt_identity()
    appointments = Appointment.query.filter_by(patient_id=current_user_id).all()
    return jsonify({
        "count": len(appointments),
        "appointments": appointments_list_schema.dump(appointments)
    }), 200