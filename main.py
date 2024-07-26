import time
import rtmidi
from mido import MidiFile
import tkinter as tk

CANVAS_HEIGHT = 500
CANVAS_WIDTH = 800
MARGIN_X = 60
MARGIN_Y = 40

window = tk.Tk()
window_max_x = window.wm_maxsize()[0]
window_max_y = window.wm_maxsize()[1]

FRET_LENGTH = window_max_x - window_max_x // 10     # x axis
FRET_WIDTH = FRET_LENGTH // 12
FRET_DISTANCE = FRET_LENGTH / 24
ONE_DOT_FRETS = [3, 5, 7, 9, 15, 17, 19, 21]
TWO_DOT_FRETS = [12, 24]
FRETS_COORDS = {}
DOT_SIZE = FRET_DISTANCE / 7

canvas = tk.Canvas(window, width=window_max_x, height=window_max_y)
canvas.create_rectangle(MARGIN_X, MARGIN_Y, MARGIN_X+FRET_LENGTH, MARGIN_Y+FRET_WIDTH,  outline="#C0994B", fill="#C0994B")
for i in range(0, 25):
    FRETS_COORDS[i] = {
        'x0': MARGIN_X + FRET_DISTANCE * i,
        'y0': MARGIN_Y,
        'x1': MARGIN_X + FRET_DISTANCE * i,
        'y1': MARGIN_Y + FRET_WIDTH
    }
    canvas.create_line(*FRETS_COORDS[i].values())

for fret in range(1, 25):
    middle_point = (
        (FRETS_COORDS[fret]['x0'] + FRETS_COORDS[fret-1]['x0']) / 2,
        (FRETS_COORDS[fret]['y0'] + FRETS_COORDS[fret]['y1']) /2
    )    
    if fret in ONE_DOT_FRETS:
        canvas.create_oval(
                middle_point[0] - DOT_SIZE,
                middle_point[1] + DOT_SIZE,
                middle_point[0] + DOT_SIZE,
                middle_point[1] - DOT_SIZE,
                outline="#FFF0C9", fill="#FFF0C9"
        )
    elif fret in TWO_DOT_FRETS:
        canvas.create_oval(
                middle_point[0] - DOT_SIZE,
                FRETS_COORDS[fret]['y0'] + DOT_SIZE,
                middle_point[0] + DOT_SIZE,
                FRETS_COORDS[fret]['y0'] + DOT_SIZE*2 + DOT_SIZE,
                outline="#FFF0C9", fill="#FFF0C9"
        )           
        canvas.create_oval(
                middle_point[0] - DOT_SIZE,
                FRETS_COORDS[fret]['y1'] - DOT_SIZE*2 - DOT_SIZE,
                middle_point[0] + DOT_SIZE,
                FRETS_COORDS[fret]['y1'] - DOT_SIZE,
                outline="#FFF0C9", fill="#FFF0C9"
        )
     


canvas.pack()

# ultimate way to do it - through the MIDI port, live stream
midi_in = rtmidi.MidiIn()

# in the meantime when I don't have access to real MIDI control device, I will work with a midi file
midi_file = MidiFile('mojeserce.mid', clip=True)
track = midi_file.tracks[0]

window.mainloop()
for msg in track:
    # print(msg)
    if msg.type == 'note_on' and msg.velocity > 0:
        print(msg.note, end=' ')
    time.sleep(msg.time / 1000)
d=1