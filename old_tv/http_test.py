# socket test
import socket

def http_image(url, image_name=None):
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
            data = s.readline()
            if data:
                f.write(data)
            else:
                print("download done!")
                download = image_name
                break
    s.close()
    return download

# if __name__ == "__main__":
http_image("http://file.hsxsix.com:9000/otv/1371_128x96.raw", "test.raw")