import json, os, subprocess, time
import tkinter as tk

from scroll import ScrolledFrame
from config import * 

DEVICE  = 'USB MIDI Interface MIDI'
CHANNEL = 1

CTL_BTN_WIDTH = 3 if os.name == 'posix' else 5

#########

send_allowed = False

def send_program(value):
    if send_allowed:
        subprocess.run(['sendmidi', 'dev', DEVICE, 'ch', str(CHANNEL), 'pc', str(value)])
        time.sleep(0.1)

def send_command(cc, value):
    if send_allowed:
        subprocess.run(['sendmidi', 'dev', DEVICE, 'ch', str(CHANNEL), 'cc', str(cc), str(value)])
        time.sleep(0.1)

def send_var(var_name):
    if check_var(var_name):
        cc = DUSK[var_name]
        value = variables[var_name].get()
        if send_allowed:
            print(f'{var_name:<8} --> {value}')
        send_command(cc, value)

def check_var(var_name):
    if var_name in ['mode', 'filter']:
        return True
    mode = variables['mode'].get()
    if mode == 1:
        if var_name == 'ramptime':
            return True
    if mode == 2:
        if var_name == 'envelope':
            return True
    if mode == 3:
        if var_name in ['waveform', 'division', 'rate_x_1', 'rate_x_2', 'rate_x_3']:
            return True
    
#########

def on_key(event):
    try:
        value = list('`12345').index(event.char)
    except ValueError:
        pass
    else:
        value = 2**int(value)
        print(f'SET DELTA  {value}')
        delta.set(value)
        
#########

def on_dusk():
    for var_name in variables:
        if not 'rate' in var_name:
            send_var(var_name)
    on_bpm_send(None)

def on_mode_select(value):
    variables['mode'].set(value)
    for bdx, btn in enumerate(btns):
        if bdx == (value-1):
            btn.config(relief='sunken')
        else:
            btn.config(relief='raised')
    on_dusk()

def on_bpm_send(x):
    now = var_bpm.get()
    if now <= 127:
        variables['rate_x_1'].set(now)
        send_var('rate_x_1')
    elif now <= 127*2:
        now = now//2
        variables['rate_x_2'].set(now)
        send_var('rate_x_2')
    elif now <= 127*3:
        now = now//3
        variables['rate_x_3'].set(now)
        send_var('rate_x_3')

######### TOP LEVEL

root = tk.Tk()
root.title("... dans le crépuscule obscur ...")
root.bind('<Key>', on_key)

delta     = tk.IntVar(name='delta')
var_pre   = tk.IntVar(name='var_pre')
var_bpm   = tk.IntVar(name='var_bpm')
variables = { var: tk.IntVar(name=var) for var in DUSK }

scrolled_frame = ScrolledFrame(root)
scrolled_frame.pack(expand=True, fill='both')

######### MAIN GRID

### ROW 0

dusk = tk.Button(scrolled_frame.interior, borderwidth=0, relief=tk.SOLID, text='DUSK', font='Helvetica 19 bold italic', command=on_dusk)
dusk.grid(row=0, column=0, columnspan=3, padx=6, pady=12)

### ROW 1

filt = tk.Frame(scrolled_frame.interior, borderwidth=2, relief=tk.SOLID)
filt.grid(row=1, column=0, padx=6, pady=(12,18))

pres = tk.Frame(scrolled_frame.interior, borderwidth=1, relief=tk.SOLID)
pres.grid(row=1, column=2, padx=6, pady=(12,18))

#### ROW 2

btns = []

btn = tk.Button(scrolled_frame.interior, text='CUT', command=lambda: on_mode_select(1))
btns.append(btn)
btn.grid(row=2, column=0, padx=6, pady=12)

btn = tk.Button(scrolled_frame.interior, text='ENV', command=lambda: on_mode_select(2))
btns.append(btn)
btn.grid(row=2, column=1, padx=6, pady=12)

btn = tk.Button(scrolled_frame.interior, text='LFO', command=lambda: on_mode_select(3))
btns.append(btn)
btn.grid(row=2, column=2, padx=6, pady=12)

#### ROW 3

