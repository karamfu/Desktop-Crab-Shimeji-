import tkinter as tk
import random
from PIL import Image, ImageTk, ImageSequence
from pathlib import Path

# Set up window (Technically, the application is a window but I'm hiding all aspects that would reveal that)
window = tk.Tk()
window.overrideredirect(True)
window.attributes('-topmost', True)
window.attributes('-transparentcolor', 'black')

screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

initial_x = screen_width // 2 - 50
initial_y = screen_height // 2 - 50

# Set up our initial variables
x = initial_x
y = initial_y
target_x = x
target_y = y
cycle = 0
last_animation_frames = None
moving = False
playing_heart = False

# The path to where all the gifs are stored
impath = Path(__file__).parent / 'gifs'

# This will randomize our pet's size , it can either spawn small or large
random_scale_factor = random.uniform(0.7, 1.30)
random_width = int(100 * random_scale_factor)
random_height = int(100 * random_scale_factor)


window.geometry(f'{random_width}x{random_height}+{initial_x}+{initial_y}')

# Load gifs
def load_gif_frames(gif_path):
    gif = Image.open(gif_path)
    frames = []
    for frame in ImageSequence.Iterator(gif):
        frame = frame.convert('RGBA')
        frames.append(ImageTk.PhotoImage(frame.resize((random_width, random_height), Image.Resampling.NEAREST)))
    return frames

idle_gif_frames = load_gif_frames(impath / 'idle0.gif')
idle_to_sleep_gif_frames = load_gif_frames(impath / 'idle_to_sleep.gif')
sleep_gif_frames = load_gif_frames(impath / 'sleep.gif')
sleep_to_idle_gif_frames = load_gif_frames(impath / 'sleep_to_idle.gif')
walk_positive_gif_frames = load_gif_frames(impath / 'walking_positive0.gif')
walk_negative_gif_frames = load_gif_frames(impath / 'walking_negative0.gif')
heart_gif_frames = load_gif_frames(impath / 'heart.gif')

# Define update function for animations
def update_animation(frames, callback=None):
    global cycle

    frame = frames[cycle]
    cycle = (cycle + 1) % len(frames)

    label.config(image=frame)
    label.place(x=0, y=0)

    if cycle == 0 and callback:
        # Show the first frame of the idle animation
        label.config(image=frames[0])
        # Random interval till the next animation cycle
        window.after(random.randint(5000, 10000), callback)
    else:
        window.after(100, lambda: update_animation(frames, callback))

# Define function to start the idle animation
def start_idle_animation():
    global cycle
    cycle = 0
    update_animation(idle_gif_frames, start_idle_animation)

# Function to give the window a new target position (moving around)
def set_new_target_position():
    global target_x, target_y

    # Set the new target position randomly
    target_x += random.randint(-200, 200)
    target_y += random.randint(-200, 200)

    #Making sure the crab stays within the dimensions of the screen
    target_x = max(0, min(window.winfo_screenwidth() - random_width, target_x))
    target_y = max(0, min(window.winfo_screenheight() - random_height, target_y))

    # Randomly decide when the next time it will move
    window.after(random.randint(5000, 10000), set_new_target_position)

# Function to smoothly move the window to the target position
def move_window_smoothly():
    global x, y, target_x, target_y, cycle, last_animation_frames, moving, playing_heart

    # Calculate the difference between the current and target positions
    dx = target_x - x
    dy = target_y - y

    move_right = dx > 0
    move_left = dx < 0
    move_up = dy < 0
    move_down = dy > 0

    # Move a fraction of the distance towards the target position
    step_size = 10
    if abs(dx) > step_size or abs(dy) > step_size:
        if abs(dx) > step_size:
            x += step_size if dx > 0 else -step_size
        else:
            x = target_x

        if abs(dy) > step_size:
            y += step_size if dy > 0 else -step_size
        else:
            y = target_y

        window.geometry(f'{random_width}x{random_height}+{x}+{y}')

        # Cancel heart animation if moving
        if playing_heart:
            playing_heart = False
            cycle = 0
            update_animation(last_animation_frames if last_animation_frames else idle_gif_frames)

        # Play walking animation based on direction (if moving left look left)
        if move_right:
            last_animation_frames = walk_positive_gif_frames
        elif move_left:
            last_animation_frames = walk_negative_gif_frames
        elif move_up or move_down:
            pass

        if last_animation_frames:
            frame = last_animation_frames[cycle % len(last_animation_frames)]
            cycle += 1
        else:
            frame = idle_gif_frames[0]

        label.config(image=frame)
        label.place(x=0, y=0)
        moving = True
        window.after(50, move_window_smoothly)
    else:
        moving = False
        # Stop walking animation when target is reached
        label.config(image=idle_gif_frames[0])
        # Schedule the next movement
        window.after(random.randint(500, 2000), move_window_smoothly)

#Function to start dragging
def start_drag(event):
    window._drag_start_x = event.x
    window._drag_start_y = event.y

# Function to perform dragging
def do_drag(event):
    global x, y
    x = window.winfo_x() + (event.x - window._drag_start_x)
    y = window.winfo_y() + (event.y - window._drag_start_y)
    window.geometry(f'{random_width}x{random_height}+{x}+{y}')

#Function to play the heart animation thing
def play_heart_animation(event=None):
    global cycle, playing_heart
    if not moving and not playing_heart:
        playing_heart = True
        cycle = 0  # Reset the cycle when starting a new animation
        update_animation(heart_gif_frames, end_heart_animation)

# Function to STOP the heart animation and play idle
def end_heart_animation():
    global playing_heart
    playing_heart = False
    start_idle_animation()

# Close the program with a command
def close_program(event):
    window.destroy()

# Create label
label = tk.Label(window, bd=0, bg='black')  # Background matches transparent color (black)
label.place(x=0, y=0)

label.bind('<Button-1>', start_drag)
label.bind('<B1-Motion>', do_drag)

# Bind 'h' key to play the heart animation
window.bind_all('h', play_heart_animation)

# Bind Ctrl + Alt + C to close the program
window.bind_all('<Control-Alt-c>', close_program)



start_idle_animation()

set_new_target_position()
move_window_smoothly()

# Run the  main loop
window.mainloop()
