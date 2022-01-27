# helium-ttn-mapper
Python flask application to take LoRaWAN data from The Things Network (or Helium network) using a JSON webhook.

## setup
* Import database.sql into your mysql database
* copy app.cfg.example to app.cfg and edit database settings.
* run python3 app.py
  * watch out, it's set to run in debug (set in app.py). Don't use this for production!
  * in production you want to deploy it as cgi under apache or nginx
 * **WATCH OUT, helium network does not accept an ip adress as url (or at least not on a non-default port), you need to make a DNS entery**

### The things network webhook setup
* In your application in the console go to integrations --> webhooks --> add webhook --> custom webhook
  * Webhook format: JSON
  * BASE URL: (flask url)/api/ttn
  * Enable uplink message
