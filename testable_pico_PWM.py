"""
This copy contains the identical code of pico_PWM.py minus the imports,
the variables that initialize hardware, and the main loop.
This is done for testing purposes.
"""

#from machine import Pin, UART, PWM, ADC, I2C
import time
#from ads1x15 import ADS1015

# Serial Communication Setup
#uart = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))
#uart.init(bits=8, parity=None, stop=1)

# GPIO 0 as PWM output channel
#pwm = PWM(Pin(0))
#pwm.freq(1000)

# potentiometer on A1 to change PWM value
#potentiometer = ADC(1)  

# Measurement Setup for ADS1015
ADS1015_ADDR = 0x48 # I2C address
ADS1015_PWM = 2  # port 2 has PWM signal
#i2c = I2C(1, sda=Pin(14), scl=Pin(15)) 
#adc = ADS1015(i2c, ADS1015_ADDR, 1) 

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
    duty_cycle = int(duty_cycle)
    # Prevent out of bounds
    if duty_cycle < 0:
        duty_cycle = 0
    elif duty_cycle > 65535:
        duty_cycle = 65535
    print("Measured and returned PWM value: ", duty_cycle)
    uart.write("Measured transmit: %d\n" % duty_cycle)
    return duty_cycle

# Read data from opposite Pico
def read():
    if uart.any():
        data = uart.read()
        if data:
            try:
                measure = data.decode('utf-8').strip() # decode bytes to string
                return measure
            except ValueError:
                pass

# Extract PWM value from received message
def extract_pwm_value(message):
    try:
        parts = message.split(":") # split at colon
        if len(parts) == 2:
            return int(parts[1].strip())
    except ValueError:
        return None
    return None

# Calculate difference between transmitted and measured PWM
def difference(transmited, measured):
    return int(transmited - measured)


"""
Main loop to handle transmission and measurement
If no message is received, transmit new PWM value.
If "Initial transmit" message is received, measure and return PWM.
If "Measured transmit" message is received, calculate and print difference.
If message is invalid, ignore and continue.
"""
# while True:
#     received = read()
#     if received is None:
#         transmited = transmit()
#     time.sleep(1)
#     if received and received.startswith("Initial transmit:"):
#         initial = extract_pwm_value(received)
#         if initial is None:
#             continue
#         print("Pico received initial transmit PWM: ", initial)
#         time.sleep(2)
#         measure_and_return_pwm()
#         time.sleep(1)
#     if received and received.startswith("Measured transmit:"):
#         measured = extract_pwm_value(received)
#         if measured is None:
#             continue
#         print ("Pico received measured PWM: ", measured)
#         time.sleep(2)
#         diff = difference(transmited, measured)
#         print("Difference between transmitted and measured PWM: ", diff)
#         time.sleep(1)
#         continue
#     else:
#         continue
#     time.sleep(1)

