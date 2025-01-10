"""Search all info about site"""
import asyncio
import json
import random
import re
from playwright.async_api import async_playwright
import pandas as pd


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
    Chrome/74.0.3729.169 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) \
    Version/17.4.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:130.0) Gecko/20100101 Firefox/130.0",
]
BROWSER_ARGS = [
    "--disable-xss-auditor",
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-blink-features=AutomationControlled",
    "--disable-features=IsolateOrigins,site-per-process",
    "--disable-infobars",
]


class FileHandler:
    """Сохраниние полученной информации"""
    def __init__(self, file_name):
        self.file_name = file_name

    def save_to_file(self, data):
        """Сохранить данные в JSON файл."""
        try:
            with open(self.file_name, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"Данные успешно сохранены в {self.file_name}")
        except FileNotFoundError:
            print(f"Ошибка при сохранении данных в файл {self.file_name}")

    def load_from_file(self):
        """Загрузить данные из JSON файла."""
        try:
            with open(self.file_name, "r", encoding="utf-8") as f:
                data = json.load(f)
            print(f"Данные успешно загружены из {self.file_name}")
            return data
        except FileNotFoundError:
            print(f"Файл {self.file_name} не найден. Возвращен пустой список.")
            return []
        except json.JSONDecodeError:
            print(f"Ошибка при разборе данных в файле {self.file_name}. Возвращен пустой список.")
            return []
        except ValueError as e:
            print(f"Ошибка при чтении файла {self.file_name}: {e}")
            return []

    def save_to_table(self, data, table_filename="output.csv"):
        """Сохранить данные в CSV таблицу."""
        try:
            df = pd.DataFrame(data)  # Преобразуем список данных в DataFrame
            df.to_csv(table_filename, index=False, encoding="utf-8")  # Сохраняем в CSV файл
            print(f"Данные успешно сохранены в таблицу {table_filename}")
        except ValueError as e:
            print(f"Ошибка при сохранении данных в таблицу {table_filename}: {e}")

    def save_to_excel(self, data, excel_filename="output.xlsx"):
        """Сохранить данные в Excel файл."""
        try:
            df = pd.DataFrame(data)  # Преобразуем список данных в DataFrame
            # df['new_price'] = pd.to_numeric(df['new_price'], errors='coerce').astype('int')
            # df['new_price'] = df['new_price'].fillna(0).astype('int')

            df.to_excel(excel_filename, index=False, engine='openpyxl')  # Сохраняем в Excel файл
            print(f"Данные успешно сохранены в Excel файл {excel_filename}")
        except ValueError as e:
            print(f"Ошибка при сохранении данных в Excel файл {excel_filename}: {e}")

    def append_to_file(self, new_data):
        """Добавить данные в существующий JSON файл."""
        try:
            existing_data = self.load_from_file()
            if isinstance(existing_data, list):
                updated_data = existing_data + new_data
            else:
                print("Существующий файл не является списком. Данные перезаписаны.")
                updated_data = new_data

            self.save_to_file(updated_data)
        except ValueError as e:
            print(f"Ошибка при добавлении данных в файл {self.file_name}: {e}")


