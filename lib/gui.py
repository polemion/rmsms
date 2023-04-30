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

# GUI Module.

import wx, wx.adv as adv, os, sys
from lib import singletons, images
from lib.conf import APPINFO, conf, aconf

SIMPLEDLG = wx.DEFAULT_DIALOG_STYLE|wx.STAY_ON_TOP
SIMPLEFRAME = wx.DEFAULT_FRAME_STYLE|wx.RESIZE_BORDER|wx.TAB_TRAVERSAL
DPOS = wx.DefaultPosition
DSIZE = wx.DefaultSize
ADRW = wx.BU_AUTODRAW
NBIT = wx.NullBitmap
AHOR = wx.ALIGN_CENTER_HORIZONTAL
AVER = wx.ALIGN_CENTER_VERTICAL


def CreateBitmap(imgName, x=0, y=0):
    """Return embedded image."""
    if all([not x, not y]): return images.catalog[imgName].Bitmap
    else: return wx.Bitmap(wx.Image(images.catalog[imgName].Image).Rescale(x, y, wx.IMAGE_QUALITY_HIGH))


def setIcon(parent, image=None):
    """Set icon of caller window."""
    appICO = wx.Icon()
    try:
        if image is None: bitmap = CreateBitmap('appICO')
        if type(image) is str: bitmap = CreateBitmap(image)
        appICO.CopyFromBitmap(bitmap)
    except:  # If for some reason the image is missing.
        return NBIT
    parent.SetIcon(appICO)


def ErrorDialog(message='Unknown error!', caption='Error!', parent=None, style=wx.OK|wx.CANCEL|wx.CENTRE|wx.ICON_ERROR):
    """Shows a simple error dialog and exits..."""
    with wx.MessageDialog(parent, '\n%s\n\nClick Cancel to force close %s.' % (message, APPINFO['name']), caption, style, pos=DPOS) as dialog:
        if dialog.ShowModal() == wx.ID_OK: return wx.ID_OK
        else:
            if singletons.MainFrame is not None: singletons.MainFrame.onExit()
            else: sys.exit(1)


def Notification(parent, title='', message='', icon=wx.ICON_INFORMATION, timeout=None):
    """Shows a system notification."""
    notif = wx.adv.NotificationMessage(title, message, parent, icon)
    notif.Show() if timeout is None else notif.Show(timeout)


