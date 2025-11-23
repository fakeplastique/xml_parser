from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
from typing import List

from src.models.search_models import SearchResult, ParsedElement


class SearchResultXMLConverter:
    """
    Конвертує результати пошуку в XML формат.

    Відповідальність: трансформація SearchResult в XML документ.
    """

    @staticmethod
    def convert_to_xml(search_result: SearchResult) -> str:
        """
        Конвертує SearchResult в XML рядок.

        Args:
            search_result: Результати пошуку для конвертації

        Returns:
            str: Відформатований XML рядок

        Example:
            <?xml version="1.0" encoding="UTF-8"?>
            <searchResults>
                <metadata>
                    <parserType>DOM</parserType>
                    <elementName>book</elementName>
                    <resultsCount>2</resultsCount>
                    <executionTime>12.5</executionTime>
                </metadata>
                <results>
                    <element>
                        <tag>book</tag>
                        <path>/catalog/book[1]</path>
                        <attributes>
                            <attribute name="id" value="bk101"/>
                        </attributes>
                        <text>...</text>
                    </element>
                </results>
            </searchResults>
        """
        root = Element('searchResults')

        # Додаємо метадані
        metadata = SubElement(root, 'metadata')

        parser_type = SubElement(metadata, 'parserType')
        parser_type.text = search_result.parser_type

        element_name = SubElement(metadata, 'elementName')
        element_name.text = search_result.query.element_name

        if search_result.query.attribute_name:
            attr_filter = SubElement(metadata, 'attributeFilter')
            attr_name = SubElement(attr_filter, 'name')
            attr_name.text = search_result.query.attribute_name
            attr_value = SubElement(attr_filter, 'value')
            attr_value.text = search_result.query.attribute_value or ''

        if search_result.query.text_contains:
            text_filter = SubElement(metadata, 'textFilter')
            text_filter.text = search_result.query.text_contains

        results_count = SubElement(metadata, 'resultsCount')
        results_count.text = str(search_result.get_count())

        execution_time = SubElement(metadata, 'executionTime')
        execution_time.text = f"{search_result.execution_time_ms:.2f}"

        # Додаємо результати
        results = SubElement(root, 'results')

        for parsed_elem in search_result.elements:
            SearchResultXMLConverter._add_element(results, parsed_elem)

        # Форматуємо XML для читабельності
        return SearchResultXMLConverter._prettify_xml(root)

    @staticmethod
    def _add_element(parent: Element, parsed_elem: ParsedElement) -> None:
        """
        Додає ParsedElement до XML дерева.

        Args:
            parent: Батьківський XML елемент
            parsed_elem: ParsedElement для додавання
        """
        element = SubElement(parent, 'element')

        # Тег елемента
        tag = SubElement(element, 'tag')
        tag.text = parsed_elem.tag

        # Шлях елемента
        if parsed_elem.path:
            path = SubElement(element, 'path')
            path.text = parsed_elem.path

        # Атрибути
        if parsed_elem.attributes:
            attributes = SubElement(element, 'attributes')
            for attr_name, attr_value in parsed_elem.attributes.items():
                attr = SubElement(attributes, 'attribute')
                attr.set('name', attr_name)
                attr.set('value', attr_value)

        # Текстовий контент
        if parsed_elem.text and parsed_elem.text.strip():
            text = SubElement(element, 'text')
            text.text = parsed_elem.text.strip()

        # Кількість дочірніх елементів
        if parsed_elem.children:
            children_count = SubElement(element, 'childrenCount')
            children_count.text = str(len(parsed_elem.children))

    @staticmethod
    def _prettify_xml(elem: Element) -> str:
        """
        Форматує XML для читабельності.

        Args:
            elem: Корневий елемент XML

        Returns:
            str: Відформатований XML рядок
        """
        rough_string = tostring(elem, encoding='utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ", encoding='utf-8').decode('utf-8')

    @staticmethod
    def convert_multiple_to_xml(search_results: List[SearchResult]) -> str:
        """
        Конвертує множину SearchResult в один XML документ.

        Args:
            search_results: Список результатів пошуку

        Returns:
            str: Відформатований XML рядок з усіма результатами
        """
        root = Element('multipleSearchResults')

        for idx, result in enumerate(search_results, 1):
            search_elem = SubElement(root, 'searchResult')
            search_elem.set('index', str(idx))

            # Додаємо метадані
            metadata = SubElement(search_elem, 'metadata')

            parser_type = SubElement(metadata, 'parserType')
            parser_type.text = result.parser_type

            element_name = SubElement(metadata, 'elementName')
            element_name.text = result.query.element_name

            results_count = SubElement(metadata, 'resultsCount')
            results_count.text = str(result.get_count())

            # Додаємо результати
            results = SubElement(search_elem, 'results')
            for parsed_elem in result.elements:
                SearchResultXMLConverter._add_element(results, parsed_elem)

        return SearchResultXMLConverter._prettify_xml(root)
