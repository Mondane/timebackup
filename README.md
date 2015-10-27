timebackup
==========

A backup like OS X timemachine for Linux/Cygwin

Script is based on the one found here: http://www.jan-muennich.de/linux-backups-time-machine-rsyn

How to setup:

Place all files in directory of your choice. Make sure backup.sh is executable (chmod +x backup.sh).

The script uses SSH for all connections, if you use localhost as a destination, make sure you have SSH installed.

Since the script is meant to be run in a cron, there must be a SSH key generated to allow passwordless login. Do this with ssh-keygen and copy the public part to the destination with ssh-copy-id.

You can see if the script is running, when you start the backup-indicator.py. This indicator uses the Ubuntu Unity app indicator functions. Should you be running Cygwin, install AutoHotKey and run backup-indicator.ahk.

NB Install the Python module gtk and appindicator for the backup indicator and make sure you start the indicator while logging in.

```sudo apt-get install python-gtk2 python-appindicator```
