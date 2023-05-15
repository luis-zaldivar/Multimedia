import vlc
from tkinter import *
import tkinter as tk
from tkinter import filedialog, ttk
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


# crear la instancia de VLC
instance = vlc.Instance('--no-xlib')
player = instance.media_player_new()
player.set_fullscreen(True)

# Función para extraer un frame del video


def extract_frame():
    # Pausa el reproductor de video
    player.pause()
    # Obtiene el tiempo actual del video
    frame_time = (player.get_time() / 1000.0) + 0.01
    # Carga el video en OpenCV
    cap = cv2.VideoCapture(player.get_media().get_mrl())
    # Va al fotograma especificado por el tiempo actual del video
    cap.set(cv2.CAP_PROP_POS_MSEC, (frame_time * 1000))
    # Lee el fotograma actual
    ret, frame = cap.read()
    # Si no se pudo leer el fotograma, sale de la función
    if not ret:
        return
    # Libera los recursos del objeto VideoCapture
    cap.release()
    # Agrega una línea al fotograma
    img = cv2.circle(frame, (377,253), 63, (0, 0, 255), -1)
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
        img = Image.open(file_path) 
        # Convierte la imagen a un objeto PhotoImage de Tkinter
        img_tk = ImageTk.PhotoImage(img)
        # Crea una etiqueta para mostrar la imagen en una ventana aparte
        img_label = Label(Toplevel(), image=img_tk)
        img_label.image = img_tk
        img_label.pack()
    else:
        print("No se seleccionó ningún archivo para guardar el fotograma.")



        

# Función para abrir un archivo de video
def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi *.mkv *.mp3")])
    media = instance.media_new(file_path)
    player.set_media(media)
    '''
    # Obtener la ruta relativa del archivo
    ruta_relativa = os.path.join(os.getcwd(), file_path)
    print(ruta_relativa)
    # Ruta del archivo de salida MP3
    output_file = "archivo.mp3"

    # Comando de ffmpeg para convertir el archivo MP4 a MP3
    command = f"ffmpeg -i {ruta_relativa} -vn -acodec libmp3lame -qscale:a 2 {output_file}"

    # Ejecutar el comando de ffmpeg
    subprocess.call(command, shell=True)
    
    model = whisper.load_model("medium")
    result = model.transcribe("archivo.mp3")
    srt_path = os.path.join("", "Sub.srt")
    write_str = WriteSRT(srt_path)
    with open(srt_path, "w", encoding="utf-8") as srt_file:
        write_str.write_result(result, srt_file, options={'max_line_width': 250, 'max_line_count': 250, 'highlight_words': True})
    '''
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
#Sub=ttk.Button(root,text="cc",command=MosSub)
#Sub.place(x=590,y=475)
ToolTip(parada,msg="detiene la reproduccion del video ")
imaframe=ttk.Button(root,text="extraer frame",command=extract_frame)
imaframe.place(x=100,y=520)
ToolTip(imaframe,msg="extra el frame que se esta viendo en imagen ")
#ToolTip(Sub, msg="Mostar Subtitulos  ")
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