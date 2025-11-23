import asyncio
import logging
from typing import Any

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .google_auth_service import GoogleAuthService
from .drive_file_writer import create_drive_writer


logger = logging.getLogger(__name__)


class GoogleDriveDocumentStorage:
    """
    Сервіс для роботи з XML/HTML документами на Google Drive.

    Надає методи для:
    - Отримання списку XML/HTML файлів
    - Завантаження документів на Google Drive
    - Скачування документів з Google Drive
    - Видалення документів
    """

    def __init__(self, auth_service: GoogleAuthService):
        """
        Ініціалізує сервіс Google Drive Document Storage.

        Args:
            auth_service: Сервіс автентифікації
        """
        self.auth_service = auth_service
        self._drive_service = None

    def _get_drive_service(self):
        """Повертає сервіс Google Drive API."""
        if not self._drive_service:
            creds = self.auth_service.get_credentials()
            self._drive_service = build('drive', 'v3', credentials=creds)
        return self._drive_service

    async def list_documents(
        self,
        file_types: list[str] | None = None
    ) -> list[dict[str, str]]:
        """
        Отримує список XML/HTML документів користувача.

        Args:
            file_types: Список типів файлів для фільтрації ['xml', 'html', 'xsl']
                       None - для всіх підтримуваних типів

        Returns:
            list[dict]: Список словників з інформацією про файли:
                - id: ID файлу
                - name: Назва файлу
                - mimeType: MIME тип
                - modifiedTime: Час останньої модифікації

        Raises:
            Exception: Якщо виникла помилка при отриманні списку файлів
        """
        loop = asyncio.get_event_loop()

        if file_types is None:
            file_types = ['xml', 'html', 'xsl']

        # Створення запиту для фільтрації по MIME типам
        mime_types = []
        for ft in file_types:
            if ft.lower() == 'xml':
                mime_types.append("mimeType='application/xml'")
                mime_types.append("mimeType='text/xml'")
            elif ft.lower() == 'html':
                mime_types.append("mimeType='text/html'")
            elif ft.lower() == 'xsl':
                mime_types.append("mimeType='application/xslt+xml'")
                mime_types.append("mimeType='text/xsl'")

        query = ' or '.join(mime_types) if mime_types else None

        try:
            drive_service = self._get_drive_service()

            response = await loop.run_in_executor(
                None,
                lambda: drive_service.files().list(
                    q=query,
                    spaces='drive',
                    fields='files(id, name, mimeType, modifiedTime)',
                    orderBy='modifiedTime desc'
                ).execute()
            )

            files = response.get('files', [])
            logger.info(f"Знайдено {len(files)} документів")

            return files

        except HttpError as error:
            logger.error(f"Помилка при отриманні списку документів: {error}")
            raise Exception(f"Не вдалося отримати список документів: {error}")

    async def upload_document(
        self,
        content: str,
        file_name: str,
        format_type: str,
        file_id: str | None = None
    ) -> str:
        """
        Завантажує документ на Google Drive.

        Args:
            content: Контент документу (HTML або XML рядок)
            file_name: Назва файлу
            format_type: Тип формату ('html' або 'xml')
            file_id: ID існуючого файлу (якщо потрібно оновити), None для нового

        Returns:
            str: ID створеного/оновленого файлу

        Raises:
            Exception: Якщо виникла помилка при завантаженні
        """
        try:
            # Використання фабричного методу для створення writer'а
            writer = create_drive_writer(format_type, self.auth_service)

            # Збереження через writer
            file_id = await writer.save_to_drive(content, file_name, file_id)

            logger.info(f"Завантажено документ {file_name} ({format_type})")
            return file_id

        except Exception as error:
            logger.error(f"Помилка при завантаженні документу: {error}")
            raise

    async def download_document(self, file_id: str) -> dict[str, Any]:
        """
        Завантажує документ з Google Drive.

        Args:
            file_id: ID файлу

        Returns:
            dict: Словник з даними:
                - content: Контент файлу
                - name: Назва файлу
                - mimeType: MIME тип

        Raises:
            Exception: Якщо виникла помилка при завантаженні
        """
        loop = asyncio.get_event_loop()

        try:
            drive_service = self._get_drive_service()

            # Отримання метаданих файлу
            file_metadata = await loop.run_in_executor(
                None,
                lambda: drive_service.files().get(
                    fileId=file_id,
                    fields='name, mimeType'
                ).execute()
            )

            # Завантаження контенту
            content_bytes = await loop.run_in_executor(
                None,
                lambda: drive_service.files().get_media(
                    fileId=file_id
                ).execute()
            )

            content = content_bytes.decode('utf-8')

            logger.info(f"Завантажено документ {file_id}: {file_metadata['name']}")

            return {
                'content': content,
                'name': file_metadata['name'],
                'mimeType': file_metadata['mimeType']
            }

        except HttpError as error:
            logger.error(f"Помилка при завантаженні документу {file_id}: {error}")
            raise Exception(f"Не вдалося завантажити документ: {error}")

    async def delete_document(self, file_id: str) -> None:
        """
        Видаляє документ з Google Drive.

        Args:
            file_id: ID файлу для видалення

        Raises:
            Exception: Якщо виникла помилка при видаленні
        """
        loop = asyncio.get_event_loop()

        try:
            drive_service = self._get_drive_service()

            await loop.run_in_executor(
                None,
                lambda: drive_service.files().delete(
                    fileId=file_id
                ).execute()
            )

            logger.info(f"Видалено документ {file_id}")

        except HttpError as error:
            logger.error(f"Помилка при видаленні документу {file_id}: {error}")
            raise Exception(f"Не вдалося видалити документ: {error}")

    def reset_service(self):
        """Скидає кешований об'єкт сервісу Google Drive."""
        self._drive_service = None
