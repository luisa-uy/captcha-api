from flask import request, render_template, make_response
from datetime import datetime as dt
from flask import current_app as app
from .models import db, Bloque, Intento


@app.route('/bloque', methods=['GET'])
def user_records():
    """Create a user via query string parameters."""
    texto = request.args.get('texto')
    if texto:
        new_bloque = Bloque(
            texto = texto,
            path_imagen = "."
        )
        db.session.add(new_bloque)  # Adds new User record to database
        db.session.commit()  # Commits all changes
    return make_response(f"{new_bloque} successfully created!")