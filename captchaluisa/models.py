"""Data models."""
from . import db

class Bloque(db.Model):
	"""Modelo para bloques de texto"""
	__tablename__ = 'bloque'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	path_imagen = db.Column(db.Text)
	texto = db.Column(db.Text)
	intentos = db.relationship('Intento')

	def __repr__(self):
		return '<Bloque {}>'.format(self.path_imagen)

class Intento(db.Model):
	"""Modelo para intento de lectura"""
	__tablename__ = 'intento'
	fecha_hora = db.Column(db.DateTime, primary_key=True)
	texto = db.Column(db.Text)
	bloque_id = db.Column(db.Integer, db.ForeignKey('bloque.id'))

	def __repr__(self):
		return '<Intento {}>'.format(self.texto)