class AboutDialog (wx.Dialog):
    """About dialog."""

    def __init__(self, parent=None, id=wx.ID_ANY, title='%s - v%s' % (APPINFO['name'], APPINFO['ver']), pos=DPOS, size=wx.Size(428, 300)):
        """Init."""
        wx.Dialog.__init__(self, parent, id, title, pos, size, style=wx.CAPTION|wx.CLOSE_BOX|wx.STAY_ON_TOP)
        self.SetSizeHints(wx.Size(428, 300), DSIZE)
        self.Centre(wx.BOTH)
        setIcon(self)
        # Content
        self.dialogContent()
        # Init flow
        self.initActions()

    def initActions(self):
        """Initial actions."""
        self.dialogEvents()
        self.okBtn.SetFocus()
        self.ShowModal()

    def dialogEvents(self):
        """Event handling."""
        self.okBtn.Bind(wx.EVT_BUTTON, self.okBtnAction)
        self.licence.Bind(wx.EVT_TEXT_URL, self.openLicenceUrl)

    def openLicenceUrl(self, event):
        """Open license URL."""
        url = self.licence.GetValue()[event.GetURLStart():event.GetURLEnd()]
        if event.MouseEvent.LeftDown():
            wx.LaunchDefaultBrowser(url)

    def dialogContent(self):
        """Dialog contents."""
        self.logo = wx.StaticBitmap(self, wx.ID_ANY, CreateBitmap('appICO', 32, 32), DPOS, DSIZE, 0)
        self.licence = wx.TextCtrl(self, wx.ID_ANY, APPINFO['license'], DPOS, DSIZE, wx.TE_AUTO_URL|wx.TE_CENTER|wx.TE_MULTILINE|wx.TE_READONLY)
        self.url1 = wx.adv.HyperlinkCtrl(self, wx.ID_ANY, 'Creator\'s Home', APPINFO['home'], DPOS, DSIZE, wx.adv.HL_DEFAULT_STYLE)
        self.url2 = wx.adv.HyperlinkCtrl(self, wx.ID_ANY, 'Source', APPINFO['source'], DPOS, DSIZE, wx.adv.HL_DEFAULT_STYLE)
        self.okBtn = wx.Button(self, wx.ID_OK)
        # Sizers
        logoSizer = wx.BoxSizer(wx.HORIZONTAL)
        logoSizer.Add( self.logo, 0, AHOR|AVER, 5 )
        licenseSizer = wx.BoxSizer(wx.HORIZONTAL)
        licenseSizer.Add(self.licence, 1, AHOR|wx.EXPAND, 5)
        btnSizer = wx.StdDialogButtonSizer()
        btnSizer.AddButton(self.okBtn)
        btnSizer.Realize()
        urlSizer = wx.BoxSizer(wx.HORIZONTAL)
        urlSizer.AddMany([(self.url1, 0, wx.ALL|AVER, 5), (self.url2, 0, wx.ALL|AVER, 5), (btnSizer, 1, AVER, 5)])
        aboutSizer = wx.BoxSizer(wx.VERTICAL)
        aboutSizer.AddMany([(logoSizer, 0, wx.ALL|AHOR, 5), (licenseSizer, 1, wx.EXPAND|wx.ALL, 5), (urlSizer, 0, AHOR|wx.ALL|wx.EXPAND, 5)])
        self.SetSizer(aboutSizer)

    def okBtnAction(self, event):
        """On OK button action."""
        self.Hide()
        self.Destroy()


class MainGUI(wx.Frame):
    """MainFrame GUI."""

    def mainContent(self):
        """MainFrame contents."""
        self.leftBtn = wx.BitmapButton(self, wx.ID_ANY, CreateBitmap('dchevron-left', 20, 20), DPOS, DSIZE, ADRW|0)
        self.rightBtn = wx.BitmapButton(self, wx.ID_ANY, CreateBitmap('dchevron-right', 20, 20), DPOS, DSIZE, ADRW|0)
        self.settingsBtn = wx.BitmapButton(self, wx.ID_ANY, CreateBitmap('cog', 20, 20), DPOS, DSIZE, ADRW|0)
        self.aboutBtn = wx.BitmapButton(self, wx.ID_ANY, CreateBitmap('info', 20, 20), DPOS, DSIZE, ADRW|0)
        self.fromTxt = wx.StaticText(self, wx.ID_ANY, '----', DPOS, DSIZE, 0)
        self.dateTxt = wx.StaticText(self, wx.ID_ANY, '----', DPOS, DSIZE, wx.ALIGN_RIGHT)
        self.smsTxt = wx.TextCtrl(self, wx.ID_ANY, 'No messages received yet!', DPOS, DSIZE, wx.TE_MULTILINE|wx.TE_NO_VSCROLL|wx.TE_READONLY)
        # Sizers
        [x.Wrap(-1) for x in (self.fromTxt, self.dateTxt)]
        topSizer = wx.BoxSizer(wx.HORIZONTAL)
        topSizer.AddMany([(self.leftBtn, 0, wx.ALL|AVER, 5), (self.fromTxt, 1, AVER|wx.ALL, 5), (self.dateTxt, 1, AVER|wx.ALL, 5), (self.rightBtn, 0, wx.ALL|AVER, 5)])
        rightSizer = wx.BoxSizer(wx.VERTICAL)
        rightSizer.AddMany([(self.settingsBtn, 0, AVER|AHOR|wx.TOP, 5), ((0, 0), 1, AHOR, 5), (self.aboutBtn, 0, AHOR|wx.BOTTOM, 5)])
        bottomSizer = wx.BoxSizer(wx.HORIZONTAL)
        bottomSizer.AddMany([(self.smsTxt, 1, wx.EXPAND|AHOR|AVER|wx.ALL, 5), (rightSizer, 0, AVER|wx.EXPAND|wx.TOP|wx.BOTTOM, 5)])
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.AddMany([(topSizer, 0, wx.EXPAND|wx.RIGHT|wx.LEFT|AHOR, 5), (bottomSizer, 1, AVER|AHOR|wx.EXPAND|wx.ALL, 5)])
        self.SetSizer(mainSizer)
        self.Layout()


