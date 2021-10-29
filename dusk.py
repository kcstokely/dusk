import json, os, subprocess
import tkinter as tk

from scroll import ScrolledFrame
from config import * 

config = dusk_config

CTL_BTN_WIDTH = 3 if os.name == 'posix' else 5

############

device = 'USB MIDI Interface MIDI'

def send_command(cc, value):
    if send_allowed:
        subprocess.run(['sendmidi', 'dev', device, 'ch', '1', 'cc', str(cc), str(value)])

def send_var(var_name):
    value = variables[var_name].get()
    print(f'{var_name:<10} --> {value}')
    cc = config[var_name]
    send_command(cc, value)

############
        
send_allowed = False

root = tk.Tk()
root.title("...crépuscule obscur...")

def onkey(event):
    try:
        value = list('`12345').index(event.char)
    except ValueError:
        pass
    else:
        value = 2**int(value)
        print(f'SET DELTA: {value}')
        delta.set(value)
        
delta = tk.IntVar(name='delta')
delta.set(1)
root.bind('<Key>', onkey)

mode_btns = []
variables = { var: tk.IntVar(name=var) for var in config }

scrolled_frame = ScrolledFrame(root)
scrolled_frame.pack(expand=True, fill='both')

### MAIN

def on_dusk():
    for var in config:
        if not 'rate' in var:
            send_var(var)
    on_bpm_send(None)

dusk = tk.Button(scrolled_frame.interior, borderwidth=2, relief=tk.SOLID, text='DUSK', font='Helvetica 19 bold italic', command=on_dusk)
dusk.pack(pady=12)

fira = tk.Frame(scrolled_frame.interior)
fira.pack(pady=12)

filt = tk.Frame(fira, borderwidth=2, relief=tk.SOLID)
filt.grid(row=0, column=0, padx=12)

ramp = tk.Frame(fira, borderwidth=2, relief=tk.SOLID)
ramp.grid(row=0, column=1, padx=12)

mode = tk.Frame(scrolled_frame.interior)
mode.pack(padx=6, pady=12)

btn = tk.Button(mode, text='CUT', command=lambda: on_mode_select(1))
mode_btns.append(btn)
btn.grid(row=0, column=0, padx=6, pady=12)

btn = tk.Button(mode, text='ENV', command=lambda: on_mode_select(2))
mode_btns.append(btn)
btn.grid(row=0, column=1, padx=6, pady=12)

btn = tk.Button(mode, text='LFO', command=lambda: on_mode_select(3))
mode_btns.append(btn)
btn.grid(row=0, column=2, padx=6, pady=12)

env = tk.Frame(mode, borderwidth=2, relief=tk.SOLID)
env.grid(row=1, column=1, sticky='n', padx=6)

lfo = tk.Frame(mode, borderwidth=2, relief=tk.SOLID)
lfo.grid(row=1, column=2, sticky='n', padx=6)

### FILTER / RAMP

def up(name, _del=None, _max=127):
    d = _del if _del else delta.get()
    variables[name].set(min(127, variables[name].get() + d))
    send_var(name)

def down(name, _del=None):
    d = _del if _del else delta.get()
    variables[name].set(max(0, variables[name].get() - d))
    send_var(name)            

tk.Label(filt, text='Filter', font='Helvetica 12 bold').grid(row=0, columnspan=2)
tk.Label(filt, textvariable=variables['filter']).grid(row=1, columnspan=2)
tk.Scale(filt, from_=0, to=127, resolution=1, showvalue=0, variable=variables['filter'], command=lambda x: send_var('filter'), orient='horizontal').grid(row=2, columnspan=2)
tk.Button(filt, width=CTL_BTN_WIDTH, text='\u2193', command=lambda: down('filter')).grid(row=3, column=0)
tk.Button(filt, width=CTL_BTN_WIDTH, text='\u2191', command=lambda: up('filter')).grid(row=3, column=1)

tk.Label(ramp, text='Ramp Speed', font='Helvetica 12 bold').grid(row=0, columnspan=2)
tk.Label(ramp, textvariable=variables['ramp_speed']).grid(row=1, columnspan=2)
tk.Scale(ramp, from_=0, to=20, resolution=1, showvalue=0, variable=variables['ramp_speed'], command=lambda x: send_var('ramp_speed'), orient='horizontal').grid(row=2, columnspan=2)
tk.Button(ramp, width=CTL_BTN_WIDTH, text='\u2193', command=lambda: down('ramp_speed', 1)).grid(row=3, column=0)
tk.Button(ramp, width=CTL_BTN_WIDTH, text='\u2191', command=lambda: up('ramp_speed', 1, 20)).grid(row=3, column=1)

### MODES...

def on_mode_select(value):
    variables['mode'].set(value)
    for bdx, btn in enumerate(mode_btns):
        if bdx == (value-1):
            btn.config(relief='sunken')
        else:
            btn.config(relief='raised')
    send_var('mode')

### ENV

btn = tk.Radiobutton(env, text='Down', variable=variables['envelope'], value=0, command=lambda: send_var('envelope'))
btn.grid(row=1, column=0)

btn = tk.Radiobutton(env, text='Up', variable=variables['envelope'], value=64, command=lambda: send_var('envelope'))
btn.grid(row=1, column=1)

### LFO

wav = tk.Frame(lfo)
wav.pack()

