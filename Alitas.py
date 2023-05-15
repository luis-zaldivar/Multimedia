from tkinter import filedialog
from tkinter import messagebox, simpledialog
import vlc
from tkinter import *
from tkinter import ttk, filedialog
import tkinter
from PIL import ImageTk, Image
import time
import cv2
import tkinter as tk
import os
import moviepy.editor as mp
from moviepy import *
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import ImageClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from imageio.core.util import Image
from PIL import Image, ImageTk


class Tooltip:
    def _init_(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None

    def show_tip(self):
        if self.tip_window or not self.text:
            return
        x, y, _cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 25
        y = y + cy + self.widget.winfo_rooty() + 25
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("arial", "10", "normal"))
        label.pack(ipadx=1)

    def hide_tip(self):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()


def create_tooltip(widget, text):
    tooltip = Tooltip(widget, text)
    widget.bind("<Enter>", lambda event: tooltip.show_tip())
    widget.bind("<Leave>", lambda event: tooltip.hide_tip())

#Fuction toopen the video file


def openfile():
    global load  # Indicate that a file has been uploaded
    file_path = filedialog.askopenfilename(
        filetypes=[("Video Files", "*.mp4 *.avi *.mkv *.mp3")])
    # Creates a media object from the media file
    media = instance.media_new(file_path)
    load = True  # the file has been uploaded
    player.set_media(media)
    subtitles = vlc.Media('PRC- Peso Pluma.srt')
    media.add_option('sub-file={}'.format(subtitles.get_mrl()))
    play()  # Play video
    buttonStop.config(state='normal')  # enable stop button
    buttonPause = ttk.Button(root, image=pauseicon, command=pause)
    buttonPause.grid(row=2, column=2)
    create_tooltip(buttonPause, "Pause video")


def play():
    global cv2image, load  # uploaded file
    if cv2image:  # destroys the image window
        cv2.destroyAllWindows()
        # disables the button to save the frame
        buttonFrame.config(state='disabled')
    if load is True:
        window_handle = canvas.winfo_id()
        # Display the video in a canvas in the main window
        player.set_hwnd(window_handle)
        player.play()  # play video


def pause():
    global playing, cv2image  # check if a video is playing
    if cv2image:  # disables the button to save the frame and destroy the image window
        cv2.destroyAllWindows()
        buttonFrame.config(state='disabled')
    if playing:
        player.pause()  # pause video
        buttonPause = ttk.Button(root, image=playicon, command=pause)
        buttonPause.grid(row=2, column=2)
        create_tooltip(buttonPause, "Play video")
        playing = False  # Change the playback status
    else:
        player.pause()
        buttonPause = ttk.Button(root, image=pauseicon, command=pause)
        buttonPause.grid(row=2, column=2)
        create_tooltip(buttonPause, "Pause video")
        playing = True  # Remove pause


def stop():
    global load, cv2image  # check if a file is uploaded
    if cv2image:  # disables the button to save the frame and destroy the image window
        cv2.destroyAllWindows()
        buttonFrame.config(state='disabled')
    player.stop()  # stops video play
    buttonPause = ttk.Button(root, image=pauseicon, command=openfile)
    buttonPause.grid(row=2, column=2)
    buttonStop.config(state='enabled')  # disables button stop
    load = False  # Change the status to upload a new file

# fuction to update the play bar


def update():
    currentTime = int(player.get_time()/1000)  # read current time
    totalTime = int(player.get_length()/1000)  # read total time
    #currentTimeLabel.config(text=time.strftime('%M:%S', time.gmtime(currentTime)))
    minutes = totalTime//60
    seconds = totalTime % 60
    #durationLabel.config(text='{0:02d}:{1:02d}'.format(minutes, seconds))
    # configure the play bar
    progressBar.config(value=currentTime, maximum=totalTime)
    root.after(1000, update)  # updates the time

# reads the cursor event in the play bar


