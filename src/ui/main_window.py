import webbrowser
from pathlib import Path
from typing import Optional, Dict

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QTextEdit,
    QFileDialog, QMessageBox, QGroupBox, QGridLayout,
    QProgressBar
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QCloseEvent

from src.parsers.base_parser import IXMLParser
from src.parsers import SAXParserStrategy, DOMParserStrategy, ElementTreeParserStrategy
from src.models.search_models import SearchQuery, SearchResult
from src.services.xml_transformer import XMLTransformer


class ParserWorker(QThread):
    """
    Background worker for parsing operations
    Responsibility: Execute parsing in separate thread to keep UI responsive
    """
    finished = Signal(SearchResult)
    error = Signal(str)

    def __init__(self, parser: IXMLParser, file_path: Path, query: SearchQuery):
        super().__init__()
        self.parser = parser
        self.file_path = file_path
        self.query = query

    def run(self):
        """Execute parsing operation"""
        try:
            result = self.parser.parse(self.file_path, self.query)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """
    Main application window
    Responsibility: Coordinate UI components and user interactions
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("XML Parser")
        self.setMinimumSize(1000, 700)

        # Initialize parsers (Strategy pattern)
        self.parsers: Dict[str, IXMLParser] = {
            "SAX Parser": SAXParserStrategy(),
            "DOM Parser": DOMParserStrategy(),
            "ElementTree (LINQ to XML)": ElementTreeParserStrategy()
        }

        # Initialize services
        self.transformer = XMLTransformer()

        # State
        self.current_xml_file: Optional[Path] = None
        self.current_xsl_file: Optional[Path] = None
        self.worker: Optional[ParserWorker] = None

        # Setup UI
        self._setup_ui()

    def _setup_ui(self):
        """
        Initialize UI components
        Responsibility: Create and layout all UI elements
        """
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Header
        self._create_header(main_layout)

        # File selection section
        self._create_file_selection_section(main_layout)

        # Parser selection section
        self._create_parser_section(main_layout)

        # Search parameters section
        self._create_search_section(main_layout)

        # Action buttons
        self._create_action_buttons(main_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # Results section
        self._create_results_section(main_layout)

        # Transformation section
        self._create_transformation_section(main_layout)

    def _create_header(self, layout: QVBoxLayout):
        """Create header with title"""
        title = QLabel("XML Parser & Transformer")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("SAX, DOM, ElementTree Parsers")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

    def _create_file_selection_section(self, layout: QVBoxLayout):
        """Create file selection controls"""
        group = QGroupBox("File Selection")
        group_layout = QGridLayout()

        # XML file selection
        xml_label = QLabel("XML File:")
        self.xml_file_label = QLabel("No file selected")
        self.xml_file_label.setStyleSheet("color: gray;")
        xml_button = QPushButton("Browse XML...")
        xml_button.clicked.connect(self._browse_xml_file)

        group_layout.addWidget(xml_label, 0, 0)
        group_layout.addWidget(self.xml_file_label, 0, 1)
        group_layout.addWidget(xml_button, 0, 2)

        # XSL file selection
        xsl_label = QLabel("XSL File:")
        self.xsl_file_label = QLabel("No file selected")
        self.xsl_file_label.setStyleSheet("color: gray;")
        xsl_button = QPushButton("Browse XSL...")
        xsl_button.clicked.connect(self._browse_xsl_file)

        group_layout.addWidget(xsl_label, 1, 0)
        group_layout.addWidget(self.xsl_file_label, 1, 1)
        group_layout.addWidget(xsl_button, 1, 2)

        group.setLayout(group_layout)
        layout.addWidget(group)

    def _create_parser_section(self, layout: QVBoxLayout):
        """Create parser selection controls"""
        group = QGroupBox("Parser Strategy")
        group_layout = QHBoxLayout()

        label = QLabel("Select Parser:")
        self.parser_combo = QComboBox()
        self.parser_combo.addItems(list(self.parsers.keys()))

        group_layout.addWidget(label)
        group_layout.addWidget(self.parser_combo)
        group_layout.addStretch()

        group.setLayout(group_layout)
        layout.addWidget(group)

    def _create_search_section(self, layout: QVBoxLayout):
        """Create search parameter controls"""
        group = QGroupBox("Search Parameters")
        group_layout = QGridLayout()

        # Element name
        elem_label = QLabel("Element Name:")
        self.element_combo = QComboBox()
        self.element_combo.setEditable(True)
        self.element_combo.currentTextChanged.connect(self._on_element_changed)

        group_layout.addWidget(elem_label, 0, 0)
        group_layout.addWidget(self.element_combo, 0, 1)

        # Attribute name
        attr_label = QLabel("Attribute Name:")
        self.attribute_combo = QComboBox()
        self.attribute_combo.setEditable(True)
        self.attribute_combo.addItem("(Any)")
        self.attribute_combo.currentTextChanged.connect(self._on_attribute_changed)

        group_layout.addWidget(attr_label, 1, 0)
        group_layout.addWidget(self.attribute_combo, 1, 1)

        # Attribute value
        val_label = QLabel("Attribute Value:")
        self.value_combo = QComboBox()
        self.value_combo.setEditable(True)
        self.value_combo.addItem("(Any)")

        group_layout.addWidget(val_label, 2, 0)
        group_layout.addWidget(self.value_combo, 2, 1)

        # Text contains
        text_label = QLabel("Text Contains:")
        self.text_combo = QComboBox()
        self.text_combo.setEditable(True)
        self.text_combo.addItem("(Any)")

        group_layout.addWidget(text_label, 3, 0)
        group_layout.addWidget(self.text_combo, 3, 1)

        # Load data button
        self.load_data_button = QPushButton("Load Available Values from XML")
        self.load_data_button.clicked.connect(self._load_xml_metadata)
        self.load_data_button.setEnabled(False)
        group_layout.addWidget(self.load_data_button, 4, 0, 1, 2)

        group.setLayout(group_layout)
        layout.addWidget(group)

    def _create_action_buttons(self, layout: QVBoxLayout):
        """Create action buttons"""
        button_layout = QHBoxLayout()

        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self._execute_search)
        self.search_button.setEnabled(False)

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self._clear_all)

        button_layout.addWidget(self.search_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addStretch()

        layout.addLayout(button_layout)

    def _create_results_section(self, layout: QVBoxLayout):
        """Create results display area"""
        group = QGroupBox("Search Results")
        group_layout = QVBoxLayout()

        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMinimumHeight(200)

        group_layout.addWidget(self.results_text)
        group.setLayout(group_layout)
        layout.addWidget(group)

    def _create_transformation_section(self, layout: QVBoxLayout):
        """Create transformation controls"""
        group = QGroupBox("XML to HTML Transformation")
        group_layout = QHBoxLayout()

        self.transform_button = QPushButton("Transform to HTML")
        self.transform_button.clicked.connect(self._transform_xml)
        self.transform_button.setEnabled(False)

        self.view_html_button = QPushButton("View HTML")
        self.view_html_button.clicked.connect(self._view_html)
        self.view_html_button.setEnabled(False)

        group_layout.addWidget(self.transform_button)
        group_layout.addWidget(self.view_html_button)
        group_layout.addStretch()

        group.setLayout(group_layout)
        layout.addWidget(group)

    def _browse_xml_file(self):
        """Handle XML file selection"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select XML File",
            str(Path.cwd() / "data"),
            "XML Files (*.xml);;All Files (*)"
        )

        if file_path:
            self.current_xml_file = Path(file_path)
            self.xml_file_label.setText(self.current_xml_file.name)
            self.xml_file_label.setStyleSheet("color: green;")
            self.load_data_button.setEnabled(True)
            self.search_button.setEnabled(True)
            self._update_transform_button()

    def _browse_xsl_file(self):
        """Handle XSL file selection"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select XSL File",
            str(Path.cwd() / "data"),
            "XSL Files (*.xsl *.xslt);;All Files (*)"
        )

        if file_path:
            self.current_xsl_file = Path(file_path)
            self.xsl_file_label.setText(self.current_xsl_file.name)
            self.xsl_file_label.setStyleSheet("color: green;")
            self._update_transform_button()

    def _update_transform_button(self):
        """Update transform button state"""
        can_transform = (
            self.current_xml_file is not None and
            self.current_xsl_file is not None
        )
        self.transform_button.setEnabled(can_transform)

    def _load_xml_metadata(self):
        """Load available element names and attributes from XML"""
        if not self.current_xml_file:
            return

        try:
            # Get current parser
            parser_name = self.parser_combo.currentText()
            parser = self.parsers[parser_name]

            # Get all unique element names using ElementTree
            import xml.etree.ElementTree as ET
            tree = ET.parse(str(self.current_xml_file))
            root = tree.getroot()

            elements = set()
            self._collect_element_names(root, elements)

            # Update element combo
            self.element_combo.clear()
            self.element_combo.addItems(sorted(elements))

            self.results_text.append("✓ Loaded available elements from XML file")

        except Exception as e:
            QMessageBox.warning(
                self,
                "Load Error",
                f"Failed to load XML metadata: {str(e)}"
            )

    def _collect_element_names(self, element, elements: set):
        """Recursively collect all element names"""
        tag = element.tag
        if '}' in tag:
            tag = tag.split('}', 1)[1]
        elements.add(tag)

        for child in element:
            self._collect_element_names(child, elements)

    def _on_element_changed(self, element_name: str):
        """Handle element name change - load attributes"""
        if not self.current_xml_file or not element_name:
            return

        try:
            parser_name = self.parser_combo.currentText()
            parser = self.parsers[parser_name]

            # Get available attributes
            attributes = parser.get_available_attributes(
                self.current_xml_file,
                element_name
            )

            # Update attribute combo
            self.attribute_combo.clear()
            self.attribute_combo.addItem("(Any)")
            self.attribute_combo.addItems(sorted(attributes))

        except Exception:
            pass  # Silently ignore errors during dynamic loading

    def _on_attribute_changed(self, attribute_name: str):
        """Handle attribute name change - load values"""
        if not self.current_xml_file or not attribute_name or attribute_name == "(Any)":
            return

        element_name = self.element_combo.currentText()
        if not element_name:
            return

        try:
            parser_name = self.parser_combo.currentText()
            parser = self.parsers[parser_name]

            # Get available values
            values = parser.get_attribute_values(
                self.current_xml_file,
                element_name,
                attribute_name
            )

            # Update value combo
            self.value_combo.clear()
            self.value_combo.addItem("(Any)")
            self.value_combo.addItems(sorted(values))

        except Exception:
            pass  # Silently ignore errors during dynamic loading

    def _execute_search(self):
        """Execute search using selected parser"""
        if not self.current_xml_file:
            QMessageBox.warning(self, "No File", "Please select an XML file first.")
            return

        element_name = self.element_combo.currentText()
        if not element_name:
            QMessageBox.warning(self, "No Element", "Please enter an element name.")
            return

        # Build query
        attribute_name = self.attribute_combo.currentText()
        attribute_value = self.value_combo.currentText()
        text_contains = self.text_combo.currentText()

        query = SearchQuery(
            element_name=element_name,
            attribute_name=attribute_name if attribute_name != "(Any)" else None,
            attribute_value=attribute_value if attribute_value != "(Any)" else None,
            text_contains=text_contains if text_contains != "(Any)" else None
        )

        # Get selected parser
        parser_name = self.parser_combo.currentText()
        parser = self.parsers[parser_name]

        # Execute in background thread
        self.worker = ParserWorker(parser, self.current_xml_file, query)
        self.worker.finished.connect(self._on_search_finished)
        self.worker.error.connect(self._on_search_error)

        # Update UI
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.search_button.setEnabled(False)
        self.results_text.append(f"\nSearching with {parser_name}...")

        self.worker.start()

    def _on_search_finished(self, result: SearchResult):
        """Handle search completion"""
        self.progress_bar.setVisible(False)
        self.search_button.setEnabled(True)

        # Display results
        self.results_text.append("\n" + "=" * 60)
        self.results_text.append(result.to_detailed_string())
        self.results_text.append("=" * 60)

    def _on_search_error(self, error_msg: str):
        """Handle search error"""
        self.progress_bar.setVisible(False)
        self.search_button.setEnabled(True)

        QMessageBox.critical(
            self,
            "Search Error",
            f"Search failed: {error_msg}"
        )

    def _clear_all(self):
        """Clear all search parameters and results"""
        self.element_combo.setCurrentText("")
        self.attribute_combo.setCurrentIndex(0)
        self.value_combo.setCurrentIndex(0)
        self.text_combo.setCurrentIndex(0)
        self.results_text.clear()

    def _transform_xml(self):
        """Transform XML to HTML using XSL"""
        if not self.current_xml_file or not self.current_xsl_file:
            return

        try:
            # Generate output file path
            output_file = self.current_xml_file.parent / "output.html"

            # Transform
            self.transformer.transform(
                self.current_xml_file,
                self.current_xsl_file,
                output_file
            )

            self.results_text.append(f"\n✓ Transformation successful!")
            self.results_text.append(f"Output saved to: {output_file}")

            self.view_html_button.setEnabled(True)

            QMessageBox.information(
                self,
                "Success",
                f"Transformation completed!\nOutput: {output_file}"
            )

        except ImportError as e:
            QMessageBox.critical(
                self,
                "Missing Dependency",
                str(e)
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Transformation Error",
                f"Failed to transform XML: {str(e)}"
            )

    def _view_html(self):
        """Open generated HTML in browser"""
        output_file = self.current_xml_file.parent / "output.html"
        if output_file.exists():
            webbrowser.open(output_file.as_uri())
        else:
            QMessageBox.warning(
                self,
                "File Not Found",
                "HTML file not found. Please run transformation first."
            )

    def closeEvent(self, event: QCloseEvent):
        """Handle window close event with confirmation"""
        reply = QMessageBox.question(
            self,
            "Exit Confirmation",
            "Чи дійсно ви хочете завершити роботу з програмою?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Clean up worker thread if running
            if self.worker and self.worker.isRunning():
                self.worker.terminate()
                self.worker.wait()
            event.accept()
        else:
            event.ignore()
