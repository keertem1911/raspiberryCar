# coding=UTF-8
from flask import *
from flask_httpauth import HTTPBasicAuth
import os,cv2,urllib.request
import time
from threading import Thread
import numpy as  np
import pygame

"""
引入gpio包
"""
import RPi.GPIO as GPIO

app=Flask(__name__)

auth=HTTPBasicAuth()
host = "wangchuanxin.uicp.top:10279"
hoststr = 'http://' + host + '/?action=snapshot'
thread=None
car=None
@auth.get_password
def authPasswd(username):
    if username=='keerte':
        return "m1911"
    return None
def getUrl(img_url):
    request = urllib.request.Request(img_url)

    return request
def download_img(img_url):
    request=getUrl(img_url)
    response = urllib.request.urlopen(request)
    if (response.getcode() == 200):
        bytes = response.read()
        a = bytes.find(b'\xff\xd8')
        b = bytes.find(b'\xff\xd9')
        if a!=-1 and b!=-1:
            jpg = bytes[a:b+3]
            bytes= bytes[b+2:]
            #flags = 1 for color image
            frame = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),flags=1)
            # frame = cv2.resize(frame, (640, 480))
            current_dir = os.path.dirname(__file__)
            pic_dir = os.path.join(current_dir, 'pic')
            nowTime =  getFormatTime(format="%Y-%m-%d_%H_%M_%S")
            cv2.putText(frame, nowTime, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,0,0), 2)
            filename=pic_dir + "/" + nowTime + '.jpg'
            cv2.imwrite(filename,frame)
    return "已保存图片"
class saveVideoClass(Thread):
    def __init__(self,hoststr):
        super().__init__()
        self.recordVideoState = False
        self.hoststr = hoststr
    def getState(self):
        return  self.recordVideoState
    def setState(self,state):
        self.recordVideoState=state
    def run(self):
        request = getUrl(self.hoststr)
        current_dir = os.path.dirname(__file__)
        video_dir = os.path.join(current_dir, 'video')
        nowTime = getFormatTime(format="%Y-%m-%d_%H_%M_%S")
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        filename = video_dir + "/" + nowTime + '.avi'
        out = cv2.VideoWriter(filename, fourcc, 20.0, (640, 480))
        while self.recordVideoState:
            response = urllib.request.urlopen(request)
            bytes = response.read()
            a = bytes.find(b'\xff\xd8')
            b = bytes.find(b'\xff\xd9')
            if a != -1 and b != -1:
                jpg = bytes[a:b + 3]
                bytes = bytes[b + 2:]
                # flags = 1 for color image
                frame = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), flags=1)
                nowTime = getFormatTime(format="%Y-%m-%d_%H_%M_%S")
                cv2.putText(frame, nowTime, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
                out.write(frame)
                print("record......")
        out.release()
        print('record finish ......')
        return '录制完成'
@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)
def getFormatTime( format="%Y%m%d%H%M%S"):
    now = int(time.time())  # 1533952277
    timeArray = time.localtime(now)
    otherStyleTime = time.strftime(format, timeArray)
    return otherStyleTime

pygame.mixer.init()
@app.route('/receiveAudio', methods=['POST'])
def receiveAudio():
    file = request.files['audio']
    if file:
        filename = os.path.join(os.path.dirname(__file__), file.name)
        file.save(filename)
        track = pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
    if os.path.exists(filename):
        os.remove(filename)
    return jsonify({'msg': "播放声音"})
"""
方向控制
    81左前    87：前     69右前
    65：左   32：停止    68：右
    90左后    83：后     67右后  16加速 
云台控制
            38 上
        37左  40下 39右
        82 拍照
"""

@app.route("/controller/api/pic",methods=['GET'])
@auth.login_required
def getPicture():
    current_dir = os.path.dirname(__file__)
    pic_dir=os.path.join(current_dir,'pic')
    data=[]
    for file in os.listdir(pic_dir):
        data.append("/pic/%s"%file)
    return jsonify(data)
@app.route("/controller/<int:dist>",methods=['GET'])
@auth.login_required
def controllerDist(dist):
    response='success'
    if dist is None:
        return abort(404)
    if dist ==87:
        forward()
    elif dist ==65:
        turnLeft()
    elif dist ==68:
        turnRight()
    elif dist ==83:
        turnBack()
    elif dist ==32:
        turnStop()
    elif dist == 90:
        turnLeftBack()
    elif dist == 67:
        turnRightBack()
    elif dist == 81:
        turnLeftForward()
    elif dist == 69 :
        turnRightForward()
    elif dist == 16 :
        speedUp()
    elif dist == 20 :
        speedDown()
    elif dist == 38:
        upCamera()
    elif dist == 40:
        downCamera()
    elif dist == 37 :
        leftCamera()
    elif dist == 39 :
        rightCamera()
    elif dist == 82 :
        response=downLoadPic()
    elif dist == 84:
        response=saveRecordVideo()
    elif dist ==70: #f
        car.whistle()
    return jsonify({'msg':response})
