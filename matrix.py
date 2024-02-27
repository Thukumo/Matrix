import cv2, time, shutil, signal, os, numpy, argparse, sounddevice, psutil, subprocess
from threading import Thread
#めも　numpy, opencv-python, sounddevice, moviepy
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
                    writing = False
                    lh = h
                else:
                    frame_array = 0.299 * frame_array[:, :, 2] + 0.587 * frame_array[:, :, 1] + 0.114 * frame_array[:, :, 0]
                    frame_txt = ""
                    for j in range(h):
                        text = ""
                        for k in range(w):
                            text += char4im[int(frame_array[j, k]*(len(char4im))/256)] #frame_array[j, k]の値は255がMAX
                        frame_txt += text+"\n"
                    os.write(1, (frame_txt+"\n\n").encode())
                writing = False
                if (i+1)/fps < time.perf_counter()-start:
                    skip = True
                else:
                    time.sleep(max(0, (i+1)/fps-(time.perf_counter()-start)))
    return drop
def audio_player(arr, rate):
    global start
    sounddevice.play(arr, rate, loop=False)
    start = time.perf_counter()
    sounddevice.wait()
def exitter(hoge, fuga):
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
parser.add_argument("-g", "--grayscale", help="モノクロで出力します。", action="store_true")
#parser.add_argument("-o", "--old", help="古い方法でカラー出力を行います。音声の再生が安定しますが縦ブレが発生します。", action="store_true")
parser.add_argument("-n", "--new", help="新しい方法でカラー出力を行います。縦ブレは無くなりますが、動画によっては映像がかなり遅れます。", action="store_true")
parser.add_argument("-r", "--rate", help="出力を消去するレートを指定します。-oオプションがない場合無視されます。単位: フレーム", type=int)
parser.add_argument("-d", "--debug", type = int)
args = parser.parse_args()
psutil.Process().nice(psutil.HIGH_PRIORITY_CLASS)
signal.signal(signal.SIGINT, exitter)
if args.filename != None:
    filename = args.filename
    cap = cv2.VideoCapture(filename)
    if shutil.which("ffmpeg") == None or shutil.which("ffprobe") == None:
        print("ffmpeg, ffproveがインストールされていないためmoviepyを使用します。")
        if os.path.splitext(filename)[1][1:]  not in ["mp4", "webm"]:
            print()
            print(f"moviepyはこのファイル形式({os.path.splitext(filename)[1][1:]})に対応していない可能性があります。")
            print("そのため、音声が再生されない可能性があります。")
            time.sleep(2)
        time.sleep(1)
        from moviepy.editor import VideoFileClip
        try:
            audio = VideoFileClip(filename).audio
            t = Thread(target=audio_player, args=[audio.to_soundarray(fps=audio.fps), audio.fps], daemon=True)
        except OSError:
            print("ファイルが開けません。ファイル名を確認してください。")
            exit()
    else:
        t = t = Thread(target=audio_player, args=[numpy.frombuffer(subprocess.Popen(["ffmpeg", "-i", filename, "-f", "wav", "-"], stdout=subprocess.PIPE).stdout.read(), dtype=numpy.int16), int(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=sample_rate", "-of", "default=noprint_wrappers=1:nokey=1", filename], capture_output=True, text=True).stdout)*2], daemon=True)
else:
    cap = cv2.VideoCapture(args.camnum)
#if args.rate != None and args.old:
if args.rate != None and not args.new:
    flushlate = args.late
    flush = True
color = not args.grayscale
#old_color = args.old
old_color = not args.new
if not cap.isOpened():
    print("OpenCVの実行に失敗しました。カメラが正しく接続されているか確認してください。")
    exit()
terminal_size = shutil.get_terminal_size()
fps = cap.get(cv2.CAP_PROP_FPS)
frame = cap.get(cv2.CAP_PROP_FRAME_COUNT)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
capw = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
caph = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
show = False
if not args.debug == None:
    if args.debug == 1 or args.debug == 3:
        show = True
    elif not args.debug in range(1, 4):
        print("エラー: 範囲外の値です。")
        exit()
drop = main(terminal_size.columns, terminal_size.lines-1, cap, capw, caph, fps, flushlate, show)
if not args.debug == None and (args.debug == 2 or args.debug == 3):
        memo = time.perf_counter()-start
        exitter(None, None)
        if not frame == -1:
            print("再生時間", frame/fps, memo, end="秒\n")
            print("ずれ", memo-frame/fps, end="秒\n")
            if not drop == 0:
                print("フレームドロップ率", drop/frame*100, end="%\n")
