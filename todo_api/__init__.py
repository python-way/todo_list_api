from flask import Flask
from todo_api.database import init_db

app = Flask(__name__)
init_db()

import todo_api.views

