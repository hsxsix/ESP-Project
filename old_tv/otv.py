# old_tv project
__author__ = "HeSixian"

import network
import socket
from time import sleep
from machine import Pin, SPI
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
        self.mqtt = network.mqtt("otv", "mqtt://t.hsxsix.com", user="six", password="1234$#@!", 
                        cleansession=True, connected_cb=self.conncb, disconnected_cb=self.disconncb, 
                        subscribed_cb=self.subscb, published_cb=self.pubcb, data_cb=self.datacb)

    def conncb(self, task):
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
        "image url|XX|XX|XX"
        '''
        # print("[{}] Data arrived from topic: {}, Message:\n".format(msg[0], msg[1]), msg[2])
        _, image_url, image_size, position = msg[2].split('|')
        print("Received a task to show image:\nimage url:{},\nimage size:{}".format(image_url,image_size))
        download_image = self.http_image(image_url)
        w,h = image_size.split(',')
        x,y = position.split(',')
        if download_image:
            self.display.clear()
            self.display.draw_image(download_image, int(x), int(y), int(w), int(h))

#根据图片url下载对应的图片文件
    def http_image(self, url, image_name=None):
        print("start download image:{}".format(url))
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
        if not image_name:
            image_name = path.split('/')[-1]
        s = socket.socket()
        s.connect(addr)
        s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
        while True:
            data = s.readline()
            if not data or data == b"\r\n":
                print(data)
                break

        with open (image_name, 'wb') as f:
            while True:
                data = s.recv(512)
                if data:
                    f.write(data)
                else:
                    print("download done!")
                    download = image_name
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
mqtt.publish('test', 'Hi from Micropython')
mqtt.stop()
'''


