' Scribe Launcher - Windows Shortcut Script
' This VBS script launches Scribe with proper window focus
' To create a shortcut:
' 1. Right-click this file -> Create shortcut
' 2. Right-click the shortcut -> Properties
' 3. Click "Change Icon" -> Browse to assets\scribe-icon.ico
' 4. Move shortcut to Desktop or Pin to Taskbar

On Error Resume Next

Set WshShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Get the directory where this script is located
ScriptDir = objFSO.GetParentFolderName(WScript.ScriptFullName)

' Change to scribe directory
WshShell.CurrentDirectory = ScriptDir

' Find Python executable - try multiple locations (prefer Python 3.12 for GPU support)
Dim PythonPath, PythonLocations, Location
PythonLocations = Array( _
    "C:\Users\" & WshShell.ExpandEnvironmentStrings("%USERNAME%") & "\AppData\Local\Programs\Python\Python312\python.exe", _
    "C:\Python312\python.exe", _
    "C:\Program Files\Python312\python.exe", _
    "C:\Python313\python.exe", _
    "C:\Python311\python.exe", _
    "C:\Python310\python.exe", _
    "C:\Program Files\Python313\python.exe", _
    "python.exe" _
)

PythonPath = ""
For Each Location In PythonLocations
    If objFSO.FileExists(Location) Or Location = "python.exe" Then
        PythonPath = Location
        Exit For
    End If
Next

If PythonPath = "" Then
    MsgBox "Python not found! Please install Python 3.10 or later from python.org", vbCritical, "Scribe Launcher"
    WScript.Quit 1
End If

' Verify run_scribe.py exists
If Not objFSO.FileExists(ScriptDir & "\run_scribe.py") Then
    MsgBox "run_scribe.py not found in " & ScriptDir, vbCritical, "Scribe Launcher"
    WScript.Quit 1
End If

' Launch Scribe (window will be visible)
' Using 1 as second parameter shows the window normally and gives it focus
Dim Command
Command = """" & PythonPath & """ """ & ScriptDir & "\run_scribe.py"""

Dim Result
Result = WshShell.Run(Command, 1, False)

If Err.Number <> 0 Then
    MsgBox "Failed to launch Scribe: " & Err.Description & vbCrLf & vbCrLf & "Command: " & Command, vbCritical, "Scribe Launcher"
End If

Set WshShell = Nothing
Set objFSO = Nothing
