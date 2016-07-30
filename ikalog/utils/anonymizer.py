#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2015 Takeshi HASEGAWA
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import cv2
import numpy as np


def is_entry_me(entry_img):
    # ヒストグラムから、入力エントリが自分かを判断
    me_img = entry_img[:, 0:43]

    me_score = np.sum(me_img)
    me_score_normalized = 0
    try:
        me_score_normalized = me_score / (43 * 45 * 255 / 10)
    except ZeroDivisionError as e:
        me_score_normalized = 0

    return (me_score_normalized > 1)


def anonymize(img,
              anonWinTeam=False,
              anonLoseTeam=False,
              anonMyTeam=False,
              anonCounterTeam=False,
              anonMe=False,
              anonOthers=False,
              anonAll=False):

    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, thresh1 = cv2.threshold(img_gray, 230, 255, cv2.THRESH_BINARY)

    # 各プレイヤー情報のスタート左位置
    entry_left = 610
    # 各プレイヤー情報の横幅
    entry_width = 610
    # 各プレイヤー情報の高さ
    entry_height = 45

    # 各エントリ内での名前スタート位置と長さ
    entry_xoffset_name = 809 - entry_left
    entry_xoffset_name_me = 770 - entry_left
    entry_width_name = 180

    entry_xoffset_nawabari_score = 995 - entry_left
    entry_width_nawabari_score = 115
    entry_top = [101, 167, 231, 296, 432, 496, 562, 627]

    entry_xoffset_kd = 1187 - entry_left
    entry_width_kd = 30
    entry_height_kd = 20

    entry_id = 0

    # 自分を探す
    me = 0
    myteam = 0
    for top in entry_top:
        entry_id = entry_id + 1
        img_entry = thresh1[top:top + entry_height,
                            entry_left:entry_left + entry_width]
        if (is_entry_me(img_entry)):
            me = entry_id
            myteam = 1 if entry_id < 5 else 2

    entry_id = 0
    entries = []

    anonymized = img.copy()

    for top in entry_top:
        entry_id = entry_id + 1
        team = 1 if entry_id < 5 else 2
        anon = anonAll or \
            (anonWinTeam and (team == 1)) or \
            (anonLoseTeam and (team == 2)) or \
            (anonMyTeam and (team == myteam)) or \
            (anonCounterTeam and (team != myteam)) or \
            (anonMe and (entry_id == me)) or \
            (anonOthers and (entry_id != me))

        if anon:
            img_entry = thresh1[top:top + entry_height,
                                entry_left:entry_left + entry_width]
            name_left = entry_xoffset_name_me if entry_id == me else entry_xoffset_name
            anon_top = top
            anon_bottom = top + entry_height
            anon_left = entry_left + name_left
            anon_right = entry_left + name_left + entry_width_name

            img_smallName = cv2.resize(anonymized[anon_top:anon_bottom, anon_left:anon_right], (int(
                entry_width_name / 4), int(entry_height / 4)))
            anonymized[anon_top:anon_bottom, anon_left:anon_right] = cv2.resize(
                img_smallName, (entry_width_name, entry_height), interpolation=cv2.INTER_NEAREST)

    return anonymized
