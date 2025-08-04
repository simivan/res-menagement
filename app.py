import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from functools import wraps

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "tajna_lozinka")

DATABASE = "resource.db"

# --------------------- DB KONFIGURACIJA --------------------- #
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    # Tabela korisnika
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)
    # Tabela opreme
    c.execute("""
        CREATE TABLE IF NOT EXISTS equipment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            serial_number TEXT NOT NULL,
            location TEXT NOT NULL,
            status TEXT NOT NULL,
            user_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()

def create_default_admin():
    conn = get_db_connection()
    c = conn.cursor()
    username = os.getenv("ADMIN_USERNAME", "admin")
    password = os.getenv("ADMIN_PASSWORD", "admin")
    hashed_pw = generate_password_hash(password)
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    if not c.fetchone():
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, hashed_pw, "admin"))
    conn.commit()
    conn.close()

# --------------------- DEKORATORI --------------------- #
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "user_id" in session:
            return f(*args, **kwargs)
        return redirect(url_for("login"))
    return wrap

def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session.get("role") == "admin":
            return f(*args, **kwargs)
        return jsonify({"error": "Unauthorized"}), 403
    return wrap

# --------------------- RUTE --------------------- #
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            return redirect(url_for("index"))
        return render_template("login.html", error="Neispravni kredencijali")
    return render_template("login.html")

@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
@login_required
def index():
    return render_template("index.html", username=session["username"], role=session["role"])

@app.route("/admin")
@login_required
@admin_required
def admin_panel():
    return render_template("admin.html")

# --------------------- API: OPREMA --------------------- #
@app.route("/api/equipment", methods=["GET", "POST"])
@login_required
def equipment_api():
    conn = get_db_connection()
    if request.method == "POST":
        data = request.get_json()
        conn.execute("""
            INSERT INTO equipment (name, serial_number, location, status, user_id)
            VALUES (?, ?, ?, ?, ?)
        """, (data["name"], data["serial_number"], data["location"], data["status"], data.get("user_id")))
        conn.commit()
        conn.close()
        return jsonify({"message": "Oprema dodata"}), 201
    else:
        result = conn.execute("""
            SELECT e.*, u.username as user_name
            FROM equipment e LEFT JOIN users u ON e.user_id = u.id
        """).fetchall()
        conn.close()
        return jsonify([dict(row) for row in result])

@app.route("/api/equipment/<int:id>", methods=["DELETE"])
@login_required
def delete_equipment(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM equipment WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return "", 204

# --------------------- API: KORISNICI --------------------- #
@app.route("/api/users", methods=["GET", "POST"])
@login_required
@admin_required
def users_api():
    conn = get_db_connection()
    if request.method == "POST":
        data = request.get_json()
        hashed_pw = generate_password_hash(data["password"])
        conn.execute("""
            INSERT INTO users (username, password, role)
            VALUES (?, ?, ?)
        """, (data["username"], hashed_pw, data["role"]))
        conn.commit()
        conn.close()
        return jsonify({"message": "Korisnik dodat"}), 201
    else:
        result = conn.execute("SELECT id, username, role FROM users").fetchall()
        conn.close()
        return jsonify([dict(row) for row in result])

@app.route("/api/users/<int:id>", methods=["DELETE"])
@login_required
@admin_required
def delete_user(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM users WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return "", 204

# --------------------- API: Dummy podaci --------------------- #
@app.route("/api/init", methods=["POST"])
@admin_required
def init_dummy_data():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO equipment (name, serial_number, location, status) VALUES (?, ?, ?, ?)",
              ("Laptop Dell", "123456", "Beograd", "aktivna"))
    c.execute("INSERT INTO equipment (name, serial_number, location, status) VALUES (?, ?, ?, ?)",
              ("Printer HP", "789123", "Novi Sad", "na_skladistu"))
    conn.commit()
    conn.close()
    return jsonify({"message": "Test podaci ubačeni"})

# --------------------- MAIN --------------------- #
if __name__ == "__main__":
    init_db()
    create_default_admin()
    app.run(host="0.0.0.0", port=5000, debug=True)
