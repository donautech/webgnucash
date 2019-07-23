from flask import redirect

from app import app


@app.route('/')
def redirect_webapp():
    return redirect("/web/index.html", code=302)
