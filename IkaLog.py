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

import numpy as np
import cv2
import time

from IkaScene_GameStart import *
from IkaScene_ResultDetail import *
from IkaScene_TowerTracker import *
from IkaScene_InGame import *
from IkaConfig import *

capture, OutputPlugins = IkaConfig().config()

def core():
	context = {
		"game": {
			'map': None,
			'rule': None,
			'livesTrack': [],
			'towerTrack': [],
		},
		"engine": {
			'frame': None,
		}
	}

	last_capture = time.time() - 100;
	last_gamestart = time.time() - 100;

	scn_gamestart = IkaScene_GameStart()
	scn_gameresult = IkaScene_ResultDetail()
	scn_ingame = IkaScene_InGame()
	scn_towerTracker = IkaScene_TowerTracker()

	while True:
		# 0.5フレームおきに処理
		for i in range(12):
			frame = capture.read()

		while frame is None:
			cv2.waitKey(1000)
			frame = capture.read()

		context['engine']['frame'] = frame
		context['engine']['inGame'] = scn_ingame.matchTimerIcon(context)

		for op in OutputPlugins:
			if hasattr(op, "onFrameRead"):
				try:
					op.onFrameRead(context)
				except:
					pass

		if context['engine']['inGame']:
			tower_data = scn_towerTracker.match(context)

			try:
				# ライフをチェック
				(team1, team2) = scn_ingame.lives(context)
				# print("味方 %s 敵 %s" % (team1, team2))

				context['game']['livesTrack'].append([team1, team2])
				if tower_data:
					context['game']['towerTrack'].append(tower_data.copy())
			except:
				pass

		# GameStart (マップ名、ルール名が表示されている) ?

		r = None
		if (not context['engine']['inGame']) and (time.time() - last_gamestart) > 10:
			r = scn_gamestart.match(context)

		if r:
			context["game"] =  {
				'map': None,
				'rule': None,
				'livesTrack': [],
				'towerTrack': [],
			}
			scn_towerTracker.reset(context)

			while (r):
				frame = capture.read()
				frame = capture.read()
				frame = capture.read()
				context['engine']['frame'] = frame
				r = scn_gamestart.match(context)

			last_gamestart = time.time()	

			for op in OutputPlugins:
				if hasattr(op, "onGameStart"):
					op.onGameStart(context)
		
		# GameResult (勝敗の詳細が表示されている）?
		r = (not context['engine']['inGame']) and (time.time() - last_capture) > 60
		if r:
			r = scn_gameresult.match(context)

		if r:
			if ((time.time() - last_capture) > 60):
				last_capture = time.time()	
				
				# 安定するまで待つ
				for x in range(10):
					new_frame = capture.read()
					if not (new_frame is None):
						frame = new_frame

				# 安定した画像で再度解析
				context['engine']['frame'] = frame
				scn_gameresult.analyze(context)

				for op in OutputPlugins:
					if hasattr(op, "onGameIndividualResultAnalyze"):
						try:
							op.onGameIndividualResultAnalyze(context)
						except:
							pass

				for op in OutputPlugins:
					if hasattr(op, "onGameIndividualResult"):
						try:
							op.onGameIndividualResult(context)
						except:
							pass

				for op in OutputPlugins:
					if hasattr(op, "onGameReset"):
						try:
							op.onGameReset(context)
						except:
							pass

				context['game']['map'] = None
				context['game']['rule'] = None
				context['game']['won'] = None
				context['game']['players'] = None

		key = None

		for op in OutputPlugins:
			if hasattr(op, "onFrameNext"):
				try:
					key = op.onFrameNext(context)
				except:
					pass

		for op in OutputPlugins:
			if hasattr(op, "onKeyPress"):
				try:
					op.onKeyPress(context, key)
				except:
					pass

	# キャプチャを解放する
	#cap.release()
	cv2.destroyAllWindows()

core()
