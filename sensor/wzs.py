# WZ-S python example

import serial
import serial.tools.list_ports
import time 

class wzs_sensor():
    def __init__(self):
        self.serial = serial.Serial(
                port=None,
                baudrate=9600,
                timeout=0.2,
                xonxoff=False,
                rtscts=False,
                write_timeout=0.5,
                dsrdtr=False,
                inter_byte_timeout=None,
                exclusive=None)
        if self.serial.is_open:
            self.serial.close()
        self.serial_list = list(serial.tools.list_ports.comports())
        if len(self.serial_list) < 1:
            print("No port")
        else:
            wsz_port = list(self.serial_list[0])[0]
            self.serial.port = wsz_port
            self.serial.open()
            self.serial.write(b'\xFF\x01\x78\x41\x00\x00\x00\x00\x46')
            time.sleep(0.1)
            self.serial.reset_input_buffer()

    def read_value(self):
        self.serial.write(b'\xFF\x01\x86\x00\x00\x00\x00\x00\x79')
        time.sleep(0.1)
        # 读取9位的结果
        if self.serial.inWaiting() == 9:
            result = self.serial.read(9)
            value_high = int(hex(result[6]), 16)
            value_low = int(hex(result[7]), 16)
            value = value_high * 256 + value_low
            return float(value)/1000
        else:
            print("Read error")
            self.serial.reset_input_buffer()
            return None

if __name__ == "__main__":
    wzs = wzs_sensor()
    formaldehyde = wzs.read_value()
    if formaldehyde != None:
        print(f"当前室内的甲醛浓度为:{formaldehyde} ppb\n国标为0.08mg/m³,约66ppb, 0.066 ppm")
    else:
        print("数据读取错误！")
