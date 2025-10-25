from machine import Pin, UART, time_pulse_us
import time

# Serial communication setup
uart = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))
uart.init(9600, bits=8, parity=None, stop=1)

# PWM setup on GP14 (measure the pwm signal)
pwm_in = Pin(14, Pin.IN)

received = False
while not received:
    if uart.any():
        data = uart.read()
        if data:
            try:
                data = data.decode('utf-8').strip()
                print("Received:", data)
            except ValueError:
                pass
            # Measure PWM duty cycle
            hi = time_pulse_us(pwm_in, 1, 20000)  # time high in microseconds
            lo = time_pulse_us(pwm_in, 0, 20000)  # time low in microseconds
            if hi > 0 and lo > 0:
                val = int(65535 * hi / (hi + lo))  # scale to 0–65535
                print("PWM value:", val)
                uart.write("%d\n" % val)
            else:
                print("No signal")
    time.sleep(0.5)