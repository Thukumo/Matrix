import cv2, time, numba, shutil, signal, os
import numpy as np

import ctypes
 
ENABLE_PROCESSED_OUTPUT = 0x0001
ENABLE_WRAP_AT_EOL_OUTPUT = 0x0002
ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
MODE = ENABLE_PROCESSED_OUTPUT + ENABLE_WRAP_AT_EOL_OUTPUT + ENABLE_VIRTUAL_TERMINAL_PROCESSING
 
kernel32 = ctypes.windll.kernel32
handle = kernel32.GetStdHandle(-11)
kernel32.SetConsoleMode(handle, MODE)
#@numba.njit(cache=True)
def main(w, h, cap, capw, caph, show=False):
    #global cap, capw, caph
    char4im = [" ", ".", "-", ":", "+", "*", "#" ,"%", "@"]
    print(w, h)
    print(capw/caph)
    print(w/capw, h/caph)
    if True:
        if w/capw < h/caph:
            print("h")
            h = int(caph*w/capw)
        else:
            print("w")
            w = int(capw*h/caph)
    print(capw, caph)
    print(w/h)
    print(w, h)
    w = int(w*2) #気にしない
    while True:
        ret, frame = cap.read()
        if show:
            cv2.imshow("frame", cv2.resize(frame, (w, h*2)))
            cv2.waitKey(1)
        frame_array = np.array(cv2.resize(frame, (w, h)), dtype=np.uint8)
        frame_array = 0.299 * frame_array[:, :, 2] + 0.587 * frame_array[:, :, 1] + 0.114 * frame_array[:, :, 0]
        frame_txt = []
        for i in range(h):
            text = ""
            for j in range(w):
                text += char4im[int(frame_array[i, j]*(len(char4im))/256)] #frame_array[i, j]の値は255がMAX
            frame_txt.append(text)
        print('\033[32m'+"\n".join(frame_txt)+'\033[0m')
        time.sleep(1/40)

def exitter(hoge, fuga):
    global cap
    cap.release()
    cv2.destroyAllWindows()
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    os._exit(0)
terminal_size = shutil.get_terminal_size()
height = terminal_size.lines
width = terminal_size.columns
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
capw = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
caph = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
signal.signal(signal.SIGINT, exitter)
main(width, height, cap, capw, caph, False)
cap.release()
cv2.destroyAllWindows()
signal.signal(signal.SIGINT, signal.SIG_DFL)
os._exit(0)