class ProductScraper:
    """Нахождение и извлечение нужной информации"""
    def __init__(self, base_url, file_handler):
        self.base_url = base_url
        self.products = []
        # Экземпляр FileHandler
        self.file_handler = file_handler

    async def extract_products_from_page(self, page):
        """Извлечение всех товаров на текущей странице."""
        try:
            await page.wait_for_selector('.catalog-elements-container--inner', timeout=5000)
            await page.wait_for_selector('.product-list-item.catalog-item', timeout=12000)
            await asyncio.sleep(random.uniform(3, 5))  # Дополнительное время для загрузки
            product_links = await page.locator('.product-list-item.catalog-item').all()

            page_products = []
            for link in product_links:
                title = (await link.locator('.catalog-item--title-main .item-name')
                         .text_content() or '').strip()
                sub_title = (await link.locator('.catalog-item--subtitle .text')
                             .text_content() or '').strip()
                ref = (await link.locator('.catalog-item--ref').
                       text_content() or "").replace('Референс:', '').strip()

                 # Извлечение новой и старой цены
                new_price = ""
                # Новая цена
                if await link.locator('.item-price--text:not(.text-md.through)').count() > 0:
                    raw_new_price = (await link.locator('.item-price--text:not(.text-md.through)')
                                     .text_content() or '').strip()
                    cleaned_new_price = re.sub(r'\s|\$', '', raw_new_price)
                    if cleaned_new_price.isdigit():
                        new_price = int(cleaned_new_price)
                    else:
                        # Сохраняем текстовое значение, если это не число
                        new_price = raw_new_price

                # Проверяем наличие разных статусов
                reserved_status = ""
                if await link.locator('.reserved-text-block').count() > 0:
                    reserved_status = (await link.locator('.reserved-text-block')
                                       .text_content()).strip()
                elif await link.locator('.reserved-text-block--short').count() > 0:
                    reserved_status = (await link.locator('.reserved-text-block--short')
                                       .text_content()).strip()

                # Гео-данные
                geo = ""
                if await link.locator('span.catalog-item-geo--in-stock').count() > 0:
                    geo_span = await link.locator('span.catalog-item-geo--in-stock').text_content()
                    geo_full = await link.locator('.catalog-item--geo p').text_content()
                    geo = geo_full.replace(geo_span, "").strip()

                # Сохраняем данные
                page_products.append(
                    {
                        "title": title,
                        "sub-title": sub_title,
                        "ref": ref,
                        "new_price": new_price,
                        # "old_price": old_price,
                        "reserved_status": reserved_status,
                        "geo": geo,
                    }
                )
            return page_products
        except ValueError as e:
            print(f"Ошибка при извлечении товаров: {e}")
            return []

    async def collect_products_from_category(self, page):
        """Сбор всех товаров из категории с учётом пагинации."""
        # Открываем начальную страницу
        await page.goto(self.base_url, timeout=40000, wait_until="commit")

        # Определяем количество страниц
        try:
            await page.wait_for_selector(".navigation-counter", timeout=4000)
            pagination_items = await page.locator(".navigation-counter-item a").all()

            page_numbers = []
            for item in pagination_items:
                text = await item.text_content()
                if text and text.strip().isdigit():
                    page_numbers.append(int(text.strip()))
            total_pages = max(page_numbers) if page_numbers else 1
            print(f"Общее количество страниц: {total_pages}")
        except ValueError as e:
            print(f"Ошибка при определении количества страниц: {e}")
            total_pages = 1

        # Переход по каждой странице и сбор данных
        for page_num in range(1, total_pages + 1):
            url_site = f"{self.base_url}?page={page_num}"
            print(f"Переход на страницу {page_num}: {url_site}")
            try:
                await page.goto(url_site, timeout=3000, wait_until="commit")
                await page.wait_for_selector('.catalog-elements-container--inner', timeout=8000)

                page_products = await self.extract_products_from_page(page)
                if not page_products:
                    print(f"Нет товаров на странице {page_num}. Завершаем сбор.")
                    break

                print(f"Найдено {len(page_products)} товаров на странице {page_num}")
                self.products.extend(page_products)

                await asyncio.sleep(random.uniform(3, 5))
            except ValueError as e:
                print(f"Ошибка на странице {page_num}: {e}")
                break

    def save_products(self):
        """Сохранить данные в файл с помощью FileHandler."""
        self.file_handler.save_to_file(self.products)

    def load_existing_products(self):
        """Загрузить уже сохранённые данные."""
        return self.file_handler.load_from_file()

    def merge_existing_products(self):
        """Объединить новые данные с уже существующими."""
        existing_products = self.load_existing_products()
        self.products.extend(existing_products)
        print(f"Объединено {len(existing_products)} старых записей с {len(self.products)} новыми.")

    def calculate_total_price(self):
        """Подсчет общей суммы цен всех товаров."""
        total_price = 0
        for product in self.products:
            try:
                if isinstance(product['new_price'], int):  # Убедитесь, что цена — число
                    total_price += product['new_price']
                elif isinstance(product['new_price'], str) and product['new_price'].isdigit():
                    total_price += int(product['new_price'])
            except ValueError as e:
                print(f"Ошибка при обработке цены {product.get('new_price')}: {e}")
        print(f"Общая сумма всех товаров: {total_price}")
        return total_price


class ScraperRunner:
    """Использование класса для Playwright"""
    def __init__(self, urls, file_name):
        # Список URL-адресов
        self.urls = urls
        self.file_name = file_name
        # Инициализация FileHandler
        self.file_handler = FileHandler(file_name)

    async def run(self):
        """Настройка и выбор браузера"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False, args=BROWSER_ARGS)
            try:
                page = await browser.new_page()

                # Установка заголовков
                await page.set_extra_http_headers({
                    "User-Agent": random.choice(USER_AGENTS),
                    "Accept-Language": "en-US,en;q=0.9,ru;q=0.8",
                    "Accept-Encoding": "gzip, deflate, br",
                })


                for url in self.urls:
                    # Передаём FileHandler в ProductScraper
                    scraper = ProductScraper(url, self.file_handler)

                    try:
                        print(f"Сбор данных для категории: {url}")
                        await scraper.collect_products_from_category(page)
                        print(f"Всего собрано {len(scraper.products)} товаров из категории {url}.")

                        # Подсчет общей суммы
                        total_price = scraper.calculate_total_price()

                        # Сохранение данных
                        scraper.save_products()
                        # Подготовка имен файлов
                        category = url.split('/')[-2]
                        table_filename = f"products_table_{category}.csv"
                        excel_filename = f"products_table_{category}.xlsx"

                        # Сохранение данных в таблицу
                        self.file_handler.save_to_table(scraper.products, table_filename)
                        # Сохранение данных в Excel
                        self.file_handler.save_to_excel(scraper.products, excel_filename)

                        # # Сохранение данных в таблицу
                        # self.file_handler.save_to_table(scraper.products,
                        #                                 "products_table_{url.split('/')[-2]}.csv")
                        # # Сохранение данных в Excel
                        # self.file_handler.save_to_excel(scraper.products,
                        #                                 "products_table_{url.split('/')[-2]}.xlsx")

                        print(f"Общая сумма всех цен для категории {url}: {total_price}")
                    except ValueError as e:
                        print(f"Ошибка при обработке {url}: {e}")
                    finally:
                        # Пауза между обработкой категорий
                        await asyncio.sleep(random.uniform(3, 6))
            finally:
                await browser.close()

# Запуск программы
if __name__ == "__main__":
    URLS = ["https://lombard-perspectiva.ru/clocks_today/",
            "https://lombard-perspectiva.ru/jewellery/",
            "https://lombard-perspectiva.ru/accessories/",
            ]
    FILE = "products.json"
    runner = ScraperRunner(URLS, FILE)
    asyncio.run(runner.run())
