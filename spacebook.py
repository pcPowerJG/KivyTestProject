# -*- coding: utf-8 -*-
#
# This file created with KivyCreatorProject
# <https://github.com/HeaTTheatR/KivyCreatorProgect
#
# Copyright (c) 2020 Ivanov Yuri and KivyMD
#
# For suggestions and questions:
# <kivydevelopment@gmail.com>
#
# LICENSE: MIT

import os
import sys
from ast import literal_eval

import os
import sys
from ast import literal_eval

from kivy.lang import Builder
from kivy.core.window import Window
from kivy.config import ConfigParser
PY2 = False # from kivy.logger import PY2
from kivy.clock import Clock
from kivy.utils import get_hex_from_color
from kivy.properties import ObjectProperty, StringProperty

from main import __version__
from libs.translation import Translation
from libs.uix.baseclass.startscreen import StartScreen
from libs.uix.lists import Lists

from kivymd.app import MDApp
from kivymd.toast import toast

from dialogs import card


class spacebook(MDApp):
    title = 'spacebook'
    icon  = 'data/images/icon.png'
    nav_drawer = ObjectProperty()
    lang = StringProperty('en')

    def __init__(self, **kvargs):
        super(spacebook, self).__init__(**kvargs)
        Window.bind(on_keyboard=self.events_program)
        Window.soft_input_mode = 'below_target'

        self.list_previous_screens = ['base']
        self.window = Window
        self.config = ConfigParser()
        self.manager = None
        self.window_language = None
        self.exit_interval = False
        self.dict_language = literal_eval(
            open(
                os.path.join(self.directory, 'data', 'locales', 'locales.txt')).read()
        )
        self.translation = Translation(
            self.lang, 'Ttest', os.path.join(self.directory, 'data', 'locales')
        )

    def get_application_config(self):
        return super(spacebook, self).get_application_config(
                        '{}/%(appname)s.ini'.format(self.directory))

    def build_config(self, config):
        config.adddefaultsection('General')
        config.setdefault('General', 'language', 'en')

    def set_value_from_config(self):
        self.config.read(os.path.join(self.directory, 'spacebook.ini'))
        self.lang = self.config.get('General', 'language')

    def build(self):
        self.set_value_from_config()
        self.load_all_kv_files(os.path.join(self.directory, 'libs', 'uix', 'kv'))
        self.screen = StartScreen()
        self.manager = self.screen.ids.manager
        self.nav_drawer = self.screen.ids.nav_drawer

        return self.screen

    def load_all_kv_files(self, directory_kv_files):
        for kv_file in os.listdir(directory_kv_files):
            kv_file = os.path.join(directory_kv_files, kv_file)
            if os.path.isfile(kv_file):
                if not PY2:
                    with open(kv_file, encoding='utf-8') as kv:
                        Builder.load_string(kv.read())
                else:
                    Builder.load_file(kv_file)

    def events_program(self, instance, keyboard, keycode, text, modifiers):
        if keyboard in (1001, 27):
            if self.nav_drawer.state == 'open':
                self.nav_drawer.set_state("toggle")
            self.back_screen(event=keyboard)
        elif keyboard in (282, 319):
            pass

        return True

    def back_screen(self, event=None):
        if event in (1001, 27):
            if self.manager.current == 'base':
                self.dialog_exit()
                return
            try:
                self.manager.current = self.list_previous_screens.pop()
            except:
                self.manager.current = 'base'
            self.screen.ids.action_bar.title = self.title
            self.screen.ids.action_bar.left_action_items = \
                [['menu', lambda x: self.nav_drawer.set_state("toggle")]]

    def show_about(self, *args):
        self.nav_drawer.set_state("toggle")
        self.screen.ids.about.ids.label.text = \
            self.translation._(
                u'[size=20][b]spacebook[/b][/size]\n\n'
                u'[b]Version:[/b] {version}\n'
                u'[b]License:[/b] MIT\n\n'
                u'[size=20][b]Developer[/b][/size]\n\n'
                u'[ref=SITE_PROJECT]'
                u'[color={link_color}]NAME_AUTHOR[/color][/ref]\n\n'
                u'[b]Source code:[/b] '
                u'[ref=REPO_PROJECT]'
                u'[color={link_color}]GitHub[/color][/ref]').format(
                version=__version__,
                link_color=get_hex_from_color(self.theme_cls.primary_color)
            )
        self.manager.current = 'about'
        self.screen.ids.action_bar.left_action_items = \
            [['chevron-left', lambda x: self.back_screen(27)]]

    def show_license(self, *args):
        self.nav_drawer.set_state("toggle")
        if not PY2:
            self.screen.ids.license.ids.text_license.text = \
                self.translation._('%s') % open(
                    os.path.join(self.directory, 'LICENSE'), encoding='utf-8').read()
        else:
            self.screen.ids.license.ids.text_license.text = \
                self.translation._('%s') % open(
                    os.path.join(self.directory, 'LICENSE')).read()
        self.manager.current = 'license'
        self.screen.ids.action_bar.left_action_items = \
            [['chevron-left', lambda x: self.back_screen(27)]]
        self.screen.ids.action_bar.title = \
            self.translation._('MIT LICENSE')

    def select_locale(self, *args):
        def select_locale(name_locale):
            for locale in self.dict_language.keys():
                if name_locale == self.dict_language[locale]:
                    self.lang = locale
                    self.config.set('General', 'language', self.lang)
                    self.config.write()

        dict_info_locales = {}
        for locale in self.dict_language.keys():
            dict_info_locales[self.dict_language[locale]] = \
                ['locale', locale == self.lang]

        if not self.window_language:
            self.window_language = card(
                Lists(
                    dict_items=dict_info_locales,
                    events_callback=select_locale, flag='one_select_check'
                ),
                size=(.85, .55)
            )
        self.window_language.open()

    def dialog_exit(self):
        def check_interval_press(interval):
            self.exit_interval += interval
            if self.exit_interval > 5:
                self.exit_interval = False
                Clock.unschedule(check_interval_press)

        if self.exit_interval:
            sys.exit(0)
            
        Clock.schedule_interval(check_interval_press, 1)
        toast(self.translation._('Press Back to Exit'))

    def on_lang(self, instance, lang):
        self.translation.switch_lang(lang)
