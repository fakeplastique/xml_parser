from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SearchQuery:
    """
    Represents a search query for XML parsing
    Responsibility: Hold search parameters
    """
    element_name: str
    attribute_name: Optional[str] = None
    attribute_value: Optional[str] = None
    text_contains: Optional[str] = None

    def matches_element(self, element_name: str) -> bool:
        """Check if element name matches query"""
        return self.element_name.lower() == element_name.lower()

    def matches_attribute(self, attributes: Dict[str, str]) -> bool:
        """Check if attributes match query criteria"""
        if not self.attribute_name or not self.attribute_value:
            return True

        return attributes.get(self.attribute_name) == self.attribute_value

    def matches_text(self, text: str) -> bool:
        """Check if text matches query criteria"""
        if not self.text_contains:
            return True

        return self.text_contains.lower() in text.lower()


@dataclass
class ParsedElement:
    """
    Represents a parsed XML element
    Responsibility: Store element data in a structured way
    """
    tag: str
    attributes: Dict[str, str] = field(default_factory=dict)
    text: str = ""
    children: List['ParsedElement'] = field(default_factory=list)
    path: str = ""

    def to_dict(self) -> Dict:
        """Convert element to dictionary representation"""
        return {
            'tag': self.tag,
            'attributes': self.attributes,
            'text': self.text,
            'path': self.path,
            'children_count': len(self.children)
        }

    def __str__(self) -> str:
        """String representation for display"""
        attrs_str = ', '.join(f"{k}='{v}'" for k, v in self.attributes.items())
        if attrs_str:
            return f"<{self.tag} {attrs_str}>"
        return f"<{self.tag}>"


@dataclass
class SearchResult:
    """
    Represents search results from XML parsing
    Responsibility: Aggregate and present search results
    """
    query: SearchQuery
    elements: List[ParsedElement] = field(default_factory=list)
    parser_type: str = ""
    execution_time_ms: float = 0.0

    def add_element(self, element: ParsedElement) -> None:
        """Add an element to results"""
        self.elements.append(element)

    def get_count(self) -> int:
        """Get number of results"""
        return len(self.elements)

    def is_empty(self) -> bool:
        """Check if results are empty"""
        return len(self.elements) == 0

    def to_summary(self) -> str:
        """Generate a text summary of results"""
        lines = [
            f"Parser: {self.parser_type}",
            f"Query: {self.query.element_name}",
            f"Results found: {self.get_count()}",
            f"Execution time: {self.execution_time_ms:.2f}ms",
            ""
        ]

        if self.query.attribute_name:
            lines.insert(2, f"Attribute filter: {self.query.attribute_name}={self.query.attribute_value}")

        if self.query.text_contains:
            lines.insert(2, f"Text filter: contains '{self.query.text_contains}'")

        return "\n".join(lines)

    def to_detailed_string(self) -> str:
        """Generate detailed string representation of all results"""
        if self.is_empty():
            return self.to_summary() + "\nNo results found."

        lines = [self.to_summary(), "Results:"]

        for idx, element in enumerate(self.elements, 1):
            lines.append(f"\n{idx}. {element}")
            if element.path:
                lines.append(f"   Path: {element.path}")
            if element.attributes:
                for key, value in element.attributes.items():
                    lines.append(f"   @{key}: {value}")
            if element.text and element.text.strip():
                text_preview = element.text.strip()[:100]
                lines.append(f"   Text: {text_preview}...")

        return "\n".join(lines)
