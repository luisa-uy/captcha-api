from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from config import Config
from datetime import datetime, date
from sqlalchemy.dialects.postgresql import UUID
from marshmallow_sqlalchemy.fields import Nested
from flask_jsonpify import jsonpify
from flask_cors import CORS, cross_origin
import random
import uuid

app = Flask(__name__)
app.config.from_object(Config)
app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app)
db = SQLAlchemy(app)
ma = Marshmallow(app)
captcha_size = 4 

class Bloque(db.Model):
	# Modelo para bloques de texto
	__tablename__ = 'bloque'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	# status ­— 0: sin_conocer, 1: conocido, 2: inválido
	status = db.Column(db.Integer, default=0)
	path_imagen = db.Column(db.Text)
	imagen = db.Column(db.Text)
	texto = db.Column(db.Text)
	intentos = db.relationship('Intento')
	captchas = db.relationship("Captcha", secondary='bloque_captcha', back_populates='bloques')

# TODO: Guardar el estado del Intento para saber si es fallido (cuando se conoce el valor)
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

def post_intento(bloque_id, texto):
	intento = Intento()
	intento.bloque_id = bloque_id
	intento.texto = texto
	db.session.add(intento)
	db.session.commit()
	return intento

@app.route("/")
def hello():
	return "<h1 style='color:blue'>Hello There!</h1>"

@app.route("/api/bloque/")
def get_bloques():
	all_bloques = Bloque.query.all()	
	return (jsonify(BloqueSchema(many=True).dump(all_bloques)), 200), 200


@app.route("/api/intento/")
def get_intentos():
	all_intentos = Intento.query.all()
	return (jsonify(IntentoSchema(many=True).dump(all_intentos)), 200), 200


@app.route("/api/captcha/", methods = ['POST', 'GET'])
def obtener_captcha():
	if request.method == 'GET':
		captcha = Captcha()
		size=db.session.query(Bloque).count()
		captcha.bloques.append(db.session.query(Bloque)[random.randrange(0, size)])
		if captcha.bloques[0].texto is None:
			subset = db.session.query(Bloque).filter(Bloque.texto.isnot(None))
		else :
			subset = db.session.query(Bloque).filter(Bloque.texto.is_(None))
		
		size = subset.count()
		captcha.bloques.append(subset[random.randrange(0, size)])

		db.session.add(captcha)
		db.session.commit()
		return jsonpify(captcha=CaptchaSchema().dump(captcha), status=200), 200

	elif request.method == 'POST':
		captcha = Captcha.query.filter_by(token=request.json['token']).first()
		if captcha.bloques[0].texto is None:
			vacio = 0
			conocido = 1
		else:
			vacio = 1
			conocido = 0

		# Se ingresan los intentos
		bloques = request.json['bloques']
		intento_0 = post_intento(captcha.bloques[0].id, bloques[0])
		intento_1 = post_intento(captcha.bloques[1].id, bloques[1])

		# El texto del bloque conocido tiene que matchear el que tenemos en base
		if captcha.bloques[conocido].texto == bloques[conocido]:

			# Cambia el estado del captcha
			captcha.status = 1 
			db.session.commit()

			return jsonify(
				intento_0=IntentoSchema().dump(intento_0),
				intento_1=IntentoSchema().dump(intento_1), 
				status=200), 200
		else:
			return jsonify(bloque=BloqueSchema().dump(captcha.bloques[conocido]), status=401), 401
	else:
		return jsonify(status=404)


if __name__ == "__main__":
	app.run(host='0.0.0.0')