cut = tk.Frame(scrolled_frame.interior, borderwidth=2, relief=tk.SOLID)
cut.grid(row=3, column=0, sticky='n', padx=6)

env = tk.Frame(scrolled_frame.interior, borderwidth=2, relief=tk.SOLID)
env.grid(row=3, column=1, sticky='n', padx=6)

lfo = tk.Frame(scrolled_frame.interior, borderwidth=2, relief=tk.SOLID)
lfo.grid(row=3, column=2, sticky='n', padx=6)

### FILTER

def up(name, inc=None, _max=127):
    d = inc if inc else delta.get()
    variables[name].set(min(_max, variables[name].get() + d))
    send_var(name)

def down(name, inc=None, _min=0):
    d = inc if inc else delta.get()
    variables[name].set(max(_min, variables[name].get() - d))
    send_var(name)            

tk.Label(filt, text='Filter', font='Helvetica 12 bold').grid(row=0, columnspan=2)
tk.Label(filt, textvariable='filter').grid(row=1, columnspan=2)
tk.Scale(filt, from_=0, to=127, resolution=1, showvalue=0, variable='filter', orient='horizontal').grid(row=2, columnspan=2)
tk.Button(filt, width=CTL_BTN_WIDTH, text='\u2193', command=lambda: down('filter')).grid(row=3, column=0)
tk.Button(filt, width=CTL_BTN_WIDTH, text='\u2191', command=lambda: up('filter')).grid(row=3, column=1)

### PRESETS

save = tk.Frame(pres)
save.grid(row=0, column=0, padx=6)

psel = tk.Frame(pres)
psel.grid(row=0, column=1, padx=6)

def on_pre_up():
    var_pre.set(min(99, var_pre.get() + 1))
    
def on_pre_down():
    var_pre.set(max(1, var_pre.get() - 1))

tk.Label(psel, text='Preset', font='Helvetica 12 bold').grid(row=0, columnspan=2)
tk.Label(psel, textvariable=var_pre).grid(row=1, columnspan=2)
tk.Scale(psel, from_=1, to=99, resolution=1, showvalue=0, variable=var_pre, orient='horizontal').grid(row=2, columnspan=2)
tk.Button(psel, width=CTL_BTN_WIDTH, text='\u2193', command=on_pre_down).grid(row=3, column=0)
tk.Button(psel, width=CTL_BTN_WIDTH, text='\u2191', command=on_pre_up).grid(row=3, column=1)    

def on_save():
    preset = var_pre.get()
    send_command(55, preset)

def on_load():
    preset = var_pre.get()
    send_program(preset)

tk.Button(save, width=CTL_BTN_WIDTH, text='Load', command=on_load).grid(row=0, column=0, padx=6, pady=12) 
tk.Button(save, width=CTL_BTN_WIDTH, text='Save', command=on_save).grid(row=1, column=0, padx=6, pady=12)

### CUT

tk.Label(cut, text='Sweep Time', font='Helvetica 12 bold').grid(row=0, columnspan=2)
tk.Label(cut, textvariable='ramptime').grid(row=1, columnspan=2)
tk.Scale(cut, from_=0, to=20, resolution=1, showvalue=0, variable='ramptime', orient='horizontal').grid(row=2, columnspan=2)
tk.Button(cut, width=CTL_BTN_WIDTH, text='\u2193', command=lambda: down('ramptime', 1, 0)).grid(row=3, column=0)
tk.Button(cut, width=CTL_BTN_WIDTH, text='\u2191', command=lambda: up('ramptime', 1, 20)).grid(row=3, column=1)

### ENV

tk.Label(env, text='Direction', font='Helvetica 12 bold').grid(row=0, columnspan=2)

tk.Radiobutton(env, text='Up', variable='envelope', value=64, command=lambda: send_var('envelope')).grid(row=1, column=0)
tk.Radiobutton(env, text='Down', variable='envelope', value=0, command=lambda: send_var('envelope')).grid(row=1, column=1)

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

btn = tk.Radiobutton(wav, text='Sine', variable='waveform', value=1, command=lambda: send_var('waveform'))
btn.grid(row=1, column=0)

