import cv2, time, shutil, signal, os, numpy, sys, argparse
from threading import Thread
from moviepy.editor import VideoFileClip
#めも　numpy, opencv-python, moviepy
if os.name == "nt": #なぜ必要なのかはしらない
    import ctypes
    ENABLE_PROCESSED_OUTPUT = 0x0001
    ENABLE_WRAP_AT_EOL_OUTPUT = 0x0002
    ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
    MODE = ENABLE_PROCESSED_OUTPUT + ENABLE_WRAP_AT_EOL_OUTPUT + ENABLE_VIRTUAL_TERMINAL_PROCESSING
    kernel32 = ctypes.windll.kernel32
    handle = kernel32.GetStdHandle(-11)
    kernel32.SetConsoleMode(handle, MODE)

def main(w, h, cap, capw, caph, fps, flushlate, show=False):
    global filename, start, t, char4im, writing, color, flush
    capw = capw*2
    if color and os.name == "nt" and not "WT_SESSION" in os.environ:
        capw = capw/2 #Windows Terminalは■の縦横比が2:1、cmdは1:1なため
    if w/capw < h/caph:
        h = int(caph*w/capw)
    else:
        w = int(capw*h/caph)
    start = 0
    skip = False
    if color and False: #必要なさそうなので無効化
        color = False
        if os.name == "nt":
            color = True
        else:
            print("実行環境がWindows NT系でないためモノクロでの出力を行います。")
            #time.sleep(3)
            color = True
    curtime = time.perf_counter()
    if int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) == -1:
        i = 0
        while True:
            i += 1
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
                oldr = 256
                oldg = 256
                oldb = 256
                if color:
                    writing = True
                    if i%flushlate == 0 and flush:
                        print("\033c", end="")
                    frame_txt = ""
                    for j in range(h):
                        text = ""
                        for k in range(w):
                            b, g, r = frame_array[j, k]
                            if oldr != r or oldg != g or oldb != b:
                                text += f"\033[38;2;{r};{g};{b}m"
                                oldr = r
                                oldg = g
                                oldb = b
                            text += "■"
                        frame_txt += text+"\n"
                    print(frame_txt+"\033[0m")
                else:
                    frame_array = 0.299 * frame_array[:, :, 2] + 0.587 * frame_array[:, :, 1] + 0.114 * frame_array[:, :, 0]
                    frame_txt = ""
                    for j in range(h):
                        text = ""
                        for k in range(w):
                            text += char4im[int(frame_array[j, k]*(len(char4im))/256)] #frame_array[j, k]の値は255がMAX
                        frame_txt += text+"\n"
                    print(frame_txt)
                time.sleep(max(0, 1/fps-(time.perf_counter()-curtime)))
                curtime = time.perf_counter()
    else: #color
        start = time.perf_counter()
        i = 0
        frame_txt = ""
        t.start()
        ret, frame = cap.read()
        if show:
            cv2.imshow("frame", cv2.resize(frame, (w, h*2)))
            cv2.waitKey(1)
        frame_array = numpy.array(cv2.resize(frame, (w, h)), dtype=numpy.uint8)
        if color:
            writing = True
            frame_txt = ""
            #print("\033[{lh}F", end="")
            oldr = 256
            oldg = 256
            oldb = 256
            for j in range(h):
                text = ""
                for k in range(w):
                    b, g, r = frame_array[j, k]
                    if oldr != r or oldg != g or oldb != b:
                        text += f"\033[38;2;{r};{g};{b}m"
                        oldr = r
                        oldg = g
                        oldb = b
                    text += "■"
                #print("\033[K"+text, end="")
                print(text)
            lh = h+1
        else:
            frame_array = 0.299 * frame_array[:, :, 2] + 0.587 * frame_array[:, :, 1] + 0.114 * frame_array[:, :, 0]
            frame_txt = ""
            for j in range(h):
                text = ""
                for k in range(w):
                    text += char4im[int(frame_array[j, k]*(len(char4im))/256)] #frame_array[j, k]の値は255がMAX
                    frame_txt += text+"\n"
        now = time.perf_counter()
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
                    #cv2.imshow("frame", cv2.resize(frame, (w, h*2)))
                    bairitu = 3
                    cv2.imshow("frame", cv2.resize(frame, (w*bairitu, h*2*bairitu)))
                    cv2.waitKey(1)
                frame_array = numpy.array(cv2.resize(frame, (w, h)), dtype=numpy.uint8)
                if color:
                    writing = True
                    frame_txt = ""
                    oldr = 256
                    oldg = 256
                    oldb = 256
                    print(f"\033[{lh}F", end="")
                    for j in range(h):
                        text = ""
                        for k in range(w):
                            b, g, r = frame_array[j, k]
                            if oldr != r or oldg != g or oldb != b:
                                text += f"\033[38;2;{r};{g};{b}m"
                                oldr = r
                                oldg = g
                                oldb = b
                            text += "■"
                        print("\033[K"+text)
                    lh = h
                else:
                    frame_array = 0.299 * frame_array[:, :, 2] + 0.587 * frame_array[:, :, 1] + 0.114 * frame_array[:, :, 0]
                    frame_txt = ""
                    for j in range(h):
                        text = ""
                        for k in range(w):
                            text += char4im[int(frame_array[j, k]*(len(char4im))/256)] #frame_array[j, k]の値は255がMAX
                        frame_txt += text+"\n"
                    os.write(1, ("\n"+frame_txt).encode())
                writing = False
                if (i+1)/fps < time.perf_counter()-start:
                    skip = True
                else:
                    time.sleep(max(0, (i+1)/fps-(time.perf_counter()-start)))

def audio_player(clip):
    global start
    start = time.perf_counter()
    clip.audio.preview()

def exitter(hoge, fuga):
    global cap, writing, color
    cap.release()
    cv2.destroyAllWindows()
    if color:
        os.write(1, b"\033[0m")
        os.write(1, b"\033[2J")
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    os._exit(0)

char4im = [" ", ".", "-", "\"", ":", "+", "|", "*", "#" ,"%", "&", "@"] #ダダダダ天使の見栄え的にひとまずこれで
#char4im = [" ", ".", "\'", "-", ":", "+", "|", "*", "$", "#", "%", "&", "@"]
writing = False
color = True
flush = False
flushlate = 30
parser = argparse.ArgumentParser(description="ビデオプレイヤー on ターミナル")
parser.add_argument("-f", "--filename", type=str, help="動画ファイル名を指定します。-cオプションを無視します。")
parser.add_argument("-c", "--camnum", help="使用するカメラの番号を指定します。既定値0", type=int, default=0)
parser.add_argument("-m", "--mono", help="モノクロで出力します。", action="store_true")
args = parser.parse_args()
signal.signal(signal.SIGINT, exitter)
if not args.filename == None:
    cap = cv2.VideoCapture(args.filename)
    try:
        t = Thread(target=audio_player, args=[VideoFileClip(args.filename)], daemon=True)
    except OSError:
        print("ファイルが開けません。ファイル名を確認してください。")
        exit()
else:
    cap = cv2.VideoCapture(args.camnum)
color = not args.mono
if not cap.isOpened():
    print("OpenCVの実行に失敗しました。カメラが正しく接続されているか確認してください。")
    exit()
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
