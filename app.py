from flask import Flask, request, jsonify, render_template
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor
import geopy.distance
from geojson import Feature, Point, FeatureCollection, LineString, MultiLineString
import requests
from requests.structures import CaseInsensitiveDict


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

@app.route("/api/geojson/hotspots")
def api_geojson_hotspots():
  features = []
  cursor = mysql.connect().cursor()
  eui = request.args.get('dev_eui', default = "%", type = str) #not yet implemented
  hotspot = request.args.get('hotspot', default = "%", type = str)
  cursor.execute("SELECT * FROM heliumhotspots WHERE id LIKE %s;",(hotspot))
  for points in cursor.fetchall():
    mypoint = Point((points["longitude"], points["latitude"]))
    features.append(Feature(geometry=mypoint, properties={"name": points["name"], "id": points["id"]}))
  return FeatureCollection(features)

@app.route("/api/geojson/points")
def api_geojson_points():
  features = []
  cursor = mysql.connect().cursor()
  eui = request.args.get('dev_eui', default = "%", type = str)
  hotspot = request.args.get('hotspot', default = "%", type = str)
  cursor.execute("SELECT fcnt, round(heliumtracker.longitude,3) as longitude, round(heliumtracker.latitude,3) as latitude, heliumhotspots.longitude, heliumhotspots.latitude, max(rssi) as rssi, distance, hotspot FROM heliumtracker INNER JOIN heliumhotspots ON heliumtracker.hotspot = heliumhotspots.id WHERE dev_eui LIKE %s AND hotspot LIKE %s GROUP BY longitude, latitude;", (eui, hotspot))
  lastlat = 0
  lastlong = 0
  lasthotspot = ""
  for points in cursor.fetchall():
    mypoint = Point((points["longitude"], points["latitude"]))
    features.append(Feature(geometry=mypoint))
  return FeatureCollection(features)

@app.route("/api/geojson/lines")
def api_geojson_lines():
  features = []
  cursor = mysql.connect().cursor()
  eui = request.args.get('dev_eui', default = "%", type = str)
  hotspot = request.args.get('hotspot', default = "%", type = str)
  cursor.execute("SELECT fcnt, round(heliumtracker.longitude,3) as longitude, round(heliumtracker.latitude,3) as latitude, heliumhotspots.longitude, heliumhotspots.latitude, max(rssi) as rssi, distance, hotspot FROM heliumtracker INNER JOIN heliumhotspots ON heliumtracker.hotspot = heliumhotspots.id WHERE dev_eui LIKE %s AND hotspot LIKE %s GROUP BY latitude, longitude, hotspot;", (eui, hotspot))
  lastlat = 0
  lastlong = 0
  lasthotspot = ""
  for points in cursor.fetchall():
      myline = LineString([(points["longitude"], points["latitude"]),(points["heliumhotspots.longitude"], points["heliumhotspots.latitude"])])
      features.append(Feature(geometry=myline, properties={"rssi": points["rssi"]}))
  return FeatureCollection(features)

@app.route("/highscore")
def highscore():
  cursor = mysql.get_db().cursor()
  cursor.execute("SELECT dev_eui, max(distance) as distance FROM heliumtracker GROUP BY dev_eui ORDER BY distance DESC;")
  
  return render_template('highscore.html.j2', scores = cursor.fetchall())

@app.route("/map")
def map():
  eui = request.args.get('dev_eui', default = "%25", type = str)
  hotspot = request.args.get('hotspot', default = "%25", type = str)
  return render_template('map.html.j2', hotspots="api/geojson/hotspots?dev_eui="+eui+"&hotspot="+hotspot, points="api/geojson/points?dev_eui="+eui+"&hotspot="+hotspot, lines="api/geojson/lines?dev_eui="+eui+"&hotspot="+hotspot)

@app.route("/waarisward")
def waarisward():
  cursor = mysql.connect().cursor()
  cursor.execute("SELECT *  FROM heliumtracker WHERE dev_eui = '6081F9D6C064A43C' ORDER BY timestamp  DESC LIMIT 1;")
  point = cursor.fetchone()
  headers = CaseInsensitiveDict()
  headers["User-Agent"] = "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0"
  resp = requests.get("https://nominatim.openstreetmap.org/reverse?format=json&lat="+str(point["latitude"])+"&lon="+str(point["longitude"])+"&zoom=27&addressdetails=1", headers=headers)
  return (resp.json()["display_name"])

if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)
