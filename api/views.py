from flask import render_template

from api import app

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/tests')
def tests():
    return render_template("report.html")

"""
@app.route('/report.html')
def report():
    return render_template("report.html")
"""
