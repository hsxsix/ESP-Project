# old_tv project
__author__ = "HeSixian"
import os
#挂载sd卡
# os.sdconfig(os.SDMODE_4LINE)
# os.mountsd(1)
import network
import socket
from time import sleep
from machine import Pin, SPI
from ssd1351 import Display

spi = SPI(2, sck=Pin(18), mosi=Pin(23), miso=Pin(19),baudrate=14500000)
display = Display(spi, dc=Pin(17), cs=Pin(5), rst=Pin(16))

#根据图片url下载对应的图片文件
def http_image(url, image_name=None):
    try:
        proto, dummy, host, path = url.split("/", 3)
    except ValueError:
        proto, dummy, host = url.split("/", 2)
        path = ""
    if proto == "http:":
        port = 80
    elif proto == "https:":
        import ussl
        port = 443
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
    flag = 1
    with open (image_name, 'wb') as f:
        while True:
            data = s.recv(1024)
            if data:
                if flag and b'\r\n\r\n' in data:
                    headers, data = data.split(b'\r\n\r\n')
                    headers = str(headers, "utf-8").split('\r\n')
                    status_code = '200'
                    if "HTTP/" in headers[0]:
                        status_code = headers[0].split(' ',2)[1]
                    flag = 0    
                    if status_code != '200':
                        print("get file failed，please check the url!")
                        download = False
                        # print("get file failed，please check the url!")
                        break
                f.write(data)
            else:
                print("accept file done!")
                download = image_name
                break
    s.close()
    return download


def show_image(img_path=None, width=128, height=96, center=True):
    """Show image code."""
    if img_path:
        display.draw_image(img_path, 0, 32, width, height)
    else:
        display.draw_image('write_bug128x96.raw', 0, 32, 128, 96)



def conncb(task):
    print("[{}] Connected".format(task))
    mqtt.subscribe('otv')

def disconncb(task):
    print("[{}] Disconnected".format(task))

def subscb(task):
    print("[{}] Subscribed".format(task))

def pubcb(pub):
    print("[{}] Published: {}".format(pub[0], pub[1]))

def datacb(msg):
    '''
    data format:
    "image url|XX|XX|XX"
    '''
    print("[{}] Data arrived from topic: {}, Message:\n".format(msg[0], msg[1]), msg[2])
    _, image_url, image_size = msg[2].split('|')
    download_image = http_image(image_url)
    w,h = image_size.split(',')
    if download_image:
        show_image(download_image, int(w),int(h))


mqtt = network.mqtt("otv", "mqtt://t.hsxsix.com", user="six", password="1234$#@!", 
        cleansession=True, connected_cb=conncb, disconnected_cb=disconncb, 
        subscribed_cb=subscb, published_cb=pubcb, data_cb=datacb)

mqtt.start()

#mqtt.config(lwt_topic='status', lwt_msg='Disconected')

'''
# Wait until status is: (1, 'Connected')
mqtt.subscribe('test')
mqtt.publish('test', 'Hi from Micropython')
mqtt.stop()
'''


