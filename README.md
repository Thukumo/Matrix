# Matrix
Matrixのあれ(ターミナルを流れ落ちる文字で映像を表現)<br>
を作ろうとして挫折したものです。<br>
動画・カメラの映像をリアルタイムでAAに変換しターミナルに出力します。<br>
まだ色々とアレな感じですが一応置いておきます
# 準備
```
pip install -r requirements.txt
```
# 実行
カメラの映像を出力させたい場合
```
python matrix.py
```
動画ファイル(mp4に対応)を再生したい場合
```
python matrix.py {動画ファイルのパス}
```
# 既知の不具合
~~・映像と音がズレる~~<br>
https://github.com/Thukumo/Matrix/commit/5d2ff69dafd740740dcc4d04fd7616b3d8e04333 でだいぶましになったかも<br>
・映像の最後数十フレームくらいが描画されない<br>
・フレームスキップがあんまり仕事しない<br>
