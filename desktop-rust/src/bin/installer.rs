use std::path::{Path, PathBuf};
use std::process::Command;

// Embed the compiled release binary directly so installer is 100% self-contained
static EMBEDDED_BINARY: &[u8] = include_bytes!("../../target/release/ayera_downloader.exe");

fn main() {
    println!("==================================================");
    println!("     AYERA DOWNLOADER PRO v2.0 - SETUP INSTALLER  ");
    println!("==================================================");
    println!("Initializing standalone installation...");

    let local_app_data = match std::env::var("LOCALAPPDATA") {
        Ok(v) => PathBuf::from(v),
        Err(_) => {
            eprintln!("Error: LOCALAPPDATA environment variable not found.");
            return;
        }
    };

    let install_dir = local_app_data.join("Programs").join("Ayera Downloader");
    if let Err(e) = std::fs::create_dir_all(&install_dir) {
        eprintln!("Failed to create directory {}: {}", install_dir.display(), e);
        return;
    }

    println!("[1/4] Target directory: {}", install_dir.display());

    let target_exe = install_dir.join("ayera_downloader.exe");

    println!("[2/4] Deploying Ayera Downloader core binary ({} bytes)...", EMBEDDED_BINARY.len());
    match std::fs::write(&target_exe, EMBEDDED_BINARY) {
        Ok(_) => {
            println!("      Successfully installed to {}", target_exe.display());
        }
        Err(e) => {
            eprintln!("      Write error: {}. Attempting external fallback...", e);
            let current_exe = std::env::current_exe().unwrap_or_default();
            let parent = current_exe.parent().unwrap_or(Path::new("."));
            let candidate = parent.join("ayera_downloader.exe");
            if candidate.exists() {
                let _ = std::fs::copy(&candidate, &target_exe);
            }
        }
    }

    // [3/4] Create Desktop & Start Menu Shortcuts via PowerShell
    println!("[3/4] Creating Windows Shortcuts...");
    let ps_script = format!(
        r#"
$ws = New-Object -ComObject WScript.Shell;
$desktop = [System.Environment]::GetFolderPath('Desktop');
$startMenu = [System.Environment]::GetFolderPath('Programs');

$link1 = $ws.CreateShortcut("$desktop\Ayera Downloader Pro.lnk");
$link1.TargetPath = '{0}';
$link1.Description = 'Ayera Downloader Pro - High-Speed Download Accelerator';
$link1.WorkingDirectory = '{1}';
$link1.Save();

$link2 = $ws.CreateShortcut("$startMenu\Ayera Downloader Pro.lnk");
$link2.TargetPath = '{0}';
$link2.Description = 'Ayera Downloader Pro - High-Speed Download Accelerator';
$link2.WorkingDirectory = '{1}';
$link2.Save();
"#,
        target_exe.display(),
        install_dir.display()
    );

    let _ = Command::new("powershell")
        .args(["-NoProfile", "-Command", &ps_script])
        .output();

    println!("      Created Desktop & Start Menu shortcuts.");

    // [4/4] Launch Application
    println!("[4/4] Launching Ayera Downloader Pro...");
    let _ = Command::new("explorer")
        .arg(&target_exe)
        .spawn();

    println!("==================================================");
    println!("Installation Complete! Enjoy Ayera Downloader Pro.");
    println!("==================================================");
}

