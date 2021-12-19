from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify
from config import Config
from datetime import datetime

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
	fecha_hora = db.Column(db.DateTime, 
						primary_key=True,
						default=datetime.utcnow, 
						onupdate=datetime.utcnow)
	texto = db.Column(db.Text)
	bloque_id = db.Column(db.Integer, db.ForeignKey('bloque.id'), nullable=False)

	def __repr__(self):
		return '<Intento {}>'.format(self.texto)

db.create_all()

@app.route("/")
def hello():
	return "<h1 style='color:blue'>Hello There!</h1>"

@app.route("/bloque", methods=['GET'])
def get_bloques():
	bloques = Bloque.query.order_by(Bloque.id).all()
	for bloque in bloques:
		print(f'{bloque.id} {bloque.path_imagen} {bloque.texto}')
	return jsonify(bloques)

@app.route("/captcha")
def obtener_captcha():
	try:
		return "OK"
	except Exception as ex:
		return "Error"

if __name__ == "__main__":
	app.run(host='0.0.0.0')
