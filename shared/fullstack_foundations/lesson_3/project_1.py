# Basic flask app.

from flask import Flask
app = Flask(__name__)

@app.route('/')
@app.route('/hello')
def hello_world():
	return 'Hello world!'

if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0', port=5000)
