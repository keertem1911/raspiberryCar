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
app=Flask(__name__)

auth=HTTPBasicAuth()
host = "192.168.3.12"
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
    elif dist==76:
        car.lightCar()
    elif dict==110:
        return jsonify({'speed':car.getCarSpeed()})
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
    if car is not None:
        car.leftBack()
        return 'success'
    return 'not init car'
def turnRightBack():
    print("turn right back")
    if car is not None:
        car.rightBack()
        return 'success'
    return 'not init car'
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
小车方向控制函数
"""
"""二度云台控制"""
from gpioCar import CarController
if __name__ == '__main__':
    thread = saveVideoClass(hoststr)
    car= CarController()
    app.run(
        host=host,
        port=8081,
        debug=False
    )