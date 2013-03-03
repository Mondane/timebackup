; Version: 27 februari 2013
; AutoHotkey script to check if the backup is running.
#NoTrayIcon  ; Initially hide the icon.

script_dir = %A_ScriptDir%

; backups are placed in a subfolder name $identifier, the identifier is also used as a lockfile
; Note, %A_ComputerName% isn't used because it returns the name as uppercase.
RegRead, identifier
  , HKEY_LOCAL_MACHINE
  , SYSTEM\CurrentControlSet\Services\Tcpip\Parameters
  , NV Hostname

; Determine lockfile, the identifier is used as a name for the lockfile
lockfile = %script_dir%\%identifier%.lck

; == START of PID check ==
is_pid_running(pid)
{
  ; The following line can be used if the process PID is shown in the Windows process list.
	; Process, Exist, %pid% ; check to see if the backup is running

  ; The following return can only be used with the function 'Process, Exist'.
  ; return (%ErrorLevel% = %pid%)
  
  ; Since the backup expects the backup to be running in cygwin, another approach must be made.
  ; The ps and grep executables from cygwin will be run
  RunWait "c:\cygwin\bin\ps.exe" -p %pid% | "c:\cygwin\bin\grep.exe" %pid%, , Hide
  
  ; For cygwin, the %ErrorLevel% equals 0 if the process is running.
  return (%ErrorLevel% = 0)
}
; == END of PID check ==

show_start_notification := true
show_stop_notification := true

; show a notification for 3 seconds
show_notification(message)
{
  TrayTip, Backup, %message%, 3
  return
}

show_start_notification()
{
  global show_start_notification
  global show_stop_notification
  
  if (show_start_notification = true)
  {
    show_notification("Backup started")
    show_start_notification := false
    show_stop_notification := true
  }
  return
}

show_stop_notification()
{
  global show_start_notification
  global show_stop_notification
  
  if (show_stop_notification = true)
  {
    show_notification("Backup stopped")
    show_start_notification := true
    show_stop_notification := false
    sleep 3500 ; Give the message time to be displayed, it is hidden when the icon is.
  }
  return
}

set_status()
{
  global lockfile
  
  IfExist, %lockfile%
  {
    ; File is found, get the pid from it and see if the process is really running.
    ; If it's not, it probably belongs to a ghost backup process (probably crashed).
    FileReadLine, pid, %lockfile%, 1
    pid := pid ; Convert string to integer.

    if (ErrorLevel = 0 and is_pid_running(pid))
    {
      Menu, Tray, Icon ; Display the icon.
      show_start_notification()
    }
    else
    {
      show_stop_notification()
      Menu, Tray, NoIcon ; Hide the icon.
    }
  }
  else
  {
    show_stop_notification()
    Menu, Tray, NoIcon ; Hide the icon.
  }
}

; Create the status indicator
icon = %script_dir%/backup-windows7_20x20.ico
Menu, Tray, Icon, %icon%
Menu, Tray, NoStandard ; remove standard Menu items
Menu, Tray, Tip, Backup running ; remove standard Menu items

set_status() ; set initial status

;  Start a loop which keeps checking the backup status.
#Persistent
SetTimer, SetStatus, 1000
return

SetStatus:
  set_status()
return