# XML Parser
## Бондар Ігор, К-25

Застосунок для аналізу та трансформації XML файлів SAF-T UA з використанням шаблону проектування **Strategy**.

## Особливості

### Реалізовані шаблони проектування
- ✅ **Strategy Pattern** - три різні стратегії парсингу XML:
  - SAX Parser (подієво-орієнтований)
  - DOM Parser (на основі дерева)
  - ElementTree Parser (аналог LINQ to XML)

### Функціональність

1. **Три способи парсингу XML**:
   - SAX API (xml.sax)
   - DOM API (xml.dom.minidom)
   - ElementTree (xml.etree.ElementTree) - LINQ to XML для Python

2. **Пошук за параметрами**:
   - Пошук за назвою елемента
   - Фільтрація за атрибутами
   - Фільтрація за текстовим вмістом
   - Динамічна генерація запитів

3. **Динамічна підгрузка даних**:
   - Автоматичне завантаження доступних елементів з XML
   - Автоматичне завантаження атрибутів для вибраного елемента
   - Автоматичне завантаження значень для вибраного атрибута

4. **Трансформація XML → HTML**:
   - Використання XSLT для перетворення
   - Збереження результату в HTML файл
   - Перегляд в браузері


## Встановлення

### 1. Вимоги
- Python 3.10+
- pip

### 2. Встановлення залежностей

```bash
pip install -r requirements.txt
```

Або вручну:
```bash
pip install PySide6 lxml
```

## Запуск

```bash
python main.py
```

## Використання

### 1. Вибір файлів
- Натисніть **"Browse XML..."** та виберіть XML файл (наприклад, `data/saft_ua_example.xml`)
- Натисніть **"Browse XSL..."** та виберіть XSL файл (наприклад, `data/saft_transform.xsl`)

### 2. Вибір парсера
- Виберіть один з трьох парсерів:
  - **SAX Parser** - швидкий, ефективний для великих файлів
  - **DOM Parser** - зручний для навігації по дереву
  - **ElementTree Parser (LINQ to XML)** - Python-native, потужний API

### 3. Завантаження метаданих
- Натисніть **"Load Available Values from XML"**
- Автоматично завантажаться всі доступні елементи з XML файлу

### 4. Налаштування пошуку
- **Element Name**: виберіть або введіть назву елемента (наприклад, `Customer`, `Invoice`, `Product`)
- **Attribute Name**: виберіть атрибут для фільтрації (або `(Any)`)
- **Attribute Value**: виберіть значення атрибута (або `(Any)`)
- **Text Contains**: введіть текст для пошуку в вмісті елемента (або `(Any)`)

### 5. Пошук
- Натисніть **"Search"**
- Результати з'являться в текстовому полі
- Буде показано:
  - Назва парсера
  - Параметри запиту
  - Кількість знайдених елементів
  - Час виконання
  - Деталі кожного знайденого елемента

### 6. Очищення
- Натисніть **"Clear"** для очищення всіх параметрів та результатів

### 7. Трансформація XML → HTML
- Після вибору XML та XSL файлів натисніть **"Transform to HTML"**
- Результат буде збережено в `data/output.html`
- Натисніть **"View HTML"** для перегляду в браузері
- Attribute Value: `electronics`
- Text Contains: `(Any)`


### Strategy Pattern
Всі парсери реалізують інтерфейс `IXMLParser`:
```python
class IXMLParser(ABC):
    @abstractmethod
    def parse(self, file_path: Path, query: SearchQuery) -> SearchResult:
        pass

    @abstractmethod
    def get_available_attributes(self, file_path: Path, element_name: str) -> Set[str]:
        pass

    @abstractmethod
    def get_attribute_values(self, file_path: Path, element_name: str, attribute_name: str) -> Set[str]:
        pass
```
