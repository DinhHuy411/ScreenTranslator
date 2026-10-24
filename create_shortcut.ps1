# Tạo shortcut "Screen Translator" ra Desktop (chạy bằng pythonw -> không hiện cửa sổ đen)
$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
$py  = (python -c "import sys;print(sys.executable)").Trim() -replace 'python\.exe$','pythonw.exe'
$ws  = New-Object -ComObject WScript.Shell
$lnk = $ws.CreateShortcut("$([Environment]::GetFolderPath('Desktop'))\Screen Translator.lnk")
$lnk.TargetPath       = $py
$lnk.Arguments        = "`"$dir\main.py`""
$lnk.WorkingDirectory = $dir
$lnk.IconLocation     = "$dir\icon.ico"
$lnk.Description      = "Screen Translator"
$lnk.Save()
Write-Host "Đã tạo shortcut trên Desktop."
