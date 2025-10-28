from machine import Pin, UART, PWM, ADC
import time

# Serial Communication Setup
uart = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))
uart.init(9600, bits=8, parity=None, stop=1)
buffer = b""

# PWM Setup
pwm = PWM(Pin(0))
pwm.freq(1000)

# potentiometer on A1 to change PWM value
adc = ADC(1)  


def transmit():
    # read potentionmeter value (0–65535)
    duty = adc.read_u16()          
    # set PWM duty
    pwm.duty_u16(duty)  
    # send duty value over UART           
    uart.write("SET:%d\n" % duty)
    #Show on console what is being sent
    print("Pico A: transmitting ", duty)
    return duty

# Send PWM value until we receive other Pico's measured value
received = False
while not received:
    Adata = transmit()
    time.sleep(1)
    if uart.any():
        data = uart.read()
        if data:
            try:
                Bdata = data.decode('utf-8').strip()
                print("Pico B measured and sent ", Bdata)
                print("Difference between values: ", abs(Adata - int(Bdata)))
            except ValueError:
                pass
            received = True
    time.sleep(1)
