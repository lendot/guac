# guac
Guacenspiel

This Raspberry Pi python program reads touches from a capacitive touch sensor module and converts them into MIDI signals. It also acts as a 4-track looping MIDI sequencer.

To configure for your setup, copy `config.py.example` to `config.py` and edit as necessary.

NOTE: This program will not make music on its own; something will have to listen for the generated MIDI signals and produce the corresponding sounds. In my case I'm using [FluidSynth](http://www.fluidsynth.org/) on the same Pi and doing everything through ALSA.

Here are the commands I used on a fresh raspbian installation to get everything setup:

```
pi@guacenspiel:~ $ sudo apt-get install build-essential python-dev python-smbus python-pip git python-pygame
pi@guacenspiel:~ $ git clone https://github.com/adafruit/Adafruit_Python_MPR121.git
pi@guacenspiel:~ $ cd Adafruit_Python_MPR121/
pi@guacenspiel:~/Adafruit_Python_MPR121 $ sudo python setup.py install
pi@guacenspiel:~/Adafruit_Python_MPR121 $ cd
pi@guacenspiel:~ $ git clone https://github.com/lendot/guac.git
pi@guacenspiel:~ $ cd guac/
pi@guacenspiel:~/guac $ cp config.py.example config.py
```
To start fluidsynth:
```
pi@guacenspiel:~ $ sudo apt-get install fluidsynth alsa-utils
pi@guacenspiel:~ $ fluidsynth -s -a alsa -m alsa_seq /usr/share/sounds/sf2/FluidR3_GM.sf2
```

In another window I use `aconnect` to connect the output device guac uses to the input device for FluidSynth:
```
pi@guacenspiel:~ $ cd guac/
pi@guacenspiel:~/guac $ aconnect -l
client 0: 'System' [type=kernel]
    0 'Timer           '
    1 'Announce        '
client 14: 'Midi Through' [type=kernel]
    0 'Midi Through Port-0'
client 128: 'FLUID Synth (751)' [type=user]
    0 'Synth input port (751:0)'
pi@guacenspiel:~/guac $ aconnect 14:0 128:0
pi@guacenspiel:~/guac $ aconnect -l
client 0: 'System' [type=kernel]
    0 'Timer           '
    1 'Announce        '
client 14: 'Midi Through' [type=kernel]
    0 'Midi Through Port-0'
        Connecting To: 128:0
client 128: 'FLUID Synth (751)' [type=user]
    0 'Synth input port (751:0)'
        Connected From: 14:0
```
In `config.py` set `midi_device=0` and run `sudo python guac.py`
