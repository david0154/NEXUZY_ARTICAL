; NEXUZY ARTICAL - Complete Inno Setup Script
; Includes: EXE + ALL configs + logo + icon + assets + docs
; Version: 3.0
; Author: Manoj Konar (monoj@nexuzy.in)

#define MyAppName "NEXUZY ARTICAL"
#define MyAppVersion "2.1"
#define MyAppPublisher "Nexuzy Tech Pvt Ltd"
#define MyAppURL "https://github.com/david0154/NEXUZY_ARTICAL"
#define MyAppExeName "NEXUZY_ARTICAL.exe"
#define MyAppDeveloper "Manoj Konar (monoj@nexuzy.in)"

[Setup]
; Unique GUID - DO NOT CHANGE!
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
OutputDir=installer_output
OutputBaseFilename=NEXUZY_ARTICAL_Setup_v{#MyAppVersion}
SetupIconFile=assets\icon.ico
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\{#MyAppExeName}
WizardImageFile=compiler:WizModernImage-IS.bmp
WizardSmallImageFile=compiler:WizModernSmallImage-IS.bmp

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1

[Files]
; ==============================
; MAIN EXECUTABLE
; ==============================
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; ==============================
; CONFIG TEMPLATES
; ==============================
Source: "dist\firebase_config.json.example"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\ftp_config.json.example"; DestDir: "{app}"; Flags: ignoreversion

; ==============================
; ASSETS (Logo, Icon, Images)
; ==============================
Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs

; ==============================
; CONFIG FOLDER
; ==============================
Source: "config\*"; DestDir: "{app}\config"; Flags: ignoreversion recursesubdirs createallsubdirs onlyifdoesntexist uninsneveruninstall

; ==============================
; DOCUMENTATION
; ==============================
Source: "dist\README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme
Source: "dist\SETUP_INSTRUCTIONS.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\QUICK_START.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\FIREBASE_SETUP.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\FTP_SETUP.md"; DestDir: "{app}"; Flags: ignoreversion

[Dirs]
; Create directories for runtime data
Name: "{app}\data"; Permissions: users-full
Name: "{app}\logs"; Permissions: users-full
Name: "{app}\config"; Permissions: users-full
Name: "{app}\assets"; Permissions: users-full
Name: "{app}\image_cache"; Permissions: users-full

[Icons]
; Start Menu
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\icon.ico"
Name: "{group}\Setup Instructions"; Filename: "{app}\SETUP_INSTRUCTIONS.txt"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

; Desktop
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\icon.ico"; Tasks: desktopicon

; Quick Launch
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\icon.ico"; Tasks: quicklaunchicon

[Run]
; Open setup instructions after install
Filename: "{app}\SETUP_INSTRUCTIONS.txt"; Description: "View Setup Instructions"; Flags: postinstall shellexec skipifsilent

; Offer to run the application
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
// ============================================
// CUSTOM INSTALLATION CODE
// ============================================

var
  ConfigPage: TInputQueryWizardPage;
  SetupFirebase, SetupFTP: Boolean;

// Show welcome message
function InitializeSetup(): Boolean;
begin
  Result := True;
  MsgBox(
    'Welcome to NEXUZY ARTICAL Setup!' + #13#10 + #13#10 +
    'This installer includes:' + #13#10 +
    '  • Main Application' + #13#10 +
    '  • Logo & Icon Assets' + #13#10 +
    '  • Config Templates (Firebase & FTP)' + #13#10 +
    '  • Complete Documentation' + #13#10 + #13#10 +
    'The app works offline by default.' + #13#10 +
    'Configuration is optional for cloud features.',
    mbInformation, MB_OK
  );
end;

// Create configuration options page
procedure InitializeWizard();
begin
  ConfigPage := CreateInputQueryPage(
    wpSelectTasks,
    'Configuration Options',
    'Do you want to set up cloud features now?',
    'The application works offline by default. ' +
    'Cloud features require Firebase (sync) and FTP (image upload) configuration.'
  );
  
  ConfigPage.Add('Setup Firebase (cloud sync)?', False);
  ConfigPage.Add('Setup FTP (image upload)?', False);
end;

// Post-installation tasks
procedure CurStepChanged(CurStep: TSetupStep);
var
  InstructionsText: String;
begin
  if CurStep = ssPostInstall then
  begin
    // Get user choices
    SetupFirebase := ConfigPage.Values[0];
    SetupFTP := ConfigPage.Values[1];
    
    // Create FIRST_RUN.txt with instructions
    InstructionsText :=
      'NEXUZY ARTICAL - FIRST RUN INSTRUCTIONS' + #13#10 +
      '========================================' + #13#10 + #13#10 +
      'Installation completed successfully!' + #13#10 + #13#10;
    
    if SetupFirebase or SetupFTP then
    begin
      InstructionsText := InstructionsText +
        'NEXT STEPS:' + #13#10 +
        '----------' + #13#10;
      
      if SetupFirebase then
        InstructionsText := InstructionsText +
          '1. FIREBASE SETUP:' + #13#10 +
          '   - Rename firebase_config.json.example to firebase_config.json' + #13#10 +
          '   - Edit with your Firebase credentials' + #13#10 +
          '   - See FIREBASE_SETUP.md for detailed guide' + #13#10 + #13#10;
      
      if SetupFTP then
        InstructionsText := InstructionsText +
          '2. FTP SETUP:' + #13#10 +
          '   - Rename ftp_config.json.example to ftp_config.json' + #13#10 +
          '   - Edit with your FTP server details' + #13#10 +
          '   - See FTP_SETUP.md for detailed guide' + #13#10 + #13#10;
    end
    else
    begin
      InstructionsText := InstructionsText +
        'OFFLINE MODE ENABLED' + #13#10 +
        '-------------------' + #13#10 +
        'App will run in offline mode (local database only).' + #13#10 +
        'To enable cloud features later, see SETUP_INSTRUCTIONS.txt' + #13#10 + #13#10;
    end;
    
    InstructionsText := InstructionsText +
      'DEFAULT LOGIN:' + #13#10 +
      '--------------' + #13#10 +
      'Username: admin' + #13#10 +
      'Password: admin123' + #13#10 + #13#10 +
      '!!! CHANGE PASSWORD AFTER FIRST LOGIN !!!' + #13#10 + #13#10 +
      'INSTALLED FILES:' + #13#10 +
      '---------------' + #13#10 +
      '  • NEXUZY_ARTICAL.exe - Main application' + #13#10 +
      '  • assets/ - Logo and icon files' + #13#10 +
      '  • config/ - User configurations' + #13#10 +
      '  • data/ - Local database' + #13#10 +
      '  • logs/ - Application logs' + #13#10 +
      '  • image_cache/ - Cached images' + #13#10 +
      '  • *_config.json.example - Config templates' + #13#10 +
      '  • *.md files - Documentation' + #13#10 + #13#10 +
      'For detailed instructions, see SETUP_INSTRUCTIONS.txt' + #13#10 + #13#10 +
      'Developer: ' + '{#MyAppDeveloper}' + #13#10 +
      'GitHub: ' + '{#MyAppURL}' + #13#10;
    
    SaveStringToFile(
      ExpandConstant('{app}\FIRST_RUN.txt'),
      InstructionsText,
      False
    );
  end;
end;

// Show completion message
procedure CurPageChanged(CurPageID: Integer);
begin
  if CurPageID = wpFinished then
  begin
    MsgBox(
      'Installation Complete!' + #13#10 + #13#10 +
      'All files including configs, logo, and documentation' + #13#10 +
      'have been installed successfully.' + #13#10 + #13#10 +
      'Check SETUP_INSTRUCTIONS.txt for configuration guide.' + #13#10 + #13#10 +
      'Default login: admin / admin123',
      mbInformation, MB_OK
    );
  end;
end;

[UninstallDelete]
; Clean up generated files (keep user data)
Type: files; Name: "{app}\*.log"
Type: files; Name: "{app}\FIRST_RUN.txt"
Type: filesandordirs; Name: "{app}\__pycache__"
Type: filesandordirs; Name: "{app}\logs\*"

; NOTE: User configs, database, and cached images are preserved
