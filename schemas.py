from marshmallow import Schema, fields, validate

class UserRegisterSchema(Schema):
    username = fields.String(required=True, validate=validate.Length(min=3, max=80))
    password = fields.String(required=True, validate=validate.Length(min=6))

class UserLoginSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)

class AppointmentSchema(Schema):
    id = fields.Integer(dump_only=True)
    patient_id = fields.Integer(dump_only=True)
    date = fields.String(
        required=True,
        validate=validate.Regexp(r'^\d{4}-\d{2}-\d{2}$', error="Date must be in YYYY-MM-DD format.")
    )
    time = fields.String(
        required=True,
        validate=validate.Regexp(r'^\d{2}:\d{2}$', error="Time must be in HH:MM format (e.g., 14:30).")
    )
    notes = fields.String(validate=validate.Length(max=200))