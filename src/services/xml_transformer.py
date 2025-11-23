from pathlib import Path
from typing import Optional
from lxml import etree # type: ignore


from src.utils import Logger


class XMLTransformer:
    """
    Transforms XML documents to HTML using XSLT
    Responsibility: Encapsulate XSLT transformation logic
    """


    def transform(
        self,
        xml_file: Path,
        xsl_file: Path,
        output_file: Optional[Path] = None
    ) -> str:
        """
        Transform XML to HTML using XSLT

        Args:
            xml_file: Path to XML source file
            xsl_file: Path to XSL transformation file
            output_file: Optional path to save HTML output

        Returns:
            HTML content as string

        Raises:
            FileNotFoundError: If XML or XSL file not found
            ValueError: If transformation fails
            ImportError: If lxml is not installed
        """

        self._validate_file(xml_file, "XML")
        self._validate_file(xsl_file, "XSL")

        try:

            # Parse XML and XSL
            xml_doc = etree.parse(str(xml_file))
            xsl_doc = etree.parse(str(xsl_file))

            # Create transformer
            transform = etree.XSLT(xsl_doc)

            # Apply transformation
            result_tree = transform(xml_doc)

            # Convert to string
            html_content = str(result_tree)

            # Log transformation
            logger = Logger()
            logger.log_transformation(
                f'XML → HTML трансформація. '
                f'Джерело: {xml_file.name}, '
                f'XSLT: {xsl_file.name}, '
                f'Розмір результату: {len(html_content)} байт'
            )

            # Save to file if requested
            if output_file:
                self._save_html(html_content, output_file)

            return html_content

        except etree.XSLTParseError as e:
            raise ValueError(f"XSLT parsing error: {str(e)}")
        except etree.XSLTApplyError as e:
            raise ValueError(f"XSLT transformation error: {str(e)}")
        except Exception as e:
            raise ValueError(f"Transformation failed: {str(e)}")

    def _validate_file(self, file_path: Path, file_type: str) -> None:
        """
        Validate that file exists
        Responsibility: Input validation
        """
        if not file_path.exists():
            raise FileNotFoundError(f"{file_type} file not found: {file_path}")

        if not file_path.is_file():
            raise ValueError(f"{file_type} path is not a file: {file_path}")

    def _save_html(self, html_content: str, output_file: Path) -> None:
        """
        Save HTML content to file
        Responsibility: File I/O for HTML output
        """
        try:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(html_content, encoding='utf-8')

            # Log saving operation
            logger = Logger()
            logger.log_saving(
                f'Збережено HTML файл: {output_file.name}, '
                f'Розмір: {len(html_content)} байт, '
                f'Шлях: {output_file.parent}'
            )

        except Exception as e:
            raise ValueError(f"Failed to save HTML file: {str(e)}")