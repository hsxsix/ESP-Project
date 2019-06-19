#smart light base on micropython esp8266

import wifi
import time
import json
import machine
import micropython
import uasyncio as asyncio
from neopixel import NeoPixel
from umqtt.simple import MQTTClient
from machine import Pin, Timer, WDT

import config
from status_code import code_table

# wifi.activate()
micropython.alloc_emergency_exception_buf(100)

class SmartLight():
    def __init__(self):
        self.wdt = WDT()
        self.auto_tim = Timer(1)
        self.publish_tim = Timer(2)
        self.ping_fail = 0
        self.ping_mqtt = 0
        self.light_state = 0
        self.int_err_count = 0
        self.light_intensity = 0
        self.sensor_interrupt = 0
        self.button_interrupt_1 = 0
        self.button_interrupt_2 = 0
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

        self.mqtt_client = MQTTClient("color_light", config.MQTT_SERVER,
                        config.MQTT_PORT,config.MQTT_USER, config.MQTT_PASSWD)
        self.mqtt_client.set_callback(self.sub_callback)
        self.mqtt_client.set_last_will(config.AVAILABILITY_TOPIC, "offline")

        self.human_sensor_1 = Pin(config.HUMAN_SENSOR_PIN_1, Pin.IN, Pin.PULL_UP)
        self.human_sensor_2 = Pin(config.HUMAN_SENSOR_PIN_2, Pin.IN, Pin.PULL_UP)
        self,human_sensor_3 = Pin(config.HUMAN_SENSOR_PIN_3, Pin.IN, Pin.PULL_UP)
        self.sound_sensor = Pin(config.SOUND_SENSOR_PIN, Pin.IN, Pin.PULL_UP)
        self.button_1 = Pin(config.BUTTON_PIN_1, Pin.IN, Pin.PULL_UP)
        self.button_2 = Pin(config.BUTTON_PIN_2, Pin.IN, Pin.PULL_UP)

    def mqtt_connect(self):
        try:
            self.mqtt_client.connect()
            for topic in [config.STATUS_TOPIC, config.SET_TOPIC, config.MQTT_CHECK_TOPIC,
                    config.HUMAN_SET_TOPIC, config.LIGHT_SET_TOPIC, config.SOUND_SET_TOPIC]:
                self.mqtt_client.subscribe(topic)
            self.mqtt_client.publish(config.AVAILABILITY_TOPIC, "online")
            self.mqtt_client.publish(config.STATUS_TOPIC, json.dumps(self.light_status))
            self.mqtt_client.publish(config.HUMAN_SET_TOPIC, self.auto_human)
            self.mqtt_client.publish(config.LIGHT_SET_TOPIC, self.auto_light)
            self.mqtt_client.publish(config.SOUND_SET_TOPIC, self.auto_sound)
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
        if topic == config.SET_TOPIC:
            msg = json.loads(msg)
            state = msg.get('state', '')
            brightness = msg.get('brightness', '')
            color = msg.get('color', {})
            effect = msg.get('effect', '')
            self.light_control(state, brightness, color, effect)
            self.mqtt_client.publish(config.STATUS_TOPIC, json.dumps(self.light_status))
        elif topic == config.MQTT_CHECK_TOPIC:
            if int(msg) == self.ping_mqtt:
                # print("MQTT is OK")
                self.ping_fail = 0
        elif topic == config.HUMAN_SET_TOPIC:
            if msg == "ON":
                self.auto_human = 1
                self.mqtt_client.publish(config.HUMAN_SET_TOPIC, "ON")
            elif msg == "OFF":
                self.auto_human = 0
                self.mqtt_client.publish(config.HUMAN_SET_TOPIC, "OFF")
        elif topic == config.LIGHT_SET_TOPIC:
            if msg == "ON":
                self.auto_light = 1
                self.mqtt_client.publish(config.LIGHT_SET_TOPIC, "ON")
            elif msg == "OFF":
                self.auto_light = 0
                self.mqtt_client.publish(config.LIGHT_SET_TOPIC, "OFF")
        elif topic == config.SOUND_SET_TOPIC:
            if msg == "ON":
                self.auto_sound = 1
                self.mqtt_client.publish(config.SOUND_SET_TOPIC, "ON")
            elif msg == "OFF":
                self.auto_sound = 0
                self.mqtt_client.publish(config.SOUND_SET_TOPIC, "OFF")


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

    def button_action_1(self, pin):
        self.button_interrupt_1 = self.button_action_1 + 1
        if self.light_state == 0:
            self.set_color(config.DEFAULT_COLOR)
            self.light_state = 1
            self.light_status["state"] = "ON"
        elif self.light_state == 1:
            self.set_color(config.DEFAULT_OFF_COLOR)
            self.light_state = 0
            self.light_status["state"] = "OFF"
        self.publish_tim.init(period=1000, mode=Timer.ONE_SHOT, callback=self.publish_light_status)


    def button_action_2(self, pin):
        self.button_interrupt_2 = self.button_interrupt_2 + 1

    def get_light_intensity(self):
        li = 540
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
        self.sound_sensor.irq(trigger=Pin.IRQ_FALLING, handler=self.sensor_action)
        self.human_sensor_1.irq(trigger=Pin.IRQ_FALLING, handler=self.sensor_action)
        self.human_sensor_2.irq(trigger=Pin.IRQ_FALLING, handler=self.sensor_action)
        self.human_sensor_3.irq(trigger=Pin.IRQ_FALLING, handler=self.sensor_action)
        self.button_1.irq(trigger=Pin.IRQ_FALLING, handler=self.button_action_1)
        self.button_2.irq(trigger=Pin.IRQ_FALLING, handler=self.button_action_2)

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
