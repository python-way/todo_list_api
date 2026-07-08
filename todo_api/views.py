from todo_api import app
from todo_api.database import db_session
from todo_api.models import User, Todo

from flask import jsonify, request

from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import jwt
import datetime

app.config['SECRET_KEY'] = 'your_secret_key_here'


## Authentication
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # JWT is expected in the Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        if not token:
            return jsonify({'message': 'Unauthorized'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = data['email']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401

        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/', methods=['GET'])
@token_required
def protected(current_user):
    return jsonify({'message': f'Hello {current_user}, you have access to this route!'})


@app.route("/register", methods=["POST"])
def register_user():
    data = request.get_json()
    username = data['name']
    password = data['password']
    email = data['email']

    if not username or not password or not email:
        return jsonify({'message': 'Username, email and password are required'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'User already exists'}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(name=username, email=email, password=hashed_password)
    db_session.add(new_user)
    db_session.commit()

    token = jwt.encode({
        'email': new_user.email,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    }, app.config['SECRET_KEY'], algorithm="HS256")

    return jsonify({'token': token})


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']

    if not email or not password:
        return jsonify({'message': 'email and password are required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'message': 'Invalid credentials'}), 401


    token = jwt.encode({
        'email': user.email,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    }, app.config['SECRET_KEY'], algorithm="HS256")

    return jsonify({'token': token})

#### CRUD
@app.route("/todos", methods=["POST"])
@token_required
def add_todo(current_user):
    data = request.get_json()
    title = data['title']
    desc  = data['description']

    if not title or not desc:
        return jsonify({ 'message': 'title and description are required'}), 400
    new_todo = Todo(title=title, description=desc, owner=current_user)
    db_session.add(new_todo)
    db_session.commit()

    return jsonify({ 'id':new_todo.id, 'title':new_todo.title, 'description': new_todo.description}), 201

@app.route("/todos/<int:todo_id>", methods=["PUT"])
@token_required
def update_todo(current_user, todo_id):
    data = request.get_json()
    title = data['title']
    desc = data['description']

    todo = Todo.query.get(todo_id)
    if not todo:
        return jsonify({'message': 'todo does not exist'})

    if current_user != todo.owner:
        return jsonify({'message': 'Forbidden'})

    todo.title = title if title else todo.title
    todo.description = desc if desc else todo.description
    db_session.commit()    

    return jsonify({'id': todo.id, 'title':todo.title, 'description':todo.description}), 200

@app.route("/todos/<int:todo_id>", methods=["DELETE"])
@token_required
def delete_todo(current_user, todo_id):
    todo = Todo.query.get(todo_id)
    if not todo:
        return jsonify({'message': 'todo does not exist'}), 400

    if current_user != todo.owner:
        return jsonify({'message': 'Forbidden'})

    db_session.delete(todo)
    db_session.commit()

    return jsonify({'message': 'todo deleted successfully'}), 204
    

@app.route("/todos", methods=["GET"])
@token_required
def get_todos(current_user):
    todos = Todo.query.filter_by(owner=current_user).all()
    return jsonify([{'id':todo.id, 'title':todo.title, 'description':todo.description} for todo in todos])





@app.teardown_appcontext
def shutdown_seesion(exception=None):
    db_session.remove()
