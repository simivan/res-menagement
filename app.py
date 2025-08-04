import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv("SECRET_KEY", "tajna")

# Testna baza u memoriji
equipment = []
users = [{"id": 1, "username": os.getenv("ADMIN_USERNAME"), "password": generate_password_hash(os.getenv("ADMIN_PASSWORD")), "role": "admin"}]
equipment_log = []
id_counter = {"equipment": 1, "users": 2}

def get_user_by_username(username):
    return next((u for u in users if u["username"] == username), None)

@app.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user = next(u for u in users if u["id"] == session["user_id"])
    return render_template("index.html", username=user["username"], role=user["role"])

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = get_user_by_username(request.form["username"])
        if user and check_password_hash(user["password"], request.form["password"]):
            session["user_id"] = user["id"]
            return redirect(url_for("index"))
        return render_template("login.html", error="Neispravno korisničko ime ili lozinka.")
    return render_template("login.html")

@app.route("/logout", methods=["POST", "GET"])
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/api/equipment", methods=["GET", "POST"])
def api_equipment():
    if request.method == "POST":
        data = request.json
        item = {
            "id": id_counter["equipment"],
            "name": data["name"],
            "serial_number": data["serial_number"],
            "location": data["location"],
            "status": data["status"],
            "user_id": data.get("user_id"),
        }
        equipment.append(item)
        id_counter["equipment"] += 1
        return jsonify(item), 201
    return jsonify(equipment)

@app.route("/api/equipment/<int:item_id>", methods=["DELETE"])
def delete_equipment(item_id):
    global equipment
    equipment = [e for e in equipment if e["id"] != item_id]
    return "", 204

@app.route("/api/users", methods=["GET", "POST"])
def api_users():
    if request.method == "POST":
        data = request.json
        user = {
            "id": id_counter["users"],
            "username": data["username"],
            "password": generate_password_hash(data["password"]),
            "role": data["role"]
        }
        users.append(user)
        id_counter["users"] += 1
        return jsonify({"id": user["id"], "username": user["username"], "role": user["role"]}), 201
    return jsonify([{"id": u["id"], "username": u["username"], "role": u["role"]} for u in users])

@app.route("/api/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    global users
    users = [u for u in users if u["id"] != user_id]
    return "", 204

if __name__ == "__main__":
    app.run(debug=True)
