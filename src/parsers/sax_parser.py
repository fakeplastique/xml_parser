import time
from pathlib import Path
from typing import Set
from xml.sax import make_parser, ContentHandler
from xml.sax.handler import feature_namespaces

from src.models.search_models import SearchQuery, SearchResult, ParsedElement
from src.utils import Logger
from .base_parser        import IXMLParser


class SAXSearchHandler(ContentHandler):
    """
    SAX Content Handler for searching elements
    Responsibility: Handle SAX parsing events and collect matching elements
    """

    def __init__(self, query: SearchQuery):
        super().__init__()
        self.query = query
        self.results: list[ParsedElement] = []
        self.current_path: list[str] = []
        self.current_text: str = ""
        self.current_element: ParsedElement | None = None

    def startElement(self, name, attrs):
        """Handle start of element"""
        self.current_path.append(name)
        self.current_text = ""

        # Check if this element matches query
        if self.query.matches_element(name):
            attributes = dict(attrs.items())

            # Check attribute filter
            if self.query.matches_attribute(attributes):
                self.current_element = ParsedElement(
                    tag=name,
                    attributes=attributes,
                    path="/".join(self.current_path)
                )

    def endElement(self, name):
        """Handle end of element"""
        # If we were tracking this element, check text filter and add to results
        if self.current_element and self.current_element.tag == name:
            self.current_element.text = self.current_text.strip()

            if self.query.matches_text(self.current_element.text):
                self.results.append(self.current_element)

            self.current_element = None

        self.current_path.pop()
        self.current_text = ""

    def characters(self, content):
        """Handle character data"""
        self.current_text += content


class SAXAttributeCollector(ContentHandler):
    """
    SAX Handler for collecting attribute information
    Responsibility: Extract attribute names and values from XML
    """

    def __init__(self, element_name: str, attribute_name: str | None = None):
        super().__init__()
        self.element_name = element_name
        self.attribute_name = attribute_name
        self.attributes: Set[str] = set()
        self.values: Set[str] = set()

    def startElement(self, name, attrs):
        """Collect attributes from matching elements"""
        if name.lower() == self.element_name.lower():
            if self.attribute_name:
                # Collecting values for specific attribute
                if self.attribute_name in attrs:
                    self.values.add(attrs[self.attribute_name])
            else:
                # Collecting all attribute names
                self.attributes.update(attrs.keys())


class SAXParserStrategy(IXMLParser):
    """
    SAX Parser implementation
    Responsibility: Implement XML parsing using SAX API
    """

    def get_parser_name(self) -> str:
        """Return parser name"""
        return "SAX Parser"

    def parse(self, file_path: Path, query: SearchQuery) -> SearchResult:
        """Parse XML file using SAX"""
        self.validate_file(file_path)

        start_time = time.time()

        # Create parser
        parser = make_parser()
        parser.setFeature(feature_namespaces, False)

        # Create and set handler
        handler = SAXSearchHandler(query)
        parser.setContentHandler(handler)

        # Parse file
        try:
            parser.parse(str(file_path))
        except Exception as e:
            raise ValueError(f"Failed to parse XML: {str(e)}")

        execution_time = (time.time() - start_time) * 1000

        # Build result
        result = SearchResult(
            query=query,
            elements=handler.results,
            parser_type=self.get_parser_name(),
            execution_time_ms=execution_time
        )

        # Log filtering operation
        logger = Logger()
        logger.log_filtering(
            f'Парсер: {self.get_parser_name()}, '
            f'Файл: {file_path.name}, '
            f'Елемент: {query.element_name}, '
            f'Знайдено: {len(handler.results)} елементів, '
            f'Час виконання: {execution_time:.2f} мс'
        )

        return result

    def get_available_attributes(self, file_path: Path, element_name: str) -> Set[str]:
        """Get all attribute names for given element type"""
        self.validate_file(file_path)

        parser = make_parser()
        parser.setFeature(feature_namespaces, False)

        handler = SAXAttributeCollector(element_name)
        parser.setContentHandler(handler)

        try:
            parser.parse(str(file_path))
        except Exception as e:
            raise ValueError(f"Failed to parse XML: {str(e)}")

        return handler.attributes

    def get_attribute_values(self, file_path: Path, element_name: str, attribute_name: str) -> Set[str]:
        """Get all values for specific attribute"""
        self.validate_file(file_path)

        parser = make_parser()
        parser.setFeature(feature_namespaces, False)

        handler = SAXAttributeCollector(element_name, attribute_name)
        parser.setContentHandler(handler)

        try:
            parser.parse(str(file_path))
        except Exception as e:
            raise ValueError(f"Failed to parse XML: {str(e)}")

        return handler.values
