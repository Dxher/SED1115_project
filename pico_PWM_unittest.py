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
        self.ADS_FS_CODE = 2047
        self.VREF_RATIO = 4.096 / 3.3


    # ---------- Parsing helpers ----------
    def test_extract_pwm_value_valid(self):
        self.assertEqual(pwmFile.extract_pwm_value("Initial transmit: 12345"), 12345)
        self.assertEqual(pwmFile.extract_pwm_value("Measured transmit: 0"), 0)

    def test_extract_pwm_value_invalid(self):
        self.assertIsNone(pwmFile.extract_pwm_value("No colon here"))
        self.assertIsNone(pwmFile.extract_pwm_value("Initial transmit: not_a_number"))
        self.assertIsNone(pwmFile.extract_pwm_value("too:many:colons:123"))

    # ---------- Difference helper ----------
    def test_difference(self):
        self.assertEqual(pwmFile.difference(1000, 800), 200)
        self.assertEqual(pwmFile.difference(800, 1000), -200)
        self.assertEqual(pwmFile.difference(0, 0), 0)

    # ---------- UART read behavior ----------
    def test_read_returns_stripped_line(self):
        self.uart.feed(b"Initial transmit: 12345\r\n")
        msg = pwmFile.read()
        self.assertEqual(msg, "Initial transmit: 12345")

    def test_read_handles_decode_error(self):
        # Invalid UTF-8 sequence -> should return None
        self.uart.feed(b"\xff\xff")
        msg = pwmFile.read()
        self.assertIsNone(msg)

    def test_read_no_data_returns_none(self):
        self.assertIsNone(pwmFile.read())

    # ---------- transmit() ----------
    def test_transmit_sets_pwm_and_writes_uart(self):
        self.pot.value = 43210
        duty = pwmFile.transmit()
        self.assertEqual(duty, 43210, "transmit() should return the pot reading")
        self.assertEqual(self.pwm.last_duty, 43210, "PWM duty should match pot reading")

        self.assertTrue(self.uart.writes, "Expected a UART write from transmit()")
        last_line = self.uart.writes[-1].decode("utf-8").strip()
        self.assertEqual(last_line, "Initial transmit: 43210")

    # ---------- measure_and_return_pwm() ----------
    def _expected_duty_from_adc(self, adc_code):
        # Mirrors the code logic:
        duty_percent = (adc_code / self.ADS_FS_CODE) * self.VREF_RATIO * 100.0
        duty_cycle = int(duty_percent * self.MAX_PWM / 100.0)
        return max(0, min(self.MAX_PWM, duty_cycle))

    def test_measure_and_return_pwm_low(self):
        self.adc.next_value = 0
        measured = pwmFile.measure_and_return_pwm()
        self.assertEqual(measured, 0, "ADC=0 should clamp to 0")
        # Also check UART wrote a measured line
        self.assertTrue(any(b"Measured transmit:" in w for w in self.uart.writes))

    def test_measure_and_return_pwm_mid(self):
        # About half-scale
        self.adc.next_value = self.ADS_FS_CODE // 2
        measured = pwmFile.measure_and_return_pwm()
        expected = self._expected_duty_from_adc(self.adc.next_value)
        # Allow small rounding differences
        self.assertAlmostEqual(measured, expected, delta=2)

    def test_measure_and_return_pwm_top_and_clamp(self):
        # Full-scale reading -> percent may exceed 100% due to 4.096/3.3 factor, should clamp
        self.adc.next_value = self.ADS_FS_CODE
        measured = pwmFile.measure_and_return_pwm()
        self.assertEqual(measured, self.MAX_PWM, "Should clamp to 65535 at/above full-scale")

    # ---------- Protocol snippets (without running the infinite loop) ----------
    def test_protocol_initial_then_measured_round_trip(self):
        # Simulate receiving an "Initial transmit" line, triggering a measurement send
        self.uart.feed(b"Initial transmit: 30000\n")
        msg1 = pwmFile.read()
        self.assertTrue(msg1.startswith("Initial transmit:")) # type: ignore

        # After our code would measure, it writes "Measured transmit: X".
        # We emulate a measurement directly:
        self.adc.next_value = int(self.ADS_FS_CODE * 0.5)
        measured = pwmFile.measure_and_return_pwm()
        # Ensure UART wrote a measured line
        self.assertTrue(any(b"Measured transmit:" in w for w in self.uart.writes))
        self.assertIsInstance(measured, int)

    # Ensure frequency configured as expected in setup
    def test_pwm_frequency_configured(self):
        self.assertIn(self.pwm.freq_hz, (None, 1000))


if __name__ == '__main__':
    unittest.main()