bpm = tk.Frame(lfo)
bpm.pack()

sub = tk.Frame(lfo)
sub.pack()

### wav

lbl = tk.Label(wav, text='Waveform', font='Helvetica 12 bold')
lbl.grid(row=0, column=0, columnspan=3)

btn = tk.Radiobutton(wav, text='Sine', variable=variables['waveform'], value=1, command=lambda: send_var('waveform'))
btn.grid(row=1, column=0)

btn = tk.Radiobutton(wav, text='Ramp', variable=variables['waveform'], value=2, command=lambda: send_var('waveform'))
btn.grid(row=1, column=1)

btn = tk.Radiobutton(wav, text='Saw', variable=variables['waveform'], value=3, command=lambda: send_var('waveform'))
btn.grid(row=1, column=2)

btn = tk.Radiobutton(wav, text='Square', variable=variables['waveform'], value=4, command=lambda: send_var('waveform'))
btn.grid(row=2, column=0)

btn = tk.Radiobutton(wav, text='S + H', variable=variables['waveform'], value=5, command=lambda: send_var('waveform'))
btn.grid(row=2, column=1)

btn = tk.Radiobutton(wav, text='Random', variable=variables['waveform'], value=6, command=lambda: send_var('waveform'))
btn.grid(row=2, column=2)

### bpm

var_bpm = tk.IntVar()

def on_bpm_up():
    var_bpm.set(min(381, var_bpm.get() + 1))
    on_bpm_send(None)

def on_bpm_down():
    var_bpm.set(max(0, var_bpm.get() - 1))
    on_bpm_send(None)

def on_bpm_send(x):
    now = var_bpm.get()
    if now <= 127:
        variables['rate_1'].set(now)
        send_var('rate_1')
    elif now <= 127*2:
        now = now//2
        variables['rate_2'].set(now)
        send_var('rate_2')
    elif now <= 127*3:
        now = now//3
        variables['rate_3'].set(now)
        send_var('rate_3')

tk.Label(bpm, text='Beats per Minute', font='Helvetica 12 bold').grid(row=0, columnspan=2)
tk.Label(bpm, textvariable=var_bpm).grid(row=1, columnspan=2)
tk.Scale(bpm, from_=0, to=380, resolution=1, showvalue=0, variable=var_bpm, command=on_bpm_send, orient='horizontal').grid(row=2, columnspan=2)
tk.Button(bpm, width=CTL_BTN_WIDTH, text='\u2193', command=on_bpm_down).grid(row=3, column=0)
tk.Button(bpm, width=CTL_BTN_WIDTH, text='\u2191', command=on_bpm_up).grid(row=3, column=1)

### sub

lbl = tk.Label(sub, text='Subdivision', font='Helvetica 12 bold')
lbl.grid(row=0, column=0, columnspan=4)

btn = tk.Radiobutton(sub, text=wn, variable=variables['subdiv'], value=1, command=lambda: send_var('subdiv'))
btn.grid(row=1, column=0)

btn = tk.Radiobutton(sub, text=hn+dot, variable=variables['subdiv'], value=2, command=lambda: send_var('subdiv'))
btn.grid(row=1, column=1)

btn = tk.Radiobutton(sub, text=hn, variable=variables['subdiv'], value=3, command=lambda: send_var('subdiv'))
btn.grid(row=1, column=2)

btn = tk.Radiobutton(sub, text=qn+dot, variable=variables['subdiv'], value=4, command=lambda: send_var('subdiv'))
btn.grid(row=1, column=3)

btn = tk.Radiobutton(sub, text=qn+trp, variable=variables['subdiv'], value=5, command=lambda: send_var('subdiv'))
btn.grid(row=2, column=0)

btn = tk.Radiobutton(sub, text=qn, variable=variables['subdiv'], value=6, command=lambda: send_var('subdiv'))
btn.grid(row=2, column=1)

btn = tk.Radiobutton(sub, text=en+dot, variable=variables['subdiv'], value=7, command=lambda: send_var('subdiv'))
btn.grid(row=2, column=2)

btn = tk.Radiobutton(sub, text=en+trp, variable=variables['subdiv'], value=8, command=lambda: send_var('subdiv'))
btn.grid(row=2, column=3)

btn = tk.Radiobutton(sub, text=en, variable=variables['subdiv'], value=9, command=lambda: send_var('subdiv'))
btn.grid(row=3, column=0)

btn = tk.Radiobutton(sub, text=sn+dot, variable=variables['subdiv'], value=10, command=lambda: send_var('subdiv'))
btn.grid(row=3, column=1)

btn = tk.Radiobutton(sub, text=sn+trp, variable=variables['subdiv'], value=11, command=lambda: send_var('subdiv'))
btn.grid(row=3, column=2)

btn = tk.Radiobutton(sub, text=sn, variable=variables['subdiv'], value=12, command=lambda: send_var('subdiv'))
btn.grid(row=3, column=3)

###

variables['filter'].set('64')
variables['ramp_speed'].set(10)
on_mode_select(1)
variables['waveform'].set(1)
var_bpm.set(96)
on_bpm_send(None)
variables['subdiv'].set(6)

delta.set(8)

###

############

if __name__ == '__main__':
    
    if os.name == 'posix':
        send_allowed = True
        
    root.mainloop()
    