btn = tk.Radiobutton(wav, text='Ramp', variable='waveform', value=2, command=lambda: send_var('waveform'))
btn.grid(row=1, column=1)

btn = tk.Radiobutton(wav, text='Saw', variable='waveform', value=3, command=lambda: send_var('waveform'))
btn.grid(row=1, column=2)

btn = tk.Radiobutton(wav, text='Square', variable='waveform', value=4, command=lambda: send_var('waveform'))
btn.grid(row=2, column=0)

btn = tk.Radiobutton(wav, text='S + H', variable='waveform', value=5, command=lambda: send_var('waveform'))
btn.grid(row=2, column=1)

btn = tk.Radiobutton(wav, text='Random', variable='waveform', value=6, command=lambda: send_var('waveform'))
btn.grid(row=2, column=2)

### bpm

def on_bpm_up():
    var_bpm.set(min(381, var_bpm.get() + 1))
    on_bpm_send(None)

def on_bpm_down():
    var_bpm.set(max(0, var_bpm.get() - 1))
    on_bpm_send(None)

tk.Label(bpm, text='Beats per Minute', font='Helvetica 12 bold').grid(row=0, columnspan=2)
tk.Label(bpm, textvariable=var_bpm).grid(row=1, columnspan=2)
tk.Scale(bpm, from_=0, to=380, resolution=1, showvalue=0, variable=var_bpm, orient='horizontal').grid(row=2, columnspan=2)
tk.Button(bpm, width=CTL_BTN_WIDTH, text='\u2193', command=on_bpm_down).grid(row=3, column=0)
tk.Button(bpm, width=CTL_BTN_WIDTH, text='\u2191', command=on_bpm_up).grid(row=3, column=1)

### sub

lbl = tk.Label(sub, text='Subdivision', font='Helvetica 12 bold')
lbl.grid(row=0, column=0, columnspan=4)

btn = tk.Radiobutton(sub, text=wn, variable='division', value=1, command=lambda: send_var('division'))
btn.grid(row=1, column=0)

btn = tk.Radiobutton(sub, text=hn+dot, variable='division', value=2, command=lambda: send_var('division'))
btn.grid(row=1, column=1)

btn = tk.Radiobutton(sub, text=hn, variable='division', value=3, command=lambda: send_var('division'))
btn.grid(row=1, column=2)

btn = tk.Radiobutton(sub, text=qn+dot, variable='division', value=4, command=lambda: send_var('division'))
btn.grid(row=1, column=3)

btn = tk.Radiobutton(sub, text=qn+trp, variable='division', value=5, command=lambda: send_var('division'))
btn.grid(row=2, column=0)

btn = tk.Radiobutton(sub, text=qn, variable='division', value=6, command=lambda: send_var('division'))
btn.grid(row=2, column=1)

btn = tk.Radiobutton(sub, text=en+dot, variable='division', value=7, command=lambda: send_var('division'))
btn.grid(row=2, column=2)

btn = tk.Radiobutton(sub, text=en+trp, variable='division', value=8, command=lambda: send_var('division'))
btn.grid(row=2, column=3)

btn = tk.Radiobutton(sub, text=en, variable='division', value=9, command=lambda: send_var('division'))
btn.grid(row=3, column=0)

btn = tk.Radiobutton(sub, text=sn+dot, variable='division', value=10, command=lambda: send_var('division'))
btn.grid(row=3, column=1)

btn = tk.Radiobutton(sub, text=sn+trp, variable='division', value=11, command=lambda: send_var('division'))
btn.grid(row=3, column=2)

btn = tk.Radiobutton(sub, text=sn, variable='division', value=12, command=lambda: send_var('division'))
btn.grid(row=3, column=3)

######### INITIALIZE

delta.set(4)

variables['filter'].set('64')
variables['ramptime'].set(10)
variables['envelope'].set(0)
variables['waveform'].set(1)
variables['division'].set(6)
var_bpm.set(96)
var_pre.set(5)

on_mode_select(1)

##################

if __name__ == '__main__':
    
    if os.name == 'posix':
        send_allowed = True
        
    root.mainloop()
    



