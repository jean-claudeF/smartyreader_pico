# -> https://www.tomshardware.com/how-to/send-and-receive-data-raspberry-pi-pico-w-mqtt

import network
import time
from umqtt.simple import MQTTClient

from wlanconfig import ssid, pwd      # wlanconfig.py has the values for ssid and pwd 

mqtt_server = "192.168.179.26"
client_id = "PicoW_Kichen"
topic = "smartyreader/#"
#-----------------------------------------------------------
#Global variables:
P1, P2, P3, Ptot, gaz = "", "", "", "", ""
tim, dat = "", ""
newmessage = False
i = 0  
#----------------------------------------------------------------------
from machine import Pin, I2C, reset
#import ssd1306
import sh1106
from display import Display

i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=100000)
oled_width = 128
oled_height = 64
#oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)          # no rotate!
oled = sh1106.SH1106_I2C(oled_width, oled_height, i2c, rotate = 180)
display = Display(oled)

led = Pin("LED", Pin.OUT)
led.off()
#-----------------------------------------------------------------------

'''Connect to existing WiFi'''
def connect_wifi(ssid, pwd):
    
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, pwd)
    
    # Wait for connect or fail:
    max_wait = 10
    while max_wait > 0:
        if wlan.status() <0 or wlan.status() >=3:
            break
        max_wait -= 1
        
        print("Waiting to connect...")
        led.on()
        time.sleep(0.5)
        led.off()
        time.sleep(0.5)

    # Handle connection error
    if wlan.status() != 3:
        ip = None
        print("WiFi connection failed!")
        display.print("WiFi ERROR " + str(wlan.status()))
        display.print("Restarting")
        wlan.disconnect()
        time.sleep(3)
        reset()
        
    else:
        print('connected')
        status = wlan.ifconfig()
        ip = status[0]
        print( 'ip = ' + ip )
        display.print("Pico:")
        display.print(ip)
    
    return ip

#-------------------------------------------------
def mqtt_connect():
    client = MQTTClient(client_id, mqtt_server, keepalive=3600)
    client.set_callback(on_message)
    client.connect()
    print('Connected to %s MQTT Broker'%(mqtt_server))
    display.print("Broker:")
    display.print(mqtt_server)
    display.print("Wait for msg")
    return client

def reconnect():
    print('Failed to connect to the MQTT Broker. Reconnecting...')
    display.print("Connect failure")
    display.print("Restarting")
    
    time.sleep(5)
    reset()
    
    
def on_message(topic, msg):
    global P1, P2, P3, Ptot, tim, dat, newmessage
    #print("New message on topic {}".format(topic.decode('utf-8')))
    msg = msg.decode('utf-8')
    topic = topic.decode('utf-8')
    topic = topic.replace("smartyreader/", "")
    extract(topic, msg)
    print_values()

def print_values():
    global newmessage, i
    if newmessage == True:
        if i % 300:
            print("# time", "date", "P1/kW", "P2/kW", "P3/kW", "Ptot/kW", "Gas/m3")
        print(tim, dat, P1, P2, P3, Ptot)
        display.clear()
        ti = tim[0:5]
        display.print(ti + "_" + dat)
        #display.print(dat)
        display.print("L1: " + P1 + "kW")
        display.print("L2: " + P2 + "kW")
        display.print("L3: " + P3 + "kW")
        display.print("Ptot: " + Ptot + "kW")
        display.print("Gas: " + gas + "m3")
        newmessage = False
    i=0


def extract(topic, msg):
    global P1, P2, P3, Ptot, tim, dat, newmessage, gas
    if "ntp_datetime" in topic:                  # this is the first message e.g. #ntp_datetime	2023-01-26T10:14:11
        t = msg.split("T")
        dat = t[0]
        tim = t[1]
        
        d = dat.split('-')
        dat = d[2]+'.' + d[1] + '.' + d[0]
    if "act_pwr_imp_p_plus_l1_kW" in topic:
        P1 = msg
    if "act_pwr_imp_p_plus_l2_kW" in topic:
        P2 = msg    
    if "act_pwr_imp_p_plus_l3_kW" in topic:
        P3 = msg
    if "act_pwr_imported_p_plus_kW" in topic:
        Ptot = msg
    if "gas_consumption_calc_cumul_day" in topic:   # this is the final message
        gas = msg
        newmessage = True
#----------------------------------------------------------------------
        
        
ip = connect_wifi(ssid, pwd)

if ip != None:
    print("WLAN OK")
    
else:
    print("WLAN ERROR") 
    display.print("WiFi ERROR!")
    reconnect()

try:
    client = mqtt_connect()
except OSError as e:
    reconnect()
    

while True:
    client.subscribe(topic)
    time.sleep(1)
    #print("Waiting " + str(i) + '\b\r')
    #display.print(".")
    display.fill_rect(0, 61, 3*i, 3, 1)
    display.show()
    i += 1

