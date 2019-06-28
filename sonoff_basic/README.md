# micropython for sonoff basic

## 简介：

sonoff basic 本身就是一个ESP8266+继电器+降压模块，因此适用于ESP8266的各种固件都是可以用的。
我尝试在sonoff上运行micropython固件，自己写控制的逻辑。

## 功能：

1. 指示灯指示当前设备状态
2. 按钮可控制设备
3. 对接homeassistant, 可用homeassistant控制
4. 可设置上电吸合/断开

## TODO:

1. wifi配网
2. 网页设置

## P.S:

把这个装在我的卧室里，卧室是单火开关，接线图如下：
![接线图](https://raw.githubusercontent.com/hsxsix/ESP-Project/master/sonoff_basic/pic/sonoff_basic_line.png)

大多数家庭都是这种单火开关吧，但是sonoff basic模块需要接入火线和零线才能工作，
所以只好接在灯的后面了，然后把sonoff一同装进灯罩里，平时保持物理开关常闭状态就行了，
如果把物理开关关了，只有下一次打开物理开关后才能对灯进行智能控制，这是唯一的方法了，
否则就使用单火智能开关。我的代码已经稳定运行了好几个月，把homeassistant做内网穿透对接天猫精灵，
可以天猫精灵语音控制卧室的的灯，效果还不错。
