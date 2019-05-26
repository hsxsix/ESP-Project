# light config

LIGHT_ID = "01"                     #light id
WIFI_SSID = "hsxsix"                     #wifi 名称（英文或数字组合，不要有中文）
WIFI_PASSWORD = "qwerrtyuiop"              #wifi 密码

WS2812_PIN = 5                      #ws2812 DI引脚
WS2812_BIT = 8                      #ws2812 LED数量
LIGHT_SENSOR_PIN = 14 	            #光线感应引脚编号（ADC）
SOUND_SENSOR_PIN = 13 	            #声音感应引脚编号
HUMAN_SENSOR_PIN_1 = 12 	    #人体感应1引脚编号
HUMAN_SENSOR_PIN_2 = 12 	    #人体感应2引脚编号
HUMAN_SENSOR_PIN_3 = 12 	    #人体感应3引脚编号
BUTTON_PIN_1 = 4		    #按钮1引脚编号
BUTTON_PIN_2 = 4                    #按钮2引脚编号

AUTO_LIGHT = 0 	                    #光线感应设置
AUTO_SOUND = 1 	                    #声音感应设置
AUTO_HUMAN = 1 	                    #人体感应设置
DELAY_TIME = 10 	            #延迟时间S
RememberLastColor = 1 	            #记住上一次的颜色

DEFAULT_COLOR = [255,255,255]	    #默认颜色()
DEFAULT_OFF_COLOR = [0, 0, 0]       #默认关灯颜色

MQTT_SERVER = "10.10.10.1"          #MQTT服务器
MQTT_PORT = 1883                    #MQTT端口（默认1883）
MQTT_USER = "six"                   #用户名
MQTT_PASSWD = "sixsixsix"           #密码
KEEPALIVE = 60                      #keepalive

STATUS_TOPIC = "smart_light/color_light/status"
SET_TOPIC = "smart_light/color_light/set"
HUMAN_SET_TOPIC  = "smart_light/colo_light/human_set"
LIGHT_SET_TOPIC  = "smart_light/colo_light/light_set"
SOUND_SET_TOPIC  = "smart_light/colo_light/sound_set"
AVAILABILITY_TOPIC = "smart_light/color_light/availability"
MQTT_CHECK_TOPIC = "smart_light/color_light/mqtt/status"
MQTT_CRIT_ERR = 10
MQTT_MAX_ERR = 5
INT_CRIT_ERR = 50
INT_MAX_ERR = 20
