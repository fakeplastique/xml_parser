import os
import pickle
from pathlib import Path
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


class GoogleAuthService:
    """
    Сервіс для управління автентифікацією Google OAuth 2.0.

    Attributes:
        SCOPES: Області доступу для Google Drive API
        TOKEN_PATH: Шлях до файлу з токеном
        CREDENTIALS_PATH: Шлях до файлу з credentials
    """

    SCOPES = [
        'https://www.googleapis.com/auth/drive',  # Повний доступ до Drive (читання всіх файлів)
        'https://www.googleapis.com/auth/spreadsheets'
    ]

    def __init__(
        self,
        credentials_path: str | Any = None,
        token_path: str | None = None
    ):
        """
        Ініціалізує сервіс автентифікації.

        Args:
            credentials_path: Шлях до файлу credentials.json
            token_path: Шлях до файлу з токеном
        """
        self.credentials_path = credentials_path or self._get_default_credentials_path()
        self.token_path = token_path or self._get_default_token_path()
        self._credentials: Credentials | Any = None

    def _get_default_credentials_path(self) -> str:
        """Повертає шлях до credentials.json за замовчуванням."""
        project_root = Path.cwd()
        return str(project_root / "credentials.json")

    def _get_default_token_path(self) -> str:
        """Повертає шлях до файлу токену за замовчуванням."""
        home = Path.home()
        config_dir = home / ".config" / "spreadsheet-app"
        config_dir.mkdir(parents=True, exist_ok=True)
        return str(config_dir / "token.pickle")

    def authenticate(self) -> Credentials | Any:
        """
        Виконує автентифікацію користувача.

        Спочатку намагається завантажити існуючі credentials з токену.
        Якщо токен недійсний або відсутній, запускає OAuth 2.0 flow.

        Returns:
            Credentials: Об'єкт з credentials користувача

        Raises:
            FileNotFoundError: Якщо файл credentials.json не знайдено
            Exception: Якщо виникла помилка під час автентифікації
        """
        creds = None

        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:

                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"Файл credentials.json не знайдено за шляхом: {self.credentials_path}\n"
                        "Будь ласка, завантажте його з Google Cloud Console."
                    )

                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path,
                    self.SCOPES
                )
                creds = flow.run_local_server(port=0)

            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)

        self._credentials = creds
        return creds

    def get_credentials(self) -> Credentials:
        """
        Повертає поточні credentials.

        Якщо credentials ще не отримані, виконує автентифікацію.

        Returns:
            Credentials або None
        """
        if not self._credentials:
            self._credentials = self.authenticate()
        return self._credentials

    def is_authenticated(self) -> bool:
        """
        Перевіряє, чи користувач автентифікований.

        Returns:
            bool: True якщо автентифікований, False інакше
        """
        try:
            creds = self.get_credentials()
            return creds is not None and creds.valid
        except Exception:
            return False

    def logout(self) -> None:
        """
        Видаляє збережений токен (вихід з акаунту).
        """
        if os.path.exists(self.token_path):
            os.remove(self.token_path)
        self._credentials = None