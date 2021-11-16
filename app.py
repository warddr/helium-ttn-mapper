from flask import Flask
from flask import request
from flaskext.mysql import MySQL

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
  print(content)
  cursor = mysql.connect().cursor()
  for hotspot in content["hotspots"]:
    cursor = mysql.get_db().cursor()
    sql = "INSERT INTO heliumtracker (dev_eui, fcnt, frequency, hotspot, rssi, snr, spreading, payload, latitude, longitude, sats, distance) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    val = (content["dev_eui"], content["fcnt"], hotspot["frequency"], hotspot["id"], hotspot["rssi"], hotspot["snr"],hotspot["spreading"], content["payload"], content["decoded"]["payload"]["latitude"],content["decoded"]["payload"]["longitude"],content["decoded"]["payload"]["sats"],0)
    cursor.execute(sql, val)
    mysql.get_db().commit()

  return "To Implement"

if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)
