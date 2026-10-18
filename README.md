# Universal Parser

Универсальный шаблон парсера на Python (requests + BeautifulSoup).

## Что умеет
- Сбор данных с каталогов (пагинация)
- Парсинг карточек товаров (название, цена, описание)
- Сохранение в CSV и Excel с оформлением

## Как адаптировать под новый сайт
Меняется только файл `config.py` (URL и CSS-селекторы). Код в `parser.py` остается без изменений.

## Запуск
1. `pip install -r requirements.txt`
2. Настрой `config.py`
3. `python parser.py`

## Контакты
- Email: 9524271.kwork@gmail.com
- Kwork: (https://kwork.ru/user/artem_parser)
