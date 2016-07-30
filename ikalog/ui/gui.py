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

import gettext
import os
import threading
import time

import wx
import yaml

from ikalog.ui.events import *
from ikalog.ui.options import *
from ikalog.ui.panel import *
from ikalog.utils import *

_ = Localization.gettext_translation('IkaUI', fallback=True).gettext

class IkaLogGUI(object):
    def on_next_frame(self, context):
        # This IkaEngine thread a bit, so that GUI thread can process events.
        time.sleep(0.01)

    # wx event
    def on_options_apply(self, event):
        '''Applies the current changes, and saves them to the file.'''
        self.engine.call_plugins('on_config_apply', debug=True)
        self.engine.call_plugins('on_config_save_to_context', debug=True)
        self.save_current_config(self.engine.context)

    # wx event
    def on_options_cancel(self, event):
        '''Cancels the current changes, and reloads the saved changes.'''
        self.engine.call_plugins('on_config_load_from_context', debug=True)

    # wx event
    def on_options_load_default(self, event):
        '''Resets the changes to the default, but not save them.'''
        r = wx.MessageDialog(
            None,
            _('IkaLog preferences will be reset to default. Continue?') + '\n' +
            _('The change will be updated when the apply button is pressed.'),
            _('Confirm'),
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION
        ).ShowModal()

        if r != wx.ID_YES:
            return

        self.engine.call_plugins('on_config_reset', debug=True)

    # 現在の設定値をYAMLファイルからインポート
    #
    def load_config(self, context, filename='IkaConfig.yaml'):
        try:
            yaml_file = open(filename, 'r')
            self.engine.context['config'] = yaml.load(yaml_file)
            yaml_file.close()
            self.engine.call_plugins('on_config_load_from_context', debug=True)
        except:
            pass

    # 現在の設定値をYAMLファイルにエクスポート
    #
    def save_current_config(self, context, filename='IkaConfig.yaml'):
        yaml_file = open(filename, 'w')
        yaml_file.write(yaml.dump(context['config']))
        yaml_file.close()

    def on_switch_panel(self, event):
        active_button = event.GetEventObject()
        self.switch_to_panel(active_button)

    def on_button_results(self, event):
        self.last_result.show()

    def on_click_button_options(self, event):
        self.options_gui.show()

    def on_ikalog_pause(self, event):
        self.engine.pause(event.pause)
        # Propagate the event as the top level event.
        wx.PostEvent(self.frame, event)

    def on_close(self, event):
        self.engine.stop()
        while self.engine_thread.is_alive():
            time.sleep(0.5)
        self.frame.Destroy()

    def on_input_file_added(self, event):
        input_file = event.input_file
        if input_file in self._file_list:
            wx.MessageBox(_('Already added.'), _('Error'))
            return
        self._file_list.append(input_file)
        self.engine.put_source_file(event.input_file)

    def on_input_initialized(self, event):
        self.engine.reset_capture()
        # Propagate the event as the top level event.
        wx.PostEvent(self.frame, event)

    def create_buttons_ui(self):
        panel = self.frame
        self.button_last_result = wx.Button(panel, wx.ID_ANY, _('Last Result'))
        self.button_options = wx.Button(panel, wx.ID_ANY, _('Options'))

        self.buttons_layout = wx.BoxSizer(wx.HORIZONTAL)
        self.buttons_layout.Add(self.button_last_result)
        self.buttons_layout.Add(self.button_options)

        self.button_last_result.Bind(wx.EVT_BUTTON, self.on_button_results)
        self.button_options.Bind(wx.EVT_BUTTON, self.on_click_button_options)

    def engine_thread_func(self):
        IkaUtils.dprint('IkaEngine thread started')
        self.engine.pause(False)
        self.engine.run()
        IkaUtils.dprint('IkaEngine thread terminated')

    def run(self):
        self.engine_thread = threading.Thread(target=self.engine_thread_func)
        self.engine_thread.daemon = True
        self.engine_thread.start()

        self.load_config(self.engine.context)

        self.frame.Show()

    def __init__(self, engine, outputs):
        self.engine = engine
        self.capture = engine.capture
        self.outputs = outputs
        self.frame = wx.Frame(None, wx.ID_ANY, "IkaLog GUI", size=(700, 500))
        self.options_gui = OptionsGUI(self)
        self.last_result = ResultsGUI(self)

        self.layout = wx.BoxSizer(wx.VERTICAL)

        self.create_buttons_ui()
        self.layout.Add(self.buttons_layout)

        self.preview = PreviewPanel(self.frame, size=(640, 420))
        self.preview.Bind(EVT_INPUT_FILE_ADDED, self.on_input_file_added)
        self.preview.Bind(EVT_IKALOG_PAUSE, self.on_ikalog_pause)

        self.layout.Add(self.preview, flag=wx.EXPAND)
        self.frame.SetSizer(self.layout)

        # Frame events
        self.frame.Bind(wx.EVT_CLOSE, self.on_close)

        # Video files processed and to be processed.
        self._file_list = []
