# Matrix
Matrixのあれ(ターミナルを流れ落ちる文字で映像を表現)を作ろうとして挫折したものです。<br>
動画・カメラの映像をリアルタイムでAAに変換しターミナルに出力します。<br>
主にWindowsでの使用を想定していますがWSLでも動いたのでUnix系でもなんとかなると思います。<br>
実行中のターミナルウインドウのサイズ変更に対応していますが、音ズレするかもしれません
# 想定している使用用途
・遊び<br>
・微妙に遅い回線経由でのSSH時の動画ファイルの内容確認
# 準備
```
pip install -r requirements.txt
```
# 実行
モノクロ出力(-mオプションで指定)では、Windows Terminalよりもcmd.exeから実行したほうが映像の縦ブレが少ない気がします。<br>
カラー出力の場合Windows Terminalのほうが出力がいいです。<br>
詳しいオプションについては`python matrix.py -h`で確認してください。<br><br>
Ctrl+Cでの途中終了に対応しています。<br>
カメラの映像を出力させたい場合
```
python matrix.py
```
動画ファイルを再生したい場合
```
python matrix.py -f {動画ファイルのパス}
```
動画ファイルは何に対応してるのかあんまわかってないです。<br>
mp4とwebmは再生できました。
# 既知の不具合
・新しい方式で描画した場合、フレームスキップ率の高い動画で映像が遅れていく<br>
    [777](https://www.youtube.com/watch?v=xHuXXaXmStk)など動きの激しい動画で、フレームスキップ率が高いことに起因してか映像が遅れていきます。<br>
    今のところどうしようもないです。その動画で-nオプションを使わないでください。<br>
・(-nオプション無しでも)一部の動画を再生すると映像が音声から遅れていく<br>
　　同じ動画をwebmからmp4に変換したものでも発生します。<br>
    条件が謎すぎるため対応予定はありません。原因に気づけたら直します。<br>
・音がなんかおかしい気がする<br>
    最近のコミットで、moviepyがコード変えてないのにエラー吐くようになったのでsounddeviceに切り替えました。<br>
    そのせいかもしれません。それか作業途中でヘッドホン変えたから変わって聞こえるだけなのか...
