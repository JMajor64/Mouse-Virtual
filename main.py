import cv2
import numpy as np
import SeguimientoManos as sm  #Programa que contiene la deteccion y seguimiento de manos
from pynput.mouse import Button, Controller
import ctypes
import time
user32 = ctypes.windll.user32

mouse = Controller()
screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

L_mouse_pressed = False

#---------------------------------Declaracion de funciones---------------------------------------
def L_Click_condition(dedos):
    if dedos[1]== 0:
        return False
    return True  

def mover_relativo(x, y):
    pos_actual = mouse.position
    nueva_pos = (pos_actual[0] + x, pos_actual[1] + y)
    mouse.position = nueva_pos

def mover_absoluto(x, y):
    mouse.position = (x, y)

#---------------------------------Declaracion de variables---------------------------------------
anchocam, altocam = 640, 480
cuadro = 150 #Rango donde podemos interacturar
anchopanta, altopanta = screensize
sua = 5
pubix, pubiy = 0,0
cubix, cubiy = 0,0

#----------------------------------- Lectura de la camara----------------------------------------
cap = cv2.VideoCapture(0)
cap.set(3,anchocam)  #Definiremos un ancho y un alto definido para siempre
cap.set(4,altocam)

detector = sm.detectormanos(maxManos=1)

while True:
    #----------------- Encontrar los puntos de la mano -----------------------------
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    frame = detector.encontrarmanos(frame)
    lista, bbox = detector.encontrarposicion(frame)

    #-----------------Obtener la punta del dedo indice y corazon----------------------------
    if len(lista) != 0:
        x1, y1 = lista[5][1:]                  #Coordenadas del dedo indice
        x2, y2 = lista[4][1:]                 #Coordenadas del pulgar

        #----------------- Comprobar que dedos estan arriba --------------------------------
        dedos = detector.dedosarriba() #Contamos con 5 posiciones nos indica si levanta cualquier dedo
        #cv2.rectangle(frame, (cuadro, cuadro), (anchocam - cuadro, altocam - cuadro), (0, 0, 0), 2)
        #----------------------------- Comprobar el click -------------------------
        if L_Click_condition(dedos):
            if not L_mouse_pressed:
                mouse.press(Button.left)
                L_mouse_pressed = True
                time.sleep(0.1)
        else:
            if L_mouse_pressed:
                mouse.release(Button.left)
                L_mouse_pressed = False

        #-----------------> conversion a pixeles de pantalla-------------
        x3 = np.interp(x1, (cuadro,anchocam-cuadro), (0,anchopanta))
        y3 = np.interp(y1, (cuadro, altocam-cuadro), (0, altopanta))
        #------------------------------- Suavizado de valores ----------------------------------
        cubix = pubix + (x3 - pubix) / sua 
        cubiy = pubiy + (y3 - pubiy) / sua

        #-------------------------------- Mover el Mouse ---------------------------------------
        mover_absoluto(cubix,cubiy)
        #cv2.circle(frame, (x1,y1), 10, (0,0,0), cv2.FILLED)
        pubix, pubiy = cubix, cubiy

                
    cv2.imshow("Mouse", frame)
    
    k = cv2.waitKey(1)
    if k == 27:
        break
cap.release()
cv2.destroyAllWindows()
