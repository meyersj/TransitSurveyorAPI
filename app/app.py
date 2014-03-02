from flask import Flask
from flask import request, render_template
from flask.ext.sqlalchemy import SQLAlchemy
import logging, datetime
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
  date = db.Column(db.DateTime)
  line = db.Column(db.Text)
  dir = db.Column(db.Text)
  lon = db.Column(db.Text)
  lat = db.Column(db.Text)

  def __init__(self, uuid, date, line, dir, lon, lat):
    self.uuid = uuid
    self.date = date
    self.line = line
    self.dir = dir
    self.lon = lon
    self.lat = lat

  def __repr__(self):
    return '<uuid: %r>' % self.id

class Matched(db.Model): 
  id = db.Column(db.Integer, primary_key = True)
  paired = db.Column(db.Integer, unique = True)

  def __init__(self, paired):
    self.paired = paired

class Pairs(db.Model):
  id = db.Column(db.Integer, primary_key = True)
  line = db.Column(db.Text)
  dir = db.Column(db.Text)
  on_date = db.Column(db.DateTime)
  on_lon = db.Column(db.Text)
  on_lat = db.Column(db.Text)
  off_date = db.Column(db.DateTime)
  off_lon = db.Column(db.Text)
  off_lat = db.Column(db.Text)

  def __init__(self, line, dir, on_date, on_lon, on_lat, off_date, off_lon, off_lat):
    self.line = date
    self.dir = dir
    self.on_date = on_date
    self.on_lon = on_lon
    self.on_lat = on_lat
    self.off_date = off_date
    self.off_lon = off_lon
    self.off_lat = off_lat

db.create_all()

@app.route('/submit', methods=['POST'])
def post():
  if request.method == 'POST':
    uuid = request.form['uuid']
    date = request.form['date']
    line = request.form['line']
    dir = request.form['dir']
    lon = request.form['lon']
    lat = request.form['lat']
    date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    add = Test(uuid=uuid, date=date, line=line, dir=dir, lon=lon, lat=lat)
    db.session.add(add)
    db.session.commit()
  else:
    app.logger.error("request not post")
 
@app.route('/stats')
def stats():
  results = Test.query.order_by(Test.line).all()
  lines = []
  for row in results:
    lines.append(int(row.line))
  lines = sorted(list(set(lines)))
  return render_template('lines.html', lines=lines)


@app.route('/stats/<in_line>')
def stats_filter(in_line):
  if in_line == 'all': 
    results = Test.query.all()
  else:
    results = Test.query.filter_by(line=in_line).all()
  return render_template('query.html', query=results)

@app.route('/pair/<in_line>')
def pair(in_line):
  result = Test.query.filter_by(line=in_line).order_by(Test.date)
  app.logger.error(result)

  first = result.first()
  #del result[0]
  #second = result.first()
  #result2 = Test.query.filter_by(line=in_line).order_by(Test.date).first()
  result = result[1:]
  
  #app.logger.error(type(result[0]))
  return first.uuid + '**' + result[2].uuid




@app.route('/')
def home():
  return render_template('home.html')



if __name__ == '__main__':
  app.run()
