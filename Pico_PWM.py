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
ADS1015_ADDR = 0x48
ADS1015_PWM = 2  # port 2 has PWM signal
i2c = I2C(1, sda=Pin(14), scl=Pin(15))
adc = ADS1015(i2c, ADS1015_ADDR, 1)

# Transmit to opposite Pico the PWM duty cycle value
def transmit():
    duty = potentiometer.read_u16()    # read potentionmeter value (0–65535)          
    pwm.duty_u16(duty)                 # set PWM duty cycle
    uart.write("Initial transmit: %d\n" % duty)
    print("Pico transmitting ", duty)
    return duty

# Measure PWM duty cycle and return measured value
def measure_and_return_pwm():
    adc_value = adc.read(0, ADS1015_PWM)                    # raw digital value (0-2047 for the ADS1015)
    # GPT Calculation
    duty_percent = (adc_value / 2047) * (4.096 / 3.3) * 100 # convert to duty cycle percentage
    duty_cycle = duty_percent * 65535 / 100                 # convert to 16-bit value
    print("Measured and returned PWM value: ", duty_cycle)
    uart.write("Measured transmit: %d\n" % duty_cycle)
    return duty_cycle

# Read data from opposite Pico
def read():
    if uart.any():
        data = uart.read()
        if data:
            try:
                measure = data.decode('utf-8').strip()
                return measure
            except ValueError:
                pass

def extract_pwm_value(message):
    try:
        parts = message.split(":")
        if len(parts) == 2:
            return int(parts[1].strip())
    except ValueError:
        return None
    return None

def difference(transmited, measured):
    return abs(transmited - measured)


while True:
    received = read()
    if received is None:
        transmited = transmit()
    time.sleep(1)
    if received and received.startswith("Measured transmit:"):
        measured = extract_pwm_value(received)
        print ("Pico received measured PWM: ", measured)
        time.sleep(2)
        diff = difference(transmited, measured)
        print("Difference between transmitted and measured PWM: ", diff)
        time.sleep(1)
        continue
    elif received and received.startswith("Initial transmit:"):
        initial = extract_pwm_value(received)
        print("Pico received initial transmit PWM: ", initial)
        time.sleep(2)
        measure_and_return_pwm()
        time.sleep(1)
    else:
        continue
    time.sleep(1)

