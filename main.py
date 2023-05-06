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

# Main.

import wx, os, sys, locale, pickle, shutil, json, time, traceback
from datetime import datetime
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import lib.singletons as singletons
from lib.conf import conf, APPINFO, aconf, cache
from lib.gui import ErrorDialog, setIcon, SysTray, MainGUI, Settings, AboutDialog, Notification
from lib.gui import DSIZE, SIMPLEFRAME
import urllib.request, base64, urllib.error

# Platform specific
if aconf['platform'] == 'windows':
    from playsound import playsound
else:
    from play_sounds import play_file


class StatusBar:
    """Statusbar actions."""

    def __init__(self, parent):
        """Init."""
        self.bar = parent.CreateStatusBar(1, wx.STB_DEFAULT_STYLE, wx.ID_ANY)
        self.timer = wx.Timer()
        self.timer.Bind(wx.EVT_TIMER, self.onUpdate)
        self.timer.Start(1000)

    def onUpdate(self, event=None):
        if cache['toolbar.timestamp'] is not None:
            if (round(time.time()) - cache['toolbar.timestamp']) >= aconf['toolbar.refresh.time']:
                self.bar.SetStatusText('')
                cache['toolbar.timestamp'] = None

    def show(self, msg):
        cache['toolbar.msg'] = msg
        self.bar.SetStatusText(' %s' % msg)
        cache['toolbar.timestamp'] = round(time.time())

    def exit(self):
        cache['toolbar.timestamp'] = None
        self.bar.SetStatusText('Exiting...')
        self.timer.Destroy()


class Log:
    """App logger."""
    maxsize = aconf['log.size']

    def __init__(self, msg=None, lvl='Notice', statusbar=False):
        """Init."""
        self.logfile = os.path.join(aconf['log.dir'], '%s.log' % APPINFO['name'])
        if not os.path.exists(self.logfile): open(self.logfile, 'w').close()
        if all([os.path.getsize(self.logfile) >= self.maxsize, msg == 'init']): self.rotateLog()
        if msg is not None: self.constructLog(msg, lvl, statusbar)

    def constructLog(self, msg, lvl, statusbar):
        """Prepare log message."""
        if msg == 'init': msg = '%s %s - %s %s' % ('='*5, APPINFO['name'], 'Log Init', '='*5)
        elif msg == 'exit': msg = '%s %s - %s %s' % ('='*5, APPINFO['name'], 'App Exit', '='*5)
        elif lvl == 'Fatal Error': msg = 'An exception was thrown:\n%s' % msg
        finmsg = '\n%s [%s]: %s' % (str(datetime.now()), lvl, msg)
        # Export log
        if 'Fatal Error' == lvl:
            self.showLog(finmsg)
            ErrorDialog(msg, lvl)
        elif aconf['debug']: self.showLog(finmsg)
        if statusbar: singletons.statusbar.show(statusbar)
        if any([aconf['debug'], 'Log Init' in msg, 'App Exit' in msg, lvl != 'Notice']):
            self.logmsg(finmsg)

    def logmsg(self, msg):
        """Add log entry"""
        with open(self.logfile, 'a') as rlog:
            rlog.writelines(msg)

    def showLog(self, msg):
        """Show log messages to user."""
        print(msg)

    def rotateLog(self):
        """Rotate log file."""
        rotfile = '%s1' % self.logfile
        if os.path.isfile(rotfile):
            os.remove(rotfile)
        if os.path.isfile(self.logfile):
            os.rename(self.logfile, rotfile)
            open(self.logfile, 'w').close()


class Storage:  # todo add support for json objects?
    """Storage functionality."""

    def store(self, fl, data):
        """Save data to a chosen file."""
        with open(fl, 'w') as out:
            out.write('\n'.join(data))

    def parse(self, fl):
        """Parse the contents of a chosen file."""
        with open(fl, 'r') as inp:
            return [x.rstrip() for x in inp.readlines()]

    def storePickle(self, fl, data):
        """Save pickled data to a chosen file."""
        with open(fl, 'wb') as out:
            pickle.dump(data, out)

    def parsePickle(self, fl):
        """Parse the contents of a pickled file."""
        with open(fl, 'rb') as inp:
            return pickle.load(inp)


