import os
from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello, World!'


if __name__ == '__main__':
    app.run(host=os.environ.get('FLASK_RUN_HOST', '0.0.0.0'))
