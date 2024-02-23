import cv2, time, shutil, signal, os, numpy, sys
from threading import Thread
from moviepy.editor import VideoFileClip
#めも　numpy, opencv-python, moviepy
if os.name == "nt":
    import ctypes
    ENABLE_PROCESSED_OUTPUT = 0x0001
    ENABLE_WRAP_AT_EOL_OUTPUT = 0x0002
    ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
    MODE = ENABLE_PROCESSED_OUTPUT + ENABLE_WRAP_AT_EOL_OUTPUT + ENABLE_VIRTUAL_TERMINAL_PROCESSING
    kernel32 = ctypes.windll.kernel32
    handle = kernel32.GetStdHandle(-11)
    kernel32.SetConsoleMode(handle, MODE)

def main(w, h, cap, capw, caph, fps, flushlate, show=False):
    global filename, start, t, char4im, writing, color
    capw = capw*2 #ターミナルのフォントの縦横比が2:1らしいので
    if w/capw < h/caph:
        h = int(caph*w/capw)
    else:
        w = int(capw*h/caph)
    start = 0
    skip = False
    if color:
        color = False
        if os.name == "nt":
            color = True
        else:
            print("実行環境がWindows NT系でないためモノクロでの出力を行います。")
            time.sleep(3)
    curtime = time.perf_counter()
    if int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) == -1:

        while True:
            terminal_size = shutil.get_terminal_size()
            w = terminal_size.columns
            h = terminal_size.lines
            if w/capw < h/caph:
                h = int(caph*w/capw)
            else:
                w = int(capw*h/caph)
            ret, frame = cap.read()
            if ret:
                if show:
                    cv2.imshow("frame", cv2.resize(frame, (w, h*2)))
                    cv2.waitKey(1)
                frame_array = numpy.array(cv2.resize(frame, (w, h)), dtype=numpy.uint8)
                frame_array = 0.299 * frame_array[:, :, 2] + 0.587 * frame_array[:, :, 1] + 0.114 * frame_array[:, :, 0]
                frame_txt = []
                for i in range(h):
                    text = ""
                    for j in range(w):
                        text += char4im[int(frame_array[i, j]*(len(char4im))/256)] #frame_array[i, j]の値は255がMAX
                    frame_txt.append(text)
                frame_txt = "\n".join(frame_txt)
                if color:
                    print(f"\033[32m"+frame_txt+"\033[00m")
                else:
                    print(frame_txt)
                time.sleep(max(0, 1/fps-(time.perf_counter()-curtime)))
                curtime = time.perf_counter()
    else:
        start = time.perf_counter()
        i = 0
        t.start()
        ret, frame = cap.read()
        if show:
            cv2.imshow("frame", cv2.resize(frame, (w, h*2)))
            cv2.waitKey(1)
        frame_array = numpy.array(cv2.resize(frame, (w, h)), dtype=numpy.uint8)
        frame_array = 0.299 * frame_array[:, :, 2] + 0.587 * frame_array[:, :, 1] + 0.114 * frame_array[:, :, 0]
        frame_txt = []
        for j in range(h):
            text = ""
            for k in range(w):
                text += char4im[int(frame_array[j, k]*(len(char4im))/256)] #frame_array[j, k]の値は255がMAX
            frame_txt.append(text)
        print("\n".join(frame_txt))
        now = time.perf_counter()
        print(time.perf_counter(), now)
        if (i+1)/fps < now-start:
            skip = True
        else:
            time.sleep(max(0, ((i+1)/fps-(now-start))))
        for i in range(1, int(cap.get(cv2.CAP_PROP_FRAME_COUNT))):
            if skip:
                skip = False
                cap.read()
                continue
            terminal_size = shutil.get_terminal_size()
            w = terminal_size.columns
            h = terminal_size.lines
            if w/capw < h/caph:
                h = int(caph*w/capw)
            else:
                w = int(capw*h/caph)
            ret, frame = cap.read()
            if ret:
                if show:
                    cv2.imshow("frame", cv2.resize(frame, (w, h*2)))
                    cv2.waitKey(1)
                frame_array = numpy.array(cv2.resize(frame, (w, h)), dtype=numpy.uint8)
                if color:
                    writing = True
                    if (i+1)%flushlate == 0:
                        print("\033c", end="")
                    frame_arrayg = 0.299 * frame_array[:, :, 2] + 0.587 * frame_array[:, :, 1] + 0.114 * frame_array[:, :, 0] 
                    frame_txt = []
                    for j in range(h):
                        text = ""
                        for k in range(w):
                            text += f"\033[38;2;{frame_array[j, k, 2]};{frame_array[j, k, 1]};{frame_array[j, k, 0]}m"+char4im[int(frame_arrayg[j, k]*(len(char4im))/256)]+"\033[0m"
                        frame_txt.append(text)
                    print("\n".join(frame_txt))
                    writing = False
                else:
                    frame_array = 0.299 * frame_array[:, :, 2] + 0.587 * frame_array[:, :, 1] + 0.114 * frame_array[:, :, 0]
                    frame_txt = []
                    for j in range(h):
                        text = ""
                        for k in range(w):
                            text += char4im[int(frame_array[j, k]*(len(char4im))/256)] #frame_array[j, k]の値は255がMAX
                        frame_txt.append(text)
                    print("\n".join(frame_txt))
                if (i+1)/fps < time.perf_counter()-start:
                    skip = True
                else:
                    time.sleep((i+1)/fps-(time.perf_counter()-start))

