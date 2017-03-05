#!/bin/sh

# ファイル名から時間の抽出
epoch_time=`basename "$1" .m4v | cut -c 12-22`
echo $epoch_time

# タイムスタンプを変更
touch -t $epoch_time "$1"

python upload_video.py \
--file="$1" \
--title="Splatoon" \
--description="私は、Nintendo Creators Programのライセンスによって、この動画で任天堂コンテンツを使用しています。この動画は、任天堂による援助や支援がなされているものではありませんが、この動画から得られる広告収益は任天堂と分け合われます。" \
--keywords="Splatoon" \
--privacyStatus="public" \
> upload_video.log

VIDEOID=`tail -n 1 upload_video.log`
/usr/local/bin/python3 IkaLog.py --input_file "$1" --video_id $VIDEOID
