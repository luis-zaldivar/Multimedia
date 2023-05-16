import vlc
from tkinter import *
import tkinter as tk
from tkinter import filedialog, ttk, messagebox, simpledialog
import time
import cv2
from PIL import Image, ImageTk
import tkinter.ttk as ttk
from tktooltip import ToolTip
import subprocess
import whisper
import pandas as pd
import os
from whisper.utils import WriteSRT
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import ImageClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from imageio.core.util import Image
import PIL

# crear la instancia de VLC
instance = vlc.Instance('--no-xlib')
player = instance.media_player_new()
player.set_fullscreen(True)
# Función para extraer un frame del video


def extract_frame():
    # Pausa el reproductor de video
    player.pause()
    # Obtiene el tiempo actual del video
    frame_time = int((player.get_time() / 1000.0) + 0.01)
    # Carga el video en OpenCV
    cap = cv2.VideoCapture(player.get_media().get_mrl())
    # Va al fotograma especificado por el tiempo actual del video
    cap.set(cv2.CAP_PROP_POS_MSEC, (frame_time * 1000))
    print(cv2.CAP_PROP_POS_MSEC, (frame_time * 1000))
    # Lee el fotograma actual
    ret, frame = cap.read()
    # Si no se pudo leer el fotograma, sale de la función
    if not ret:
        return
    # Libera los recursos del objeto VideoCapture
    cap.release()
    # Agrega una línea al fotograma
    img = cv2.circle(frame, (377, 253), 63, (0, 0, 255), -1)
    # Pide al usuario que seleccione un archivo para guardar el fotograma
    file_path = filedialog.asksaveasfilename(defaultextension=".jpg")
    # escribir fotograma modificado en el video
    out = cv2.VideoWriter(player.get_media().get_mrl(), cv2.VideoWriter_fourcc(*'mp4v'), cap.get(
        cv2.CAP_PROP_FPS), (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))
    out.write(img)
    while(cap.isOpened()):
        ret, frame = cap.read()
        if not ret:
            break
        if cap.get(cv2.CAP_PROP_POS_FRAMES) == frame_index:
            continue  # saltar fotograma a reemplazar
        out.write(frame)
    if file_path:
        # Guarda el fotograma en el archivo seleccionado
        cv2.imwrite(file_path, img)
        # Carga la imagen en un objeto Image de Pillow
        img = PIL.Image.open(file_path)
        # Convierte la imagen a un objeto PhotoImage de Tkinter
        img_tk = PIL.ImageTk.PhotoImage(img)
        # Crea una etiqueta para mostrar la imagen en una ventana aparte
        img_label = tk.Label(tk.Toplevel(), image=img_tk)
        img_label.image = img_tk
        img_label.pack()
    else:
        print("No se seleccionó ningún archivo para guardar el fotograma.")

# Función para abrir un archivo de video
def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi *.mkv *.mp3")])
    media = instance.media_new(file_path)
    player.set_media(media)
    player.play()
# Función para pausar el video
def pause():
    player.pause()
# Función para detener el video
def stop():
    player.stop()
def update():
    currentTime = int(player.get_time() / 1000)  # read current time
    totalTime = int(player.get_length() / 1000)  # read total time
    currentTimeLabel.config(text=time.strftime('%M:%S', time.gmtime(currentTime)))
    minutes = totalTime // 60
    seconds = totalTime % 60
    durationLabel.config(text='{0:02d}:{1:02d}'.format(minutes, seconds))
    progressBar.config(value=currentTime, maximum=totalTime)  # configure the play bar
    root.after(1000, update)
# reads the cursor event in the play bar
def progressBarClic(event):
    x = event.x  # read event
    totalTime = int(player.get_length() / 1000)
    position = x / progressBar.winfo_width()
    timeJump = int(totalTime * position)  # jumps at the right time
    player.set_time(timeJump * 1000)  # reproduce at the right time
def borrar_archivo():
    archivo = "archivo.mp3"
    if os.path.exists(archivo):
        os.remove(archivo)