def saveRecordVideo():
    state= thread.getState()
    if state is False:
        thread.setState(True)
        thread.start()
        return "正在录制.."
    else:
        thread.setState(False)
        return '录制完成..'
def downLoadPic():
    response = download_img(hoststr)
    return response
def takePicture():
    print('takePicture')
    print()
def upCamera():
    print('upCamera')
    if car is not None:
        car.servo_up()
        return 'success'
    return 'not init car'
def downCamera():
    print('downCamera')
    if car is not None:
        car.servo_down()
        return 'success'
    return 'not init car'

def leftCamera():
    print('leftCamera')
    if car is not None:
        car.servo_left()
        return 'success'
    return 'not init car'

def rightCamera():
    print('rightCamera')
    if car is not None:
        car.servo_right()
        return 'success'
    return 'not init car'

def speedUp():
    if car is not None:
        car.speedUp()
        return 'success'
    return 'not init car'
def speedDown():
    if car is not None:
        car.speedDown()
        return 'success'
    return 'not init car'

def forward():
    if car is not None:
        car.run()
        return "success"
    print("forward")
    return "not init car"
def turnLeft():
    if car is not None:
        car.left()
        return "success"
    print("turn left")
    return "not init car"
def turnRight():
    if car is not None:
        car.right()
        return "success"
    print("turn right")
    return "not init car"
def turnBack():
    if car is not None:
        car.back()
        return "success"
    print("turn back")
    return "not init car"
def turnStop():
    if car is not None:
        car.brake()
        return 'success'
    print("turn stop")
    return 'not init car'
def turnLeftBack():
    print("turn left back")
def turnRightBack():
    print("turn right back")
def turnLeftForward():
    if car is not None:
        car.spin_left()
        return "success"
    print("turn left Forward")
    return 'not init car'
def turnRightForward():
    if car is not None:
        car.spin_right()
        return "success"
    print("turn right Forward")
    return 'not init car'
@app.route('/index')
@auth.login_required
def home():
    return send_file("templates/index.html")




"""
GPIO控制端
"""
#状态值定义
enSTOP = 0
enRUN =1
enBACK = 2
enLEFT = 3
enRIGHT = 4
enTLEFT =5
enTRIGHT = 6


#小车电机引脚定义
IN1 = 20
IN2 = 21
IN3 = 19
IN4 = 26
ENA = 16
ENB = 13
"""
小车方向控制函数
"""
#舵机引脚定义
ServoUpDownPin = 9
ServoLeftRightPin = 11

ServoLeftRightPos = 90
ServoUpDownPos = 90
#蜂鸣器引脚定义
buzzer = 8

