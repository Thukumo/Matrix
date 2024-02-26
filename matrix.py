import cv2, time, shutil, signal, os, numpy, argparse, sounddevice, psutil
from threading import Thread
from pydub import AudioSegment
#めも　numpy, opencv-python, sounddevice, pydub
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
    global filename, start, t, char4im, writing, color, old_color, flush
    drop = 0
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
            h = terminal_size.lines-1
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
    else: #movie
        start = time.perf_counter()
        i = 0
        t.start()
        frame_txt = ""
        ret, frame = cap.read()
        if show:
            cv2.imshow("frame", cv2.resize(frame, (w, h*2)))
            cv2.waitKey(1)
        frame_array = numpy.array(cv2.resize(frame, (w, h)), dtype=numpy.uint8)
        if color:
            writing = True
            frame_txt = ""
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
                print(text)
            lh = h
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
                drop += 1
                cap.read()
                continue
            terminal_size = shutil.get_terminal_size()
            w = terminal_size.columns
            h = terminal_size.lines-1 if 1 < terminal_size.lines else 1
            if w/capw < h/caph:
                h = int(caph*w/capw)
            else:
                w = int(capw*h/caph)
            ret, frame = cap.read()
            if ret:
                if show:
                    bairitu = 3
                    cv2.imshow("frame", cv2.resize(frame, (w*bairitu, h*2*bairitu)))
                    cv2.waitKey(1)
                frame_array = numpy.array(cv2.resize(frame, (w, h)), dtype=numpy.uint8)
                if color:
                    if i%flushlate == 0 and flush:
                        print("\033c", end="")
                    writing = True
                    frame_txt = ""
                    oldr = 256
                    oldg = 256
                    oldb = 256
                    if not old_color:
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
                        if not old_color:
                            print("\033[K"+text)
                        else:
                            frame_txt += text+"\n"
                    if old_color:
                        print(frame_txt)
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
    return drop
def audio_player(arr, rate):
    global start
    arr = arr/numpy.max(numpy.abs(arr))
    sounddevice.play(numpy.append(arr[::2], arr[1::2]).reshape(-1, 2), rate/2)
    start = time.perf_counter()
    sounddevice.wait()

def exitter(hoge, fuga):
    global cap, writing, color
    cap.release()
    sounddevice.stop()
    cv2.destroyAllWindows()
    if color:
        os.write(1, b"\033[0m")
        os.write(1, b"\033[2J")
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    os.write(1, b"\n")
    if args.debug == None or args.debug == 1:
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
parser.add_argument("-o", "--old", help="古い方法でカラー出力を行います。音声の再生が安定しますが縦ブレが発生します。", action="store_true")
parser.add_argument("-r", "--rate", help="出力を消去するレートを指定します。-oオプションがない場合無視されます。単位: フレーム", type=int)
parser.add_argument("-d", "--debug", type = int)
args = parser.parse_args()
psutil.Process().nice(psutil.HIGH_PRIORITY_CLASS)
signal.signal(signal.SIGINT, exitter)
if args.filename != None:
    filename = args.filename
    cap = cv2.VideoCapture(filename)
    audio = AudioSegment.from_file(filename, os.path.splitext(filename)[1][1:])
    #os.system(f"start \"C:\\Program Files\\VideoLAN\\VLC\\vlc.exe\" \"{filename}\"")
    time.sleep(0.25)
    try:
        t = Thread(target=audio_player, args=[numpy.array(audio.get_array_of_samples(), dtype=numpy.int32), audio.frame_rate], daemon=True)
    except OSError:
        print("ファイルが開けません。ファイル名を確認してください。")
        exit()
else:
    cap = cv2.VideoCapture(args.camnum)
if args.rate != None and args.old:
    flushlate = args.late
    flush = True
color = not args.mono
old_color = args.old
if not cap.isOpened():
    print("OpenCVの実行に失敗しました。カメラが正しく接続されているか確認してください。")
    exit()
terminal_size = shutil.get_terminal_size()
height = terminal_size.lines-1
width = terminal_size.columns
fps = cap.get(cv2.CAP_PROP_FPS)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
capw = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
caph = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
show = False
if not args.debug == None and args.debug == 1 or args.debug == 3:
        show = True
drop = main(width, height, cap, capw, caph, fps, flushlate, show)
if not args.debug == None and args.debug == 2 or args.debug == 3:
        frame = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        memo = (time.perf_counter()-start)/60
        exitter(None, None)
        print(memo, end="分\n")
        if not frame == -1 and drop != 0:
            print(drop/frame*100, end="%\n")
