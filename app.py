from flask import Flask, request, jsonify, render_template
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor
import geopy.distance
from geojson import Feature, Point, FeatureCollection, LineString, MultiLineString

app = Flask(__name__, template_folder='templates')
app.config.from_pyfile("app.cfg")

mysql = MySQL(cursorclass=DictCursor)
mysql.init_app(app)

@app.route("/")
def hello():
  return "Hello World!"

@app.route("/api/helium", methods = ['POST'])
def api_helium():
  content = request.json
  cursor = mysql.connect().cursor()
  for hotspot in content["hotspots"]:
    distance = geopy.distance.distance((hotspot["lat"], hotspot["long"]), (content["decoded"]["payload"]["latitude"],content["decoded"]["payload"]["longitude"])).km
    cursor = mysql.get_db().cursor()
    sql = "INSERT INTO heliumtracker (dev_eui, fcnt, frequency, hotspot, rssi, snr, spreading, payload, latitude, longitude, sats, distance) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    val = (content["dev_eui"], content["fcnt"], hotspot["frequency"], hotspot["id"], hotspot["rssi"], hotspot["snr"],hotspot["spreading"], content["payload"], content["decoded"]["payload"]["latitude"],content["decoded"]["payload"]["longitude"],content["decoded"]["payload"]["sats"],distance)
    cursor.execute(sql, val)
    mysql.get_db().commit()

    cursor2 = mysql.get_db().cursor()
    cursor2.execute("SELECT * FROM heliumhotspots WHERE id = %s;", hotspot["id"]);
    if not cursor2.fetchone(): #gateway is not yet in our db
      cursor3 = mysql.get_db().cursor()
      sql = "INSERT INTO heliumhotspots (id,name,latitude,longitude) VALUES (%s,%s,%s,%s)"
      val = (hotspot["id"], hotspot["name"], hotspot["lat"], hotspot["long"])
      cursor3.execute(sql, val)
      mysql.get_db().commit()
  return "Done"

@app.route("/api/geojson")
def api_geojson():
  features = []
  cursor = mysql.connect().cursor()
  cursor.execute("SELECT * FROM heliumtracker INNER JOIN heliumhotspots ON heliumtracker.hotspot = heliumhotspots.id ORDER BY fcnt;");
  lastfcnt = -1
  for points in cursor.fetchall():
    if points["fcnt"] != lastfcnt: #only 1 point if received by multiple gateways
      mypoint = Point((points["longitude"], points["latitude"]))
      features.append(Feature(geometry=mypoint))
      lastfcnt = points["fcnt"]
    myline = LineString([(points["longitude"], points["latitude"]),(points["heliumhotspots.longitude"], points["heliumhotspots.latitude"])])
    features.append(Feature(geometry=myline, properties={"rssi": points["rssi"]}))
  return FeatureCollection(features)

@app.route("/highscore")
def highscore():
  cursor = mysql.get_db().cursor()
  cursor.execute("SELECT dev_eui, max(distance) as distance FROM heliumtracker GROUP BY dev_eui ORDER BY distance;")
  
  return render_template('highscore.html.j2', scores = cursor.fetchall())

@app.route("/map")
def map():
  return render_template('map.html.j2')


if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)
