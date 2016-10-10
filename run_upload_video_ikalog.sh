#!/bin/sh

# ファイル名から時間の抽出
epoch_time=`basename "$1" .m4v | cut -c 12-22`
echo $epoch_time

# タイムスタンプを変更
touch -t $epoch_time "$1"

python upload_video.py --file="$1" --title="Splatoon" --privacyStatus="public" > upload_video.log
VIDEOID=`tail -n 1 upload_video.log`
/usr/local/bin/python3 IkaLog.py --input_file "$1" --video_id $VIDEOID
