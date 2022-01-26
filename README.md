# helium-ttn-mapper
flask application to map data from TTN and Helium

## setup
* copy app.cfg.example to app.cfg and edit database settings.
* run python3 app.py
  * watch out, it's set to run in debug (set in app.py). Don't use this for production!
  * in production you want to deploy it as cgi under apache or nginx
