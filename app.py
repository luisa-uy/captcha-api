from flask import Flask
from Flask import request
from flask_sqlalchemy import SQLAlchemy
from config import Config
from captchaluisa.models import Bloque, Intento

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

@app.route("/")
def hello():
	return "<h1 style='color:blue'>Hello There!</h1>"

@app.route("/captcha")
def obtener_captcha():
	try:
		return "OK"
	except Exception as ex:
		return "Error"

if __name__ == "__main__":
	app.run(host='0.0.0.0')
