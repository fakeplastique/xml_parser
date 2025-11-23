import time
from pathlib import Path
from typing import Set
from xml.dom import minidom
from xml.dom.minidom import Element

from src.models.search_models import SearchQuery, SearchResult, ParsedElement
from src.utils import Logger
from .base_parser import IXMLParser


class DOMParserStrategy(IXMLParser):
    """
    DOM Parser implementation
    Responsibility: Implement XML parsing using DOM API
    """

    def get_parser_name(self) -> str:
        """Return parser name"""
        return "DOM Parser"

    def parse(self, file_path: Path, query: SearchQuery) -> SearchResult:
        """Parse XML file using DOM"""
        self.validate_file(file_path)

        start_time = time.time()

        try:
            # Parse XML into DOM tree
            dom = minidom.parse(str(file_path))
        except Exception as e:
            raise ValueError(f"Failed to parse XML: {str(e)}")

        # Search for matching elements
        results = []
        self._search_elements(dom.documentElement, query, results, [])

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
        node: Element,
        query: SearchQuery,
        results: list,
        path: list
    ) -> None:
        """
        Recursively search DOM tree for matching elements
        Responsibility: Traverse DOM tree and collect matches
        """
        if node.nodeType != node.ELEMENT_NODE:
            return

        # Update path
        current_path = path + [node.nodeName]

        # Check if element matches query
        if query.matches_element(node.nodeName):
            # Extract attributes
            attributes = {}
            if node.attributes:
                for i in range(node.attributes.length):
                    attr = node.attributes.item(i)
                    attributes[attr.name] = attr.value

            # Check attribute filter
            if query.matches_attribute(attributes):
                # Extract text content
                text = self._get_element_text(node)

                # Check text filter
                if query.matches_text(text):
                    element = ParsedElement(
                        tag=node.nodeName,
                        attributes=attributes,
                        text=text,
                        path="/".join(current_path)
                    )
                    results.append(element)

        # Recursively search child elements
        for child in node.childNodes:
            if child.nodeType == child.ELEMENT_NODE:
                self._search_elements(child, query, results, current_path)

    def _get_element_text(self, node: Element) -> str:
        """
        Extract text content from element
        Responsibility: Get direct text content (not from children)
        """
        text_parts = []
        for child in node.childNodes:
            if child.nodeType == child.TEXT_NODE:
                text_parts.append(child.data)
        return "".join(text_parts).strip()

    def get_available_attributes(self, file_path: Path, element_name: str) -> Set[str]:
        """Get all attribute names for given element type"""
        self.validate_file(file_path)

        try:
            dom = minidom.parse(str(file_path))
        except Exception as e:
            raise ValueError(f"Failed to parse XML: {str(e)}")

        attributes = set()
        self._collect_attributes(dom.documentElement, element_name, attributes)

        return attributes

    def _collect_attributes(
        self,
        node: Element,
        element_name: str,
        attributes: Set[str]
    ) -> None:
        """
        Recursively collect attribute names from matching elements
        Responsibility: Traverse DOM and collect attribute names
        """
        if node.nodeType != node.ELEMENT_NODE:
            return

        # Check if element matches
        if node.nodeName.lower() == element_name.lower():
            if node.attributes:
                for i in range(node.attributes.length):
                    attr = node.attributes.item(i)
                    attributes.add(attr.name)

        # Recursively search children
        for child in node.childNodes:
            if child.nodeType == child.ELEMENT_NODE:
                self._collect_attributes(child, element_name, attributes)

    def get_attribute_values(
        self,
        file_path: Path,
        element_name: str,
        attribute_name: str
    ) -> Set[str]:
        """Get all values for specific attribute"""
        self.validate_file(file_path)

        try:
            dom = minidom.parse(str(file_path))
        except Exception as e:
            raise ValueError(f"Failed to parse XML: {str(e)}")

        values = set()
        self._collect_attribute_values(
            dom.documentElement,
            element_name,
            attribute_name,
            values
        )

        return values

    def _collect_attribute_values(
        self,
        node: Element,
        element_name: str,
        attribute_name: str,
        values: Set[str]
    ) -> None:
        """
        Recursively collect attribute values from matching elements
        Responsibility: Traverse DOM and collect attribute values
        """
        if node.nodeType != node.ELEMENT_NODE:
            return

        # Check if element matches
        if node.nodeName.lower() == element_name.lower():
            if node.hasAttribute(attribute_name):
                values.add(node.getAttribute(attribute_name))

        # Recursively search children
        for child in node.childNodes:
            if child.nodeType == child.ELEMENT_NODE:
                self._collect_attribute_values(
                    child,
                    element_name,
                    attribute_name,
                    values
                )
