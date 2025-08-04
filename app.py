# app.py (refaktorisan za SQLite + Flask + SQLAlchemy)

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "tajna123")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///resource.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# MODELI
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(10), nullable=False)
    equipment = db.relationship('Equipment', backref='owner', lazy=True)

class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    serial_number = db.Column(db.String(100), unique=True, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(30), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# DEKORATORI

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get("role") != "admin":
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated

# RUTE
@app.route("/")
@login_required
def index():
    return render_template("index.html", username=session["username"], role=session["role"])

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()
        if user and check_password_hash(user.password, request.form["password"]):
            session["username"] = user.username
            session["role"] = user.role
            return redirect(url_for("index"))
        return render_template("login.html", error="Pogrešni podaci")
    return render_template("login.html")

@app.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    return redirect(url_for("login"))

# API ENDPOINTI
@app.route("/api/equipment", methods=["GET"])
@login_required
def get_equipment():
    eq = Equipment.query.all()
    return jsonify([{
        "id": e.id,
        "name": e.name,
        "serial_number": e.serial_number,
        "location": e.location,
        "status": e.status,
        "user": e.owner.username if e.owner else None
    } for e in eq])

@app.route("/api/equipment", methods=["POST"])
@admin_required
def add_equipment():
    data = request.get_json()
    if Equipment.query.filter_by(serial_number=data["serial_number"]).first():
        return jsonify({"error": "Duplikat serijskog broja"}), 400
    user = User.query.get(data["user_id"]) if data.get("user_id") else None
    new_eq = Equipment(
        name=data["name"],
        serial_number=data["serial_number"],
        location=data["location"],
        status=data["status"],
        owner=user
    )
    db.session.add(new_eq)
    db.session.commit()
    return jsonify({"message": "Oprema dodata"})

@app.route("/api/equipment/<int:id>", methods=["PUT"])
@admin_required
def update_equipment(id):
    data = request.get_json()
    eq = Equipment.query.get_or_404(id)
    eq.name = data["name"]
    eq.serial_number = data["serial_number"]
    eq.location = data["location"]
    eq.status = data["status"]
    eq.user_id = data.get("user_id")
    db.session.commit()
    return jsonify({"message": "Oprema izmenjena"})

@app.route("/api/equipment/<int:id>", methods=["DELETE"])
@admin_required
def delete_equipment(id):
    eq = Equipment.query.get_or_404(id)
    db.session.delete(eq)
    db.session.commit()
    return jsonify({"message": "Oprema obrisana"})

@app.route("/api/users", methods=["GET"])
@admin_required
def list_users():
    users = User.query.all()
    return jsonify([{"id": u.id, "username": u.username, "role": u.role} for u in users])

@app.route("/api/users", methods=["POST"])
@admin_required
def create_user():
    data = request.get_json()
    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "Korisničko ime već postoji"}), 400
    new_user = User(
        username=data["username"],
        password=generate_password_hash(data["password"]),
        role=data["role"]
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "Korisnik dodat"})

@app.route("/api/users/<int:id>", methods=["DELETE"])
@admin_required
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "Korisnik obrisan"})

@app.route("/api/users/<int:id>", methods=["PUT"])
@admin_required
def update_user(id):
    data = request.get_json()
    user = User.query.get_or_404(id)
    user.role = data["role"]
    db.session.commit()
    return jsonify({"message": "Uloga izmenjena"})

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
