from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

class Bloque(db.Model):
	"""Modelo para bloques de texto"""
	__tablename__ = 'bloque'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	path_imagen = db.Column(db.Text)
	imagen = db.Column(db.Text)
	texto = db.Column(db.Text)
	intentos = db.relationship('Intento')

	def __repr__(self):
		return '<Bloque {}>'.format(self.path_imagen)

class Intento(db.Model):
	"""Modelo para intento de lectura"""
	__tablename__ = 'intento'
	fecha_hora = db.Column(db.DateTime, primary_key=True)
	texto = db.Column(db.Text)
	bloque_id = db.Column(db.Integer, db.ForeignKey('bloque.id'), nullable=False)

	def __repr__(self):
		return '<Intento {}>'.format(self.texto)

db.create_all()

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
