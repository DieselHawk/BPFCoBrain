
Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "C:\Users\Jaques\Documents\Obsidian Vault\Brain.lnk"

Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "C:\Users\Jaques\Documents\Obsidian Vault\launch-brain.bat"
oLink.WorkingDirectory = "C:\Users\Jaques\Documents\Obsidian Vault"
oLink.IconLocation = "C:\Users\Jaques\Documents\Obsidian Vault\brain-icon.ico"
oLink.Description = "Brain Desktop - Your Knowledge Vault"
oLink.WindowStyle = 1
oLink.Save
