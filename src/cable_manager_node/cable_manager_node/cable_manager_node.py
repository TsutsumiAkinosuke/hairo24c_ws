import rclpy
from rclpy.node import Node
from std_msgs.msg import Int8MultiArray
import RPi.GPIO as GPIO
import atexit

class CableManagerNode(Node):

    def __init__(self):

        super().__init__('cable_manager_node')

        # duty比を受信
        self.subscription = self.create_subscription(Int8MultiArray, 'duty', self.duty_callback, 10)
        self.duty = Int8MultiArray()

        # 50msごとにモータの状態を更新
        self.timer = self.create_timer(0.050, self.timer_callback)

        # GPIOライブラリのモード設定
        GPIO.setmode(GPIO.BCM)

        # MD用ピンのセットアップ
        self.mt1A = 15
        self.mt1B = 18
        self.mt2A = 23
        self.mt2B = 24
        GPIO.setup(self.mt1A, GPIO.OUT)
        GPIO.setup(self.mt1B, GPIO.OUT)
        GPIO.setup(self.mt2A, GPIO.OUT)
        GPIO.setup(self.mt2B, GPIO.OUT)

        # PWMピンのセットアップ(pin, hz)
        self.mt_freq = 1000
        self.pwm1A = GPIO.PWM(self.mt1A, self.mt_freq)
        self.pwm1B = GPIO.PWM(self.mt1B, self.mt_freq)
        self.pwm2A = GPIO.PWM(self.mt2A, self.mt_freq)
        self.pwm2B = GPIO.PWM(self.mt2B, self.mt_freq)

        # duty比0でpwm波を出力
        self.pwm1A.start(0.0)
        self.pwm1B.start(0.0)
        self.pwm2A.start(0.0)
        self.pwm2B.start(0.0)
        
    def duty_callback(self, msg):

        # ケーブル機構のduty比をクラスのメンバに落とす
        self.duty = msg.data[2:4]
    
    def timer_callback(self):

        # duty比が5より大きく100以下のとき正回転
        if 5 < self.duty[0] <= 100:
            self.pwm1A.ChangeDutyCycle(self.duty[0])
            self.pwm1B.ChangeDutyCycle(0.0)
        # duty比が-100以上-5未満のとき逆回転
        elif -100 <= self.duty[0] < -5:
            self.pwm1A.ChangeDutyCycle(0.0)
            self.pwm1B.ChangeDutyCycle(abs(self.duty[0]))
        # duty比が+5~-5以内または絶対値が100より大きいときモータを回さない
        else:
            self.pwm1A.ChangeDutyCycle(0.0)
            self.pwm1B.ChangeDutyCycle(0.0)
        
        # duty比が5より大きく100以下のとき正回転
        if 5 < self.duty[1] <= 100:
            self.pwm2A.ChangeDutyCycle(self.duty[1])
            self.pwm2B.ChangeDutyCycle(0.0)
        # duty比が-100以上-5未満のとき逆回転
        elif -100 <= self.duty[1] < -5:
            self.pwm2A.ChangeDutyCycle(0.0)
            self.pwm2B.ChangeDutyCycle(abs(self.duty[1]))
        # duty比が+5~-5以内または絶対値が100より大きいときモータを回さない
        else:
            self.pwm2A.ChangeDutyCycle(0.0)
            self.pwm2B.ChangeDutyCycle(0.0)
        
    def close(self):

        self.pwm1A.ChangeDutyCycle(0.0)
        self.pwm1B.ChangeDutyCycle(0.0)
        self.pwm2A.ChangeDutyCycle(0.0)
        self.pwm2B.ChangeDutyCycle(0.0)


def main(args=None):

    rclpy.init(args=args)
    node = CableManagerNode()
    atexit.register(node.close)
    try:
        rclpy.spin(node)
    finally:
        node.close()
        GPIO.cleanup()
        rclpy.shutdown()

if __name__ == '__main__':
    main()