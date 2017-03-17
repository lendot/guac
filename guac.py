import sys
import time
import pygame
import pygame.midi

import RPi.GPIO as GPIO

import Adafruit_MPR121.MPR121 as MPR121

import config

octave=config.default_octave

patch=config.default_patch



# handler for record button press
def record_button():
    return

# handler for play button press
def play_button():
    return

# handler for stop button press
def stop_button():
    return

# handler for clear button press
def clear_button():
    return

# handler for track advance button press
def track_advance_button():
    return

# handler for track1 enable/disable button press
def track1_mute_button():
    return

# handler for track2 enable/disable button press
def track2_mute_button():
    return

# handler for track3 enable/disable button press
def track3_mute_button():
    return

# handler for track4 enable/disable button press
def track4_mute_button():
    return

# handler for octave up button press
def octave_up_button():
    global octave
    if octave<8:
        octave += 1
        print ("New octave: {0}".format(octave))
    return


# handler for octave down button press
def octave_down_button():
    global octave
    if octave>0:
        octave -= 1
        print ("New octave: {0}".format(octave))
    return


# handler for patch up button press
def patch_up_button():
    global patch
    if patch<127:
        patch += 1
        print ("New patch: {0}".format(patch))
        midi.set_instrument(patch)
    return


# handler for patch down button press
def patch_down_button():
    global patch
    if patch>0:
        patch -= 1
        print ("New patch: {0}".format(patch))
        midi.set_instrument(patch)
    return


buttons = {
    'record':{'handler':record_button,'on':False,'last_change':0},
    'play':{'handler':play_button,'on':False,'last_change':0},
    'stop':{'handler':stop_button,'on':False,'last_change':0},
    'clear':{'handler':clear_button,'on':False,'last_change':0},
    'track_advance':{'handler':track_advance_button,'on':False,'last_change':0},
    'track1_mute':{'handler':track1_mute_button,'on':False,'last_change':0},
    'track2_mute':{'handler':track2_mute_button,'on':False,'last_change':0},
    'track3_mute':{'handler':track3_mute_button,'on':False,'last_change':0},
    'track4_mute':{'handler':track4_mute_button,'on':False,'last_change':0},
    'octave_up':{'handler':octave_up_button,'on':False,'last_change':0},
    'octave_down':{'handler':octave_down_button,'on':False,'last_change':0},
    'patch_up':{'handler':patch_up_button,'on':False,'last_change':0},
    'patch_down':{'handler':patch_down_button,'on':False,'last_change':0},
}
    


# Create MPR121 instance.
cap = MPR121.MPR121()

if not cap.begin():
    print('Error initializing MPR121.')
    sys.exit(1)


cap.set_thresholds(config.on_threshold,config.off_threshold)

# Alternatively, specify a custom I2C address such as 0x5B (ADDR tied to 3.3V),
# 0x5C (ADDR tied to SDA), or 0x5D (ADDR tied to SCL).
#cap.begin(address=0x5B)

# Also you can specify an optional I2C bus with the bus keyword parameter.
#cap.begin(busnum=1)

pygame.mixer.pre_init(44100, -16, 12, 512)
pygame.init()


GPIO.setmode(GPIO.BCM)

for pin in config.button_pins.keys():
    GPIO.setup(config.button_pins[pin],GPIO.IN)


pygame.midi.init()
dev_info=pygame.midi.get_device_info(config.midi_device)
print dev_info

midi=pygame.midi.Output(config.midi_device)


midi.set_instrument(patch)

last_touched = cap.touched()


def loop():
    global last_touched
    
    current_touched = cap.touched()
    # Check each pin's last and current state to see if it was pressed or released.
    for i in range(12):
        # Each pin is represented by a bit in the touched value.  A value of 1
        # means the pin is being touched, and 0 means it is not being touched.
        pin_bit = 1 << i
        # First check if transitioned from not touched to touched.
        if current_touched & pin_bit and not last_touched & pin_bit:
            print('{0} touched!'.format(i))
            midi.note_off(octave*12+config.NOTE_OFFSET[i])
            midi.note_on(octave*12+config.NOTE_OFFSET[i],127,0)
        if not current_touched & pin_bit and last_touched & pin_bit:
            print('{0} released!'.format(i))
            midi.note_off(octave*12+config.NOTE_OFFSET[i])


    # check buttons
    for button in config.button_pins:
        if (GPIO.input(config.button_pins[button]) == True) and not buttons[button]['on']:
            print('{0} pressed'.format(button))
            buttons[button]['on']=True
            buttons[button]['handler']()
        if (GPIO.input(config.button_pins[button]) == False) and buttons[button]['on']:
            print('{0} released'.format(button))
            buttons[button]['on']=False

            
    # Update last state and wait a short period before repeating.
    last_touched = current_touched
    return



print('Press Ctrl-C to quit.')
while True:
    loop()
    time.sleep(0.001)

