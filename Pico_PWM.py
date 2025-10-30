from machine import Pin, UART, PWM, ADC, I2C
import time
from ads1x15 import ADS1015

# Serial Communication Setup
uart = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))
uart.init(bits=8, parity=None, stop=1)

# PWM OUT on GP0
pwm = PWM(Pin(0))
pwm.freq(1000)

# potentiometer on A1 to change PWM value
potentiometer = ADC(1)  

# ---- I2C + ADS1015 ----
I2C_SDA = 14
I2C_SCL = 15
ADS1015_ADDR = 0x48
ADS1015_PWM = 2  # port 2 has PWM signal
i2c = I2C(1, sda=Pin(I2C_SDA), scl=Pin(I2C_SCL))
adc = ADS1015(i2c, ADS1015_ADDR, 1)

# Transmit to opposite Pico the PWM duty cycle value
def transmit():
    duty = potentiometer.read_u16()    # read potentionmeter value (0–65535)          
    pwm.duty_u16(duty)                 # set PWM duty cycle
    uart.write("%d\n" % duty)
    print("Pico transmitting ", duty)
    return duty

# Measure PWM duty cycle and return measured value
def measure_and_return_pwm():
    value = adc.read(0, ADS1015_PWM)   # just the channel
    print("Measured PWM value: ", value)
    return value

# Read data from opposite Pico
def read():
    if uart.any():
        data = uart.read()
        if data:
            try:
                measure = data.decode('utf-8').strip()
                print("Received measured PWM value: ", measure)
                return measure
            except ValueError:
                pass


while True:
    transmitted = transmit()
    time.sleep(1)
    received = read()
    time.sleep(1)
    #if transmitted and received:
        #print("Difference between transmitted and received: ", abs(transmitted - int(received.split(":")[1])))
    measure_and_return_pwm()
    time.sleep(1)