def audio_player(clip):
    global start
    start = time.perf_counter()
    clip.audio.preview()

def exitter(hoge, fuga):
    global cap, writing, color
    cap.release()
    cv2.destroyAllWindows()
    if color:
        while writing:
            time.sleep(0.01)
        print("\033[0m")
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    os._exit(0)

char4im = [" ", ".", "-", "\"", ":", "+", "|", "*", "#" ,"%", "&", "@"] #ダダダダ天使の見栄え的にひとまずこれで
#char4im = [" ", ".", "\'", "-", ":", "+", "|", "*", "$", "#", "%", "&", "@"]
writing = False
color = True
flushlate = 30
if len(sys.argv) == 4:
    for i in sys.argv:
        if i.startswith("-f"):
            flushlate = int(i[2:])
        elif i.startswith("-m"):
            color = False
        else:
            filename = i
    cap = cv2.VideoCapture(filename)
    try:
        t = Thread(target=audio_player, args=[VideoFileClip(filename)])
    except OSError:
        print("ファイルが開けませんでした。")
        print("ファイル名が正しいか確認してください。")
        exit()
if len(sys.argv) == 3:
    if sys.argv[1].startswith("-m") or sys.argv[2].startswith("-m"):
        filename = sys.argv[1] if sys.argv[2].startswith("-m") else sys.argv[2]
        color = False
    elif sys.argv[1].startswith("-f") or sys.argv[2].startswith("-f"):
        flushlate = int(sys.argv[1][2:]) if sys.argv[1].startswith("-f") else int(sys.argv[2][2:])
        filename = sys.argv[2] if sys.argv[1].startswith("-f") else sys.argv[1]
    else:
        print("引数が正しくありません")
        exit()
    cap = cv2.VideoCapture(filename)
    try:
        t = Thread(target=audio_player, args=[VideoFileClip(filename)])
    except OSError:
        print("ファイルが開けませんでした。")
        print("ファイル名が正しいか確認してください。")
        exit()
elif len(sys.argv) == 2:
    filename = sys.argv[1]
    cap = cv2.VideoCapture(filename)
    try:
        t = Thread(target=audio_player, args=[VideoFileClip(filename)])
    except OSError:
        print("ファイルが開けませんでした。")
        print("ファイル名が正しいか確認してください。")
        exit()
elif len(sys.argv) == 1:
    cap = cv2.VideoCapture(0)
else:
    print("引数の数が正しくありません")
    exit()
if not cap.isOpened():
    print("OpenCVの実行に失敗しました。")
    print("カメラが正しく接続されているか確認してください。")
    exit()
signal.signal(signal.SIGINT, exitter)
terminal_size = shutil.get_terminal_size()
height = terminal_size.lines
width = terminal_size.columns
fps = cap.get(cv2.CAP_PROP_FPS)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
capw = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
caph = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
main(width, height, cap, capw, caph, fps, flushlate, False)
cap.release()
cv2.destroyAllWindows()
signal.signal(signal.SIGINT, signal.SIG_DFL)
sys.exit(0)
