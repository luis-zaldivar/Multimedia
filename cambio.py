import cv2

# Cargar el video
cap = cv2.VideoCapture('1_4938376825987400055.mp4')

# Verificar si el video se ha cargado correctamente
if not cap.isOpened():
    print("Error al cargar el video")
    exit()

# Obtener el número total de fotogramas en el video
num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

# Leer el segundo fotograma del video
cap.set(cv2.CAP_PROP_POS_FRAMES, 1)
ret, frame = cap.read()

# Cargar la imagen que se desea insertar en el video
img = cv2.imread('x.jpg')

# Reemplazar el segundo fotograma del video con la imagen cargada
cap.set(cv2.CAP_PROP_POS_FRAMES, 3)
cap = cv2.VideoWriter('nuevo_video.mp4', cv2.VideoWriter_fourcc(*'mp4v'), cap.get(
    cv2.CAP_PROP_FPS), (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))
cap.write(img)

# Liberar el objeto de captura y cerrar la ventana
cap.release()
cv2.destroyAllWindows()
