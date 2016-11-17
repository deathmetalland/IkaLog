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
from __future__ import print_function

import copy
import os
import platform
import re
import sys
import time
from datetime import datetime

from PIL import Image

from ikalog.constants import stages, rules, gear_abilities, lobby_types
# Constants for death_reason2text
from ikalog.constants import hurtable_objects, oob_reasons, special_weapons, sub_weapons, weapons
from ikalog.utils.localization import Localization
from ikalog.utils import imread

class IkaUtils(object):

    @staticmethod
    def isWindows():
        return platform.system() == 'Windows'

    @staticmethod
    def isOSX():
        return platform.system() == 'Darwin'

    @staticmethod
    def dprint(text):
        print(text, file=sys.stderr)

    @staticmethod
    def get_path(*dirs):
        '''Returns the path prepended the top dir and appened subdirs.'''
        path = ''
        if dirs:
            path = os.path.join(*dirs)
            if os.path.isabs(path):
                return path

        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        base_dir = re.sub('[\\/]+$', '', base_dir)

        if os.path.isfile(base_dir):
            # In this case, this version of IkaLog is py2exe'd,
            # and base_dir is still pointing at the executable.
            base_dir = os.path.dirname(base_dir)

        return os.path.abspath(os.path.join(base_dir, path))

    # Find the local player.
    #
    # @param context   IkaLog Context.
    # @return The player information (Directionary class) if found.
    @staticmethod
    def getMyEntryFromContext(context):
        if not context['game'].get('players'):
            return None
        for e in context['game']['players']:
            if e['me']:
                return e
        return None

    # Get player's title.
    #
    # @param playerEntry The player.
    # @return Title in string. Returns None if playerEntry doesn't have title data.
    @staticmethod
    def playerTitle(playerEntry):
        if playerEntry is None:
            return None

        if not (('gender' in playerEntry) and ('prefix' in playerEntry)):
            return None

        prefix = re.sub('の', '', playerEntry['prefix'])
        return "%s%s" % (prefix, playerEntry['gender'])

    @staticmethod
    def extend_languages(languages=None):
        if languages is None:
            languages = Localization.get_languages()

        if not isinstance(languages, list):
            languages = [languages]

        # fallback list
        languages.extend(['en', 'ja'])
        return languages

    @staticmethod
    def map2text(map_id, unknown='?', languages=None):
        if map_id is None:
            return unknown

        if stages.get(map_id, None) is None:
            return unknown

        for lang in IkaUtils.extend_languages(languages):
            map_text = stages[map_id].get(lang, None)
            if map_text is not None:
                return map_text

        # Should not reach here
        return map_id

    @staticmethod
    def rule2text(rule_id, unknown='?', languages=None):
        if rule_id is None:
            return unknown

        if rules.get(rule_id, None) is None:
            return unknown

        for lang in IkaUtils.extend_languages(languages):
            rule_text = rules[rule_id].get(lang, None)
            if rule_text is not None:
                return rule_text

        # Should not reach here
        return rule_id

    @staticmethod
    def gear_ability2text(gear_ability, unknown='?', languages=None):
        if gear_ability is None:
            return unknown

        if gear_abilities.get(gear_ability, None) is None:
            return unknown

        for lang in IkaUtils.extend_languages(languages):
            gear_ability_text = gear_abilities[gear_ability].get(lang, None)
            if gear_ability_text is not None:
                return gear_ability_text

        # Should not reach here
        return gear_ability_id

    @staticmethod
    def weapon2text(weapon_id, unknown='?', languages=None):
        weapon_dict = {}
        if weapon_id in weapons:
            weapon_dict = weapons[weapon_id]

        for lang in IkaUtils.extend_languages(languages):
            if lang in weapon_dict:
                return weapon_dict[lang]

        return unknown

    @staticmethod
    def death_reason2text(reason, unknown='?', languages=None):
        reason_dict = {}
        if reason in weapons:
            reason_dict = weapons[reason]
        if reason in sub_weapons:
            reason_dict = sub_weapons[reason]
        if reason in special_weapons:
            reason_dict = special_weapons[reason]
        if reason in oob_reasons:
            reason_dict = oob_reasons[reason]
        if reason in hurtable_objects:
            reason_dict = hurtable_objects[reason]

        for lang in IkaUtils.extend_languages(languages):
            if lang in reason_dict:
                return reason_dict[lang]

        return unknown

    @staticmethod
    def lobby2text(lobby_type, unknown='?', languages=None):
        lobby_dict = {}
        if lobby_type in lobby_types:
            lobby_dict = lobby_types[lobby_type]

        for lang in IkaUtils.extend_languages(languages):
            if lang in lobby_dict:
                return lobby_dict[lang]

        return unknown

    @staticmethod
    def getWinLoseText(won, win_text="勝ち", lose_text="負け", unknown_text="不明"):
        if won is None:
            return unknown_text
        return win_text if won else lose_text

    @staticmethod
    def writeScreenshot(destfile, img):
        img_pil = Image.fromarray(img[:, :, ::-1])

        try:
            img_pil.save(destfile)
            assert os.path.isfile(destfile)
        except:
            IkaUtils.dprint("Screenshot: failed")
            return False
        return True

    @staticmethod
    def getTime(context):
        """Returns the current time in sec considering the epoch time."""
        epoch_time = context['engine']['epoch_time']
        if epoch_time is None:
            return time.time()
        time_sec = context['engine']['msec'] / 1000.0
        return epoch_time + time_sec

    @staticmethod
    def get_end_time(context):
        unix_time = context['game'].get('end_time')
        if unix_time:
            return datetime.fromtimestamp(unix_time)
        else:
            return datetime.now()

    @staticmethod
    def get_game_offset_msec(context):
        """Returns the offset time in msec since the game start."""
        if (context['engine'].get('msec') and
            context['game'].get('start_offset_msec')):
            return (context['engine']['msec'] -
                    context['game']['start_offset_msec'])
        return None

    @staticmethod
    def add_event(context, key, value):
        events = context['game'].setdefault('events', {}).setdefault(key, [])
        game_time = IkaUtils.get_game_offset_msec(context)

        # events is a list of lists of [time, value].
        if events and events[-1][0] == game_time:
            event = events[-1]
            event[1] = value
        else:
            event = [game_time, value]
            events.append(event)

    @staticmethod
    def get_file_name(filename, context):
        """Returns filename modifying index and macro values."""
        if not filename:
            return filename

        source_file = context['engine']['source_file']
        filename = filename.replace('__INPUT_FILE__',
                                    (source_file or '__INPUT_FILE__'))

        index = context['game']['index']
        if index == 0:
            return filename

        base, ext = os.path.splitext(filename)
        return '%s-%d%s' % (base, index, ext)

    @staticmethod
    def copy_context(context):
        """Copies context as deep copy without Python objects."""
        context2 = context.copy()  # shallow copy
        context2['engine'] = context['engine'].copy()  # shallow copy
        # Because some Python objects cannot be copied as deepcopy,
        # these values are replaced with None before deepcopy.
        context2['engine']['engine'] = None  # IkaEngine
        context2['engine']['service'] = {}  # functions of IkaEngine
        return copy.deepcopy(context2)
