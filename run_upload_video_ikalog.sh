#!/bin/sh
python upload_video.py --file="$1" --title="Splatoon" --privacyStatus="public" > upload_video.log
VIDEOID=`tail -n 1 upload_video.log`
/usr/local/bin/python3 IkaLog.py --input_file "$1" --video_id $VIDEOID