class SysTray(adv.TaskBarIcon):
    """Systray/Tasktray implementation."""
    trueICO = True

    def __init__(self):
        """Init."""
        adv.TaskBarIcon.__init__(self)
        setIcon(self)
        # Event
        self.Bind(adv.EVT_TASKBAR_LEFT_DOWN, self.OnSyTrayLeftClick)

    def OnSyTrayLeftClick(self, event=None):
        """Restore app window."""
        if singletons.MainFrame.IsShown():
            singletons.MainFrame.storeWindowProperties(None)
            singletons.MainFrame.Hide()
        else: singletons.MainFrame.Show()

    def changeICO(self, bitmap=None):
        """Change systray icon."""
        if bitmap is not None:
            aconf['systray.def.ico'] = False
        else: aconf['systray.def.ico'] = True
        setIcon(self, bitmap)

    def onQuit(self):
        """Exit app actions."""
        singletons.MainFrame.storeWindowProperties(None)
        singletons.MainFrame.onExit()

    def CreatePopupMenu(self):
        """Systray context menu."""
        # Menu items
        menu = wx.Menu()
        openItm = menu.Append(wx.NewId(), 'Open')
        settingsItm = menu.Append(wx.NewId(), 'Settings')
        menu.AppendSeparator()
        quitItm = menu.Append(wx.NewId(), 'Quit')
        # Menu actions
        def openItmAction(event): self.OnSyTrayLeftClick()
        def settingsItmAction(event): singletons.MainFrame.settingsBtnAct()
        def quitItmAction(event): self.onQuit()
        # Menu events
        self.Bind(wx.EVT_MENU, openItmAction, openItm)
        self.Bind(wx.EVT_MENU, settingsItmAction, settingsItm)
        self.Bind(wx.EVT_MENU, quitItmAction, quitItm)
        # Inactive items
        if singletons.MainFrame.IsShown(): openItm.Enable(False)
        # Show menu
        return menu

    def onExit(self):
        """Exit systray."""
        self.RemoveIcon()
        self.Destroy()


