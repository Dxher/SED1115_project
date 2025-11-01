# SED1115_project

## Overview 

This repository holds Anthony and Owen's PWM signal measurer project.

Pico_PWM.py holds the code that allows to receive and transmit PWM 
signals. Furthermore, it calculates the measured difference and 
displays it.

In this project, a first Pico device sets a value for its PWM output duty cycle and then communicates this desired value to a second Pico device via a serial interface. The second Pico device will then measure the value of that PWM output signal. Once measured, the second Pico device must communicate the measured PWM value back to the first Pico device, using the same serial interface in the reverse direction.


## Status: Green

## Setup
You need to have a copy of ads1x15.py in the Mpy Remote Workspace.
You need to connect the UART 8-pins. Make sure TX is connected to the opposite side's RX.
GP0 Needs to be connected to the opposite Pico's PWM pin (both picos need to do this)

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
| ✓ | Build RC filter and validate analog response | Both | Oct 28 - Nov 2 |
| ✓ | Final testing, documentation, and cleanup | Both | Oct 19 – Nov 4|
| ✓ | Code submission for Final Demo | Both | Nov 4 |

