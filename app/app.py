from flask import Flask
from flask import request, render_template
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)


class Test(db.Model):
  __tablename__ = 'test'
  uuid = db.Column(db.Text, primary_key = True)
  date = db.Column(db.Text)
  time = db.Column(db.Text)
  line = db.Column(db.Text)
  dir = db.Column(db.Text)
  lon = db.Column(db.Text)
  lat = db.Column(db.Text)

  def __init__(self, uuid, date, time, line, dir, lon, lat):
    self.uuid = uuid
    self.date = date
    self.time = time
    self.line = line
    self.dir = dir
    self.lon = lon
    self.lat = lat

  def __repr__(self):
    return '<uuid: %r>' % self.uuid

@app.route('/', methods=['POST'])
def post():
  if request.method == 'POST':
    uuid = request.form['uuid']
    date = request.form['date']
    time = request.form['time']
    line = request.form['line']
    dir = request.form['dir']
    lon = request.form['lon']
    lat = request.form['lat']

    add = Test(uuid, date, time, line, dir, lon, lat)
    db.session.add(add)
    db.session.commit()
    return "recieved"
 
@app.route('/index')
def hello():
  query = Test.query.all()
  return render_template('query.html', query = query)

if __name__ == '__main__':
  app.run()
