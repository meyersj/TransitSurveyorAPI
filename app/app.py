from flask import Flask
from flask import request, render_template
from flask.ext.sqlalchemy import SQLAlchemy
import logging
from logging import FileHandler



app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)
handler = FileHandler('/tmp/app.log')
handler.setLevel(logging.DEBUG)
app.logger.addHandler(handler)

class Test(db.Model):
  id = db.Column(db.Integer, primary_key = True)
  uuid = db.Column(db.Text)
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
    return '<uuid: %r>' % self.id

db.create_all()

@app.route('/submit', methods=['POST'])
def post():
  if request.method == 'POST':
    app.logger.error("request is post")
    uuid = request.form['uuid']
    date = request.form['date']
    time = request.form['time']
    line = request.form['line']
    dir = request.form['dir']
    lon = request.form['lon']
    lat = request.form['lat']
    add = Test(uuid=uuid, date=date, time=time, line=line, dir=dir, lon=lon, lat=lat)
    db.session.add(add)
    db.session.commit()
  else:
    app.logger.error("request not post")
  
  return "recieved"
 
@app.route('/stats')
def stats():
  results = Test.query.order_by(Test.line).all()
  
  lines = []
  for row in results:
    app.logger.error(type(int(row.line)))
    lines.append(int(row.line))
  
  app.logger.error(lines)
  app.logger.error(set(lines))
  app.logger.error(list(set(lines))) 
  app.logger.error(sorted(list(set(lines))))
  
  lines = sorted(list(set(lines)))

  return render_template('lines.html', lines=lines)


@app.route('/stats/<line>')
def stats_filter(line):
  if line == 'all': 
    results = Test.query.all()
  else:
    results = Test.query.filter_by(line=line).all()
  return render_template('query.html', query=results)

@app.route('/')
def home():
  return render_template('home.html')

if __name__ == '__main__':
  app.run()
