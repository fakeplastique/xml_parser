"""
Parsers package implementing Strategy pattern
Each parser is a different strategy for parsing XML
"""

from .base_parser import IXMLParser
from .sax_parser import SAXParserStrategy
from .dom_parser import DOMParserStrategy
from .elementtree_parser import ElementTreeParserStrategy

__all__ = [
    'IXMLParser',
    'SAXParserStrategy',
    'DOMParserStrategy',
    'ElementTreeParserStrategy'
]
