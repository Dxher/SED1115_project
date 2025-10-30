from machine import Pin, UART, PWM, ADC, I2C
import time
from ads1x15 import ADS1015

# Serial Communication Setup
uart = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))
uart.init(9600, bits=8, parity=None, stop=1)
buffer = b""

# PWM Setup
pwm = PWM(Pin(0))
pwm.freq(1000)

# Measure the pwm signal
pwm_in = Pin(14, Pin.IN)

# potentiometer on A1 to change PWM value
adc2 = ADC(1)  

# --- Hardware config (matches your given files) ---
I2C_SDA = 14
I2C_SCL = 15
ADS1015_ADDR = 0x48
PWM_CH = 2            # low-pass filtered PWM wired to A2
VHIGH = 3.3           # logic-high / supply of the PWM signal (adjust if different)

# --- Init once ---
i2c = I2C(1, sda=Pin(I2C_SDA), scl=Pin(I2C_SCL))
adc = ADS1015(i2c, ADS1015_ADDR, gain=1)  # gain index 1 => ±4.096 V full-scale

# Transmit to opposite Pico the PWM duty cycle value
def transmit():
    # read potentionmeter value (0–65535)
    duty = adc2.read_u16()          
    # set PWM duty
    pwm.duty_u16(duty)  
    # send duty value over UART           
    uart.write("SET:%d\n" % duty)
    #Show on console what is being sent
    print("Pico transmitting ", duty)
    return duty

# Measure PWM duty cycle and return measured value
def measure_and_return_pwm(channel: int = PWM_CH,
                  samples: int = 8,
                  rate: int = 4,
                  vhigh: float = VHIGH) -> float:
    """
    Returns duty cycle (0.0..1.0) measured via the RC-filtered PWM on ADS1015.

    channel: 0..3 single-ended ADS channel number
    samples: number of averaged ADC readings
    rate: ADS data rate index (see driver; 4 ≈ 1600 SPS on ADS1115, 3300 SPS on ADS1015)
    vhigh: actual high voltage of the PWM source (e.g., 3.3V)

    Note: Requires an RC low-pass so the PWM becomes a DC level ~ duty*vhigh.
    """
    acc = 0.0
    for _ in range(samples):
        raw = adc.read(rate=rate, channel1=channel, channel2=None)
        volts = adc.raw_to_v(raw)
        acc += volts
    v = acc / samples
    duty = max(0.0, min(1.0, v / vhigh))  # clamp to [0,1]
    return duty

# Read data from opposite Pico
def read():
    global buffer
    if uart.any():
        data = uart.read()
        if data:
            try:
                Bdata = data.decode('utf-8').strip()
                print("Received measured: ", Bdata)
                return Bdata
            except ValueError:
                pass


while True:
    transmitted = transmit()
    received = read()
    if transmitted and received:
        print("Difference between transmitted and received: ", abs(transmitted - int(received.split(":")[1])))
    measure_and_return_pwm()
    time.sleep(1)

