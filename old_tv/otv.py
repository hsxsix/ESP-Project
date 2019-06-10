# old_tv project
__author__ = "HeSixian"

import json
import socket
import network
from time import sleep
from machine import Pin, SPI, Timer
from ssd1351 import Display
import os
#挂载sd卡
try:
    os.sdconfig(os.SDMODE_4LINE)
    os.mountsd(1)
except:
    print("mounted sd card failed!")

class OTV():
    def __init__(self):
        spi = SPI(2, sck=Pin(18), mosi=Pin(23), miso=Pin(19),baudrate=14500000)
        self.display = Display(spi, dc=Pin(17), cs=Pin(5), rst=Pin(16))
        # self.display("连接MQTT服务器...")
        self.mqtt = network.mqtt("otv", "mqtt://t.hsxsix.com", user="six", password="1234$#@!", 
                        cleansession=True, connected_cb=self.conncb, disconnected_cb=self.disconncb, 
                        subscribed_cb=self.subscb, published_cb=self.pubcb, data_cb=self.datacb)
        self.weather_data = {} 
        self.weather_api = 'http://118.24.144.127/weather/v1?city={}&node=micropython_ssd1351'
        self.weather_tm = Timer(2)
        self.weather_tm.init(period=1000*60*20, 
                mode=self.weather_tm.PERIODIC, callback=self.update_weather)

    def publish(self, msg):
        self.mqtt.publish('otv', 'Hi from Micropython')

    def conncb(self, task):
        # self.dispaly("连接MQTT成功")
        print("[{}] Connected".format(task))
        self.mqtt.subscribe('otv')

    def disconncb(self, task):
        print("[{}] Disconnected".format(task))

    def subscb(self, task):
        print("[{}] Subscribed".format(task))

    def pubcb(self, pub):
        print("[{}] Published: {}".format(pub[0], pub[1]))

    def datacb(self, msg):
        '''
        data format:
        "tv_id|image url|XX|XX|XX"
        '''
        _, image_url, image_size, position = msg[2].split('|')
        print("Received a task to show image:\nimage url:{},\nimage size:{}".format(image_url,image_size))
        # self.display.draw_image("收到文件，正在下载。。。")
        download_image = self.http_get(image_url)
        w,h = image_size.split(',')
        x,y = position.split(',')
        if download_image:
            self.display.clear()
            self.display.draw_image(download_image, int(x), int(y), int(w), int(h))

    def update_weather(self, timer):
        # self.display("update weather data。。。")
        self.http_get(self.weather_api, types='text',
                    file_name='weather.txt')
        with open(weather_file, 'r') as f:
            self.weather_data = json.loads(f.read())

    def show_today_weather(self):
        if self.weather_data['code'] == 'ok':
            today_weather = self.weather_data['0']['weather_code']
            current_temp = self.weather_data['0']['current_temp']
            current_weather = self.weather_data['0']['current_weather']
            date = self.weather_data['0']['date']
            temp = self.weather_data['0']['temp']
            today_aqi = self.weather_data['0']['aqi']
            # self.display.draw_image('bg.raw',0,32,128,96)
            self.display.draw_image('{}.raw'.format(today_weather),5,37,50,50)
            i=0
            for char in current_weather:
                start_x=50+int((78-15*len(current_weather))/2)+15*i 
                self.display.draw_bitarray(w_char, start_x,42,15,16)
                i+=1

            i=0
            for t_char in temp:
                start_x =50+int((78-9*len(current_weather))/2)+9*i 
                self.display.draw_bitarray(w_char, start_x,64,9,16)
                i+=1

            x = 9 if len(today_aqi)==9 else 5
            for char in today_aqi:
                if len(char) > 100:
                    self.display.draw_bitarray(w_char, x,92,15,16)
                    x = x+15
                else:
                    self.display.draw_bitarray(w_char, x,92,9,16)
                    x = x+9
            # for char in date:
                # self.display.draw_bitarray(w_char, 0,32,9,16)

            # for char in current_temp:
                # self.display.draw_bitarray(w_char, 0,32,9,16)
        else:
            pass
            # self.display.draw_image("weather data error！")

    def show_three_day_weather(self):
        for day in ('1','2','3'):
            weather = self.weather_data[day]['weather_code']
            temp = self.weather_data[day]['temp']
            date = self.weather_data[day]['date']
            aqi = self.weather_data[day]['aqi']

    def http_get(self, url, types='image', file_name=None):
        download = None
        try:
            proto, dummy, host, path = url.split("/", 3)
        except ValueError:
            proto, dummy, host = url.split("/", 2)
            path = ""
        if proto == "http:":
            port = 80
        else:
            raise ValueError("Unsupported protocol: " + proto)

        if ":" in host:
            host, port = host.split(":", 1)
            port = int(port)

        addr = socket.getaddrinfo(host, port)[0][-1]
        if not file_name:
            file_name = path.split('/')[-1]
        s = socket.socket()
        s.connect(addr)
        s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))

        while True:
            data = s.readline()
            if not data or data == b"\r\n":
                print(data)
                break
        if types == 'image':
            with open (file_name, 'wb') as f:
                while True:
                    data = s.recv(512)
                    if data:
                        f.write(data)
                    else:
                        download = file_name
                        break
        else:
            with open(file_name, 'w') as f:
                while True:
                    data = s.recv(512)
                    if data:
                        f.write(data)
                    else:
                        download = file_name
                        break
        s.close()
        return download

    def start(self):
        self.mqtt.start()


if __name__ == "__main__":
    otv = OTV()
    otv.start()










#mqtt.config(lwt_topic='status', lwt_msg='Disconected')

'''
# Wait until status is: (1, 'Connected')
mqtt.subscribe('test')
publish(self, msg):
self.mqtt.publish('otv', 'Hi from Micropython')
mqtt.stop()
'''


