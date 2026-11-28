; BOYDE Atölye kurulum dosyası (Inno Setup 6): Python'suz, bat'sız; kur, masaüstündeki simgeyle aç.
; GitHub Actions'ta derlenir (.github/workflows/atolye-windows.yml). Kaynak klasörü scripts/atolye_windows.py hazırlar
; (build\BOYDE_Atolye); simge konsolsuz başlatıcıyı açar (atolye/masaustu.py).
; Yönetici izni istemez: kullanıcının klasörüne kurulur (%LOCALAPPDATA%\Programs\BOYDE Atolye). Müşteri kayıtları
; Belgeler\BOYDE Atolye'de; güncelleme ve kaldırma onlara dokunmaz.

#ifndef Surum
  #define Surum "1.0.0"
#endif

[Setup]
AppId={{5B7E2C1A-8E3D-4C4B-9F2A-B0D1E7A3C9F4}
AppName=BOYDE Atölye
AppVersion={#Surum}
AppVerName=BOYDE Atölye {#Surum}
AppPublisher=BOYDE LABS
DefaultDirName={autopf}\BOYDE Atolye
DefaultGroupName=BOYDE Atölye
DisableDirPage=yes
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=..\..\dist
OutputBaseFilename=BOYDE_Atolye_Kurulum
SetupIconFile=BOYDE_Atolye.ico
UninstallDisplayIcon={app}\BOYDE_Atolye.ico
UninstallDisplayName=BOYDE Atölye
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "tr"; MessagesFile: "compiler:Languages\Turkish.isl"

[Tasks]
Name: "masaustu"; Description: "Masaüstüne BOYDE Atölye simgesi koy"; GroupDescription: "Simgeler:"

[InstallDelete]
; güncellemede eski sürümün dosyaları kalmasın
Type: filesandordirs; Name: "{app}\atolye"
Type: filesandordirs; Name: "{app}\scripts"
Type: filesandordirs; Name: "{app}\python"
Type: filesandordirs; Name: "{app}\tarayici"

[Files]
Source: "..\..\build\BOYDE_Atolye\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\BOYDE Atölye"; Filename: "{app}\python\pythonw.exe"; Parameters: "-m atolye.masaustu"; WorkingDir: "{app}"; IconFilename: "{app}\BOYDE_Atolye.ico"; Comment: "Sipariş, katalog ve baskı dosyaları"
Name: "{autodesktop}\BOYDE Atölye"; Filename: "{app}\python\pythonw.exe"; Parameters: "-m atolye.masaustu"; WorkingDir: "{app}"; IconFilename: "{app}\BOYDE_Atolye.ico"; Comment: "Sipariş, katalog ve baskı dosyaları"; Tasks: masaustu

[Run]
Filename: "{app}\python\pythonw.exe"; Parameters: "-m atolye.masaustu"; WorkingDir: "{app}"; Description: "BOYDE Atölye'yi şimdi aç"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
Type: filesandordirs; Name: "{localappdata}\BOYDE Atolye\pencere"
