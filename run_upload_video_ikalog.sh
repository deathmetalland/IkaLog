#!/bin/sh

# ファイル名から時間の抽出
# この時間は動画ファイル作成時間だからここからプレイ時間を減算すれば録画開始時間になるか？
#HH=`basename "$1" .mov | cut -c 19-20`
#mm=`basename "$1" .mov | cut -c 21-22`
#echo $HH:$mm

python upload_video.py --file="$1" --title="Splatoon" --privacyStatus="public" > upload_video.log
VIDEOID=`tail -n 1 upload_video.log`
/usr/local/bin/python3 IkaLog.py --input_file "$1" --video_id $VIDEOID
