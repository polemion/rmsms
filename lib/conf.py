#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# rmSMS, Copyright (C) <2023~>  <Dimitrios Koukas>
# You may contact me in my web address here: https://www.dnkoukas.xyz/contact-me/

#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published
#   by the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.

#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.

#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

# Configuration Module.

import wx

DPOS = wx.DefaultPosition

APPINFO = {

    'ver': '0.90',
    'name': 'rmSMS',

    'home': 'https://www.dnkoukas.xyz',
    'source': 'https://github.com/polemion/rmsms',

    'license': '\nThis software is licensed under the GNU Affero General Public License version 3'
               ' (AGPLv3) or later.\n\nCopyright 2023-%s Dimitrios Koukas\n\nTo view the full text '
               'of the license, please visit:\n https://www.gnu.org/licenses/' % wx.DateTime.GetYear(wx.DateTime.Now())

}

aconf = {

    'platform': None,
    'app.dir': None,
    'app.path': None,
    'app.conf': None,
    'conf.dir': None,
    'log.dir': None,
    'themes.dir': None,
    'profiles.dir': None,
    'debug': False,
    'toolbar.refresh.time': 4,  # Seconds
    'log.size': 51200,  # Bytes
    'settings.mutex': False,
    'systray.def.ico': True

}

cache = {

    'toolbar.msg': '',
    'toolbar.timestamp': None,
    'sms.data.raw': [],
    'sms.data.store': [],
    'sms.active': 0,
    'sms.api.first.parse': True

}

conf = {

    # Mainframe
    'mainframe.pos': DPOS,
    'mainframe.size': wx.Size(391, 252),
    'active.theme': None,

    # Settings Dialog
    'settings.pos': DPOS,
    'settings.size': wx.Size(495, 293),

    # General Settings
    'config.iconify.onclose': True,
    'config.systray.onstart': False,

    # API settings
    'config.api.url': '',
    'config.api.un': '',
    'config.api.ps': '',
    'config.api.time.interval': 5000,  # In ms

    # Notification settings
    'config.ring': ' Bongo',
    'notif.open.app': True,
    'notif.system': True,
    'notif.timeout': False,
    'notif.timeout.sec': None

}

if __name__ == '__main__':
    import sys
    print('Please run the main executable.')
    sys.exit(0)