def progressBarClic(event):
    global cv2image
    x = event.x  # read event
    totalTime = int(player.get_length()/1000)
    position = x/progressBar.winfo_width()
    player.pause()  # pause video play
    timeJump = int(totalTime*position)  # jumps at the right time
    player.set_time(timeJump*1000)  # reproduce at the right time
    image = cv2.VideoCapture(player.get_media().get_mrl())
    image.set(cv2.CAP_PROP_POS_MSEC, timeJump * 1000)
    ret, frame = image.read()  # read frame
    cv2.imshow('Frame', cv2.resize(frame, (700, 500)))
    cv2image = True
    image.release()  # frees up memory
    buttonFrame.config(state='normal')  # enable stop button

# extracts the image frame


def extractFrame():
    global cv2image
    frame_time = player.get_time()/1000  # gets the time
    image = cv2.VideoCapture(player.get_media().get_mrl())
    image.set(cv2.CAP_PROP_POS_MSEC, frame_time * 1000)
    ret, frame = image.read()  # read frame
    if not ret:
        return
    image.release()  # frees up memory
    filePath = filedialog.asksaveasfilename(filetypes=[("PNG File", "*.png"), ("JPG File", "*.jpg")],
                                            defaultextension=".jpg")
    if filePath:
        cv2.imwrite(filePath, frame)  # save the frame


def updateSubtitlesBox():
    position = player.get_time()


# Create instance
instance = vlc.Instance()
# Add video player
player = instance.media_player_new()
# create window root
root = Tk()
canvas = Canvas(root, bg='black', width=800, height=500)
canvas.grid(row=0, column=0, columnspan=8)

load = False
playing = True
cv2image = False


s = ttk.Style()
s.theme_use('clam')
s.configure("blue.Horizontal.TProgressbar",
            foreground='blue', background='blue')
progressBar = ttk.Progressbar(root, style='blue.Horizontal.TProgressbar',
                              orient='horizontal', length=600, mode='determinate')
progressBar.grid(row=1, column=1)
progressBar.bind('<Button-1>', progressBarClic)


# config button open file
openicon = ImageTk.PhotoImage(Image.open(r'load.jpg').resize((25, 25)))
buttonFile = ttk.Button(root, image=openicon, command=openfile)
create_tooltip(buttonFile, "Upload a video")
buttonFile.grid(row=2, column=1)
# config button play
playicon = ImageTk.PhotoImage(Image.open(r'play.png').resize((25, 25)))
pauseicon = ImageTk.PhotoImage(Image.open(r'pause.png').resize((25, 25)))
buttonPause = ttk.Button(root, image=playicon, command=openfile)
buttonPause.grid(row=2, column=2)
create_tooltip(buttonPause, "Play video")
# config button stop
stopicon = ImageTk.PhotoImage(Image.open(r'stop.png').resize((25, 25)))
buttonStop = ttk.Button(root, image=stopicon, command=stop)
buttonStop.grid(row=2, column=3)
buttonStop.config(state='disabled')
create_tooltip(buttonStop, "Stop video")

# config button frame
frameicon = ImageTk.PhotoImage(Image.open(r'save.png').resize((25, 25)))
buttonFrame = ttk.Button(root, image=frameicon, command=extractFrame)
buttonFrame.grid(row=2, column=4)
buttonFrame.config(state='enabled')
create_tooltip(buttonFrame, "Save Image")


