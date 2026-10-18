import requests
from bs4 import BeautifulSoup
import csv
import time
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

import config


def get_page(url):
    """Скачивает страницу. Возвращает HTML или None."""
    try:
        response = requests.get(
            url,
            headers=config.HEADERS,
            timeout=config.TIMEOUT,
        )
        response.encoding = 'utf-8'
        if response.status_code == 200:
            return response.text
        print(f'    Сатус {response.status_code}')
        return None
    except Exception as e:
        print(f'    Ошибка: {e}')
        return None


def get_cards_links(html):
    """Из страницы каталога достаёт ссылки на карточки."""
    soup = BeautifulSoup(html, 'html.parser')
    cards = soup.select(config.SELECTORS['card'])
    links = []
    for card in cards:
        link_tag = card.select_one(config.SELECTORS['card_link'])
        if link_tag:
            href = link_tag.get('href')
            # Если ссылка уже полная — оставляем
            if href.startswith('http'):
                links.append(href)
            else:
                # Убираем возможные "../" в начале
                href = href.lstrip('./')
                # Если ссылка уже содержит "catalogue/" — не добавляем
                if href.startswith('catalogue/'):
                    full_url = config.BASE_URL + href
                else:
                    full_url = config.BASE_URL + 'catalogue/' + href
                links.append(full_url)
    return links


def parse_card(html):
    """Парсит карточку. Возвращает словарь с данными."""
    soup = BeautifulSoup(html, 'html.parser')
    data = {}

    for field, selector in config.SELECTORS.items():
        if field in ('card', 'card_link'):
            continue

        tag = soup.select_one(selector)
        if tag:
            text = tag.get_text(strip=True)
            text = text.replace('\n', ' ').replace('\r', ' ')
            text = ' '.join(text.split())
            data[field] = text
        else:
            data[field] = ''

    return data


def save_to_csv(rows, filename):
    """Сохраняет данные в CSV."""
    if not rows:
        print('Нет данных для CSV')
        return
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=config.FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f'CSV сохранен: {filename}')


def save_to_xlsx(rows, filename):
    """Сохраняет данные в Excel с оформлением."""
    if not rows:
        print('Нет данных для Excel')
        return

    wb = Workbook()
    ws = wb.active
    ws.title = 'Данные'

    # Заголовки
    ws.append(config.FIELDS)
    header_font = Font(bold=True, color='FFFFFF')
    header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
    for cell in ws[1]:
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal='center')

    # Данные
    for row in rows:
        ws.append([row.get(f, '') for f in config.FIELDS])

    # Автоширина
    for col in ws.columns:
        max_len = max(len(str(cell.value)) for cell in col if cell.value is not None)
        ws.column_dimensions[col[0].column_letter].width = min(max_len + 2, 60)

    wb.save(filename)
    print(f'Excel сохранен: {filename}')


def main():
    print('=' * 50)
    print('Универсальный парсер запущен')
    print('=' * 50)

    if config.TWO_STEP:

        # Шаг 1: собираем ссылки из каталога
        all_links = []

        for page_num in range(1, config.TOTAL_PAGES + 1):
            print(f'Каталог: страница {page_num}/{config.TOTAL_PAGES}')
            url = config.CATALOG_URL.format(page_num)
            html = get_page(url)
            if html:
                links = get_cards_links(html)
                all_links.extend(links)
                print(f'  Ссылок: {len(links)}')
            time.sleep(config.PAUSE_BETWEEN_PAGES)

        print(f'\nВсего ссылок: {len(all_links)}\n')

        # Шаг 2: парсим каждую карточку
        all_data = []
        errors = []

        for i, url in enumerate(all_links, start=1):
            print(f'Карточка {i}/{len(all_links)}')
            html = get_page(url)
            if html:
                try:
                    data = parse_card(html)
                    data['id'] = i
                    data['url'] = url
                    all_data.append(data)
                except Exception as e:
                    print(f'    Ошибка парсинга: {e}')
                    errors.append((url, 'не скачалось'))

                time.sleep(config.PAUSE_BETWEEN_CARDS)

        # Шаг 3: сохраняем
        print(f'\nВсего карточек: {len(all_data)}')
        print(f'Ошибок: {len(errors)}')
        save_to_csv(all_data, config.CSV_FILE)
        save_to_xlsx(all_data, config.XLSX_FILE)

        # Шаг 4: ошибки
        if errors:
            with open(config.ERRORS_FILE, 'w', encoding='utf-8') as f:
                for url, err in errors:
                    f.write(f'{url} - {err}\n')
            print(f'Ошибка сохранены: {config.ERRORS_FILE}')

    else:

        # если 1 шаг
        all_data = []
        errors = []
        item_id = 0

        for page_num in range(1, config.TOTAL_PAGES + 1):
            print(f'Страница {page_num}/{config.TOTAL_PAGES}')
            url = config.CATALOG_URL.format(page_num)
            html = get_page(url)

            if not html:
                errors.append((url, "не скачалось"))
                continue

            soup = BeautifulSoup(html, 'html.parser')
            cards = soup.select(config.SELECTORS['card'])

            for card in cards:
                item_id += 1
                item = {'id': item_id}

                for field, selector in config.SELECTORS.items():
                    if field in ('card', 'card_link'):
                        continue

                    if field == 'tags':
                        tags = card.select(selector)
                        item[field] = ', '.join(t.get_text(strip=True) for t in tags) if tags else ''
                        continue

                    tag = card.select_one(selector)
                    if tag:
                        text = tag.get_text(strip=True)
                        text = text.replace('\n', ' ').replace('\r', ' ')
                        text = ' '.join(text.split())
                        item[field] = text
                    else:
                        item[field] = ''

                all_data.append(item)

            time.sleep(config.PAUSE_BETWEEN_PAGES)

        print(f"\nВсего записей: {len(all_data)}")
        print(f"Ошибок: {len(errors)}")
        save_to_csv(all_data, config.CSV_FILE)
        save_to_xlsx(all_data, config.XLSX_FILE)

        if errors:
            with open(config.ERRORS_FILE, 'w', encoding='utf-8') as f:
                for url, err in errors:
                    f.write(f'{url} - {err}\n')
            print(f'Ошибки сохранены: {config.ERRORS_FILE}')


if __name__ == '__main__':
    main()