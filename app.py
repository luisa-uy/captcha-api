from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from config import Config
from datetime import datetime
from flask_restful import Api, Resource
import random

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
ma = Marshmallow(app)
captcha_size = 4 

class Bloque(db.Model):
	# Modelo para bloques de texto
	__tablename__ = 'bloque'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	path_imagen = db.Column(db.Text)
	imagen = db.Column(db.Text)
	texto = db.Column(db.Text)
	intentos = db.relationship('Intento')
	captchas = db.relationship("Captcha", secondary='bloque_captcha', back_populates='bloques')

class Intento(db.Model):
	# Modelo para intento de lectura
	__tablename__ = 'intento'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	fecha_hora = db.Column(db.DateTime,
						default=datetime.utcnow, 
						onupdate=datetime.utcnow)
	texto = db.Column(db.Text)
	bloque_id = db.Column(db.Integer, db.ForeignKey('bloque.id'), nullable=False)

class Captcha(db.Model):
	# Modelo para Captcha
	__tablename__ = 'captcha'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	fecha_hora = db.Column(db.DateTime, default=datetime.utcnow)
	status = db.Column(db.Boolean, default=False)
	token = db.Column(db.String)
	bloques = db.relationship("Bloque", secondary="bloque_captcha", back_populates='captchas')

class BloqueCaptcha(db.Model):
	# ManyToMany entre Bloque y Captcha
	__tablename__ = 'bloque_captcha'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	bloques = db.Column(db.Integer, db.ForeignKey('bloque.id'))
	captchas = db.Column(db.Integer, db.ForeignKey('captcha.id'))


class BloqueSchema(ma.SQLAlchemyAutoSchema):
	class Meta:
		model = Bloque
		include_fk = True
		load_instance = True
		
class IntentoSchema(ma.SQLAlchemyAutoSchema):
	class Meta:
		model = Intento
		include_fk = True
		load_instance = True

class CaptchaSchema(ma.SQLAlchemyAutoSchema):
	class Meta:
		model = Captcha
		load_instance = True

db.create_all()
bloque_schema = BloqueSchema()
bloques_schema = BloqueSchema(many=True)
intento_schema = IntentoSchema()
intentos_schema = IntentoSchema(many=True)
captcha_schema = CaptchaSchema()

db.session.commit()

@app.route("/")
def hello():
	return "<h1 style='color:blue'>Hello There!</h1>"

@app.route("/api/bloque/")
def get_bloques():
	all_bloques = Bloque.query.all()	
	return (jsonify(bloques_schema.dump(all_bloques)), 200)


@app.route("/api/intento/")
def get_intentos():
	all_intentos = Intento.query.all()
	return (jsonify(intentos_schema.dump(all_intentos)), 200)


@app.route("/api/captcha/")
def obtener_captcha():

	res = []
	size=db.session.query(Bloque).count()
	for i in range(captcha_size):
		res.append(db.session.query(Bloque)[random.randrange(0, size)])
	return jsonify(bloques_schema.dump(res), 200)
		
	try:
		return "OK"
	except Exception as ex:
		return "Error"

if __name__ == "__main__":
	app.run(host='0.0.0.0')
