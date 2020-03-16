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
#��Ҫע����ǣ�����Ķ�ȡ����ֻ�ǻ�ȡ��ǰһ˲������������ź�
GPIO.setup(pin,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
"""
�����Ҫʵʱ������ŵ�״̬�仯�����������ְ취��
���ԭʼ�ķ�ʽ��ÿ��һ��ʱ����������ź�ֵ�����ַ�ʽ����Ϊ��ѯ��
�����ĳ����ȡ��ʱ��������ܿ��ܻᶪʧ�����źš�
��ѯ����ѭ����ִ�еģ����ַ�ʽ�Ƚ�ռ�ô�������Դ��
"""
while GPIO.input(pin)== GPIO.LOW:
    time.sleep(0.1)
"""
��һ����ӦGPIO����ķ�ʽ��ʹ���жϣ���Ե��⣩��
����ı�Ե��ָ�źŴӸߵ��͵ı任���½��أ���ӵ͵��ߵı任�������أ���
"""
"""
��Ե���
��Ե��ָ�ź�״̬�ĸı䣬�ӵ͵��ߣ������أ���Ӹߵ��ͣ��½��أ���ͨ������£����Ǹ�����������״̬�ĸñ߶����������źŵ�ֵ������״̬�ĸñ߱���Ϊ�¼���

wait_for_edge() ����
wait_for_edge()��������ֹ����ļ���ִ�У�ֱ����⵽һ����Ե��
"""
channel = GPIO.wait_for_edge(pin,GPIO.RISING,timeout=5000)

"""
add_event_detect() ����
�ú�����һ�����Ž��м�����һ����������״̬�����˸ı䣬����event_detected()�����᷵��true��
"""
GPIO.add_event_detect(pin,GPIO.RISING)
if GPIO.add_event_detected(pin):
    print("break event")
"""
RPI.GPIO ģ���������ƣ�PWM������
�������(PWM)��ָ��΢�������������������ģ���·���п��ƣ���һ�ֶ�ģ���źŵ�ƽ�������ֱ���ķ���������ݮ���ϣ�����ͨ����GPIO�ı����ʵ��PWM��
����һ�� PWM ʵ����
"""
p=GPIO.PWM(pin,50)#50hz
"""
���� PWM��ռ�ձȣ���Χ��0.0 <= dc <= 100.0��
"""
p.start(10)
"""
����Ƶ�ʣ�
"""
p.changeFrequency(40)
"""
����ռ�ձȣ�  ��Χ��0.0 <= dc >= 100.0
"""
p.ChangeDutyCycle(10)

"""
ֹͣ PWM��
"""
p.stop()