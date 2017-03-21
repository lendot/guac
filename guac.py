import sys
import time
import pygame
import pygame.midi

import RPi.GPIO as GPIO

import Adafruit_MPR121.MPR121 as MPR121

import config

playing=False
recording=False
loop_length=-1
loop_start=-1

events=[]
event_index=0

tracks=[]
for i in range(4):
    tracks.append({'midi_channel':i,
                     'on':True,
                     'patch':config.default_patch,
                     'octave':config.default_octave})

tracks[3]['midi_channel']=9
print(tracks)

num_tracks=len(tracks)
current_track=0


key_states=[]
for i in range(12):
    key_states.append({'on':False,'last_change':0})


def debug_print(msg):
    if config.debug:
        print(msg)

# get the current time, in ms
def get_time():
    current_time=int(round(time.time() * 1000))
    return current_time
        
#turns off all notes on the current track
def notes_off():
    global tracks
    global key_states
    global current_track
    track=tracks[current_track]
    octave=track['octave']
    midi_channel=track['midi_channel']
    current_time=get_time()
    for i in range(len(key_states)):
        key_state=key_states[i]
        if key_state['on']:
            midi.note_off(octave*12+config.NOTE_OFFSET[i],None,midi_channel)
            key_state['on']=False
            key_state['last_change']=current_time
    
# handler for record button press
def record_button():
    global playing,recording,event_index,loop_start,loop_length
    print("Record")
    if recording and loop_length==-1:
        # This is a new loop. Mark now as the loop end
        current_time=get_time()
        loop_length=current_time-loop_start
        event_index=0
        loop_start=current_time
        playing=True
        debug_print("end new loop. Length: {0}".format(loop_length))
    elif not recording:
        debug_print("starting loop record")
        recording=True
        if not playing:
            playing=True
            current_time=get_time()
            loop_start=current_time
            event_index=0
            debug_print("starting loop play")
    return

# handler for play button press
def play_button():
    global playing,recording,event_index,loop_start,loop_length
    print("Play")
    if playing and not recording:
        # right now we'll just do nothing in this state.
        return
    elif recording:
        # come out of recording into play mode
        debug_print("changing from loop record to playback")
        recording=False
        playing=True # just to be on the safe side
        if loop_length==-1:
            # this is a new loop. Mark now as the loop end
            current_time=get_time()
            loop_length=current_time-loop_start
            event_index=0
            loop_start=current_time
            debug_print("end new loop. Length: {0}".format(loop_length))
    elif not playing and loop_length>0:
        debug_print("starting loop play")
        playing=True
        event_index=0
        loop_start=get_time()
    return

# handler for stop button press
def stop_button():
    print("Stop")
    global loop_start,recording,loop_length,event_index,playing,recording
    if recording and loop_length==-1:
        # stop was hit during a new loop. Mark this as the loop end
        current_time=get_time()
        loop_length=current_time-loop_start
        debug_print("end new loop. Length: {0}".format(loop_length))
    recording=False
    playing=False
    event_index=0
    return

# handler for clear button press
def clear_button():
    global recording,playing,loop_length,loop_start,events,event_index
    print("Clear")
    recording=False
    playing=False
    loop_length=-1
    del events[:]
    event_index=0
    return

# handler for track advance button press
def track_advance_button():
    global current_track
    notes_off()
    GPIO.output(config.track_led_pins[current_track],GPIO.LOW)
    current_track+=1
    if current_track>=num_tracks:
        current_track=0
    GPIO.output(config.track_led_pins[current_track],GPIO.HIGH)
    print("new track: {0}".format(current_track))
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
    global tracks
    global current_track

    notes_off()
    
    track=tracks[current_track]
    
    if track['octave']<8:
        track['octave']+=1
        print ("New octave: {0}".format(track['octave']))
    

# handler for octave down button press
def octave_down_button():
    global tracks
    global current_track

    notes_off()

    track=tracks[current_track]
    
    if track['octave']>0:
        track['octave']-=1
        print ("New octave: {0}".format(track['octave']))



# handler for patch up button press
def patch_up_button():
    global tracks
    global current_track

    notes_off()
    
    track=tracks[current_track]

    if track['patch']<127:
        track['patch'] += 1
        print ("New patch: {0}".format(track['patch']))
        midi.set_instrument(track['patch'],track['midi_channel'])
    return


