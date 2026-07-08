from sqlalchemy import Column, Integer, String
from todo_api.database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(200), nullable=False)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password
    
    def __repr__(self):
        return f"<User {self.name!r}>"

class Todo(Base):
    __tablename__ = 'todos'
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(String(1000))

    def __init__(self, title, description):
        self.title = title
        self.description = description

    def __repr__(self):
        return f"<Todo {self.title!r}>"