class AppSettings(Storage):
    """Application's settings manager."""

    def __init__(self):
        """Init."""
        self.appConf = aconf['app.conf']
        self.appConfBck = '%s.bck' % self.appConf
        self.appConfCorrupt = '%s.corrupt' % self.appConf
        if not os.path.isfile(self.appConf):
            self.storeConf()

    def parseConf(self):
        """Parse application's configuration."""
        try:
            raw = self.parsePickle(self.appConf)
        except pickle.UnpicklingError:
            singletons.log('Configuration file %s is corrupt. Will attempt to load backup configuration.' % aconf['app.conf'], 'Error')
            if os.path.isfile(self.appConfBck):
                try:
                    raw = self.parsePickle(self.appConfBck)
                    singletons.log('Backup configuration file loaded successfully. Renamed old configuration to %s.' % self.appConfCorrupt, 'Warning')
                    os.rename(self.appConf, self.appConfCorrupt)
                    shutil.copy(self.appConfBck, self.appConf)
                except pickle.UnpicklingError:
                    singletons.log('Backup configuration file %s is corrupt. Will use default configuration.' % self.appConfBck, 'Error')
            else: singletons.log('Backup configuration file %s not detected. Will use default configuration.' % self.appConfBck, 'Error')
        except Exception as err:
            singletons.log('Unable to parse Configuration file %s. Will use default configuration. Error trace:\n%s' % (aconf['app.conf'], err), 'Error')
        else:  # Apply settings
            for x in raw: conf[x] = raw[x]
        finally:  # Store a backup of the last successful conf restored.
            self.storeConf(True)

    def storeConf(self, bck=False):
        """Store application's configuration."""
        if bck: conftostore = self.appConfBck
        else: conftostore = self.appConf
        try: self.storePickle(conftostore, conf)
        except PermissionError:
            singletons.log('Access Denied - Unable to save configuration file %s.' % conftostore, 'Error')
        except Exception as err:
            singletons.log('Unable to save configuration file %s. Error trace:\n%s' % (conftostore, err), 'Error')


