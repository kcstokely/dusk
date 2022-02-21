A GUI for controlling DrScientist's DUSK through MIDI:

    * run: python dusk.py

    * click DUSK or change mode to send current state
        - buttons send current value
        - sliders do not send value, use button instead
        -   (this limits msgs-per-sec sent)

    * uses https://github.com/gbevin/SendMIDI to send messages
        - use "sendmidi list" to get your device name
        - thanks gbevin

    * "scrolled frame" is re-organized stack overflow code
        - thanks world
