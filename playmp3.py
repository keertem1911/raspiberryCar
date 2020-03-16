import RPi.GPIO as GPIO
import time
pin=40
GPIO.setmode(GPIO.BCM)
mode=GPIO.getmode()
GPIO.setup(pin,GPIO.IN,inital=GPIO.HIGHT)
list=[11,12]
GPIO.setup(list,GPIO.OUT)
GPIO.cleanup()
GPIO.setwarnings(False)
GPIO.setup(pin,GPIO.IN,pull_up_donw=GPIO.PUD_UP)
#需要注意的是，上面的读取代码只是获取当前一瞬间的引脚输入信号
GPIO.setup(pin,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
"""
如果需要实时监控引脚的状态变化，可以有两种办法。
最简单原始的方式是每隔一段时间检查输入的信号值，这种方式被称为轮询。
如果你的程序读取的时机错误，则很可能会丢失输入信号。
轮询是在循环中执行的，这种方式比较占用处理器资源。
"""
while GPIO.input(pin)== GPIO.LOW:
    time.sleep(0.1)
"""
另一种响应GPIO输入的方式是使用中断（边缘检测），
这里的边缘是指信号从高到低的变换（下降沿）或从低到高的变换（上升沿）。
"""
"""
边缘检测
边缘是指信号状态的改变，从低到高（上升沿）或从高到低（下降沿）。通常情况下，我们更关心于输入状态的该边而不是输入信号的值。这种状态的该边被称为事件。

wait_for_edge() 函数
wait_for_edge()被用于阻止程序的继续执行，直到检测到一个边缘。
"""
channel = GPIO.wait_for_edge(pin,GPIO.RISING,timeout=5000)

"""
add_event_detect() 函数
该函数对一个引脚进行监听，一旦引脚输入状态发生了改变，调用event_detected()函数会返回true，
"""
GPIO.add_event_detect(pin,GPIO.RISING)
if GPIO.add_event_detected(pin):
    print("break event")
"""
RPI.GPIO 模块的脉宽调制（PWM）功能
脉宽调制(PWM)是指用微处理器的数字输出来对模拟电路进行控制，是一种对模拟信号电平进行数字编码的方法。在树莓派上，可以通过对GPIO的编程来实现PWM。
创建一个 PWM 实例：
"""
p=GPIO.PWM(pin,50)#50hz
"""
启用 PWM：占空比（范围：0.0 <= dc <= 100.0）
"""
p.start(10)
"""
更改频率：
"""
p.changeFrequency(40)
"""
更改占空比：  范围：0.0 <= dc >= 100.0
"""
p.ChangeDutyCycle(10)

"""
停止 PWM：
"""
p.stop()