class APIInterface:
    """Remote API Interface"""

    def __init__(self):
        """Init."""
        self.timer = wx.Timer()
        self.timer.Bind(wx.EVT_TIMER, self.onUpdate)
        self.timer.Start(150)

    def onUpdate(self, event):
        """Timer actions."""
        # In case there are any time interval changes in settings.
        if self.timer.GetInterval() != conf['config.api.time.interval']:
            self.timer.Start(conf['config.api.time.interval'])
        if aconf['settings.mutex']: return
        if self.checkCreds():
            singletons.log('Connecting to remote API.', 'Notice', 'Connecting to remote API...')
            response = self.connectAPI()
            if response:
                if response != cache['sms.data.raw']:
                    cache['sms.data.raw'] = response
                    msg = 'SMS data updated. New SMS received!'
                    singletons.log(msg, 'Notice', msg)

    def connectAPI(self):
        """Connect to remote API."""
        auth_header = 'Basic ' + base64.b64encode((conf['config.api.un'] + ':' + conf['config.api.ps']).encode()).decode()
        request = urllib.request.Request(conf['config.api.url'], headers={'Authorization': auth_header})
        try:
            with urllib.request.urlopen(request) as response:
                remoteStorage = response.read().decode('utf-8').splitlines()
                singletons.log('Successfully connected to remote API.', 'Notice', 'Connected to remote API...')
                result = [self._parseJSON(x) for x in remoteStorage]
                result.reverse()
                return [x for x in result if type(x) is dict]
        except urllib.error.HTTPError as e:  # HTTP errors
            msg = 'Unable to connect to remote API, received HTTP%s!' % e.code
            singletons.log('%s, "%s"' % (msg, e.reason), 'HTTP Error', msg)
        except urllib.error.URLError as e:  # URL errors
            msg = 'Unable to connect to remote API (%s)!' % e.reason
            singletons.log(msg, 'URL Error', msg)
        except Exception as e:  # General errors
            singletons.log('%s\n%s' % ('Unable to connect to remote API:\n', e), 'Error', 'Unable to connect to remote API, please check log!')
        return []

    def _parseJSON(self, line):
        """Parse JSON data."""
        data = None
        try:
            data = json.loads(line)
        except ValueError:
            try:
                rawline = self._decrypt(line)
                if rawline:
                    data = json.loads(rawline)
            except ValueError as e:  # Garbage removal
                singletons.log('JSON structure problem, unable to extract:\n %s' % e, 'Warning')
            except Exception:  # General errors
                err = traceback.format_exc(chain=False)
                singletons.log('Unexpected error in line while trying to decrypt remote API response:\n %s' % err, 'Warning')
        except Exception:  # General errors
            err = traceback.format_exc(chain=False)
            singletons.log('Unexpected error in line while parsing remote API response:\n %s' % err, 'Warning')
        finally: return data

    def _decrypt(self, encrypted_data):
        """Decrypt line.
            This is most probably a bad implementation, replicate/copy at your own peril!!!
        """
        if not conf['config.api.key']: return ''
        key = bytes(conf['config.api.key'], encoding='utf-8')
        # Decode the base64-encoded string to obtain the IV and ciphertext
        encrypted_data = base64.b64decode(encrypted_data)
        iv = encrypted_data[:16]
        ciphertext = encrypted_data[16:]
        # Create a Cipher object using the same key, IV, and algorithm/mode of operation
        backend = default_backend()
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
        # Decrypt the ciphertext
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
        # Remove any padding, we always expect a JSON structure
        unpadder = padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(decrypted_data) + unpadder.finalize()
        # Return the decrypted data
        return plaintext.decode('utf-8')

    def checkCreds(self):
        """Examine supplied API credentials if valid."""
        if conf['config.api.url'].strip():
            return True
        else: return False


