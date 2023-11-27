A GUI for controlling DrScientist's DUSK through MIDI:

* to run: python dusk.py

* runs on Linux; change 'posix' in script to try on other OS (untested)

* click DUSK (or change the mode) to send current values to pedal
    - clicking buttons will send the new value
    - changing sliders will not send the new value, click DUSK after changing
    - (this limits msgs-per-sec sent)

* uses https://github.com/gbevin/SendMIDI to send messages
    - use "sendmidi list" to get your device name
    - add it to dusk.py (set variable DEVICE)
    - thanks gbevin

* "scrolled frame" is re-organized stack overflow code
    - thanks world
