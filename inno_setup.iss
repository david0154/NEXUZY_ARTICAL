; Enhanced Inno Setup Script for NEXUZY ARTICAL
; Includes: EXE, configs, assets, documentation

#define MyAppName "NEXUZY ARTICAL"
#define MyAppVersion "2.1"
#define MyAppPublisher "Nexuzy Tech Pvt Ltd"
#define MyAppURL "https://github.com/david0154/NEXUZY_ARTICAL"
#define MyAppExeName "NEXUZY_ARTICAL.exe"

[Setup]
AppId={{A8F9E7D6-4C3B-4A5E-9F1D-2E8C7B6A5D4C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=LICENSE
OutputDir=installer_output
OutputBaseFilename=NEXUZY_ARTICAL_Setup_v{#MyAppVersion}
SetupIconFile=assets\icon.ico
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Main executable
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Config templates (users will rename .example to actual config)
Source: "dist\firebase_config.json.example"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\ftp_config.json.example"; DestDir: "{app}"; Flags: ignoreversion

; Assets folder (logo, icon)
Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs

; Documentation
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme
Source: "FIXES.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "QUICK_START.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "FIREBASE_SETUP.md"; DestDir: "{app}"; Flags: ignoreversion

; Config folder (for saved credentials)
Source: "config\*"; DestDir: "{app}\config"; Flags: ignoreversion recursesubdirs createallsubdirs onlyifdoesntexist

[Dirs]
; Create directories that app will use
Name: "{app}\data"; Permissions: users-full
Name: "{app}\logs"; Permissions: users-full
Name: "{app}\config"; Permissions: users-full
Name: "{app}\assets"; Permissions: users-full

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
; Offer to run the application after installation
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
// Custom code for post-install configuration
function InitializeSetup(): Boolean;
begin
  Result := True;
  MsgBox('Welcome to NEXUZY ARTICAL Setup!' + #13#10 + #13#10 +
         'After installation, you will need to:' + #13#10 +
         '1. Rename firebase_config.json.example to firebase_config.json' + #13#10 +
         '2. Rename ftp_config.json.example to ftp_config.json' + #13#10 +
         '3. Edit both files with your credentials' + #13#10 + #13#10 +
         'The application will work offline without these configs.', 
         mbInformation, MB_OK);
end;

procedure CurStepChanged(CurStep: TSetupStep):
begin
  if CurStep = ssPostInstall then
  begin
    // Create default admin user instructions file
    SaveStringToFile(ExpandConstant('{app}\FIRST_RUN.txt'),
      'FIRST RUN INSTRUCTIONS' + #13#10 +
      '=====================' + #13#10 + #13#10 +
      '1. FIREBASE CONFIGURATION (Optional for cloud sync):' + #13#10 +
      '   - Rename firebase_config.json.example to firebase_config.json' + #13#10 +
      '   - Edit with your Firebase credentials' + #13#10 + #13#10 +
      '2. FTP CONFIGURATION (Optional for image upload):' + #13#10 +
      '   - Rename ftp_config.json.example to ftp_config.json' + #13#10 +
      '   - Edit with your FTP server details' + #13#10 + #13#10 +
      '3. OFFLINE MODE:' + #13#10 +
      '   - App works without configs (local database only)' + #13#10 + #13#10 +
      '4. FIRST LOGIN:' + #13#10 +
      '   - If Firebase configured: Downloads existing data automatically' + #13#10 +
      '   - Create admin user from Admin Dashboard' + #13#10 + #13#10 +
      'For detailed setup guide, see FIREBASE_SETUP.md' + #13#10,
      False);
  end;
end;

[UninstallDelete]
; Clean up generated files on uninstall (but keep user data)
Type: files; Name: "{app}\*.log"
Type: filesandordirs; Name: "{app}\__pycache__"
