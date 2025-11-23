from abc import ABC, abstractmethod
from typing import Set
from pathlib import Path

from src.models.search_models import SearchQuery, SearchResult


class IXMLParser(ABC):
    """
    Interface for XML parsing strategies
    Responsibility: Define contract for all XML parsers
    """

    @abstractmethod
    def parse(self, file_path: Path, query: SearchQuery) -> SearchResult:
        """
        Parse XML file and search for elements matching query

        Args:
            file_path: Path to XML file
            query: Search query parameters

        Returns:
            SearchResult with matched elements

        Raises:
            FileNotFoundError: If XML file doesn't exist
            ValueError: If XML is malformed
        """
        pass

    @abstractmethod
    def get_available_attributes(self, file_path: Path, element_name: str) -> Set[str]:
        """
        Extract all unique attribute names for a given element type
        Used for dynamic UI population

        Args:
            file_path: Path to XML file
            element_name: Name of element to analyze

        Returns:
            Set of attribute names found in the XML
        """
        pass

    @abstractmethod
    def get_attribute_values(self, file_path: Path, element_name: str, attribute_name: str) -> Set[str]:
        """
        Extract all unique values for a specific attribute
        Used for dynamic UI population

        Args:
            file_path: Path to XML file
            element_name: Element type to search
            attribute_name: Attribute to extract values from

        Returns:
            Set of attribute values found
        """
        pass

    @abstractmethod
    def get_parser_name(self) -> str:
        """
        Get the name of this parser strategy

        Returns:
            Human-readable parser name
        """
        pass

    def validate_file(self, file_path: Path) -> None:
        """
        Validate that file exists and is accessible

        Args:
            file_path: Path to validate

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        if not file_path.exists():
            raise FileNotFoundError(f"XML file not found: {file_path}")

        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
