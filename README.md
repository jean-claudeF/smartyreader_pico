# smartyreader_pico
Micropython software for a picoW that reads Smarty data from an MQTT broker

You must add a file wlanconfig.py containing the ssid and password information:
ssid = "MySSID"
pwd = "Mypassword"

The circuit is very simple: there is a PicoW with an OLED display connected to the I2C bus.

It is assumed that you use an ESP8266 MQTT client connected to the smart meter, that transfers its messages to a Raspi3 MQTT broker.