class MainFrame(MainGUI):
    """MainFrame GUI."""

    def __init__(self, parent, title, pos, size, style=SIMPLEFRAME|wx.STAY_ON_TOP):
        """Init."""
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=title, pos=pos, size=size, style=style)
        self.SetSizeHints(wx.Size(391, 252), DSIZE)
        setIcon(self)
        self.mainTimer = wx.Timer()
        if pos == (-1, -1): self.Centre(wx.BOTH)
        singletons.systray = SysTray()
        singletons.statusbar = StatusBar(self)
        # Content
        self.mainContent()
        # Events
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.Bind(wx.EVT_ICONIZE, self.onMinimize)
        self.leftBtn.Bind(wx.EVT_BUTTON, self.leftBtnAct)
        self.rightBtn.Bind(wx.EVT_BUTTON, self.rightBtnAct)
        self.aboutBtn.Bind(wx.EVT_BUTTON, self.aboutBtnAct)
        self.settingsBtn.Bind(wx.EVT_BUTTON, self.settingsBtnAct)
        self.mainTimer.Bind(wx.EVT_TIMER, self.onUpdate)
        # App flow
        self.initAppFlow()

    def initAppFlow(self):
        """Initial Application flow."""
        singletons.interfaceAPI = APIInterface()
        self.mainTimer.Start(100)

    def onUpdate(self, event):
        """MainFrame timed events."""
        self.chkDataStoreUpdate()
        # Revert systray icon to default.
        self.setDefSystryIco()
        # Update chevrons.
        self.setChevron()

    def chkDataStoreUpdate(self):
        """Check for updates in the data store."""
        if cache['sms.data.store'] != cache['sms.data.raw']:
            cache['sms.data.store'] = cache['sms.data.raw']
            cache['sms.active'] = 0
            self.updateSMSGUI()
            self.notifyNewSMS()

    def setDefSystryIco(self):
        """Revert systray icon to default when app is open."""
        if self.IsShown():
            if not aconf['systray.def.ico']:
                singletons.systray.changeICO()

    def setChevron(self):
        """Chevron buttons state detection."""
        if len(cache['sms.data.store']) <= 1:
            if self.leftBtn.IsEnabled():
                self.leftBtn.Disable()
            if self.rightBtn.IsEnabled():
                self.rightBtn.Disable()
        else:
            if cache['sms.active'] == 0:
                if self.leftBtn.IsEnabled():
                    self.leftBtn.Disable()
                if not self.rightBtn.IsEnabled():
                    self.rightBtn.Enable()
            elif len(cache['sms.data.store']) - 1 == cache['sms.active']:
                if self.rightBtn.IsEnabled():
                    self.rightBtn.Disable()
                if not self.leftBtn.IsEnabled():
                    self.leftBtn.Enable()
            else:
                if not self.rightBtn.IsEnabled():
                    self.rightBtn.Enable()
                if not self.leftBtn.IsEnabled():
                    self.leftBtn.Enable()

    def notifyNewSMS(self):
        """Notification actions when receiving an SMS."""
        if not cache['sms.api.first.parse']:  # Do not notify on app boot if the Server already has messages.
            # When a new SMS arrives
            singletons.systray.changeICO('appICOnotify')
            if conf['notif.system']:
                Notification(self, 'New SMS received!', '', timeout=conf['notif.timeout.sec'])
            if conf['notif.open.app']:
                if not self.IsShown(): self.Show()
            # Lessen the blocking effect of sounds
            wx.CallLater(100, self.audioNotify)
        else: cache['sms.api.first.parse'] = False

    def updateSMSGUI(self):
        """Update SMS data on the MainFrame GUI."""
        cur = cache['sms.data.store'][cache['sms.active']]
        self.fromTxt.SetLabel(cur['from'])
        self.dateTxt.SetLabel('%s' % wx.DateTime.FromTimeT(round(cur['receivedStamp']/1000)))
        self.smsTxt.SetValue(cur['text'])

    def leftBtnAct(self, event):
        """On button actions."""
        if cache['sms.active'] == 0:
            return
        cache['sms.active'] -= 1
        self.updateSMSGUI()

    def rightBtnAct(self, event):
        """On button actions."""
        if len(cache['sms.data.store']) - 1 == cache['sms.active']:
            return
        cache['sms.active'] += 1
        self.updateSMSGUI()

    def aboutBtnAct(self, event):
        """On about actions."""
        AboutDialog(self)

    def audioNotify(self):
        """Hopeful audio notification."""
        try:
            if conf['config.ring'] == 'None'.strip(): return
            audiofl = os.path.join(aconf['app.dir'], 'rings', '%s.mp3' % conf['config.ring'].strip())
            if not os.path.isfile(audiofl):
                conf['config.ring'] = ' None'
                return
            if aconf['platform'] == 'windows':
                from playsound import playsound
                playsound(audiofl)
            else:
                play_file(audiofl, False)
        except Exception as e:
            singletons.log('Audio system failure =>\n %s' % e, 'Error')

    def settingsBtnAct(self, event=None):
        """Open settings."""
        aconf['settings.mutex'] = True
        Settings(self)
        aconf['settings.mutex'] = False

    def onMinimize(self, event):
        """On minimize button actions."""
        if self.IsIconized():
            self.Restore()
        else: self.toSystray()

    def onClose(self, event):
        """On close button actions."""
        if conf['config.iconify.onclose']:
            if self.IsShown():
                self.toSystray()
        else: self.onExit()

    def toSystray(self):
        """On Systray actions."""
        self.storeWindowProperties()
        self.Hide()
        if singletons.systray is None:
            SysTray()

    def storeWindowProperties(self, event=None):
        """Store window size and position."""
        conf['mainframe.pos'] = self.GetPosition()
        conf['mainframe.size'] = self.GetSize()

    def onExit(self, event=None):
        """Exit actions."""
        singletons.statusbar.exit()
        if singletons.systray is not None:
            singletons.systray.onExit()
        AppSettings().storeConf()
        self.Hide()
        self.mainTimer.Destroy()
        self.Destroy()
        singletons.app.ExitMainLoop()
        singletons.log('exit')