class NotifSettings (wx.Dialog):

    def __init__(self, parent, id=wx.ID_ANY, title='Notifications', pos=DPOS, size=wx.Size(460, 223)):
        """Init."""
        wx.Dialog.__init__(self, parent, id, title, pos, size, style=wx.CAPTION|wx.CLOSE_BOX|wx.STAY_ON_TOP)
        self.SetSizeHints(wx.Size(460, 223), DSIZE)
        setIcon(self)
        # Content
        self.audioChoices = self.scanRings()
        self.dialogContent()
        # Init flow
        self.initActions()

    def initActions(self):
        """Initial dialog actions."""
        self.initSettings()
        self.setCurRing()
        self.cancelBtn.SetFocus()
        # Initial flow
        self.dialogEvents()
        self.ShowModal()

    def initSettings(self):
        """Initial stored/default settings."""
        self.timeoutInp.Enable(conf['notif.timeout'])
        self.notif1Chk.SetValue(conf['notif.open.app'])
        self.notif2Chk.SetValue(conf['notif.system'])
        self.timeoutChk.SetValue(conf['notif.timeout'])
        if conf['notif.timeout']:
            self.timeoutInp.SetValue(conf['notif.timeout.sec'])

    def saveSettings(self):
        """Save settings."""
        conf['config.ring'] = self.getSelectedRing()
        conf['notif.open.app'] = self.notif1Chk.GetValue()
        conf['notif.system'] = self.notif2Chk.GetValue()
        conf['notif.timeout'] = self.timeoutChk.GetValue()
        if self.timeoutInp.IsEnabled():
            conf['notif.timeout.sec'] = self.timeoutInp.GetValue()
        else: conf['notif.timeout.sec'] = None

    def setCurRing(self):
        """Select currently stored ringtone."""
        itm = self.audioChoice.FindString(conf['config.ring'], True)
        if itm != wx.NOT_FOUND:
            self.audioChoice.SetSelection(itm)
        else: self.audioChoice.SetSelection(self.audioChoice.FindString(' None', True))

    def scanRings(self):
        """Scan ringtones dir for sound-effects."""
        ringDir = os.path.join(aconf['app.dir'], 'rings')
        if not os.path.exists(ringDir): os.mkdir(ringDir)
        ringList = [' None']
        ringList.extend(sorted([' %s' % x.replace('.mp3', '') for x in os.listdir(ringDir) if x.endswith('.mp3')]))
        return ringList

    def getSelectedRing(self):
        """Returns selected ringtone."""
        itm = self.audioChoice.GetSelection()
        if itm != wx.NOT_FOUND:
            return self.audioChoice.GetString(itm)
        else: return ' None'

    def ontimeoutChkAction(self, event):
        """On checking/unchecking the timeout check ctrl."""
        self.timeoutInp.Enable(self.timeoutChk.GetValue())

    def dialogContent(self):
        """Dialog contents."""
        self.audioTxt = wx.StaticText(self, wx.ID_ANY, 'Audio Alert: ', DPOS, DSIZE, 0)
        self.audioChoice = wx.Choice(self, wx.ID_ANY, DPOS, DSIZE, self.audioChoices, 0)
        self.notif1Chk = wx.CheckBox(self, wx.ID_ANY, 'Open the application when receiving a new message.', DPOS, DSIZE, 0)
        self.notif2Chk = wx.CheckBox(self, wx.ID_ANY, 'Use system notification when receiving a new message.', DPOS, DSIZE, 0)
        self.timeoutChk = wx.CheckBox(self, wx.ID_ANY, 'Override default system notification timeout:', DPOS, DSIZE, 0)
        self.timeoutInp = wx.SpinCtrl(self, wx.ID_ANY, '', DPOS, DSIZE, AHOR|wx.SP_ARROW_KEYS, 1, 99999, 1)
        self.okBtn = wx.Button(self, wx.ID_OK)
        self.cancelBtn = wx.Button(self, wx.ID_CANCEL)
        # Sizers
        self.audioTxt.Wrap(-1)
        audioSizer = wx.BoxSizer(wx.HORIZONTAL)
        audioSizer.AddMany([(self.audioTxt, 1, wx.ALL|AVER, 5), (self.audioChoice, 1, AVER|wx.ALL, 5)])
        timeoutSizer = wx.BoxSizer(wx.HORIZONTAL)
        timeoutSizer.AddMany([(self.timeoutChk, 0, AHOR|AVER, 5), ((0, 0), 0, wx.EXPAND|AVER, 5), (self.timeoutInp, 0, AVER|wx.RIGHT|wx.LEFT, 5)])
        btnSizer = wx.StdDialogButtonSizer()
        [btnSizer.AddButton(x) for x in (self.okBtn, self.cancelBtn)]
        btnSizer.Realize()
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.AddMany([(audioSizer, 0, wx.EXPAND|AHOR|wx.RIGHT|wx.LEFT, 5), (self.notif1Chk, 0, wx.ALL|AHOR|wx.EXPAND, 5), (self.notif2Chk,
            0, wx.ALL|AHOR|wx.EXPAND, 5), (timeoutSizer, 0, AHOR|wx.EXPAND|wx.RIGHT|wx.LEFT, 5), ((0, 0), 1, 0, 5), (btnSizer, 0, AHOR|wx.EXPAND|wx.TOP|wx.BOTTOM, 5)])
        self.SetSizer(mainSizer)
        self.Layout()

    def dialogEvents(self):
        """Settings event handling."""
        # Main dialog buttons
        self.okBtn.Bind(wx.EVT_BUTTON, self.okBtnAction)
        self.cancelBtn.Bind(wx.EVT_BUTTON, self.onExit)
        self.timeoutChk.Bind(wx.EVT_CHECKBOX, self.ontimeoutChkAction)
        # On Exiting
        self.Bind(wx.EVT_CLOSE, self.onExit)

    def okBtnAction(self, event):
        """Save settings and exit."""
        self.saveSettings()
        self.onExit(None)

    def onExit(self, event):
        """On closing the dialog."""
        self.Hide()
        self.Destroy()


