; NEXUZY ARTICAL - Inno Setup Installer Script
; Creates professional Windows installer for the application
; Author: Manoj Konar (monoj@nexuzy.in)

#define MyAppName "NEXUZY ARTICAL"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Nexuzy"
#define MyAppURL "https://nexuzy.in"
#define MyAppExeName "NEXUZY_ARTICAL.exe"
#define MyAppAssocName MyAppName + " File"
#define MyAppAssocExt ".nxa"
#define MyAppAssocKey StringChange(MyAppAssocName, " ", "") + MyAppAssocExt

[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{8E2F4A3B-9C1D-4E5F-A2B3-6D7E8F9A0B1C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
; Uncomment the following line to run in non administrative install mode (install for current user only.)
;PrivilegesRequired=lowest
OutputDir=installer_output
OutputBaseFilename=NEXUZY_ARTICAL_Setup_v{#MyAppVersion}
SetupIconFile=assets\icon.ico
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
begin
  Result := True;
  
  // Check if application is already running
  if CheckForMutexes('NEXUZY_ARTICAL_MUTEX') then
  begin
    if MsgBox('NEXUZY ARTICAL is currently running. Please close it before continuing installation.', mbError, MB_OKCANCEL) = IDOK then
    begin
      Result := False;
    end;
  end;
end;

function InitializeUninstall(): Boolean;
var
  ResultCode: Integer;
begin
  Result := True;
  
  // Check if application is running before uninstall
  if CheckForMutexes('NEXUZY_ARTICAL_MUTEX') then
  begin
    if MsgBox('NEXUZY ARTICAL is currently running. Please close it before continuing.', mbError, MB_OKCANCEL) = IDOK then
    begin
      Result := False;
    end;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Create necessary directories
    CreateDir(ExpandConstant('{app}\data'));
    CreateDir(ExpandConstant('{app}\logs'));
    CreateDir(ExpandConstant('{app}\exports'));
  end;
end;

[UninstallDelete]
Type: filesandordirs; Name: "{app}\data"
Type: filesandordirs; Name: "{app}\logs"
Type: filesandordirs; Name: "{app}\exports"
Type: filesandordirs; Name: "{app}\__pycache__"

[Messages]
WelcomeLabel2=This will install [name/ver] on your computer.%n%nNEXUZY ARTICAL is an offline-first article management application with Firebase synchronization.%n%nDeveloped by Manoj Konar%nEmail: monoj@nexuzy.in%n%nIt is recommended that you close all other applications before continuing.
