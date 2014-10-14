from flask import render_template, send_from_directory

from api import app

downloads_dir = "/home/meyersj/api/app/api/static/downloads"

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/tests')
def tests():
    return render_template("report.html")


@app.route('/downloads')
def download_list():
    return render_template("download.html")


@app.route('/downloads/<filename>')
def download(filename):
    return send_from_directory(directory=downloads_dir, filename=filename)

"""
@app.route('/report.html')
def report():
    return render_template("report.html")
"""
