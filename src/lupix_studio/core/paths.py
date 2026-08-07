from pathlib import Path

APP_NAME = "LupixStudio"


def user_data_dir() -> Path:
    """Diretório de dados persistentes do Lupix Studio."""
    return Path.home() / ".lupixstudio"


def logs_dir() -> Path:
    """Diretório de logs."""
    return user_data_dir() / "logs"


def settings_file() -> Path:
    """Arquivo de configurações."""
    return user_data_dir() / "settings.json"


def ensure_directories() -> None:
    """Cria os diretórios necessários."""
    user_data_dir().mkdir(parents=True, exist_ok=True)
    logs_dir().mkdir(parents=True, exist_ok=True)