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

@app.route("/api/ttn", methods = ['POST']) #voor UA
def api_ttn():
  content = request.json
  conn = mysql.connect()
  cursor = conn.cursor()
  dev_eui = content["end_device_ids"]["dev_eui"]
  payload = content["uplink_message"]["frm_payload"]
  latitude = float(content["uplink_message"]["decoded_payload"]["latitude"])
  longitude = float(content["uplink_message"]["decoded_payload"]["longitude"])
  sql = "INSERT INTO bike (id, dev_eui, payload, latitude, longitude) VALUES (Null, %s,%s,%s,%s);"
  val = (dev_eui, payload, latitude, longitude,)
  cursor.execute(sql, val)
  print(cursor._executed)
  conn.commit()
  for row in cursor:
    print(row)        
  #print(content)
  return "Done"

@app.route("/api/UA-bike/lastlocation") #voor UA
def api_UA_lastlocation():
  features = []
  conn = mysql.connect()
  cursor = conn.cursor()
  eui = request.args.get('dev_eui', default = "Null", type = str)
  print(eui)
  cursor.execute("SELECT * FROM bike WHERE dev_eui LIKE %s ORDER BY timestamp DESC LIMIT 1;",(eui))
  conn.commit()
  for points in cursor.fetchall():
    mypoint = Point((points["longitude"], points["latitude"]))
    headers = CaseInsensitiveDict()
    headers["User-Agent"] = "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0"
    resp = requests.get("https://nominatim.openstreetmap.org/reverse?format=json&lat="+str(points["latitude"])+"&lon="+str(points["longitude"])+"&zoom=27&addressdetails=1", headers=headers)
    features.append(Feature(geometry=mypoint, properties={"last-timestamp": points["timestamp"], "adres": resp.json()["display_name"]}))
   
  resp = jsonify(FeatureCollection(features))
  resp.headers['Access-Control-Allow-Origin'] = '*'
  return resp

if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)
