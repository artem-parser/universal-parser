# config.py — настройки парсера

TWO_STEP = False # в 1 или 2 шага в зависимости от доступности данных

# Сайт
BASE_URL = "https://quotes.toscrape.com/"
CATALOG_URL = "https://quotes.toscrape.com/page/{}/"
TOTAL_PAGES = 5

# Селекторы (CSS)
SELECTORS = {
    "card": "div.quote",              # карточка в каталоге
    "card_link": "span a",            # ссылка на карточку
    "text": "span.text",              # название в карточке
    "author": "small.author",         # автор
    "tags": "div.tags a.tag",         # теги
}

# Поля для CSV/Excel — порядок важен
FIELDS = ["id", "text", "author", "tags"]

# Настройки парсинга
PAUSE_BETWEEN_PAGES = 1    # пауза между страницами каталога
PAUSE_BETWEEN_CARDS = 1    # пауза между карточками
TIMEOUT = 10               # таймаут на запрос

# Файлы результата
CSV_FILE = "result.csv"
XLSX_FILE = "result.xlsx"
ERRORS_FILE = "errors.txt"

# User-Agent
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}