def cerrar_ventana():
    borrar_archivo()
    root.destroy()

#funcion para mostrar subtitulos usando libreria vlc usando archivo srt
def MosSub():
    subtitles = vlc.Media('Sub.srt')
    media.add_option('sub-file={}'.format(subtitles.get_mrl()))

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
        edited_frame = edited_frame.resize((video.w, video.h))
        edited_frame = edited_frame.set_duration(1/video.fps)  # Duración de 1 fotograma
        edited_frame = edited_frame.set_start((index_to_replace + i) / video.fps)  # Tiempo de inicio del fotograma
        frames.insert(index_to_replace + i, edited_frame)

    # Generar el nuevo video
    new_video_path = os.path.splitext(original_video_path)[0] + "_edited2.mp4"
    new_video = ImageSequenceClip(frames, fps=video.fps)
    new_video = new_video.set_audio(audio)
    new_video.write_videofile(new_video_path, codec="libx264")
    messagebox.showinfo(
        "Éxito", f"El video editado se ha guardado en {new_video_path}.")


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
               i] = edited_frame.set_position((0, 0)).img

    # Generar el nuevo video
    new_video_path = os.path.splitext(original_video_path)[0] + "_edited2.mp4"
    new_video = ImageSequenceClip(frames, fps=video.fps)
    new_video = new_video.set_audio(audio)
    new_video.write_videofile(new_video_path, codec="libx264")
    messagebox.showinfo(
        "Éxito", f"El video editado se ha guardado en {new_video_path}.")


# crear la root principal de tkinterdis
root = tk.Tk()
root.title("Reproductor de Video")
# agregar la barra de progreso
load = False
playing = True
currentTimeLabel = ttk.Label(root, text='00:00')
currentTimeLabel.grid(row=1,column=0)
durationLabel = ttk.Label(root, text='00:00')
durationLabel.grid(row=1, column=6)
s = ttk.Style()
s.theme_use('clam')
s.configure("red.Horizontal.TProgressbar", foreground='red', background='red')
progressBar = ttk.Progressbar(root, style = 'red.Horizontal.TProgressbar', orient='horizontal', length=600, mode='determinate')
progressBar.grid(row=1, column=1)
progressBar.bind('<Button-1>', progressBarClic)
BTopen=ttk.Button(root,text="abir",command=open_file)
BTopen.place(x=0,y=475)
ToolTip(BTopen,msg="selecciona un archivo de video para reproducir")
Pausas=ttk.Button(root,text="pausa",command=pause)
Pausas.place(x=0,y=520)
ToolTip(Pausas,msg="Pausar el video en reproduccion")
parada=ttk.Button(root,text="parar",command=stop)
parada.place(x=100,y=475)
ToolTip(parada,msg="detiene la reproduccion del video ")
imaframe=ttk.Button(root,text="extraer frame",command=extract_frame)
imaframe.place(x=100,y=520)
ToolTip(imaframe,msg="extra el frame que se esta viendo en imagen ")
NewVideo=ttk.Button(root,text="nuevo video",command=insert_frame)
NewVideo.place(x=600,y=475)
load = False
playing = True
currentTimeLabel = ttk.Label(root, text='00:00')
currentTimeLabel.grid(row=1,column=0)
durationLabel = ttk.Label(root, text='00:00')
durationLabel.grid(row=1, column=6)
# agregar el reproductor de video a la root principal de tkinter
player.set_hwnd(root.winfo_id())
progressBar.lift()
# iniciar el bucle de eventos de tkinter
ancho_root = 700
alto_root = 550
x_root = root.winfo_screenwidth() // 2 - ancho_root // 2
y_root = root.winfo_screenheight() // 2 - alto_root // 2
root.geometry('{}x{}+{}+{}'.format(ancho_root, alto_root, x_root, y_root))
root.resizable(False, False)#para que no se redimensione la ventana
update()
root.protocol("WM_DELETE_WINDOW", cerrar_ventana)
root.mainloop()