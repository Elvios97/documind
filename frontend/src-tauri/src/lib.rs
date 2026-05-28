use std::{
    env,
    net::{SocketAddr, TcpStream},
    path::PathBuf,
    process::{Child, Command, Stdio},
    sync::Mutex,
    thread,
    time::{Duration, Instant},
};

use tauri::Manager;

const BACKEND_HOST: &str = "127.0.0.1";
const BACKEND_PORT: u16 = 8000;
const BACKEND_READY_TIMEOUT: Duration = Duration::from_secs(15);
const BACKEND_CHECK_INTERVAL: Duration = Duration::from_millis(250);

#[derive(Default)]
struct BackendProcess {
    child: Mutex<Option<Child>>,
}

impl BackendProcess {
    fn set(&self, child: Child) {
        if let Ok(mut current_child) = self.child.lock() {
            *current_child = Some(child);
        }
    }
}

impl Drop for BackendProcess {
    fn drop(&mut self) {
        if let Ok(mut child) = self.child.lock() {
            if let Some(child) = child.as_mut() {
                let _ = child.kill();
                let _ = child.wait();
            }
        }
    }
}

struct BackendCommand {
    label: String,
    program: PathBuf,
    args: Vec<String>,
    current_dir: Option<PathBuf>,
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .manage(BackendProcess::default())
        .setup(|app| {
            if cfg!(debug_assertions) {
                app.handle().plugin(
                    tauri_plugin_log::Builder::default()
                        .level(log::LevelFilter::Info)
                        .build(),
                )?;
            }

            match ensure_backend_running() {
                Ok(Some(child)) => {
                    app.state::<BackendProcess>().set(child);
                    log::info!("Documind backend wurde automatisch gestartet.");
                }
                Ok(None) => {
                    log::info!("Documind backend laeuft bereits.");
                }
                Err(error) => {
                    log::warn!(
                        "Documind backend konnte nicht automatisch gestartet werden: {error}"
                    );
                }
            }

            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

fn ensure_backend_running() -> Result<Option<Child>, String> {
    if is_backend_running() {
        return Ok(None);
    }

    let commands = backend_commands();
    if commands.is_empty() {
        return Err("kein Backend-Startkandidat gefunden".to_string());
    }

    let mut errors = Vec::new();

    for backend_command in commands {
        match spawn_backend(&backend_command) {
            Ok(mut child) => {
                if wait_until_backend_ready(BACKEND_READY_TIMEOUT) {
                    return Ok(Some(child));
                }

                let _ = child.kill();
                let _ = child.wait();
                errors.push(format!(
                    "{} wurde gestartet, aber der Healthcheck blieb offline",
                    backend_command.label
                ));
            }
            Err(error) => {
                errors.push(format!("{}: {error}", backend_command.label));
            }
        }
    }

    Err(errors.join("; "))
}

fn backend_commands() -> Vec<BackendCommand> {
    let mut commands = Vec::new();

    if let Ok(path) = env::var("DOCUMIND_BACKEND_EXE") {
        let program = PathBuf::from(path);
        if program.exists() {
            commands.push(BackendCommand {
                label: format!("DOCUMIND_BACKEND_EXE ({})", program.display()),
                program,
                args: Vec::new(),
                current_dir: None,
            });
        }
    }

    if let Ok(current_exe) = env::current_exe() {
        if let Some(app_dir) = current_exe.parent() {
            let bundled_backend = app_dir.join(backend_executable_name());
            if bundled_backend.exists() {
                commands.push(BackendCommand {
                    label: format!("gebuendeltes Backend ({})", bundled_backend.display()),
                    program: bundled_backend,
                    args: Vec::new(),
                    current_dir: Some(app_dir.to_path_buf()),
                });
            }
        }
    }

    if cfg!(debug_assertions) {
        let backend_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
            .join("..")
            .join("..")
            .join("backend");
        let python = backend_dir.join(venv_python_path());

        if python.exists() {
            commands.push(BackendCommand {
                label: format!("lokale Backend-venv ({})", python.display()),
                program: python,
                args: vec![
                    "-m".to_string(),
                    "uvicorn".to_string(),
                    "main:app".to_string(),
                    "--host".to_string(),
                    BACKEND_HOST.to_string(),
                    "--port".to_string(),
                    BACKEND_PORT.to_string(),
                ],
                current_dir: Some(backend_dir),
            });
        }
    }

    commands
}

fn spawn_backend(backend_command: &BackendCommand) -> Result<Child, String> {
    let mut command = Command::new(&backend_command.program);
    command
        .args(&backend_command.args)
        .stdin(Stdio::null())
        .stdout(Stdio::null())
        .stderr(Stdio::null());

    if let Some(current_dir) = &backend_command.current_dir {
        command.current_dir(current_dir);
    }

    hide_backend_window(&mut command);

    command.spawn().map_err(|error| error.to_string())
}

fn wait_until_backend_ready(timeout: Duration) -> bool {
    let deadline = Instant::now() + timeout;

    while Instant::now() < deadline {
        if is_backend_running() {
            return true;
        }

        thread::sleep(BACKEND_CHECK_INTERVAL);
    }

    false
}

fn is_backend_running() -> bool {
    let address = SocketAddr::from(([127, 0, 0, 1], BACKEND_PORT));
    TcpStream::connect_timeout(&address, BACKEND_CHECK_INTERVAL).is_ok()
}

#[cfg(windows)]
fn hide_backend_window(command: &mut Command) {
    use std::os::windows::process::CommandExt;

    const CREATE_NO_WINDOW: u32 = 0x08000000;
    command.creation_flags(CREATE_NO_WINDOW);
}

#[cfg(not(windows))]
fn hide_backend_window(_command: &mut Command) {}

#[cfg(windows)]
fn backend_executable_name() -> &'static str {
    "documind-backend.exe"
}

#[cfg(not(windows))]
fn backend_executable_name() -> &'static str {
    "documind-backend"
}

#[cfg(windows)]
fn venv_python_path() -> PathBuf {
    PathBuf::from(".venv").join("Scripts").join("python.exe")
}

#[cfg(not(windows))]
fn venv_python_path() -> PathBuf {
    PathBuf::from(".venv").join("bin").join("python")
}
