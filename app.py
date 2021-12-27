from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from config import Config
from datetime import datetime, date
from sqlalchemy.dialects.postgresql import UUID
from marshmallow_sqlalchemy.fields import Nested
import random
import uuid

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
ma = Marshmallow(app)
captcha_size = 4 

#TODO: Ponerle Status (para saber el estado del bloque)
class Bloque(db.Model):
	# Modelo para bloques de texto
	__tablename__ = 'bloque'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	# status = db.Column(db.Integer, default=0)
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
	status = db.Column(db.Integer, default=0)
	token = db.Column(UUID(as_uuid=True), default=uuid.uuid4)
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
	class Meta(BloqueSchema.Meta):
		model = Captcha
		load_instance = True
		include_relationships = True
	bloques = Nested(BloqueSchema(many=True))

db.create_all()
db.session.commit()

@app.route("/")
def hello():
	return "<h1 style='color:blue'>Hello There!</h1>"

@app.route("/api/bloque/")
def get_bloques():
	all_bloques = Bloque.query.all()	
	return (jsonify(BloqueSchema(many=True).dump(all_bloques)), 200)


@app.route("/api/intento/")
def get_intentos():
	all_intentos = Intento.query.all()
	return (jsonify(IntentoSchema(many=True).dump(all_intentos)), 200)


@app.route("/api/captcha/")
def obtener_captcha():

	captcha = Captcha()
	size=db.session.query(Bloque).count()
	for i in range(captcha_size):
		captcha.bloques.append(db.session.query(Bloque)[random.randrange(0, size)])

	db.session.add(captcha)
	db.session.commit()
	return  jsonify(captcha=CaptchaSchema().dump(captcha), status=200)


if __name__ == "__main__":
	app.run(host='0.0.0.0')
