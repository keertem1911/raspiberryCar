# coding=UTF-8
import RPi.GPIO as GPIO
import time
class CarController:
    def __init__(self):
        # 设置GPIO口为BCM编码方式
        GPIO.setmode(GPIO.BCM)
        """
        GPIO控制端
        """
        # 小车电机引脚定义 IN1,IN2,IN3,IN4
        self.carWheelPins=[20,21,19,26]
        # ENA,ENb
        self.carWheelEnPins=[16,13]
        """
        小车方向控制函数
        """
        """
        车灯 	IN7	12
        """
        self.lightPin = 12
        # 舵机引脚定义 上下|左右
        self.SerCarmers=[9,11]
        self.ServoLeftRightPos = 0
        self.ServoUpDownPos = 0
        # 蜂鸣器引脚定义
        self.buzzer = 8
        # 忽略警告信息
        GPIO.setwarnings(False)
        # 初始化速度
        self.CarSpeedControl = 50
        self.cameraSpeedControl = 1.8
        self.lightOpen = False
        """
        初始化小车控制
        """
        GPIO.setup(self.carWheelEnPins, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(self.carWheelPins, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.SerCarmers, GPIO.OUT)
        GPIO.setup(self.buzzer, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(self.lightPin, GPIO.LOW, initial=GPIO.LOW)
        # 设置pwm引脚和频率为2000hz
        self.pwm_ENA = GPIO.PWM(self.carWheelEnPins[0], 2000)
        self.pwm_ENB = GPIO.PWM(self.carWheelEnPins[1], 2000)
        self.pwm_UpDownServo = GPIO.PWM(self.SerCarmers[0], 50)
        self.pwm_LeftRightServo = GPIO.PWM(self.SerCarmers[1], 50)
        self.pwm_ENA.start(0)
        self.pwm_ENB.start(0)
        self.pwm_UpDownServo.start(0)
        self.pwm_LeftRightServo.start(0)
        """
        初始化小车控制结束
        """
    def getCarStatus(self):
        return ("speend:%d,light:%s" % (self.CarSpeedControl, self.lightOpen))
    def getCarSpeed(self):
        return self.CarSpeedControl
    # 小车前进
    def run(self):
        GPIO.output(self.carWheelPins[0:4:2], GPIO.HIGH)
        GPIO.output(self.carWheelPins[1:4:2], GPIO.LOW)
        self.pwm_ENA.ChangeDutyCycle(self.CarSpeedControl)
        self.pwm_ENB.ChangeDutyCycle(self.CarSpeedControl)
        time.sleep(1)
    # 小车后退
    def back(self):
        GPIO.output(self.carWheelPins[0:4:2], GPIO.LOW)
        GPIO.output(self.carWheelPins[1:4:2], GPIO.HIGH)
        self.pwm_ENA.ChangeDutyCycle(self.CarSpeedControl)
        self.pwm_ENB.ChangeDutyCycle(self.CarSpeedControl)
        time.sleep(1)
    # 小车左转
    def left(self):
        GPIO.output(self.carWheelPins[0:4:2], GPIO.HIGH)
        GPIO.output(self.carWheelPins[1:4:2], GPIO.LOW)
        leftSpeed = 5
        if self.CarSpeedControl - 10 > 0:
            leftSpeed = self.CarSpeedControl - 10
        self.pwm_ENA.ChangeDutyCycle(leftSpeed)
        self.pwm_ENB.ChangeDutyCycle(self.CarSpeedControl)
        time.sleep(2)
    # 小车右转
    def right(self):
        GPIO.output(self.carWheelPins[0:4:2], GPIO.HIGH)
        GPIO.output(self.carWheelPins[1:4:2], GPIO.LOW)
        rightSpeed = 5
        if self.CarSpeedControl - 10 > 0:
            rightSpeed = self.CarSpeedControl - 10
        self.pwm_ENA.ChangeDutyCycle(self.CarSpeedControl)
        self.pwm_ENB.ChangeDutyCycle(rightSpeed)
        time.sleep(2)
        # 小车左转
    # 后左转
    def leftBack(self):
        GPIO.output(self.carWheelPins[0:4:2], GPIO.LOW)
        GPIO.output(self.carWheelPins[1:4:2], GPIO.HIGH)
        leftSpeed = 5
        if self.CarSpeedControl - 10 > 0:
            leftSpeed = self.CarSpeedControl - 10
        self.pwm_ENA.ChangeDutyCycle(leftSpeed)
        self.pwm_ENB.ChangeDutyCycle(self.CarSpeedControl)

    # 后右转
    def rightBack(self):
        GPIO.output(self.carWheelPins[0:4:2], GPIO.LOW)
        GPIO.output(self.carWheelPins[1:4:2], GPIO.HIGH)
        rightSpeed = 5
        if self.CarSpeedControl - 10 > 0:
            rightSpeed = self.CarSpeedControl - 10
        self.pwm_ENA.ChangeDutyCycle(self.CarSpeedControl)
        self.pwm_ENB.ChangeDutyCycle(rightSpeed)
        time.sleep(2)
    # 小车原地左转
    def spin_left(self):
        GPIO.output(self.carWheelPins[0:4:3], GPIO.LOW)
        GPIO.output(self.carWheelPins[1:3], GPIO.HIGH)
        self.pwm_ENA.ChangeDutyCycle(self.CarSpeedControl)
        self.pwm_ENB.ChangeDutyCycle(self.CarSpeedControl)

    # 小车原地右转
    def spin_right(self):
        GPIO.output(self.carWheelPins[0:4:3], GPIO.HIGH)
        GPIO.output(self.carWheelPins[1:3], GPIO.LOW)
        self.pwm_ENA.ChangeDutyCycle(self.CarSpeedControl)
        self.pwm_ENB.ChangeDutyCycle(self.CarSpeedControl)

    # 小车停止
    def brake(self):
        GPIO.output(self.carWheelPins, GPIO.LOW)

    # 加速
    def speedUp(self):
        self.CarSpeedControl += 10
        if self.CarSpeedControl >= 100:
            self.CarSpeedControl = 100

    # 减速
    def speedDown(self):
        self.CarSpeedControl -= 10
        if self.CarSpeedControl <= 0:
            self.CarSpeedControl = 0

    def getSpeed(self):
        return self.CarSpeedControl

    # 摄像头舵机左右旋转到指定角度
    def leftrightservo_appointed_detection(self, pos):
        self.pwm_LeftRightServo.ChangeDutyCycle(2.5 + 10 * pos / 180)
        time.sleep(0.02)  # 等待20ms周期结束
        self.pwm_LeftRightServo.ChangeDutyCycle(0)  # 归零信号

    # 摄像头舵机上下旋转到指定角度
    def updownservo_appointed_detection(self, pos):
        self.pwm_UpDownServo.ChangeDutyCycle(2.5 + 10 * pos / 180)
        time.sleep(0.02)  # 等待20ms周期结束
        self.pwm_UpDownServo.ChangeDutyCycle(0)  # 归零信号

    # 小车鸣笛
    def whistle(self):
        GPIO.output(self.buzzer, GPIO.LOW)
        time.sleep(0.1)
        GPIO.output(self.buzzer, GPIO.HIGH)
        time.sleep(0.001)

    def lightCar(self):
        if self.lightOpen:
            GPIO.output(self.lightPin, GPIO.LOW)
            self.lightOpen = False
        else:
            self.lightOpen = True
            GPIO.output(self.lightPin, GPIO.HIGH)

    # 摄像头舵机向上运动
    def servo_up(self):
        pos = self.ServoUpDownPos
        self.updownservo_appointed_detection(pos)
        # time.sleep(0.05)
        pos += self.cameraSpeedControl
        self.ServoUpDownPos = pos
        if self.ServoUpDownPos >= 180:
            self.ServoUpDownPos = 180

    # 摄像头舵机向下运动
    def servo_down(self):
        pos = self.ServoUpDownPos
        self.updownservo_appointed_detection(pos)
        # time.sleep(0.05)
        pos -= self.cameraSpeedControl
        self.ServoUpDownPos = pos
        if self.ServoUpDownPos <= 45:
            self.ServoUpDownPos = 45

    # 摄像头舵机向左运动
    def servo_left(self):
        pos = self.ServoLeftRightPos
        self.leftrightservo_appointed_detection(pos)
        # time.sleep(0.10)
        pos += self.cameraSpeedControl
        self.ServoLeftRightPos = pos
        if self.ServoLeftRightPos >= 180:
            self.ServoLeftRightPos = 180

    # 摄像头舵机向右运动
    def servo_right(self):

        pos = self.ServoLeftRightPos
        self.leftrightservo_appointed_detection(pos)
        # time.sleep(0.10)
        pos -= self.cameraSpeedControl
        self.ServoLeftRightPos = pos
        if self.ServoLeftRightPos <= 0:
            self.ServoLeftRightPos = 0
    # 前舵机向左
    def front_servo_left(self):
        self.frontservo_appointed_detection(180)
    # 前舵机向右
    def front_servo_right(self):
        self.frontservo_appointed_detection(0)
    # 所有舵机归位
    def servo_init(self):
        servoflag = 0
        servoinitpos = 90
        if servoflag != servoinitpos:
            self.updownservo_appointed_detection(servoinitpos)
            self.leftrightservo_appointed_detection(servoinitpos)
            time.sleep(0.5)
            self.pwm_LeftRightServo.ChangeDutyCycle(0)  # 归零信号
            self.pwm_UpDownServo.ChangeDutyCycle(0)  # 归零信号

    # 摄像头舵机上下归位
    def servo_updown_init(self):
        self.updownservo_appointed_detection(90)

    # 舵机停止
    def servo_stop(self):
        self.pwm_LeftRightServo.ChangeDutyCycle(0)  # 归零信号
        self.pwm_UpDownServo.ChangeDutyCycle(0)  # 归零信号