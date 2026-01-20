; Inno Setup Script for NEXUZY ARTICAL
; Author: Manoj Konar (monoj@nexuzy.in)
; Version: 1.0.0

[Setup]
AppName=NEXUZY ARTICAL
AppVersion=1.0.0
AppPublisher=Nexuzy
AppPublisherURL=https://nexuzy.in
AppSupportURL=https://github.com/david0154/NEXUZY_ARTICAL
AppUpdatesURL=https://github.com/david0154/NEXUZY_ARTICAL
DefaultDirName={pf}\NexuzyArtical
DefaultGroupName=Nexuzy\NEXUZY ARTICAL
SetupIconFile=assets\icon.ico
UninstallDisplayIcon={app}\NEXUZY_ARTICAL.exe
LicenseFile=LICENSE.txt
OutputDir=build\output
OutputBaseFilename=NEXUZY_ARTICAL_Installer
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ShowLanguageDialog=no
LanguageDetectionMethod=locale

[Files]
Source: "dist\NEXUZY_ARTICAL.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "assets\icon.ico"; DestDir: "{app}\assets"; Flags: ignoreversion
Source: "assets\logo.png"; DestDir: "{app}\assets"; Flags: ignoreversion
Source: "assets\logo.ico"; DestDir: "{app}\assets"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\NEXUZY ARTICAL"; Filename: "{app}\NEXUZY_ARTICAL.exe"; IconFilename: "{app}\assets\icon.ico"
Name: "{commondesktop}\NEXUZY ARTICAL"; Filename: "{app}\NEXUZY_ARTICAL.exe"; IconFilename: "{app}\assets\icon.ico"
Name: "{group}\README"; Filename: "{app}\README.md"
Name: "{group}\Uninstall"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\NEXUZY_ARTICAL.exe"; Description: "Launch NEXUZY ARTICAL"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: dirifempty; Name: "{app}"
Type: dirifempty; Name: "{app}\assets"

[Messages]
WelcomeLabel1=Welcome to NEXUZY ARTICAL Setup
WelcomeLabel2=This will install NEXUZY ARTICAL on your computer.

[CustomMessages]
ProductName=NEXUZY ARTICAL v1.0.0
