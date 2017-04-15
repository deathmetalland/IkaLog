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

# @package IkaOutput_Mastodon

import os
import json

from ikalog.utils import *

from mastodon import Mastodon

_ = Localization.gettext_translation('mastodon', fallback=True).gettext

# IkaOutput_Mastodon: IkaLog Output Plugin for Mastodon
#
# Toot Splatton game events.


class Mastodon(object):

    last_me = None

    def config_reset(self):
        self.enabled = False
        self.attach_image = False
        self.tweet_kd = False
        self.tweet_my_score = False
        self.tweet_udemae = False
        self.use_reply = True
        self.client_id = ''
        self.access_token = ''
        self.footer = ''

    def on_config_save_to_context(self, context):
        context['config']['twitter'] = {
            'Enable': self.enabled,
            'AttachImage': self.attach_image,
            'TweetMyScore': self.tweet_my_score,
            'TweetKd': self.tweet_kd,
            'TweetUdemae': self.tweet_udemae,
            'UseReply': self.use_reply,
            'ClientId': self.client_id,
            'AccessToken': self.access_token,
            'Footer': self.footer,
        }

    ##
    # Post a toot
    # @param self    The object pointer.
    # @param s       Text to toot
    #
    def toot(self, s):
        mastodon = Mastodon(
            client_id = self.client_id,
            access_token = self.access_token
        )
        return mastodon.toot(s)

    ##
    # get_text_game_individual_result
    # Generate a record for on_game_individual_result.
    # @param self      The Object Pointer.
    # @param context   IkaLog context
    #
    def get_text_game_individual_result(self, context):
        stage = IkaUtils.map2text(context['game']['map'], unknown=_('unknown stage'))
        rule = IkaUtils.rule2text(context['game']['rule'], unknown=_('unknown rule'))

        result = IkaUtils.getWinLoseText(
            context['game']['won'], win_text=_('won'),
            lose_text=_('lost'),
            unknown_text=_('played'))

        t = IkaUtils.get_end_time(context).strftime("%Y/%m/%d %H:%M")

        s = _('Just %(result)s %(rule)s at %(stage)s') % \
            { 'stage': stage, 'rule': rule, 'result': result}

        me = IkaUtils.getMyEntryFromContext(context)

        if ('score' in me) and self.tweet_my_score:
            s = s + ' %sp' % (me['score'])

        if ('kills' in me) and ('deaths' in me) and self.tweet_kd:
            s = s + ' %dk/%dd' % (me['kills'], me['deaths'])

        if ('udemae_pre' in me) and self.tweet_udemae:
            s = s + _(' Rank: %s') % (me['udemae_pre'])

        fes_title = IkaUtils.playerTitle(me)
        if fes_title:
            s = s + ' %s' % (fes_title)

        s = s + ' (%s) %s #IkaLogResult' % (t, self.footer)

        if self.use_reply:
            s = '@_ikalog_ ' + s

        return s

    ##
    # on_result_detail_still Hook
    # @param self      The Object Pointer
    # @param context   IkaLog context
    #
    def on_result_detail_still(self, context):
        self.img_result_detail = context['game']['image_scoreboard']

    def on_game_session_end(self, context):
        IkaUtils.dprint('%s (enabled = %s)' % (self, self.enabled))

        if not self.enabled:
            return False

        if self.img_result_detail is None:
            return False

        s = self.get_text_game_individual_result(context)
        IkaUtils.dprint('Toot: %s' % s)

        self.toot(s)

        self.img_result_detail = None

    ##
    # Constructor
    # @param self              The Object Pointer.
    # @param client_id         Client ID of the application.
    # @param access_token      Authentication token of the user account.
    # @param attach_image      If true, post screenshots.
    # @param footer            Footer text.
    # @param tweet_my_score    If true, post score.
    # @param tweet_kd          If true, post killed/death.
    # @param tweet_udemae      If true, post udemae(rank).
    # @param use_reply         If true, post the tweet as a reply to @_ikalog_
    #
    def __init__(self, client_id=None, access_token=None, attach_image=False, footer='', tweet_my_score=False, tweet_kd=False, tweet_udemae=False, use_reply=True):
        self.enabled = not((client_id is None) or (access_token is None))
        self.consumer_key_type = 'own'
        self.client_id = client_id
        self.access_token = access_token
        self.attach_image = attach_image
        self.tweet_my_score = tweet_my_score
        self.tweet_kd = tweet_kd
        self.tweet_udemae = tweet_udemae
        self.use_reply = use_reply
        self.footer = footer

        self.img_result_detail = None

if __name__ == "__main__":
    import sys
    obj = Mastodon(
        client_id=sys.argv[1],
        access_token=sys.argv[2],
    )
    print(obj.get_text_game_individual_result({
        "game": {
            "map": {"name": "map_name"},
            "rule": {"name": "rule_name"},
            "won": True, }}))
    obj.toot('Staaaay Fresh!')
