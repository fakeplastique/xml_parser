import time
from pathlib import Path
from typing import Set
import xml.etree.ElementTree as ET

from src.models.search_models import SearchQuery, SearchResult, ParsedElement
from src.utils import Logger
from .base_parser import IXMLParser


class ElementTreeParserStrategy(IXMLParser):
    """
    ElementTree Parser implementation (LINQ to XML equivalent)
    Responsibility: Implement XML parsing using ElementTree API
    """

    def get_parser_name(self) -> str:
        """Return parser name"""
        return "ElementTree Parser (LINQ to XML)"

    def parse(self, file_path: Path, query: SearchQuery) -> SearchResult:
        """Parse XML file using ElementTree"""
        self.validate_file(file_path)

        start_time = time.time()

        try:
            # Parse XML
            tree = ET.parse(str(file_path))
            root = tree.getroot()
        except Exception as e:
            raise ValueError(f"Failed to parse XML: {str(e)}")

        # Search for matching elements using LINQ-like approach
        results = []
        self._search_elements(root, query, results, [])

        execution_time = (time.time() - start_time) * 1000

        # Build result
        result = SearchResult(
            query=query,
            elements=results,
            parser_type=self.get_parser_name(),
            execution_time_ms=execution_time
        )

        # Log filtering operation
        logger = Logger()
        logger.log_filtering(
            f'Парсер: {self.get_parser_name()}, '
            f'Файл: {file_path.name}, '
            f'Елемент: {query.element_name}, '
            f'Знайдено: {len(results)} елементів, '
            f'Час виконання: {execution_time:.2f} мс'
        )

        return result

    def _search_elements(
        self,
        element: ET.Element,
        query: SearchQuery,
        results: list,
        path: list
    ) -> None:
        """
        Recursively search ElementTree for matching elements
        Uses LINQ-like approach with generators and comprehensions
        Responsibility: Traverse tree and collect matches
        """
        # Remove namespace from tag if present
        tag = self._remove_namespace(element.tag)

        # Update path
        current_path = path + [tag]

        # Check if element matches query (LINQ-like filter)
        if query.matches_element(tag):
            # Extract attributes
            attributes = dict(element.attrib)

            # Check attribute filter (LINQ-like where clause)
            if query.matches_attribute(attributes):
                # Extract text content
                text = element.text or ""

                # Check text filter (LINQ-like contains)
                if query.matches_text(text):
                    parsed_element = ParsedElement(
                        tag=tag,
                        attributes=attributes,
                        text=text.strip(),
                        path="/".join(current_path)
                    )
                    results.append(parsed_element)

        # Recursively search children (LINQ-like SelectMany)
        for child in element:
            self._search_elements(child, query, results, current_path)

    def _remove_namespace(self, tag: str) -> str:
        """
        Remove namespace from tag name
        Responsibility: Clean tag names for comparison
        """
        if '}' in tag:
            return tag.split('}', 1)[1]
        return tag

    def get_available_attributes(self, file_path: Path, element_name: str) -> Set[str]:
        """
        Get all attribute names for given element type
        Uses LINQ-like comprehension approach
        """
        self.validate_file(file_path)

        try:
            tree = ET.parse(str(file_path))
            root = tree.getroot()
        except Exception as e:
            raise ValueError(f"Failed to parse XML: {str(e)}")

        # LINQ-like query: Select all attributes from matching elements
        attributes = set()
        self._collect_attributes(root, element_name, attributes)

        return attributes

    def _collect_attributes(
        self,
        element: ET.Element,
        element_name: str,
        attributes: Set[str]
    ) -> None:
        """
        Recursively collect attribute names
        Uses LINQ-like aggregation
        """
        tag = self._remove_namespace(element.tag)

        if tag.lower() == element_name.lower():
            # Add all attribute names from this element
            attributes.update(element.attrib.keys())

        # Recursively search children
        for child in element:
            self._collect_attributes(child, element_name, attributes)

    def get_attribute_values(
        self,
        file_path: Path,
        element_name: str,
        attribute_name: str
    ) -> Set[str]:
        """
        Get all values for specific attribute
        Uses LINQ-like Select approach
        """
        self.validate_file(file_path)

        try:
            tree = ET.parse(str(file_path))
            root = tree.getroot()
        except Exception as e:
            raise ValueError(f"Failed to parse XML: {str(e)}")

        # LINQ-like query: Select attribute values from matching elements
        values = set()
        self._collect_attribute_values(root, element_name, attribute_name, values)

        return values

    def _collect_attribute_values(
        self,
        element: ET.Element,
        element_name: str,
        attribute_name: str,
        values: Set[str]
    ) -> None:
        """
        Recursively collect attribute values
        Uses LINQ-like Where().Select() pattern
        """
        tag = self._remove_namespace(element.tag)

        # Where clause: filter by element name
        if tag.lower() == element_name.lower():
            # Select clause: get attribute value if exists
            if attribute_name in element.attrib:
                values.add(element.attrib[attribute_name])

        # Recursively search children (SelectMany)
        for child in element:
            self._collect_attribute_values(
                child,
                element_name,
                attribute_name,
                values
            )

    def get_elements_by_xpath(self, file_path: Path, xpath: str) -> list[ET.Element]:
        """
        Additional LINQ-to-XML feature: XPath queries
        Responsibility: Provide XPath-based element selection
        """
        self.validate_file(file_path)

        try:
            tree = ET.parse(str(file_path))
            root = tree.getroot()
        except Exception as e:
            raise ValueError(f"Failed to parse XML: {str(e)}")

        return root.findall(xpath)