# handler for patch down button press
def patch_down_button():
    global tracks
    global current_track

    notes_off()
    
    track=tracks[current_track]

    if track['patch']>0:
        track['patch'] -= 1
        print ("New patch: {0}".format(track['patch']))
        midi.set_instrument(track['patch'],track['midi_channel'])
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


# Alternatively, specify a custom I2C address such as 0x5B (ADDR tied to 3.3V),
# 0x5C (ADDR tied to SDA), or 0x5D (ADDR tied to SCL).
#cap.begin(address=0x5B)

# Also you can specify an optional I2C bus with the bus keyword parameter.
#cap.begin(busnum=1)

cap.set_thresholds(config.on_threshold,config.off_threshold)

pygame.mixer.pre_init(44100, -16, 12, 512)
pygame.init()


GPIO.setmode(GPIO.BCM)

for pin in config.button_pins.keys():
    GPIO.setup(config.button_pins[pin],GPIO.IN)


pygame.midi.init()
dev_info=pygame.midi.get_device_info(config.midi_device)
print dev_info

midi=pygame.midi.Output(config.midi_device)


for track in tracks:
    midi.set_instrument(track['patch'],track['midi_channel'])


for i in range(4):
    GPIO.setup(config.track_led_pins[i],GPIO.OUT)
    status=GPIO.LOW
    if i==current_track:
        status=GPIO.HIGH
    GPIO.output(config.track_led_pins[i],status)

def loop():
    global loop_start,event_index,loop_length

    if playing and loop_length>0:
        current_time=get_time()
        loop_offset=current_time-loop_start
        if loop_offset>=loop_length:
            loop_start=current_time
            loop_offset=0
            event_index=0
        while event_index<len(events) and events[event_index]['time']<=loop_offset:
            event=events[event_index]
            debug_print(event)
            debug_print(loop_offset)
            if event['velocity']==0:
                midi.note_off(event['note'],None,event['midi_channel'])
            else:
                midi.note_on(event['note'],event['velocity'],event['midi_channel'])
            event_index+=1

    current_touched = cap.touched()
    # Check each pin's last and current state to see if it was pressed or released.
    for i in range(12):
        # Each pin is represented by a bit in the touched value.  A value of 1
        # means the pin is being touched, and 0 means it is not being touched.
        pin_bit = 1 << i

        key_state = (current_touched & pin_bit)
        
        if key_state != key_states[i]['on']:
            current_time=get_time()
            if (current_time-key_states[i]['last_change'])>config.key_debounce:
                key_states[i]['on']=key_state
                track=tracks[current_track]
                octave=track['octave']
                midi_channel=track['midi_channel']
                debug_print("track {0} octave {1} midi_channel {2}".format(track,octave,midi_channel))
                note=octave*12+config.NOTE_OFFSET[i]
                if key_state:
                    debug_print('{0} touched'.format(i))
                    midi.note_off(note,None,midi_channel)
                    midi.note_on(note,config.note_velocity,midi_channel)
                    if recording:
                        note_event={
                            'time':current_time-loop_start,
                            'note':note,
                            'midi_channel':midi_channel,
                            'velocity':config.note_velocity
                            }
                        events.insert(event_index,note_event)
                        event_index+=1
                        debug_print(note_event)
                else:
                    debug_print('{0} released'.format(i))
                    midi.note_off(note,None,midi_channel)
                    if recording:
                        note_event={
                            'time':current_time-loop_start,
                            'note':note,
                            'midi_channel':midi_channel,
                            'velocity':0
                            }
                        events.insert(event_index,note_event)
                        event_index+=1
                key_states[i]['last_change']=current_time
        
        

    # check buttons
    for button in config.button_pins:
        button_state=GPIO.input(config.button_pins[button])
        if button_state != buttons[button]['on']:
            current_time=get_time()
            if (current_time-buttons[button]['last_change'])>config.button_debounce:
                buttons[button]['on']=button_state
                if button_state:
                    debug_print('{0} pressed'.format(button))
                    buttons[button]['handler']()
                else:
                    debug_print('{0} released'.format(button))
                buttons[button]['last_change']=current_time
            

            
            
    return



print('Press Ctrl-C to quit.')
while True:
    loop()
    time.sleep(0.001)

