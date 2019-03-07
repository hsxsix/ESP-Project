wifi_ssid = "hsxsix"
wifi_passwd = "qwertyuiop"
my_timezone = "CST-8" 

import network
import machine
import time

#ap_if = network.WLAN(network.AP_IF);ap_if.active(True)
sta_if = network.WLAN(network.STA_IF); sta_if.active(True)
sta_if.connect(wifi_ssid, wifi_passwd)

time.sleep(5)
sta_if.ifconfig()

rtc = machine.RTC()
rtc.init((2018, 01, 01, 12, 12, 12))
rtc.ntp_sync(server= "ntp.api.bz", tz=my_timezone, update_period=3600)
network.ftp.start(user="esp32", password="micropython", buffsize=1024, timeout=300)
network.telnet.start(user="esp32", password="micropython", timeout=300)
print("IP of this ESP32 is : " + sta_if.ifconfig()[0])
print("Hello, Micropython!")