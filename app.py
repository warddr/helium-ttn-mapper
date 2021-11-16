from flask import Flask
from flask import request
from flaskext.mysql import MySQL
import geopy.distance

app = Flask(__name__)
app.config.from_pyfile("app.cfg")

mysql = MySQL()
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

if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)
