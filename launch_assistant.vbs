Set WshShell = CreateObject("WScript.Shell") 
WshShell.CurrentDirectory = "D:\PROJECTS\pdf convert tool" 
WshShell.Run """C:\Python313\pythonw.exe"" ""unified_manual_assistant.py""", 0, False 
