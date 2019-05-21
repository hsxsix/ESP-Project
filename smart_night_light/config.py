# light config

LIGHT_ID = "01"                     #light id
WIFI_SSID = "hsxsix"                     #wifi 名称（英文或数字组合，不要有中文）
WIFI_PASSWORD = "qwerrtyuiop"              #wifi 密码

WS2812_PIN = 5                      #ws2812 DI引脚
WS2812_BIT = 8                      #ws2812 LED数量
LightSensorPin = 14 	            #光线感应引脚编号
SoundSensorPin = 13 	            #声音感应引脚编号
HumanSensorPin = 12 	            #人体感应引脚编号
ButtonPin = 4		                #按钮引脚编号

AutoLightSensor = 0 	            #光线感应设置
AutoSoundSensor = 1 	            #声音感应设置
AutoHumanSensor = 1 	            #人体感应设置
DelayTime = 10 	                    #延迟时间S
HumanInterval = 2                   #人体感应探测间隔时间s
RememberLastColor = 1 	            #记住上一次的颜色

DefaultColor = [255,255,255]	    #默认颜色(当RememberLastColor值为0时有效)
DefaultOffColor = [0, 0, 0]         #默认关灯颜色

MQTT_SERVER = "10.10.10.1"      #MQTT服务器
MQTT_PORT = 1883                    #MQTT端口（默认1883）
MQTT_USER = "six"                   #用户名
MQTT_PASSWD = "sixsixsix"            #密码
KEEPALIVE = 60                      #keepalive

STATUS_TOPIC = "smart_light/color_light/status"
SET_TOPIC = "smart_light/color_light/set"
AVAILABILITY_TOPIC = "smart_light/color_light/availability"
MQTT_CHECK_TOPIC = "smart_light/color_light/mqtt/status"
MQTT_CRIT_ERR = 10
MQTT_MAX_ERR = 5
INT_CRIT_ERR = 50
INT_MAX_ERR = 20
