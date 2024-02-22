import cv2, time, numba, shutil, signal, os, numpy, ctypes, sys
from threading import Thread
from moviepy.editor import VideoFileClip
#めも　numpy, numba, opencv-python, moviepy
ENABLE_PROCESSED_OUTPUT = 0x0001
ENABLE_WRAP_AT_EOL_OUTPUT = 0x0002
ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
MODE = ENABLE_PROCESSED_OUTPUT + ENABLE_WRAP_AT_EOL_OUTPUT + ENABLE_VIRTUAL_TERMINAL_PROCESSING
 
kernel32 = ctypes.windll.kernel32
handle = kernel32.GetStdHandle(-11)
kernel32.SetConsoleMode(handle, MODE)

def main(w, h, cap, capw, caph, fps, show=False):
    global filename, start
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
    start = 0
    skip = False
    curtime = time.perf_counter()
    print(fps)
    if int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) == -1:
        while True:
            curtime = time.perf_counter()
            ret, frame = cap.read()
            if show:
                cv2.imshow("frame", cv2.resize(frame, (w, h*2)))
                cv2.waitKey(1)
            frame_array = numpy.array(cv2.resize(frame, (w, h)), dtype=numpy.uint8)
            print("\n".join(conv2txt(w, h, frame_array)))
            time.sleep(max(0, 1/fps-(time.perf_counter()-curtime)))
            curtime = time.perf_counter()
    else:
        for i in range(int(cap.get(cv2.CAP_PROP_FRAME_COUNT))):
            if i == 0:
                start = time.perf_counter()-2.7
                t.start()
            elif skip:
                skip = False
                print("skipped")
                continue
            curtime = time.perf_counter()
            ret, frame = cap.read()
            if show:
                cv2.imshow("frame", cv2.resize(frame, (w, h*2)))
                cv2.waitKey(1)
            print("\n".join(conv2txt(w, h, numpy.array(cv2.resize(frame, (w, h)), dtype=numpy.uint8))))
            now = time.perf_counter()
            if (i+1)/fps < now-start:
                skip = True
            else:
                time.sleep(max(0, 1/fps-(now-curtime))) #なぜかたまにエラーでるからmax(0, 1/fps-(time.perf_counter()-curtime))にした
            curtime = time.perf_counter()

def audio_player(clip):
    global start
    clip.audio.preview()

@numba.njit(cache=True)
def conv2txt(w, h, frame_array): #numbaのために分ける。あんま速度変わってない？
    char4im = [" ", ".", "-", ":", "+", "*", "#" ,"%", "@"]
    frame_array = 0.299 * frame_array[:, :, 2] + 0.587 * frame_array[:, :, 1] + 0.114 * frame_array[:, :, 0]
    frame_txt = []
    for i in range(h):
        text = ""
        for j in range(w):
            text += char4im[int(frame_array[i, j]*(len(char4im))/256)] #frame_array[i, j]の値は255がMAX
        frame_txt.append(text)
    return frame_txt
def exitter(hoge, fuga):
    global cap
    cap.release()
    cv2.destroyAllWindows()
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    os._exit(0)
if len(sys.argv) == 2:
    filename = sys.argv[1]
    cap = cv2.VideoCapture(filename)
    t = Thread(target=audio_player, args=[VideoFileClip(filename)])
elif len(sys.argv) == 1:
    cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("OpenCVの実行に失敗しました")
    exit()
terminal_size = shutil.get_terminal_size()
height = terminal_size.lines
width = terminal_size.columns
fps = 40
fps = cap.get(cv2.CAP_PROP_FPS)
#fps *= 1.05
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
capw = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
caph = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
signal.signal(signal.SIGINT, exitter)
main(width, height, cap, capw, caph, fps, show=False)
cap.release()
cv2.destroyAllWindows()
signal.signal(signal.SIGINT, signal.SIG_DFL)
os._exit(0)
