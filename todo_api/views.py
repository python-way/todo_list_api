from todo_api import app
from todo_api.database import db_session
from todo_api.models import User, Todo


from flask import jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash

@app.route("/")
def home():
    return "HELLO WORLD!"

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

    return jsonify({'message': 'User registered successfully', 'username':new_user.name, 'email':new_user.email}), 200

    
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']

    if not email or not password:
        return jsonify({'message': 'email and password are required'}), 400

    user = User.query.filter_by(email=email).first()
    if user:
        if check_password_hash(user.password, password):
            return jsonify({'massage': 'Logged in successfully'}), 200
        else:
            return jsonify({'message': "Wrong password"}), 400
    else:
        return jsonify({'User does not exist'}), 400

#### CRUD
@app.route("/todos", methods=["POST"])
def add_todo():
    data = request.get_json()
    title = data['title']
    desc  = data['description']

    if not title or not desc:
        return jsonify({ 'message': 'title and description are required'}), 400
    new_todo = Todo(title=title, description=desc)
    db_session.add(new_todo)
    db_session.commit()
    return jsonify({ 'message': 'todo created successfully', 'todo_title':new_todo.title}), 201

@app.route("/todos/<int:todo_id>", methods=["PUT"])
def update_todo(todo_id):
    data = request.get_json()
    title = data['title']
    desc = data['description']

    todo = Todo.query.get(todo_id)
    if not todo:
        return jsonify({'message': 'todo does not exist'})

    todo.title = title if title else todo.title
    todo.description = desc if desc else todo.description
    db_session.commit()    

    return jsonify({'message': 'todo updated successfully', 'todo_title':todo.title, 'todo_desc':todo.description}), 200

@app.route("/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if not todo:
        return jsonify({'message': 'todo does not exist'}), 400

    db_session.delete(todo)
    db_session.commit()

    return jsonify({'message': 'todo deleted successfully'}), 204
    

@app.route("/todos", methods=["GET"])
def get_todos():
    todos = Todo.query.all()
    return jsonify([{'id':todo.id, 'title':todo.title, 'description':todo.description} for todo in todos])





@app.teardown_appcontext
def shutdown_seesion(exception=None):
    db_session.remove()
