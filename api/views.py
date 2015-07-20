from api import app

@app.route('/')
def index():
    return "On-Off Index"

