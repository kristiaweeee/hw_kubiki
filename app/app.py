from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import redis
import os
from prometheus_client import generate_latest
from flask import Response

app = Flask(__name__)

@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype="text/plain")

# Подключение к Postgres
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Подключение к Redis
redis_client = redis.Redis(host="redis", port=6379)

# Модель таблицы users
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))

# Создаём таблицы при старте приложения
#with app.app_context():
#    db.create_all()


# ======================
# CREATE
# ======================
@app.route("/users", methods=["POST"])
def create_user():
    data = request.json
    user = User(name=data["name"], email=data["email"])
    db.session.add(user)
    db.session.commit()
    redis_client.flushall()  # сброс кеша
    return jsonify({"message": "User created"}), 201


# ======================
# READ ALL (с кешированием)
# ======================
@app.route("/users", methods=["GET"])
def get_users():
    cached = redis_client.get("users")

    if cached:
        return cached, 200, {"Content-Type": "application/json"}

    users = User.query.all()
    result = [{"id": u.id, "name": u.name, "email": u.email} for u in users]

    response = jsonify(result)

    # кешируем результат в Redis на 60 секунд
    redis_client.setex("users", 60, response.get_data())

    return response


# ======================
# READ ONE
# ======================
@app.route("/users/<int:id>", methods=["GET"])
def get_user(id):
    user = User.query.get(id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email
    })


# ======================
# UPDATE
# ======================
@app.route("/users/<int:id>", methods=["PUT"])
def update_user(id):
    user = User.query.get(id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    data = request.json
    user.name = data.get("name", user.name)
    user.email = data.get("email", user.email)

    db.session.commit()
    redis_client.flushall()

    return jsonify({"message": "Updated"})


# ======================
# DELETE
# ======================
@app.route("/users/<int:id>", methods=["DELETE"])
def delete_user(id):
    user = User.query.get(id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()
    redis_client.flushall()

    return jsonify({"message": "Deleted"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