CarSpeedControl=50
class CarController:
    def __init__(self):
        # 设置GPIO口为BCM编码方式
        GPIO.setmode(GPIO.BCM)
        global pwm_UpDownServo
        global pwm_LeftRightServo
        # 忽略警告信息
        GPIO.setwarnings(False)
        global pwm_ENA
        global pwm_ENB
        # 初始化速度
        self.CarSpeedControl=50
        """
        初始化小车控制
        """
        GPIO.setup(ENA, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(IN1, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(IN2, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(ENB, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(IN3, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(IN4, GPIO.OUT, initial=GPIO.LOW)
        # 设置pwm引脚和频率为2000hz
        pwm_ENA = GPIO.PWM(ENA, 2000)
        pwm_ENB = GPIO.PWM(ENB, 2000)
        pwm_UpDownServo = GPIO.PWM(ServoUpDownPin, 50)
        self.pwm_LeftRightServo = GPIO.PWM(ServoLeftRightPin, 50)
        pwm_ENA.start(0)
        pwm_ENB.start(0)
        pwm_UpDownServo.start(0)
        pwm_LeftRightServo.start(0)

        """
        初始化小车控制结束
        """
# 小车前进
    def run(self):
        GPIO.output(IN1, GPIO.HIGH)
        GPIO.output(IN2, GPIO.LOW)
        GPIO.output(IN3, GPIO.HIGH)
        GPIO.output(IN4, GPIO.LOW)
        pwm_ENA.ChangeDutyCycle(CarSpeedControl)
        pwm_ENB.ChangeDutyCycle(CarSpeedControl)
        time.sleep(1)

    # 小车后退
    def back(self):
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.HIGH)
        GPIO.output(IN3, GPIO.LOW)
        GPIO.output(IN4, GPIO.HIGH)
        pwm_ENA.ChangeDutyCycle(CarSpeedControl)
        pwm_ENB.ChangeDutyCycle(CarSpeedControl)
        time.sleep(1)

    # 小车左转
    def left(self):
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.LOW)
        GPIO.output(IN3, GPIO.HIGH)
        GPIO.output(IN4, GPIO.LOW)
        pwm_ENA.ChangeDutyCycle(CarSpeedControl)
        pwm_ENB.ChangeDutyCycle(CarSpeedControl)
        time.sleep(2)
    # 小车右转
    def right(self):
        GPIO.output(IN1, GPIO.HIGH)
        GPIO.output(IN2, GPIO.LOW)
        GPIO.output(IN3, GPIO.LOW)
        GPIO.output(IN4, GPIO.LOW)
        pwm_ENA.ChangeDutyCycle(CarSpeedControl)
        pwm_ENB.ChangeDutyCycle(CarSpeedControl)
        time.sleep(2)
    # 小车原地左转
    def spin_left(self):
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.HIGH)
        GPIO.output(IN3, GPIO.HIGH)
        GPIO.output(IN4, GPIO.LOW)
        pwm_ENA.ChangeDutyCycle(CarSpeedControl)
        pwm_ENB.ChangeDutyCycle(CarSpeedControl)

    # 小车原地右转
    def spin_right(self):
        GPIO.output(IN1, GPIO.HIGH)
        GPIO.output(IN2, GPIO.LOW)
        GPIO.output(IN3, GPIO.LOW)
        GPIO.output(IN4, GPIO.HIGH)
        pwm_ENA.ChangeDutyCycle(CarSpeedControl)
        pwm_ENB.ChangeDutyCycle(CarSpeedControl)
    # 小车停止
    def brake(self):
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.LOW)
        GPIO.output(IN3, GPIO.LOW)
        GPIO.output(IN4, GPIO.LOW)
    #加速
    def speedUp(self):
        self.CarSpeedControl += 10
        if self.CarSpeedControl>=100:
            self.CarSpeedControl=100
    #减速
    def speedDown(self):
        self.CarSpeedControl -= 10
        if self.CarSpeedControl <=0:
            self.CarSpeedControl = 0
    def getSpeed(self):
        return self.CarSpeedControl
    # 摄像头舵机左右旋转到指定角度
    def leftrightservo_appointed_detection(self,pos):
        for i in range(1):
            pwm_LeftRightServo.ChangeDutyCycle(2.5 + 10 * pos / 180)
            time.sleep(0.02)  # 等待20ms周期结束
            # pwm_LeftRightServo.ChangeDutyCycle(0)	#归零信号

    # 摄像头舵机上下旋转到指定角度
    def updownservo_appointed_detection(self,pos):
        for i in range(1):
            pwm_UpDownServo.ChangeDutyCycle(2.5 + 10 * pos / 180)
            time.sleep(0.02)  # 等待20ms周期结束
            # pwm_UpDownServo.ChangeDutyCycle(0)	#归零信号
    # 小车鸣笛
    def whistle(self):
        GPIO.output(buzzer, GPIO.LOW)
        time.sleep(0.1)
        GPIO.output(buzzer, GPIO.HIGH)
        time.sleep(0.001)
    # 摄像头舵机向上运动
    def servo_up(self):
        global ServoUpDownPos
        pos = ServoUpDownPos
        self.updownservo_appointed_detection(pos)
        # time.sleep(0.05)
        pos += 0.7
        ServoUpDownPos = pos
        if ServoUpDownPos >= 180:
            ServoUpDownPos = 180
    # 摄像头舵机向下运动
    def servo_down(self):
        global ServoUpDownPos
        pos = ServoUpDownPos
        self.updownservo_appointed_detection(pos)
        # time.sleep(0.05)
        pos -= 0.7
        ServoUpDownPos = pos
        if ServoUpDownPos <= 45:
            ServoUpDownPos = 45
    # 摄像头舵机向左运动
    def servo_left(self):
        global ServoLeftRightPos
        pos = ServoLeftRightPos
        self.leftrightservo_appointed_detection(pos)
        # time.sleep(0.10)
        pos += 0.7
        ServoLeftRightPos = pos
        if ServoLeftRightPos >= 180:
            ServoLeftRightPos = 180
    # 摄像头舵机向右运动
    def servo_right(self):
        global ServoLeftRightPos
        pos = ServoLeftRightPos
        self.leftrightservo_appointed_detection(pos)
        # time.sleep(0.10)
        pos -= 0.7
        ServoLeftRightPos = pos
        if ServoLeftRightPos <= 0:
            ServoLeftRightPos = 0
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
            pwm_LeftRightServo.ChangeDutyCycle(0)  # 归零信号
            pwm_UpDownServo.ChangeDutyCycle(0)  # 归零信号
    # 摄像头舵机上下归位
    def servo_updown_init(self):
        self.updownservo_appointed_detection(90)
    # 舵机停止
    def servo_stop(self):
        pwm_LeftRightServo.ChangeDutyCycle(0)  # 归零信号
        pwm_UpDownServo.ChangeDutyCycle(0)  # 归零信号


"""
小车方向控制函数
"""
"""二度云台控制"""

if __name__ == '__main__':
    thread = saveVideoClass(hoststr)
    car= CarSpeedControl
    app.run(
        host="localhost",
        port=8081,
        debug=False
    )