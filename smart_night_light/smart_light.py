#smart light base on micropython esp8266
import wifi
import time 
import json
import machine 
import uasyncio as asyncio 
from neopixel import NeoPixel
from umqtt.simple import MQTTClient
# from umqtt.robust import MQTTClient 
from machine import Pin, Timer, WDT

import config 

# wifi.activate()
# micropython.alloc_emergency_exception_buf(100)

class SmartLight():
    def __init__(self):
        self.wdt = WDT()
        self.ping_fail = 0
        self.ping_mqtt = 0
        self.int_err_count = 0
        self.current_color = [255,255,255]
        self.light_status = {
                        "state":"OFF", 
                        "brightness":100, 
                        "color":{
                            "r":255, 
                            "g":255, 
                            "b":255
                            }, 
                        "effetc":""
                            }
        
        # self.bt_pin = Pin(config.ButtonPin, Pin.IN)
        self.np = NeoPixel(Pin(config.WS2812_PIN, Pin.OUT), config.WS2812_BIT)

        self.mqtt_client = MQTTClient("color_light", config.MQTT_SERVER, 
                        config.MQTT_PORT,config.MQTT_USER, config.MQTT_PASSWD)
        self.mqtt_client.set_callback(self.sub_callback)
        self.mqtt_client.set_last_will(config.AVAILABILITY_TOPIC, "offline")
    
    def mqtt_connect(self):
        try:
            self.mqtt_client.connect()
            for topic in [config.STATUS_TOPIC, config.SET_TOPIC, config.MQTT_CHECK_TOPIC]:
                self.mqtt_client.subscribe(topic)
            self.mqtt_client.publish(config.AVAILABILITY_TOPIC, "online")
            self.mqtt_client.publish(config.STATUS_TOPIC, json.dumps(self.light_status))
        except Exception as e:
            print("mqtt connect faild", e) 

    def set_color(self, color):
        if isinstance(color, dict):
            r, g, b = color.values()
        elif isinstance(color, list):
            r, g, b = color 
        for i in range(config.WS2812_BIT):
            self.np[i] = (b, g, r)
        self.np.write()

    def show_effects(self, effect):
        print(effect) 

    def sub_callback(self, topic, mesg):
        if topic.decode('utf-8') == config.SET_TOPIC:
            msg = json.loads(mesg.decode('utf-8'))
            state = msg.get('state', '')
            brightness = msg.get('brightness', '')
            color = msg.get('color', {})
            effect = msg.get('effect', '')
            self.light_control(state, brightness, color, effect)
            # self.mqtt_client.publish(config.STATUS_TOPIC, mesg)
        if topic.decode('utf-8') == config.MQTT_CHECK_TOPIC:
            if int(mesg.decode('utf-8')) == self.ping_mqtt:
                # print("MQTT is OK")
                self.ping_fail = 0


    def light_control(self, state, brightness, color, effect):
        if color:
            self.set_color(color)
            self.light_status["state"] = "ON" 
            self.light_status['color'] = color 
            self.light_status['brightness'] = int(max(color.values()) / 255 * 100)
        if type(brightness) == int:
            print("brightness:", brightness)
            if brightness == 0:
                # print("turn off")
                self.set_color(config.DefaultOffColor)
            else:
                scale = max(self.light_status["color"].values())/int(brightness / 100 * 255)
                for c in ['r', 'g', 'b']:
                    self.light_status["color"][c] = int(self.light_status["color"][c]/scale)
                self.set_color(self.light_status["color"])
            self.light_status["brightness"] = brightness 
        if effect:
            self.show_effects(effect)
        if state == "OFF":
            self.light_status["state"] = "OFF"
            self.set_color(config.DefaultOffColor)
        if state == "ON":
            if any([color, type(brightness)==int, effect]):
                pass 
            else:
                self.set_color(config.DefaultColor)
                self.light_status["state"] = "ON"
        self.mqtt_client.publish(config.STATUS_TOPIC, json.dumps(self.light_status))

    def internet_connected(self):
        return True 

    # Check MQTT brocker
    async def mqtt_check(self):
        while True:
            await asyncio.sleep(10)
            self.ping_mqtt = time.time()
            self.mqtt_client.publish(config.MQTT_CHECK_TOPIC, "%s" % self.ping_mqtt)
            # print("Send MQTT ping (%i)" % self.ping_mqtt)
            self.ping_fail += 1

            if self.ping_fail >= config.MQTT_CRIT_ERR:
                # print("MQTT ping false... reset (%i)" % self.ping_fail)
                machine.reset()

            if self.ping_fail >= config.MQTT_MAX_ERR:
                # print("MQTT ping false... reconnect (%i)" % self.ping_fail)
                self.mqtt_client.disconnect()
                self.mqtt_connect()

    # Check MQTT message
    async def check_message(self):
        while True:
            self.wdt.feed()
            await asyncio.sleep(0.2)
            # print("Check message...")
            try:
                self.mqtt_client.check_msg()
            except Exception as error:
                # print("Error in mqtt check message: [Exception] %s: %s" % (type(error).__name__, error))
                self.mqtt_connect()


    # Check Internet connected and reconnect
    async def check_internet(self):
        try:
            while True:
                await asyncio.sleep(60)
    #            print("Check Internet connect... ")
                if not self.internet_connected():
                    # print("Internet connect fail...")
                    self.int_err_count += 1

                    if self.int_err_count >= config.INT_CRIT_ERR:
                        self.mqtt_client.disconnect()
                        wifi.wlan.disconnect()
                        machine.reset()

                    if self.int_err_count >= config.INT_MAX_ERR:
                        # print("Internet reconnect")
                        self.mqtt_client.disconnect()
                        wifi.wlan.disconnect()
                        wifi.activate()
        except Exception as error:
            pass
            # print("Error in Internet connection: [Exception] %s: %s" % (type(error).__name__, error))
    

    def run(self):
        # self.ss_pin.irq(trigger=Pin.IRQ_FALLING, handler=self.sound_action)
        # self.bt_pin.irq(trigger=Pin.IRQ_FALLING, handler=self.button_action)
        # self.human_break_tm.init(period=self.human_interval*1000, mode=Timer.PERIODIC, 
                    # callback=lambda t:self.human_action())
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(self.check_message())
            loop.create_task(self.check_internet())
            loop.create_task(self.mqtt_check())
            loop.run_forever()
        except Exception as e:
            print(e)


# sl = SmartLight()
# sl.run()