class Settings (wx.Dialog):

    def __init__(self, parent=None, id=wx.ID_ANY, title='Settings', pos=DPOS, size=conf['settings.size']):
        """Init."""
        wx.Dialog.__init__(self, parent, id, title, pos, size, style=SIMPLEDLG|wx.RESIZE_BORDER)
        self.SetSizeHints(wx.Size(495, 293), DSIZE)
        self.Centre(wx.BOTH)
        setIcon(self)
        # Data
        self.initSettings()
        # Init flow
        self.initActions()

    def initActions(self):
        """Initial dialog actions."""
        self.settingsContent()
        self.minCloseBox.SetValue(self.minCloseCheck)
        self.startMinBox.SetValue(self.startMinCheck)
        self.cancelBtn.SetFocus()
        # Initial flow
        self.settingsEvents()
        self.ShowModal()

    def initSettings(self):
        """Initial stored/default settings."""
        self.minCloseCheck = conf['config.iconify.onclose']
        self.startMinCheck = conf['config.systray.onstart']
        self.apiUrlInit = conf['config.api.url']
        self.apiUserInit = conf['config.api.un']
        self.apiPassInit = conf['config.api.ps']

    def storeWindowProperties(self):
        """Store window size."""
        conf['settings.size'] = self.GetSize()

    def saveSettings(self):
        """Save settings."""
        conf['config.iconify.onclose'] = self.minCloseBox.GetValue()
        conf['config.systray.onstart'] = self.startMinBox.GetValue()
        conf['config.api.url'] = self.apiUrlInput.GetValue().strip()
        conf['config.api.un'] = self.apiUserInput.GetValue().strip()
        conf['config.api.ps'] = self.apiPassInput.GetValue().strip()

    def settingsContent(self):
        """Dialog contents."""
        remoteBox = wx.StaticBox(self, wx.ID_ANY, 'Remote API:')
        self.apiUrlText = wx.StaticText(remoteBox, wx.ID_ANY, 'URL:', DPOS, DSIZE, 0)
        self.apiUrlInput = wx.TextCtrl(remoteBox, wx.ID_ANY, self.apiUrlInit, DPOS, DSIZE, wx.TE_PROCESS_TAB|wx.TE_RIGHT)
        self.apiUserText = wx.StaticText(remoteBox, wx.ID_ANY, 'Username:', DPOS, DSIZE, 0)
        self.apiUserInput = wx.TextCtrl(remoteBox, wx.ID_ANY, self.apiUserInit, DPOS, DSIZE, wx.TE_PROCESS_TAB|wx.TE_RIGHT)
        self.apiPassText = wx.StaticText(remoteBox, wx.ID_ANY, 'Password:', DPOS, DSIZE, 0)
        self.apiPassInput = wx.TextCtrl(remoteBox, wx.ID_ANY, self.apiPassInit, DPOS, DSIZE, wx.TE_PASSWORD|wx.TE_PROCESS_TAB|wx.TE_RIGHT)
        generalBox = wx.StaticBox(self, wx.ID_ANY, 'General:')
        self.notifBtn = wx.Button(generalBox, wx.ID_ANY, 'Setup Notifications Details', DPOS, DSIZE, 0)
        self.minCloseBox = wx.CheckBox(generalBox, wx.ID_ANY, 'Minimize On Close', DPOS, DSIZE, wx.ALIGN_RIGHT)
        self.startMinBox = wx.CheckBox(generalBox, wx.ID_ANY, 'Start Minimized', DPOS, DSIZE, wx.ALIGN_RIGHT)
        self.okBtn = wx.Button(self, wx.ID_OK)
        self.applyBtn = wx.Button(self, wx.ID_APPLY)
        self.cancelBtn = wx.Button(self, wx.ID_CANCEL)
        # Sizers
        [x.Wrap(-1) for x in (self.apiUrlText, self.apiUserText, self.apiPassText)]
        apiUrlSizer = wx.BoxSizer(wx.HORIZONTAL)
        apiUrlSizer.AddMany([(self.apiUrlText, 0, wx.ALL|AVER, 5), (self.apiUrlInput, 1, AVER|wx.ALL, 5)])
        apiUserSizer = wx.BoxSizer(wx.HORIZONTAL)
        apiUserSizer.AddMany([(self.apiUserText, 0, wx.ALL|AVER, 5), (self.apiUserInput, 1, wx.ALL|AVER, 5)])
        apiPassSizer = wx.BoxSizer(wx.HORIZONTAL)
        apiPassSizer.AddMany([(self.apiPassText, 0, wx.ALL|AVER, 5), (self.apiPassInput, 1, wx.ALL|AVER, 5)])
        apiSizer = wx.StaticBoxSizer(remoteBox, wx.VERTICAL)
        apiSizer.AddMany([(apiUrlSizer, 1, wx.EXPAND, 5), (apiUserSizer, 1, wx.EXPAND, 5), (apiPassSizer, 1, wx.EXPAND, 5)])
        genSizer = wx.StaticBoxSizer(generalBox, wx.HORIZONTAL)
        genSizer.AddMany([(self.notifBtn, 0, wx.ALL|AVER, 5), ((0, 0), 1, AVER, 5), (self.minCloseBox, 0, wx.ALL|AVER, 5), (self.startMinBox, 0, wx.ALL|AVER, 5)])
        btnSizer = wx.StdDialogButtonSizer()
        [btnSizer.AddButton(x) for x in (self.okBtn, self.applyBtn, self.cancelBtn)]
        btnSizer.Realize()
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.AddMany([(apiSizer, 0, wx.EXPAND|wx.ALL|AHOR, 5), (genSizer, 0, wx.ALL|AHOR|wx.EXPAND, 5), (btnSizer, 1, wx.EXPAND, 5)])
        self.SetSizer(mainSizer)
        self.Layout()

    def settingsEvents(self):
        """Settings event handling."""
        # Main dialog buttons
        self.notifBtn.Bind(wx.EVT_BUTTON, self.notifBtnAction)
        self.applyBtn.Bind(wx.EVT_BUTTON, self.applyBtnAction)
        self.cancelBtn.Bind(wx.EVT_BUTTON, self.onExit)
        self.okBtn.Bind(wx.EVT_BUTTON, self.okBtnAction)
        # On Exiting
        self.Bind(wx.EVT_CLOSE, self.onExit)

    def notifBtnAction(self, event):
        """Open notifications settings.."""
        NotifSettings(self)

    def applyBtnAction(self, event):
        """Save settings but do not exit."""
        self.saveSettings()

    def okBtnAction(self, event):
        """Save settings and exit."""
        self.saveSettings()
        self.onExit(None)

    def onExit(self, event):
        """On closing the dialog."""
        self.storeWindowProperties()
        self.Hide()
        self.Destroy()


if __name__ == '__main__':
    import sys
    print('Please run the main executable.')
    sys.exit(0)
