# SED1115_project

This repository holds Anthony and Owen's PWM signal measurer project.

Pico_A.py holds the sender's code
Pico_B.py holds the receiver's code

In this project, a first Pico device sets a value for its PWM output duty cycle and then communicates this desired value to a second Pico device via a serial interface. The second Pico device will then measure the value of that PWM output signal. Once measured, the second Pico device must communicate the measured PWM value back to the first Pico device, using the same serial interface in the reverse direction.
