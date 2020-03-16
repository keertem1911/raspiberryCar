# coding=UTF-8
from flask import *
from flask_httpauth import HTTPBasicAuth
import os,cv2,urllib.request
import sys,time
from threading import Thread
import numpy as  np
import pygame
app=Flask(__name__)

auth=HTTPBasicAuth()
host = "wangchuanxin.uicp.top:10279"
hoststr = 'http://' + host + '/?action=snapshot'
thread=None
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
    elif dist == 38:
        upCamera()
    elif dist == 40:
        downCamera()
    elif dist == 37 :
        leftCamera()
    elif dist == 39 :
        downCamera()
    elif dist == 82 :
        response=downLoadPic()
    elif dist == 84:
        response=saveRecordVideo()
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

def downCamera():
    print('downCamera')

def leftCamera():
    print('leftCamera')
def rightCamera():
    print('rightCamera')
def speedUp(value=10):
    print('speed',value)
def forward():
    print("forward")
def turnLeft():
    print("turn left")
def turnRight():
    print("turn right")
def turnBack():
    print("turn back")
def turnStop():
    print("turn stop")
def turnLeftBack():
    print("turn left back")
def turnRightBack():
    print("turn right back")
def turnLeftForward():
    print("turn left Forward")
def turnRightForward():
    print("turn right Forward")
@app.route('/index')
@auth.login_required
def home():
    return send_file("templates/index.html")

if __name__ == '__main__':
    thread = saveVideoClass(hoststr)
    app.run(
        host="localhost",
        port=8081,
        debug=False
    )
