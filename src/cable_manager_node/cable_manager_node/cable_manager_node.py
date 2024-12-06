import rclpy
from rclpy.node import Node
from std_msgs.msg import Int16MultiArray
import RPi.GPIO as GPIO

class CableManagerNode(Node):

    def __init__(self):

        super().__init__('cable_manager_node')

        # duty比を受信
        self.subscription = self.create_subscription(Int16MultiArray, 'duty', self.duty_callback, 10)
        self.duty = Int16MultiArray()

        # 50msごとにモータの状態を更新
        self.timer = self.create_timer(0.050, self.timer_callback)

        # GPIOライブラリのモード設定
        GPIO.setmode(GPIO.BCM)

        # MD用ピンのセットアップ
        self.mtA = 5    # Aピン
        self.mtB = 6    # Bピン
        self.mtP = 13   # Pピン
        GPIO.setup(self.mtA, GPIO.OUT)
        GPIO.setup(self.mtB, GPIO.OUT)
        GPIO.setup(self.mtP, GPIO.OUT)

        # PWMピンのセットアップ
        self.pwm = GPIO.PWM(13, 1000)  # pin, hz

        # duty比0でpwm波を出力
        self.pwm.start(0)
        
    def duty_callback(self, msg):

        # ケーブル機構のduty比をクラスのメンバに落とす
        self.duty = msg.data[2]
    
    def timer_callback(self):

        # duty比が5より大きく100以下のとき正回転
        if 5 < self.duty <= 100:
            GPIO.output(self.mtA, GPIO.HIGH)
            GPIO.output(self.mtB, GPIO.LOW)
            self.pwm.ChangeDutyCycle(self.duty)
        # duty比が-100以上-5未満のとき逆回転
        elif -100 <= self.duty < -5:
            GPIO.output(self.mtA, GPIO.LOW)
            GPIO.output(self.mtB, GPIO.HIGH)
            self.pwm.ChangeDutyCycle(abs(self.duty))
        # duty比が+5~-5以内または絶対値が100より大きいときモータを回さない
        else:
            GPIO.output(self.mtA, GPIO.LOW)
            GPIO.output(self.mtB, GPIO.LOW)
            self.pwm.ChangeDutyCycle(0.0)

def main(args=None):

    rclpy.init(args=args)
    node = CableManagerNode()
    rclpy.spin(node)
    GPIO.cleanup()
    rclpy.shutdown()

if __name__ == '__main__':
    main()