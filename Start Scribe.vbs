' Scribe Launcher - Windows Shortcut Script
' This VBS script launches Scribe with proper window focus
' To create a shortcut:
' 1. Right-click this file -> Create shortcut
' 2. Right-click the shortcut -> Properties
' 3. Click "Change Icon" -> Browse to assets\scribe-icon.ico
' 4. Move shortcut to Desktop or Pin to Taskbar

Set WshShell = CreateObject("WScript.Shell")

' Get the directory where this script is located
ScriptDir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)

' Change to scribe directory
WshShell.CurrentDirectory = ScriptDir

' Find Python executable
PythonPath = "C:\Python313\python.exe"

' Check if Python exists at default location, otherwise try to find it
Set objFSO = CreateObject("Scripting.FileSystemObject")
If Not objFSO.FileExists(PythonPath) Then
    ' Try python from PATH
    PythonPath = "python.exe"
End If

' Launch Scribe (window will be visible)
' Using 1 as second parameter shows the window normally and gives it focus
WshShell.Run """" & PythonPath & """ """ & ScriptDir & "\run_scribe.py""", 1, False

Set WshShell = Nothing
Set objFSO = Nothing
