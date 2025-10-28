# SED1115_project

## Overview 

This repository holds Anthony and Owen's PWM signal measurer project.

Pico_A.py holds the sender's code
Pico_B.py holds the receiver's code

In this project, a first Pico device sets a value for its PWM output duty cycle and then communicates this desired value to a second Pico device via a serial interface. The second Pico device will then measure the value of that PWM output signal. Once measured, the second Pico device must communicate the measured PWM value back to the first Pico device, using the same serial interface in the reverse direction.


## Status: Orange
We have a functional setup, we simply need to implement the provided adc code to measure the PWM value.

## Work Plan

| Status | Task | Responsible | Duration |
|:------:|------|--------------|-----------|
| ✓ | Research PWM and Complete PA Report | Both | Sept 30 – Oct 06 |
| ✓ | Setup PWM output and test it | Anthony | Oct 07 |
| ✓ | Implement ADC reading and value calibration | Owen | Oct 08 – 10 |
| ✓ | Establish UART link between Picos | Both | Oct 11 – 13 |
| ✓ | Send/receive measured analog values | Both | Oct 13 – 15 |
| ✓ | Implement error handling | Both | Oct 16 – 18 |
| ✓ | Submit PB report | Both | Oct 25 |
| ✓ | Submit code for demonstration | Both | Oct 28 |
| WiP | Build RC filter and validate analog response | Both | Oct 28 - Nov 2 |
| WiP | Final testing, documentation, and cleanup | Both | Oct 19 – Nov 4|
| WiP | Code submission for Final Demo | Both | Nov 4 |

