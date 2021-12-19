from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from config import Config
from datetime import datetime
from flask_restful import Api, Resource

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
ma = Marshmallow(app)

class Bloque(db.Model):
	# Modelo para bloques de texto
	__tablename__ = 'bloque'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	path_imagen = db.Column(db.Text)
	imagen = db.Column(db.Text)
	texto = db.Column(db.Text)
	intentos = db.relationship('Intento')

class Intento(db.Model):
	# Modelo para intento de lectura
	__tablename__ = 'intento'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	fecha_hora = db.Column(db.DateTime,
						default=datetime.utcnow, 
						onupdate=datetime.utcnow)
	texto = db.Column(db.Text)
	bloque_id = db.Column(db.Integer, db.ForeignKey('bloque.id'), nullable=False)

class BloqueSchema(ma.SQLAlchemyAutoSchema):
	class Meta:
		# fields = ("id", "path_imagen", "imagen", "texto", "_links")
		model = Bloque
		include_fk = True
		load_instance = True

		# id = ma.auto_field()
		# path_imagen = ma.auto_field()
		# imagen = ma.auto_field()
		# texto = ma.auto_field()
		# intentos = ma.auto_field()

	# _links = ma.Hyperlinks({
	# 	'self': ma.URLFor('bloque', values=dict(id='<id>')),
	# 	'collection': ma.URLFor('bloques'),
	# })
		
class IntentoSchema(ma.SQLAlchemyAutoSchema):
	class Meta:
		model = Intento
		include_fk = True
		load_instance = True
		

db.create_all()
bloque_schema = BloqueSchema()
bloques_schema = BloqueSchema(many=True)
intento_schema = IntentoSchema()
intentos_schema = IntentoSchema(many=True)

db.session.commit()

@app.route("/")
def hello():
	return "<h1 style='color:blue'>Hello There!</h1>"

@app.route("/api/bloque/")
def get_bloques():
	all_bloques = Bloque.query.all()	
	return (jsonify({ "data" :  bloques_schema.dump(all_bloques) } ), 200)

@app.route("/captcha")
def obtener_captcha():
	try:
		return "OK"
	except Exception as ex:
		return "Error"

if __name__ == "__main__":
	app.run(host='0.0.0.0')
