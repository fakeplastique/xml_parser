import asyncio
import logging
from abc import ABC, abstractmethod
from io import BytesIO
from typing import Any

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload

from .google_auth_service import GoogleAuthService


logger = logging.getLogger(__name__)


class GoogleDriveFileWriter(ABC):
    """
    Базовий абстрактний клас для збереження файлів на Google Drive.

    Використовує патерн Factory Method для створення конкретних writer'ів.
    Відповідальність: надає шаблон для збереження файлів різних форматів.
    """

    def __init__(self, auth_service: GoogleAuthService):
        """
        Ініціалізує writer.

        Args:
            auth_service: Сервіс автентифікації Google
        """
        self.auth_service = auth_service
        self._drive_service = None

    def _get_drive_service(self):
        """Повертає сервіс Google Drive API."""
        if not self._drive_service:
            creds = self.auth_service.get_credentials()
            self._drive_service = build('drive', 'v3', credentials=creds)
        return self._drive_service

    @abstractmethod
    def _prepare_content(self, data: Any) -> str:
        """
        Фабричний метод для підготовки контенту в конкретному форматі.

        Args:
            data: Дані для конвертації

        Returns:
            str: Підготовлений контент
        """
        pass

    @abstractmethod
    def _get_mime_type(self) -> str:
        """
        Повертає MIME тип для конкретного формату файлу.

        Returns:
            str: MIME тип
        """
        pass

    async def save_to_drive(
        self,
        data: Any,
        file_name: str,
        file_id: str | None = None
    ) -> str:
        """
        Зберігає файл на Google Drive.

        Args:
            data: Дані для збереження
            file_name: Назва файлу
            file_id: ID існуючого файлу (для оновлення) або None для нового

        Returns:
            str: ID створеного/оновленого файлу

        Raises:
            Exception: Якщо виникла помилка при збереженні
        """
        loop = asyncio.get_event_loop()

        try:
            # Підготовка контенту через фабричний метод
            content = self._prepare_content(data)

            # Створення медіа об'єкту
            media = MediaIoBaseUpload(
                BytesIO(content.encode('utf-8')),
                mimetype=self._get_mime_type(),
                resumable=True
            )

            drive_service = self._get_drive_service()

            if file_id:
                # Оновлення існуючого файлу
                result = await loop.run_in_executor(
                    None,
                    lambda: drive_service.files().update(
                        fileId=file_id,
                        media_body=media
                    ).execute()
                )
                logger.info(f"Оновлено файл {file_id}: {file_name}")
                return file_id
            else:
                # Створення нового файлу
                file_metadata = {
                    'name': file_name,
                    'mimeType': self._get_mime_type()
                }

                result = await loop.run_in_executor(
                    None,
                    lambda: drive_service.files().create(
                        body=file_metadata,
                        media_body=media,
                        fields='id'
                    ).execute()
                )

                new_file_id = result.get('id')
                logger.info(f"Створено новий файл {new_file_id}: {file_name}")
                return new_file_id

        except HttpError as error:
            logger.error(f"Помилка при збереженні файлу: {error}")
            raise Exception(f"Не вдалося зберегти файл: {error}")

    async def download_from_drive(self, file_id: str) -> str:
        """
        Завантажує файл з Google Drive.

        Args:
            file_id: ID файлу

        Returns:
            str: Контент файлу

        Raises:
            Exception: Якщо виникла помилка при завантаженні
        """
        loop = asyncio.get_event_loop()

        try:
            drive_service = self._get_drive_service()

            result = await loop.run_in_executor(
                None,
                lambda: drive_service.files().get_media(
                    fileId=file_id
                ).execute()
            )

            content = result.decode('utf-8')
            logger.info(f"Завантажено файл {file_id}, розмір: {len(content)} байт")
            return content

        except HttpError as error:
            logger.error(f"Помилка при завантаженні файлу {file_id}: {error}")
            raise Exception(f"Не вдалося завантажити файл: {error}")

    def reset_service(self):
        """Скидає кешований об'єкт сервісу Google Drive."""
        self._drive_service = None


class HTMLDriveWriter(GoogleDriveFileWriter):
    """
    Конкретний writer для збереження HTML файлів на Google Drive.
    """

    def _prepare_content(self, data: Any) -> str:
        """
        Підготовка HTML контенту.

        Args:
            data: HTML контент як рядок або dict з результатами трансформації

        Returns:
            str: HTML контент
        """
        if isinstance(data, str):
            return data
        elif isinstance(data, dict) and 'html_content' in data:
            return data['html_content']
        else:
            raise ValueError("Невірний формат даних для HTML writer")

    def _get_mime_type(self) -> str:
        """Повертає MIME тип для HTML."""
        return 'text/html'


class XMLDriveWriter(GoogleDriveFileWriter):
    """
    Конкретний writer для збереження XML файлів на Google Drive.
    """

    def _prepare_content(self, data: Any) -> str:
        """
        Підготовка XML контенту.

        Args:
            data: XML контент як рядок або об'єкт для конвертації в XML

        Returns:
            str: XML контент
        """
        if isinstance(data, str):
            # Якщо вже є XML рядок
            return data
        elif hasattr(data, 'to_xml'):
            # Якщо об'єкт має метод to_xml
            return data.to_xml()
        else:
            raise ValueError("Невірний формат даних для XML writer")

    def _get_mime_type(self) -> str:
        """Повертає MIME тип для XML."""
        return 'application/xml'


def create_drive_writer(
    format_type: str,
    auth_service: GoogleAuthService
) -> GoogleDriveFileWriter:
    """
    Фабрична функція для створення writer'а потрібного типу.

    Args:
        format_type: Тип формату ('html' або 'xml')
        auth_service: Сервіс автентифікації

    Returns:
        GoogleDriveFileWriter: Конкретна реалізація writer'а

    Raises:
        ValueError: Якщо format_type невідомий
    """
    writers = {
        'html': HTMLDriveWriter,
        'xml': XMLDriveWriter
    }

    writer_class = writers.get(format_type.lower())
    if not writer_class:
        raise ValueError(
            f"Невідомий тип формату: {format_type}. "
            f"Доступні: {', '.join(writers.keys())}"
        )

    return writer_class(auth_service)