class MyApp(wx.App):
    """Bootstrap wxPython."""

    def InitLocale(self):
        """Init locale."""
        locale.setlocale(locale.LC_ALL, 'C')

    def OnInit(self):
        """OnInit."""
        wx.Locale(wx.LANGUAGE_ENGLISH_US)
        self.SetAppName(APPINFO['name'])
        return True


class Main:
    """Let the fun begin..."""

    def __init__(self):
        """Init."""
        singletons.app = MyApp()
        aconf['platform'] = self.getOS()
        self.setAPPpaths()
        singletons.log = Log
        singletons.confStore = AppSettings()
        self.initGUI()

    def initGUI(self):
        """Init GUI."""
        singletons.log('init')
        singletons.confStore.parseConf()
        # Mainframe
        singletons.MainFrame = MainFrame(None, APPINFO['name'], conf['mainframe.pos'], conf['mainframe.size'])
        singletons.app.SetTopWindow(singletons.MainFrame)
        if not conf['config.systray.onstart']:
            singletons.MainFrame.Show()
        singletons.app.MainLoop()

    def getOS(self):
        """OS Detection."""
        import platform
        syst, arch = platform.system().lower(), platform.architecture()[1].lower()
        if any(['windows' in syst, 'windows' in arch]): return 'windows'
        elif any(['linux' in syst, 'sunos' in syst]): return 'linux'
        elif 'darwin' in syst: return'macos'

    def setAPPpaths(self):
        """Set application paths."""
        # Check if the application is frozen or not.
        if getattr(sys, 'frozen', False):  # If frozen
            try:  # pyinstaller
                appPath = sys._MEIPASS
            except:   # py2exe
                appPath = sys.executable
            # Check if frozen as onefile, hacky
            if '/tmp' in appPath:
                appPath = sys.executable
        else:  # Running through the interpreter
            appPath = os.path.abspath(__file__)
        # Set application dir/path
        aconf['app.dir'] = os.path.dirname(appPath)
        aconf['app.path'] = appPath
        # Set/Create conf dir
        if aconf['platform'] == 'linux':
            uname = os.getenv("SUDO_USER") or os.getenv("USER")
            uhome = os.path.expanduser('~'+uname)
            if os.path.isdir(uhome):
                # Set conf in .config dir
                configDirOS = os.path.join(uhome, '.config')
                if os.path.isdir(configDirOS):
                    configDir = os.path.join(configDirOS, APPINFO['name'])
                    if not os.path.isdir(configDir):
                        os.mkdir(configDir)
                else:  # TODO: Detect and set conf in $XDG_CONFIG_HOME - or exit
                    print('Unable to detect the user\'s .config directory, exiting.')
                    sys.exit(1)
            else:  # Something is wrong with our $HOME detection, abort.
                print('Unable to detect the user\'s home directory, aborting.')
                sys.exit(1)
        elif aconf['platform'] == 'windows':  # Portable
            configDir = aconf['log.dir'] = aconf['app.dir']
        elif aconf['platform'] == 'macos':  # todo: add
            print('MACOS not supported!')
            sys.exit(1)
        # Set directories
        aconf['profiles.dir'] = os.path.join(configDir, 'profiles')
        aconf['themes.dir'] = os.path.join(configDir, 'themes')
        aconf['app.conf'] = os.path.join(configDir, '%s.pkl' % APPINFO['name'])
        aconf['conf.dir'] = configDir
        if aconf['platform'] == 'linux': aconf['log.dir'] = configDir


if __name__ == '__main__':
    Main()