def select_frame():
    global cv2image
    file_path = filedialog.askopenfilename(
        filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp")])
    if file_path:
        cv2image = cv2.imread(file_path)
        cv2image = cv2.cvtColor(cv2image, cv2.COLOR_BGR2RGB)
        cv2image = cv2.resize(
            cv2image, (canvas.winfo_width(), canvas.winfo_height()))
        cv2image = cv2.rectangle(
            cv2image, (0, 0), (canvas.winfo_width(), canvas.winfo_height()), (255, 0, 0), 10)
        cv2.line(cv2image, (0, 0), (canvas.winfo_width(),
                 canvas.winfo_height()), (255, 0, 0), 10)
        cv2.line(cv2image, (canvas.winfo_width(), 0),
                 (0, canvas.winfo_height()), (255, 0, 0), 10)
        photo = ImageTk.PhotoImage(image=Image.fromarray(cv2image))
        canvas.create_image(0, 0, image=photo, anchor=NW)
        canvas.image = photo
        buttonFrame.config(state='enabled')
        buttonSave.config(state='normal')


def save_frame():
    if cv2image is not None:
        filename = filedialog.asksaveasfilename(
            defaultextension='.png', filetypes=[("PNG files", "*.png")])
        if filename:
            for i in range(30):
                filename_with_number = f"{filename[:-4]}_{i+1}.png"
                cv2.imwrite(filename_with_number, cv2image)


def select_frames():
    root.filename1 = filedialog.askopenfilename(
        initialdir="/", title="Select original frame", filetypes=(("jpeg files", "*.jpg"), ("all files", "*.*")))
    root.filename2 = filedialog.askopenfilename(
        initialdir="/", title="Select edited frame", filetypes=(("jpeg files", "*.jpg"), ("all files", "*.*")))


buttonSelectFrames = ttk.Button(
    root, text="Select Frames", command=select_frames)
buttonSelectFrames.grid(row=3, column=7)


def insert_frame():
    # Seleccionar el video original
    root = Tk()
    root.withdraw()
    original_video_path = filedialog.askopenfilename(title="Seleccionar video original",
                                                     filetypes=(("Archivos de video", "*.mp4 *.avi *.mov"), ("Todos los archivos", "*.*")))
    if not original_video_path:
        messagebox.showerror("Error", "Debe seleccionar un video original.")
        return
    video = VideoFileClip(original_video_path)

    # Extraer el audio y los frames
    audio = video.audio
    frames = []
    for i, frame in enumerate(video.iter_frames()):
        frames.append(frame)

    # Seleccionar el frame editado
    edited_frame_path = filedialog.askopenfilename(title="Seleccionar frame editado",
                                                   filetypes=(("Archivos de imagen", "*.jpg *.png *.bmp"), ("Todos los archivos", "*.*")))
    if not edited_frame_path:
        messagebox.showerror("Error", "Debe seleccionar un frame editado.")
        return
    edited_frame = ImageClip(edited_frame_path)

    # Seleccionar el marco donde se insertará el frame editado
    total_frames = len(frames)
    frame_to_replace = simpledialog.askinteger("Seleccionar marco",
                                               f"El video tiene un total de {total_frames} marcos. ¿En qué marco desea insertar el frame editado?",
                                               minvalue=1,
                                               maxvalue=total_frames)
    if not frame_to_replace or frame_to_replace < 1 or frame_to_replace > total_frames:
        messagebox.showerror("Error", "Debe seleccionar un marco válido.")
        return
    index_to_replace = frame_to_replace - 1

    # Insertar el frame editado en el marco seleccionado
    for i in range(30):
        frames[index_to_replace +
               i] = edited_frame.to_RGB().resize((video.w, video.h)).img

    # Generar el nuevo video
    new_video_path = os.path.splitext(original_video_path)[0] + "_edited2.mp4"
    new_video = ImageSequenceClip(frames, fps=video.fps)
    new_video = new_video.set_audio(audio)
    new_video.write_videofile(new_video_path, codec="libx264")
    messagebox.showinfo(
        "Éxito", f"El video editado se ha guardado en {new_video_path}.")


buttonSelectFrame = ttk.Button(root, text="Select Frame", command=select_frame)
buttonSelectFrame.grid(row=2, column=5)
buttonSave = ttk.Button(root, text="Guardar Frame",
                        command=save_frame, state='disabled')
buttonSave.grid(row=2, column=6)
buttonInsert = ttk.Button(root, text="Generar video",
                          command=insert_frame, state='enabled')
buttonInsert.grid(row=2, column=7)

# add the player to the root window
player.set_hwnd(root.winfo_id())
canvas2 = Canvas(root, bg='white', width=350, height=500)
canvas2.grid(row=0, column=8, columnspan=4)


# Window root
root.config(bg='white')  # Root colour
root.title('Video Player')  # Root name
root.iconbitmap(r'load2.png')  # Root icon
root.geometry('1000x600')  # Root size

root.resizable(False, False)  # Prevents it from redeeming itself
update()  # update the time
root.mainloop()
