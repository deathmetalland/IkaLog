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

#  Unit test for ikautils.
#  Usage:
#    python ./test_ikautils.py
#  or
#    py.test ./test_ikautils.py

import unittest
import os.path
import sys
import time

# Append the Ikalog root dir to sys.path to import IkaUtils.
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from ikalog.utils import IkaUtils

class TestIkaUtils(unittest.TestCase):

    #
    # Test Cases
    #
    def test_get_path(self):
        self.assertTrue(os.path.isfile(IkaUtils.get_path('IkaLog.py')))
        self.assertTrue(os.path.isdir(IkaUtils.get_path('test')))
        self.assertTrue(os.path.isdir(IkaUtils.get_path()))
        self.assertEqual(os.path.abspath(__file__),
                         IkaUtils.get_path('test', 'utils', 'test_ikautils.py'))

        if IkaUtils.isWindows():
            pass
            # TODO: add test cases
        else:
            abspath = '/tmp/test/dir'
            self.assertEqual(abspath, IkaUtils.get_path(abspath))


    def test_getMyEntryFromContext(self):
        context = {'game': {}}
        self.assertIsNone(IkaUtils.getMyEntryFromContext(context))

        context['game']['players'] = [
            {'me': False, 'team': 1, 'rank_in_team': 1},
            {'me': False, 'team': 1, 'rank_in_team': 2},
            {'me': False, 'team': 2, 'rank_in_team': 1},
            {'me': False, 'team': 2, 'rank_in_team': 2},
        ]
        self.assertIsNone(IkaUtils.getMyEntryFromContext(context))

        context['game']['players'][2]['me'] = True
        me = IkaUtils.getMyEntryFromContext(context)
        self.assertEqual(2, me['team'])
        self.assertEqual(1, me['rank_in_team'])


    def test_extend_languages(self):
        # Default languages
        self.assertIsNotNone(IkaUtils.extend_languages(None))

        # The specified language(s) should be in the beginning.
        # 'en' and 'ja' as fallback languages should also exist.
        languages = IkaUtils.extend_languages('??')
        self.assertEqual('??', languages[0])
        self.assertTrue('en' in languages)
        self.assertTrue('ja' in languages)

        # Input can be a list.
        languages = IkaUtils.extend_languages(['ja', 'fr'])
        self.assertEqual('ja', languages[0])
        self.assertEqual('fr', languages[1])
        self.assertTrue('en' in languages)
        self.assertTrue('ja' in languages)


    def test_map2text(self):
        map_id = 'shottsuru'

        # English
        self.assertEqual('Piranha Pit',
                         IkaUtils.map2text(map_id, languages='en'))

        # Japanese
        self.assertEqual('ショッツル鉱山',
                         IkaUtils.map2text(map_id, languages='ja'))

        # Fallback to English
        self.assertEqual('Piranha Pit',
                         IkaUtils.map2text(map_id, languages='??'))

        # Multiple languages
        self.assertEqual('ショッツル鉱山',
                         IkaUtils.map2text(map_id, languages=['ja', 'en']))

        # Unkonwn
        unknown_map_id = 'unknown'
        self.assertEqual('?', IkaUtils.map2text(unknown_map_id))
        self.assertEqual('<:=',
                         IkaUtils.map2text(unknown_map_id, unknown='<:='))


    def test_rule2text(self):
        rule_id = 'area'

        # English
        self.assertEqual('Splat Zones',
                         IkaUtils.rule2text(rule_id, languages='en'))

        # Japanese
        self.assertEqual('ガチエリア',
                         IkaUtils.rule2text(rule_id, languages='ja'))

        # Fallback to English
        self.assertEqual('Splat Zones',
                         IkaUtils.rule2text(rule_id, languages='??'))

        # Multiple languages
        self.assertEqual('ガチエリア',
                         IkaUtils.rule2text(rule_id, languages=['ja', 'en']))

        # Unkonwn
        unknown_rule_id = 'unknown'
        self.assertEqual('?', IkaUtils.rule2text(unknown_rule_id))
        self.assertEqual('<:=',
                         IkaUtils.rule2text(unknown_rule_id, unknown='<:='))


    def test_gear_ability2text(self):
        gear = 'ninja_squid'

        # English
        self.assertEqual('Ninja Squid',
                         IkaUtils.gear_ability2text(gear, languages='en'))

        # Japanese
        self.assertEqual('イカニンジャ',
                         IkaUtils.gear_ability2text(gear, languages='ja'))

        # Fallback to English
        self.assertEqual('Ninja Squid',
                         IkaUtils.gear_ability2text(gear, languages='??'))

        # Multiple languages
        self.assertEqual('イカニンジャ',
                         IkaUtils.gear_ability2text(gear,
                                                    languages=['ja', 'en']))

        # Unkonwn
        unknown_gear = 'unknown'
        self.assertEqual('?', IkaUtils.gear_ability2text(unknown_gear))
        self.assertEqual('<:=',
                         IkaUtils.gear_ability2text(unknown_gear,
                                                    unknown='<:='))


    def test_weapon2text(self):
        ### Weapons
        weapon = 'bamboo14mk3'

        # English
        self.assertEqual('Bamboozler 14 Mk III',
                         IkaUtils.weapon2text(weapon, languages='en'))

        # Japanese
        self.assertEqual('14式竹筒銃・丙',
                         IkaUtils.weapon2text(weapon, languages='ja'))

        # Fallback to English
        self.assertEqual('Bamboozler 14 Mk III',
                         IkaUtils.weapon2text(weapon, languages='??'))

        # Multiple languages
        self.assertEqual('14式竹筒銃・丙',
                         IkaUtils.weapon2text(weapon, languages=['ja', 'en']))

        ### Invalid weapons
        weapon = 'kyubanbomb'  # Suction Bomb
        self.assertEqual('?', IkaUtils.weapon2text(weapon, languages='en'))
        self.assertEqual('?', IkaUtils.weapon2text(weapon, languages='ja'))

        ### Unkonwn
        unknown_weapon = 'unknown'
        self.assertEqual('?', IkaUtils.weapon2text(unknown_weapon))
        self.assertEqual('<:=',
                         IkaUtils.weapon2text(unknown_weapon, unknown='<:='))


    def test_death_reason2text(self):
        ### Weapons
        reason = 'hokusai'

        # English
        self.assertEqual('Octobrush',
                         IkaUtils.death_reason2text(reason, languages='en'))

        # Japanese
        self.assertEqual('ホクサイ',
                         IkaUtils.death_reason2text(reason, languages='ja'))

        # Fallback to English
        self.assertEqual('Octobrush',
                         IkaUtils.death_reason2text(reason, languages='??'))

        # Multiple languages
        self.assertEqual('ホクサイ',
                         IkaUtils.death_reason2text(reason,
                                                    languages=['ja', 'en']))

        ### Sub weapons
        reason = 'trap'
        self.assertEqual('Ink Mine',
                         IkaUtils.death_reason2text(reason, languages='en'))
        self.assertEqual('トラップ',
                         IkaUtils.death_reason2text(reason, languages='ja'))

        ### Special weapons
        reason = 'daioika'
        self.assertEqual('Kraken',
                         IkaUtils.death_reason2text(reason, languages='en'))
        self.assertEqual('ダイオウイカ',
                         IkaUtils.death_reason2text(reason, languages='ja'))

        ### Hurtable objects
        reason = 'hoko_shot'
        self.assertEqual('Rainmaker Shot',
                         IkaUtils.death_reason2text(reason, languages='en'))
        self.assertEqual('ガチホコショット',
                         IkaUtils.death_reason2text(reason, languages='ja'))

        ### OOB reasons
        reason = 'oob'
        self.assertEqual('Out of Bounds',
                         IkaUtils.death_reason2text(reason, languages='en'))
        self.assertEqual('場外',
                         IkaUtils.death_reason2text(reason, languages='ja'))

        ### Unkonwn
        unknown_reason = 'unknown'
        self.assertEqual('?', IkaUtils.death_reason2text(unknown_reason))
        self.assertEqual('<:=',
                         IkaUtils.death_reason2text(unknown_reason,
                                                    unknown='<:='))


    def test_lobby2text(self):
        lobby = 'tag'

        # English
        self.assertEqual('Squad Battle',
                         IkaUtils.lobby2text(lobby, languages='en'))

        # Japanese
        self.assertEqual('タッグマッチ',
                         IkaUtils.lobby2text(lobby, languages='ja'))

        # Fallback to English
        self.assertEqual('Squad Battle',
                         IkaUtils.lobby2text(lobby, languages='??'))

        # Multiple languages
        self.assertEqual('タッグマッチ',
                         IkaUtils.lobby2text(lobby, languages=['ja', 'en']))

        ### Invalid lobby type
        lobby = 'nawabari'  # Turf War
        self.assertEqual('?', IkaUtils.lobby2text(lobby, languages='en'))
        self.assertEqual('?', IkaUtils.lobby2text(lobby, languages='ja'))

        ### Unkonwn
        unknown_lobby = 'unknown'
        self.assertEqual('?', IkaUtils.lobby2text(unknown_lobby))
        self.assertEqual('<:=',
                         IkaUtils.lobby2text(unknown_lobby, unknown='<:='))


    def test_get_time(self):
        mock_context = {'engine': {'epoch_time': None, 'msec': 5000}}

        # epoch_time is None
        time_before = time.time()
        time_actual = IkaUtils.getTime(mock_context)
        time_after = time.time()
        self.assertTrue(time_before <= time_actual <= time_after)

        # epoch_time is 0
        mock_context['engine']['epoch_time'] = 0
        expected_time = (mock_context['engine']['epoch_time'] +
                         mock_context['engine']['msec'] / 1000.0)
        self.assertEqual(expected_time, IkaUtils.getTime(mock_context))

        # epoch_time is 2015-05-28 10:00:00, msec is 1 hour
        mock_context['engine']['epoch_time'] = (
            time.mktime(time.strptime("20150528_100000", "%Y%m%d_%H%M%S")))
        mock_context['engine']['msec'] = 60 * 60 * 1000
        time_actual = IkaUtils.getTime(mock_context)
        self.assertEqual("20150528_110000",
                         time.strftime("%Y%m%d_%H%M%S",
                                       time.localtime(time_actual)))

    def test_get_game_offset_msec(self):
        mock_context = {'game': {}, 'engine': {}}
        self.assertIsNone(IkaUtils.get_game_offset_msec(mock_context))
        mock_context['engine']['msec'] = 1234567
        self.assertIsNone(IkaUtils.get_game_offset_msec(mock_context))
        mock_context['game']['start_offset_msec'] = 1000000
        self.assertEqual(234567, IkaUtils.get_game_offset_msec(mock_context))

    def test_add_event(self):
        mock_context = {'game': {'start_offset_msec': 100},
                        'engine': {'msec': 101}}
        IkaUtils.add_event(mock_context, 'key', 7)
        self.assertEqual({'key': [[1, 7]]}, mock_context['game']['events'])
        IkaUtils.add_event(mock_context, 'key', 11)
        self.assertEqual({'key': [[1, 11]]}, mock_context['game']['events'])
        IkaUtils.add_event(mock_context, 'key2', 13)
        self.assertEqual({'key': [[1, 11]], 'key2': [[1, 13]]},
                         mock_context['game']['events'])

        mock_context['engine']['msec'] = 102
        IkaUtils.add_event(mock_context, 'key', 7)
        self.assertEqual({'key': [[1, 11], [2, 7]], 'key2': [[1, 13]]},
                         mock_context['game']['events'])

    def test_get_file_name(self):
        mock_context = {'game': {'index': 0},
                        'engine': {'source_file': None}}

        self.assertIsNone(IkaUtils.get_file_name(None, mock_context))
        self.assertEqual('/tmp/statink.msgpack',
                         IkaUtils.get_file_name('/tmp/statink.msgpack',
                                                mock_context))
        mock_context['game']['index'] = 1
        self.assertEqual('/tmp/statink-1.msgpack',
                         IkaUtils.get_file_name('/tmp/statink.msgpack',
                                                mock_context))
        mock_context['game']['index'] = 10
        self.assertEqual('/tmp/statink-10.msgpack',
                         IkaUtils.get_file_name('/tmp/statink.msgpack',
                                                mock_context))
        mock_context['game']['index'] = 1
        self.assertEqual('/tmp/video.mp4-1.statink',
                         IkaUtils.get_file_name('/tmp/video.mp4.statink',
                                                mock_context))

        self.assertEqual('/tmp/video.mp4-1.statink',
                         IkaUtils.get_file_name('/tmp/video.mp4.statink',
                                                mock_context))

        mock_context['engine']['source_file'] = None
        mock_context['game']['index'] = 0
        self.assertEqual('__INPUT_FILE__.statink',
                         IkaUtils.get_file_name('__INPUT_FILE__.statink',
                                                mock_context))

        mock_context['engine']['source_file'] = None
        mock_context['game']['index'] = 2
        self.assertEqual('__INPUT_FILE__-2.statink',
                         IkaUtils.get_file_name('__INPUT_FILE__.statink',
                                                mock_context))

        mock_context['engine']['source_file'] = '/tmp/video.mp4'
        mock_context['game']['index'] = 0
        self.assertEqual('/tmp/video.mp4.statink',
                         IkaUtils.get_file_name('__INPUT_FILE__.statink',
                                                mock_context))

        mock_context['engine']['source_file'] = '/tmp/video.mp4'
        mock_context['game']['index'] = 3
        self.assertEqual('/tmp/video.mp4-3.statink',
                         IkaUtils.get_file_name('__INPUT_FILE__.statink',
                                                mock_context))

    def test_copy_context(self):
        mock_context = {
            'engine': {
                'engine': self,
                'source_file': 'video.mp4',
                'service': {'call_plugins_later': self.test_copy_context},
            },
            'game': {
                'map': 'kinmedai',
                'rule': 'area',
            }}

        copied_context = IkaUtils.copy_context(mock_context)
        copied_context['engine']['source_file'] = 'movie.ts'
        copied_context['game']['map'] = 'hokke'
        copied_context['game']['rule'] = 'nawabari'
        self.assertEqual('video.mp4', mock_context['engine']['source_file'])
        self.assertEqual('movie.ts', copied_context['engine']['source_file'])

        self.assertIsNotNone(mock_context['engine']['engine'])
        self.assertIsNotNone(
            mock_context['engine']['service'].get('call_plugins_later'))
        self.assertEqual('kinmedai', mock_context['game']['map'])
        self.assertEqual('area', mock_context['game']['rule'])

        self.assertIsNone(copied_context['engine']['engine'])
        self.assertIsNone(
            copied_context['engine']['service'].get('call_plugins_later'))
        self.assertEqual('hokke', copied_context['game']['map'])
        self.assertEqual('nawabari', copied_context['game']['rule'])

if __name__ == '__main__':
    unittest.main()
