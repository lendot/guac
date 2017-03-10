import sys
import time
import pygame
import pygame.midi

import RPi.GPIO as GPIO

import Adafruit_MPR121.MPR121 as MPR121

# octave to start with
octave=5

# patch to start with
patch=0

# Create MPR121 instance.
cap = MPR121.MPR121()

if not cap.begin():
    print('Error initializing MPR121.')
    sys.exit(1)


cap.set_thresholds(16,4)

# Alternatively, specify a custom I2C address such as 0x5B (ADDR tied to 3.3V),
# 0x5C (ADDR tied to SDA), or 0x5D (ADDR tied to SCL).
#cap.begin(address=0x5B)

# Also you can specify an optional I2C bus with the bus keyword parameter.
#cap.begin(busnum=1)

pygame.mixer.pre_init(44100, -16, 12, 512)
pygame.init()

button_pins={'patch_down' : 19,
             'patch_up' : 13,
             'octave_down' : 6,
             'octave_up' : 5}

#button_pins=[5,6,13,19]
button_on={'patch_down' : False,
           'patch_up' : False,
           'octave_down' : False,
           'octave_up' : False}

GPIO.setmode(GPIO.BCM)

for pin in button_pins.keys():
    GPIO.setup(button_pins[pin],GPIO.IN)


pygame.midi.init()
dev_info=pygame.midi.get_device_info(0)
print dev_info

midi=pygame.midi.Output(0)


#NOTE_MAPPING = [60,62,64,65,67,69,71,72,74,76,77,79]
NOTE_OFFSET = [0,2,4,5,7,9,11,12,14,16,17,19]


midi.set_instrument(patch)

print('Press Ctrl-C to quit.')
last_touched = cap.touched()
while True:
    current_touched = cap.touched()
    # Check each pin's last and current state to see if it was pressed or released.
    for i in range(12):
        # Each pin is represented by a bit in the touched value.  A value of 1
        # means the pin is being touched, and 0 means it is not being touched.
        pin_bit = 1 << i
        # First check if transitioned from not touched to touched.
        if current_touched & pin_bit and not last_touched & pin_bit:
            print('{0} touched!'.format(i))
            midi.note_off(octave*12+NOTE_OFFSET[i])
            midi.note_on(octave*12+NOTE_OFFSET[i],127,0)
        if not current_touched & pin_bit and last_touched & pin_bit:
            print('{0} released!'.format(i))
            midi.note_off(octave*12+NOTE_OFFSET[i])


    # check for patch up and down presses
    if (GPIO.input(button_pins['patch_up']) == True) and not button_on['patch_up']:
        print("patch_up pressed")
        if patch<127:
            patch += 1
            print ("New patch: {0}".format(patch))
            midi.set_instrument(patch)
        button_on['patch_up']=True
    if (GPIO.input(button_pins['patch_up']) == False) and button_on['patch_up']:
        print("patch_up released")
        button_on['patch_up']=False 
            
    if (GPIO.input(button_pins['patch_down']) == True) and not button_on['patch_down']:
        print("patch_down pressed")
        if patch>0:
            patch -= 1
            print ("New patch: {0}".format(patch))
            midi.set_instrument(patch)
        button_on['patch_down']=True
    if (GPIO.input(button_pins['patch_down']) == False) and button_on['patch_down']:
        print("patch_down released")
        button_on['patch_down']=False 
            

    # check for octave up and down presses
    if (GPIO.input(button_pins['octave_up']) == True) and not button_on['octave_up']:
        print("octave_up pressed")
        if octave<8:
            octave += 1
            print ("New octave: {0}".format(octave))
        button_on['octave_up']=True
    if (GPIO.input(button_pins['octave_up']) == False) and button_on['octave_up']:
        print("octave_up released")
        button_on['octave_up']=False 
            
    if (GPIO.input(button_pins['octave_down']) == True) and not button_on['octave_down']:
        print("octave_down pressed")
        if octave>0:
            octave -= 1
            print ("New octave: {0}".format(octave))
        button_on['octave_down']=True
    if (GPIO.input(button_pins['octave_down']) == False) and button_on['octave_down']:
        print("octave_down released")
        button_on['octave_down']=False 

    # Update last state and wait a short period before repeating.
    last_touched = current_touched
    time.sleep(0.001)
