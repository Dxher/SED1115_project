import unittest

import testable_pico_PWM as pwmFile

class FakeUART:
    def __init__(self):
        self._rx = b""
        self.writes = []
    def any(self): return len(self._rx) > 0
    def read(self):
        if not self._rx: return None
        data = self._rx
        self._rx = b""
        return data
    def write(self, data):
        if isinstance(data, str):
            data = data.encode("utf-8")
        self.writes.append(data)
    def feed(self, data_bytes):
        self._rx += data_bytes

class FakePWM:
    def __init__(self):
        self.freq_hz = None
        self.last_duty = None
    def freq(self, hz): self.freq_hz = hz
    def duty_u16(self, duty): self.last_duty = int(duty)

class FakePot:
    def __init__(self, value=0): self.value = int(value)
    def read_u16(self): return int(self.value)

class FakeADC1015:
    def __init__(self): self.next_value = 0
    def read(self, *args, **kwargs): return int(self.next_value)

class FakeTime:
    def __init__(self): self.slept = []
    def sleep(self, s): self.slept.append(s)


class TestPicoComm(unittest.TestCase):
    def setUp(self):
        # Replace module globals with fakes
        self.uart = FakeUART()
        self.pwm = FakePWM()
        self.pot = FakePot(0)
        self.adc = FakeADC1015()
        self.fake_time = FakeTime()

        pwmFile.uart = self.uart # type: ignore
        pwmFile.pwm = self.pwm # type: ignore
        pwmFile.potentiometer = self.pot # type: ignore
        pwmFile.adc = self.adc # type: ignore

        # constants mirrored from pico_PWM.py
        self.MAX_PWM = 65535
        self.MAX_MEASURE = 2047

    # ---------- extract_pwm_value() ----------
    def test_extract_pwm_value_valid(self):
        self.assertEqual(pwmFile.extract_pwm_value("Initial transmit: 12345"), 12345)
        self.assertEqual(pwmFile.extract_pwm_value("Measured transmit: 12345"), 12345)
        self.assertEqual(pwmFile.extract_pwm_value("Initial transmit: 0"), 0)
        self.assertEqual(pwmFile.extract_pwm_value("Measured transmit: 0"), 0)
        self.assertEqual(pwmFile.extract_pwm_value("Initial transmit: 4000"), 4000)
        self.assertEqual(pwmFile.extract_pwm_value("Measured transmit: 4000"), 4000)

    def test_extract_pwm_value_invalid(self):
        self.assertIsNone(pwmFile.extract_pwm_value("No colon here"))
        self.assertIsNone(pwmFile.extract_pwm_value("Initial transmit: not_a_number"))
        self.assertIsNone(pwmFile.extract_pwm_value("Initial transmit:: 500"))
        self.assertIsNone(pwmFile.extract_pwm_value("Initial transmit 500"))
        self.assertIsNone(pwmFile.extract_pwm_value("too:many:colons:123"))

    # ---------- difference() ----------
    def test_difference(self):
        self.assertEqual(pwmFile.difference(1000, 800), 200)
        self.assertEqual(pwmFile.difference(800, 1000), -200)
        self.assertEqual(pwmFile.difference(0, 0), 0)
    
    def test_difference_with_none(self):
        self.assertIsNone(pwmFile.difference(None, 1000))
        self.assertIsNone(pwmFile.difference(1000, None))
        self.assertIsNone(pwmFile.difference(None, None))

    # ---------- read() ----------
    def test_read_returns_stripped_line(self):
        self.uart.feed(b"Initial transmit: 12345\r\n")
        msg = pwmFile.read()
        self.assertEqual(msg, "Initial transmit: 12345")
        self.uart.feed(b"Measured transmit: 12345\r\n")
        msg = pwmFile.read()
        self.assertEqual(msg, "Measured transmit: 12345")

    def test_read_handles_decode_error(self):
        self.uart.feed(b"\xff\xff")
        msg = pwmFile.read()
        self.assertIsNone(msg)

    def test_read_wrong_format_returns_none(self):
        self.uart.feed(b"Just some random text\n")
        msg = pwmFile.read()
        self.assertEqual(msg, "Just some random text")

    def test_read_no_data_returns_none(self):
        self.assertIsNone(pwmFile.read())

    # ---------- transmit() ----------
    def test_transmit(self):
        self.pot.value = 43210
        duty = pwmFile.transmit()
        self.assertEqual(duty, 43210, "transmit() should return the pot reading")
        self.assertEqual(self.pwm.last_duty, 43210, "PWM duty should match pot reading")

        self.assertTrue(self.uart.writes, "Expected a UART write from transmit()")
        last_line = self.uart.writes[-1].decode("utf-8").strip()
        self.assertEqual(last_line, "Initial transmit: 43210")

    def test_transmit_below_value(self):
        self.pot.value = -100
        duty = pwmFile.transmit()
        self.assertEqual(duty, 0, "transmit() should clamp value to 0")
        self.assertEqual(self.pwm.last_duty, 0, "PWM duty should be clamped to 0")

        self.assertTrue(self.uart.writes, "Expected a UART write from transmit()")
        last_line = self.uart.writes[-1].decode("utf-8").strip()
        self.assertEqual(last_line, "Initial transmit: 0")

    def test_transmit_above_value(self):
        self.pot.value = 70000
        duty = pwmFile.transmit()
        self.assertEqual(duty, 65535, "transmit() should clamp value to 65535")
        self.assertEqual(self.pwm.last_duty, 65535, "PWM duty should be clamped to 65535")

        self.assertTrue(self.uart.writes, "Expected a UART write from transmit()")
        last_line = self.uart.writes[-1].decode("utf-8").strip()
        self.assertEqual(last_line, "Initial transmit: 65535")

    def test_transmit_exception_handling(self):
        self.pot.read_u16 = Exception("Read error") # type: ignore
        duty = pwmFile.transmit()
        self.assertEqual(duty, 0, "transmit() should return 0 on read exception")
        self.assertEqual(self.pwm.last_duty, 0, "PWM duty should be set to 0 on read exception")

        self.assertTrue(self.uart.writes, "Expected a UART write from transmit()")
        last_line = self.uart.writes[-1].decode("utf-8").strip()
        self.assertEqual(last_line, "Initial transmit: 0")

    # ---------- measure_and_return_pwm() ----------
    def test_measure_and_return_pwm_normal(self):
        self.adc.next_value = 1024
        measured = pwmFile.measure_and_return_pwm()
        self.assertEqual(measured, 40691, "Measured duty should match expected from ADC")

    def test_measure_and_return_pwm_low(self):
        self.adc.next_value = 0
        measured = pwmFile.measure_and_return_pwm()
        self.assertEqual(measured, 0, "ADC=0 should clamp to 0")
        self.assertTrue(any(b"Measured transmit:" in w for w in self.uart.writes))

    def test_measure_and_return_pwm_high(self):
        self.adc.next_value = self.MAX_MEASURE
        measured = pwmFile.measure_and_return_pwm()
        self.assertEqual(measured, 65535, "ADC=max should map to expected max duty")
        self.assertTrue(any(b"Measured transmit:" in w for w in self.uart.writes))

    def test_measure_and_return_pwm_out_of_bounds_low(self):
        self.adc.next_value = -100
        measured = pwmFile.measure_and_return_pwm()
        self.assertEqual(measured, 0, "ADC<0 should clamp to 0")
        self.assertTrue(any(b"Measured transmit:" in w for w in self.uart.writes))
    
    def test_measure_and_return_pwm_out_of_bounds_high(self):
        self.adc.next_value = self.MAX_MEASURE + 100
        measured = pwmFile.measure_and_return_pwm()
        self.assertEqual(measured, 65535, "ADC>max should clamp to max duty")
        self.assertTrue(any(b"Measured transmit:" in w for w in self.uart.writes))

    def test_measure_and_return_pwm_exception_handling(self):
        self.adc.read = Exception("ADC read error") # type: ignore
        measured = pwmFile.measure_and_return_pwm()
        self.assertIsNone(measured, "Should return None on ADC read exception")

if __name__ == '__main__':
    unittest.main()
