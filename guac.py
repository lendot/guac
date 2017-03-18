import sys
import time
import pygame
import pygame.midi

import RPi.GPIO as GPIO

import Adafruit_MPR121.MPR121 as MPR121

import config

#octave=config.default_octave

#patch=config.default_patch

channels=[]
for i in range(4):
    channels.append({'midi_channel':i,
                     'on':True,
                     'patch':config.default_patch,
                     'octave':config.default_octave})

num_channels=len(channels)
current_channel=0


key_states=[]
for i in range(12):
    key_states.append({'on':False,'last_change':0})

    

#turns off all notes on the current channel
def notes_off():
    global channels
    global key_states
    global current_channel
    channel=channels[current_channel]
    octave=channel['octave']
    midi_channel=channel['midi_channel']
    current_time=int(round(time.time() * 1000))
    for i in range(len(key_states)):
        key_state=key_states[i]
        if key_state['on']:
            midi.note_off(octave*12+config.NOTE_OFFSET[i],None,midi_channel)
            key_state['on']=False
            key_state['last_change']=current_time
    
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
    global current_channel
    notes_off()
    current_channel+=1
    if current_channel>=num_channels:
        current_channel=0
    print("new channel: {0}".format(current_channel))
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
    global channels
    global current_channel

    notes_off()
    
    channel=channels[current_channel]
    
    if channel['octave']<8:
        channel['octave']+=1
        print ("New octave: {0}".format(channel['octave']))
    

# handler for octave down button press
def octave_down_button():
    global channels
    global current_channel

    notes_off()

    channel=channels[current_channel]
    
    if channel['octave']>0:
        channel['octave']-=1
        print ("New octave: {0}".format(channel['octave']))



# handler for patch up button press
def patch_up_button():
    global channels
    global current_channel

    notes_off()
    
    channel=channels[current_channel]

    if channel['patch']<127:
        channel['patch'] += 1
        print ("New patch: {0}".format(channel['patch']))
        midi.set_instrument(channel['patch'],channel['midi_channel'])
    return


# handler for patch down button press
def patch_down_button():
    global channels
    global current_channel

    notes_off()
    
    channel=channels[current_channel]

    if channel['patch']>0:
        channel['patch'] -= 1
        print ("New patch: {0}".format(channel['patch']))
        midi.set_instrument(channel['patch'],channel['midi_channel'])
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


for channel in channels:
    midi.set_instrument(channel['patch'],channel['midi_channel'])

#midi.set_instrument(patch)


def loop():
    
    current_touched = cap.touched()
    # Check each pin's last and current state to see if it was pressed or released.
    for i in range(12):
        # Each pin is represented by a bit in the touched value.  A value of 1
        # means the pin is being touched, and 0 means it is not being touched.
        pin_bit = 1 << i

        key_state = (current_touched & pin_bit)
        
        if key_state != key_states[i]['on']:
            current_time=int(round(time.time() * 1000))
            if (current_time-key_states[i]['last_change'])>config.key_debounce:
                key_states[i]['on']=key_state
                channel=channels[current_channel]
                octave=channel['octave']
                midi_channel=channel['midi_channel']
                if key_state:
                    print('{0} touched'.format(i))
                    midi.note_off(octave*12+config.NOTE_OFFSET[i],None,midi_channel)
                    midi.note_on(octave*12+config.NOTE_OFFSET[i],config.note_velocity,midi_channel)
                else:
                    print('{0} released'.format(i))
                    midi.note_off(octave*12+config.NOTE_OFFSET[i],None,midi_channel)
                key_states[i]['last_change']=current_time
        
        

    # check buttons
    for button in config.button_pins:
        button_state=GPIO.input(config.button_pins[button])
        if button_state != buttons[button]['on']:
            current_time=int(round(time.time() * 1000))
            if (current_time-buttons[button]['last_change'])>config.button_debounce:
                buttons[button]['on']=button_state
                if button_state:
                    print('{0} pressed'.format(button))
                    buttons[button]['handler']()
                else:
                    print('{0} released'.format(button))
                buttons[button]['last_change']=current_time
            

            
            
    return



print('Press Ctrl-C to quit.')
while True:
    loop()
    time.sleep(0.001)

