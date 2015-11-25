#!/usr/bin/env python
# Version: 20 februari 2013
# AppIndicator script based on http://ubuntuforums.org/showthread.php?t=1824899 
# Fallback to Qt taken from http://askubuntu.com/a/90738/71572

import os.path
import socket
import sys

script_dir = os.path.dirname(os.path.realpath(__file__))

# Backups are placed in a subfolder name $identifier, the identifier is also used for the lockfile.
# Load the settings to determine the identifier.
settingsfile='{script_dir}/settings.inc'.format(  **locals())

import ConfigParser
# FakeSecHead taken from http://stackoverflow.com/a/2819788
class FakeSecHead(object):
    def __init__(self, fp):
        self.fp = fp
        self.sechead = '[settings]\n'

    def readline(self):
        if self.sechead:
            try: 
                return self.sechead
            finally: 
                self.sechead = None
        else: 
            return self.fp.readline()

cp = ConfigParser.SafeConfigParser()
cp.readfp(FakeSecHead(open(settingsfile)))

# Using eval to get rid of quotes, see http://stackoverflow.com/a/33730075
if (len(eval(cp.get('settings', 'identifier'))) > 0):
   identifier = eval(cp.get('settings', 'identifier'))
else:
   identifier = socket.gethostname()

# Check and create lockfile, the identifier is used as a name for the lockfile
lockfile='{script_dir}/{identifier}.lck'.format(  **locals())

# Is appindicator possiblem, otherwise fallback to qt.
# TODO Finish the Qt fallback, timer isn't working
use_appindicator = not ( sys.platform[:3] == 'win' or 'kde' in os.environ.get('DESKTOP_SESSION') )

# == START of PID check ==
# Taken from http://www.madebuild.org/blog/?p=30
# GetExitCodeProcess uses a special exit code to indicate that the process is
# still running.
import os
import platform
import ctypes

_STILL_ACTIVE = 259
 
def is_pid_running(pid):
  return (_is_pid_running_on_windows(pid) if platform.system() == "Windows"
    else _is_pid_running_on_unix(pid))
 
def _is_pid_running_on_unix(pid):
  try:
    os.kill(pid, 0)
  except OSError:
    return False
  return True
 
def _is_pid_running_on_windows(pid):
  import ctypes.wintypes
 
  kernel32 = ctypes.windll.kernel32
  handle = kernel32.OpenProcess(1, 0, pid)
  if handle == 0:
    return False
 
  # If the process exited recently, a pid may still exist for the handle.
  # So, check if we can get the exit code.
  exit_code = ctypes.wintypes.DWORD()
  is_running = (
    kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)) == 0)
  kernel32.CloseHandle(handle)
 
  # See if we couldn't get the exit code or the exit code indicates that the
  # process is still running.
  return is_running or exit_code.value == _STILL_ACTIVE

# == END of PID check ==

def set_status():
  if os.path.isfile(lockfile):
    # File is found, get the pid from it and see if the process is really running.
    # If it's not, it probably belongs to a ghost backup process (probably crashed).
    infile = open(lockfile, 'r')
    
    try:
      pid = int(infile.readline())
    except ValueError:
      pid = None

    if isinstance( pid, int ) and is_pid_running(pid):
      if use_appindicator:
        i.set_status(appindicator.STATUS_ACTIVE)
      else:
        i.show()
    else:
      if use_appindicator:
        i.set_status(appindicator.STATUS_PASSIVE)
      else:
        i.hide()
  else:
      if use_appindicator:
        i.set_status(appindicator.STATUS_PASSIVE)
      else:
        i.hide()

  return True # so this timeout is scheduled again

# Create the appindicator
icon = '{script_dir}/backup-ambiance_20x20.png'.format(  **locals())
if use_appindicator:
  import gtk
  import gobject
  import appindicator

  i = appindicator.Indicator(
    'Backup indicator',
    icon,
    appindicator.CATEGORY_APPLICATION_STATUS
  )

  i.set_menu( gtk.Menu()) # the indicator is not visible without this
else:
  from PyQt4 import QtGui, QtCore

  i_app = QtGui.QApplication([])
  i = QtGui.QSystemTrayIcon(QtGui.QIcon(icon), i_app)

set_status() # set initial status

# Start a loop which keeps checking the backup status.
if use_appindicator:
  gobject.timeout_add( 1000, set_status)
  gtk.main()
else:
  # TODO Fix this timer
  # Create a QTimer
  i_timer = QtCore.QTimer()
  # Connect it to f
  i_timer.timeout.connect(set_status)
  # Call set_status() every second
  i_timer.start(1000)
