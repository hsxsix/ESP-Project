#coding:utf-8

import utime as time
import uasyncio as asyncio
from umqtt.robust import MQTTClient
from machine import Pin
import config
from config_line_map import config_map

class SonOff():
    led = Pin(13, Pin.OUT, value=1)
    relay = Pin(12, Pin.OUT, value = 0)
    button = Pin(0, Pin.IN, Pin.PULL_UP)
    device_status = "OFF"

    def __init__(self):
        if config.POWER_ON_STATE:
            self.relay_control(1)
            self.led_control(0)
            self.device_status = "ON"
        self.mqtt_client = MQTTClient(client_id=config.DEVICE_NAME, server=config.MQTT_SERVER,
                        port=config.MQTT_PORT, user=config.MQTT_USER, passwd=config.MQTT_PASSWD,
                        keepalive=60)
        self.mqtt_client.set_callback(self.sub_callback)
        self.mqtt_client.set_last_will(config.AVAILABILITY_TOPIC, "offline")
        self.ping_mqtt = 0
        self.ping_fail = 0
        self.button_interrupt = 0

    def relay_control(self, value):
        self.relay.value(value)
        return self.relay.value()

    def led_control(self, value):
        self.led.value(value)
        return self.led.value()

    def mqtt_connect(self):
        try:
            self.mqtt_client.connect()
            for topic in [config.SET_TOPIC, config.POS_SET_TOPIC, config.MQTT_CHECK]:
                self.mqtt_client.subscribe(topic)
            self.publish_device_status()
            self.publish_pos_status("ON" if config.POWER_ON_STATE else "OFF")
        except:
            self.ping_fail += 1

    def sub_callback(self, topic, msg):
        topic = topic.decode('utf-8')
        msg = msg.decode('utf-8')
        if topic == config.SET_TOPIC:
            if msg == "ON":
                self.relay_control(1)
                self.led_control(0)
                self.device_status = "ON"
            else:
                self.relay_control(0)
                self.led_control(1)
                self.device_status = "OFF"
            self.publish_device_status()
        elif topic == config.POS_SET_TOPIC:
            if msg == "ON":
                self.change_config({"POWER_ON_STATE": 1})
            else:
                self.change_config({"POWER_ON_STATE": 0})
            self.publish_pos_status(msg)
        elif topic == config.MQTT_CHECK:
            if int(msg) == self.ping_mqtt:
                self.ping_fail = 0

    def publish_device_status(self):
        if self.ping_fail == 0:
            self.mqtt_client.publish(config.STATE_TOPIC, self.device_status)

    def publish_pos_status(self, value):
        if self.ping_fail == 0:
            self.mqtt_client.publish(config.POS_STATE_TOPIC, value)

    def button_action(self, pin):
        self.button_interrupt = 1

    def change_config(self, config_data):
        with open('config.py', 'r') as rf:
            config_list = rf.readlines()
        for config_name, config_value in config_data.items():
            if config_name in config_map:
                if isinstance(config_value, int):
                    config_list[config_map[config_name]] = "{} = {}\n".format(config_name, config_value)
                elif config_value.isdigit():
                    config_list[config_map[config_name]] = "{} = {}\n".format(config_name, int(config_value))
                else:
                    config_list[config_map[config_name]] = '{} = "{}"\n'.format(config_name, config_value)
        with open('config.py', 'w') as wf:
            for conf in config_list:
                wf.write(conf)

    async def check_message(self):
        while True:
            await asyncio.sleep(0.2)
            try:
                self.mqtt_client.check_msg()
            except:
                self.mqtt_connect()

    async def check_mqtt(self):
        while True:
            await asyncio.sleep(10)
            self.ping_mqtt = time.time()
            self.mqtt_client.publish(config.MQTT_CHECK, str(self.ping_mqtt))
            self.ping_fail += 1

            if self.ping_fail > 10:
                pass
            if self.ping_fail > 3:
                self.mqtt_client.disconnect()
                self.mqtt_connect()

    async def check_button(self):
        while True:
            await asyncio.sleep(0.4)
            if self.button_interrupt > 0:
                self.button_interrupt = 0
                if self.device_status == "ON":
                    self.relay_control(0)
                    self.led_control(1)
                    self.device_status = "OFF"
                else:
                    self.relay_control(1)
                    self.led_control(0)
                    self.device_status = "ON"
                self.publish_device_status()

    def run(self):
        self.button.irq(trigger=Pin.IRQ_FALLING, handler=self.button_action)
        self.mqtt_connect()
        loop = asyncio.get_event_loop()
        loop.create_task(self.check_message())
        loop.create_task(self.check_mqtt())
        loop.create_task(self.check_button())
        try:
            loop.run_forever()
        except:
            pass
