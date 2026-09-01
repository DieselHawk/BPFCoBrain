
Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = oWS.SpecialFolders("Desktop") & "\Brain.lnk"

Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "C:\BPFCo\BPFCoBrain\launch-brain.bat"
oLink.WorkingDirectory = "C:\BPFCo\BPFCoBrain"
oLink.IconLocation = "C:\BPFCo\BPFCoBrain\brain-icon.ico"
oLink.Description = "Brain Desktop - Your Knowledge Vault"
oLink.WindowStyle = 1
oLink.Save
