#smart light base on micropython esp8266

import wifi
import time
import json
import machine
import micropython
import uasyncio as asyncio
from neopixel import NeoPixel
from umqtt.simple import MQTTClient
from machine import Pin, Timer, WDT, ADC

import config
from status_code import code_table

# wifi.activate()
micropython.alloc_emergency_exception_buf(100)

class SmartLight():
    def __init__(self):
        self.wdt = WDT()
        self.adc = ADC(0)
        self.auto_tim = Timer(1)
        self.publish_tim = Timer(2)
        self.ping_fail = 0
        self.ping_mqtt = 0
        self.light_state = 0
        self.light_intensity = 0
        self.sensor_interrupt = 0
        self.button_interrupt = 0
        self.current_color = [255,255,255]
        self.auto_human = config.AUTO_HUMAN
        self.auto_sound = config.AUTO_SOUND
        self.auto_light = config.AUTO_LIGHT
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

        self.np = NeoPixel(Pin(config.WS2812_PIN, Pin.OUT), config.WS2812_BIT)

        self.mqtt_client = MQTTClient(client_id=config.DEVICE_NAME, server=config.MQTT_SERVER,
                                    port=config.MQTT_PORT, user=config.MQTT_USER, 
                                    password=config.MQTT_PASSWD, keepalive=60)
        self.mqtt_client.set_callback(self.sub_callback)
        self.mqtt_client.set_last_will(config.AVAILABILITY_TOPIC, "offline")

        self.human_sensor_1 = Pin(config.HUMAN_SENSOR_PIN_1, Pin.IN, Pin.PULL_UP)
        self.human_sensor_2 = Pin(config.HUMAN_SENSOR_PIN_2, Pin.IN, Pin.PULL_UP)
        self.human_sensor_3 = Pin(config.HUMAN_SENSOR_PIN_3, Pin.IN, Pin.PULL_UP)
        self.sound_sensor = Pin(config.SOUND_SENSOR_PIN, Pin.IN, Pin.PULL_UP)
        self.button = Pin(config.BUTTON_PIN, Pin.IN, Pin.PULL_UP)

    def mqtt_connect(self):
        try:
            self.mqtt_client.connect()
            for topic in [config.DEVICE_SET_TOPIC, config.MQTT_CHECK_TOPIC, config.HUMAN_SET_TOPIC, 
                            config.LIGHT_SET_TOPIC, config.SOUND_SET_TOPIC]:
                self.mqtt_client.subscribe(topic)
            self.mqtt_client.publish(config.AVAILABILITY_TOPIC, "online")
            self.mqtt_client.publish(config.DEVICE_STATE_TOPIC, json.dumps(self.light_status))
            self.mqtt_client.publish(config.HUMAN_STATE_TOPIC, self.auto_human)
            self.mqtt_client.publish(config.LIGHT_STATE_TOPIC, self.auto_light)
            self.mqtt_client.publish(config.SOUND_STATE_TOPIC, self.auto_sound)
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

    def sub_callback(self, topic, msg):
        topic = topic.decode('utf-8')
        msg = msg.decode('utf-8')
        if topic == config.DEVICE_SET_TOPIC:
            msg = json.loads(msg)
            state = msg.get('state', '')
            brightness = msg.get('brightness', '')
            color = msg.get('color', {})
            effect = msg.get('effect', '')
            self.light_control(state, brightness, color, effect)
            self.mqtt_client.publish(config.DEVICE_STATE_TOPIC, json.dumps(self.light_status))
        elif topic == config.MQTT_CHECK_TOPIC:
            if int(msg) == self.ping_mqtt:
                # print("MQTT is OK")
                self.ping_fail = 0
        elif topic == config.HUMAN_SET_TOPIC:
            if msg == "ON":
                self.auto_human = 1
                self.mqtt_client.publish(config.HUMAN_STA_TOPIC, "ON")
            elif msg == "OFF":
                self.auto_human = 0
                self.mqtt_client.publish(config.HUMAN_STATE_TOPIC, "OFF")
        elif topic == config.LIGHT_SET_TOPIC:
            if msg == "ON":
                self.auto_light = 1
                self.mqtt_client.publish(config.LIGHT_STATE_TOPIC, "ON")
            elif msg == "OFF":
                self.auto_light = 0
                self.mqtt_client.publish(config.LIGHT_STATE_TOPIC, "OFF")
        elif topic == config.SOUND_SET_TOPIC:
            if msg == "ON":
                self.auto_sound = 1
                self.mqtt_client.publish(config.SOUND_STATE_TOPIC, "ON")
            elif msg == "OFF":
                self.auto_sound = 0
                self.mqtt_client.publish(config.SOUND_STATE_TOPIC, "OFF")


    def light_control(self, state, brightness, color, effect):
        # TODO:当灯处于关闭状态时调节亮度无效的
        if color:
            self.set_color(color)
            self.light_state = 2
            self.light_status["state"] = "ON"
            self.light_status['color'] = color
            self.light_status['brightness'] = int(max(color.values()) / 255 * 100)
        if type(brightness) == int:
            if brightness == 0:
                # print("turn off")
                self.set_color(config.DEFAULT_OFF_COLOR)
                self.light_state = 0
            else:
                scale = max(self.light_status["color"].values())/int(brightness / 100 * 255)
                for c in ['r', 'g', 'b']:
                    self.light_status["color"][c] = int(self.light_status["color"][c]/scale)
                self.set_color(self.light_status["color"])
                self.light_state = 2
            self.light_status["brightness"] = brightness
        if effect:
            self.show_effects(effect)
        if state == "OFF":
            self.light_status["state"] = "OFF"
            self.set_color(config.DEFAULT_OFF_COLOR)
            self.light_state = 0
        if state == "ON":
            if any([color, type(brightness)==int, effect]):
                pass
            else:
                self.set_color(config.DEFAULT_COLOR)
                self.light_status["state"] = "ON"
                self.light_state = 2

    def sensor_action(self, pin):
        self.sensor_interrupt = self.sensor_interrupt+1

    def button_action(self, pin):
        self.button_interrupt = self.button_action + 1
        if self.light_state == 0:
            self.set_color(config.DEFAULT_COLOR)
            self.light_state = 1
            self.light_status["state"] = "ON"
        elif self.light_state == 1:
            self.set_color(config.DEFAULT_OFF_COLOR)
            self.light_state = 0
            self.light_status["state"] = "OFF"
        self.publish_tim.init(period=1000, mode=Timer.ONE_SHOT, callback=self.publish_light_status)

    def get_light_intensity(self):
        li = self.adc.read()
        return 1 if li > 512 else 0

    def publish_light_status(self):
        if self.ping_fail == 0:
            self.mqtt_client.publish(config.STATUS_TOPIC, json.dumps(self.light_status))

    def internet_connected(self):
        return True

    async def check_interrupt(self, pin):
        while True:
            await asyncio.slepp(0.5)
            if self.sensor_interrupt>0:
                if self.auto_light:
                    self.light_intensity = self.get_light_intensity()
                else:
                    self.light_intensity = 0

                if pin == config.SOUND_SENSOR_PIN:
                    code = "{}{}{}{}".format(self.auto_sound, self.auto_light,
                                        self.light_intensity, self.light_state)
                else:
                    code = "{}{}{}{}".format(self.auto_human, self.auto_light,
                                        self.light_intensity, self.light_state)
                are_light = code_table[code]
                if are_light == 1:
                    self.set_color(config.DEFAULT_COLOR)
                    self.auto_tim.init(period=config.DELAY_TIME*1000, mode=Timer.ONE_SHOT,
                                callback=lambda t: self.set_color(config.DEFAULT_OFF_COLOR))
                    self.light_state = 1
                    print("Turn off the lights after {} s".format(config.DELAY_TIME))
                else:
                    pass
                self.sensor_interrupt = 0

    async def keep_mqtt(self):
        while True:
            await asyncio.sleep(10)
            self.ping_mqtt = time.time()
            self.mqtt_client.publish(config.MQTT_CHECK_TOPIC, "%s" % self.ping_mqtt)
            # print("Send MQTT ping (%i)" % self.ping_mqtt)
            self.ping_fail += 1

            if self.ping_fail > 10:
                # print("MQTT ping false... reset (%i)" % self.ping_fail)
                machine.reset()

            if self.ping_fail > 3:
                # print("MQTT ping false... reconnect (%i)" % self.ping_fail)
                self.mqtt_client.disconnect()
                self.mqtt_connect()

    async def check_message(self):
        while True:
            self.wdt.feed()
            await asyncio.sleep(0.2)
            try:
                self.mqtt_client.check_msg()
            except:
                self.mqtt_connect()

    def run(self):
        self.sound_sensor.irq(trigger=Pin.IRQ_FALLING, handler=self.sensor_action)
        self.human_sensor_1.irq(trigger=Pin.IRQ_FALLING, handler=self.sensor_action)
        self.human_sensor_2.irq(trigger=Pin.IRQ_FALLING, handler=self.sensor_action)
        self.human_sensor_3.irq(trigger=Pin.IRQ_FALLING, handler=self.sensor_action)
        self.button.irq(trigger=Pin.IRQ_FALLING, handler=self.button_action)

        try:
            loop = asyncio.get_event_loop()
            loop.create_task(self.check_message())
            loop.create_task(self.check_interrupt())
            loop.create_task(self.keep_mqtt())
            loop.run_forever()
        except Exception as e:
            print(e)

# sl = SmartLight()
# sl.run()
