from flask import render_template

from api import app

@app.route('/')
def index():
    return "BASE"

@app.route('/tests')
def tests():
    return render_template("report.html")


