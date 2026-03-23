import logging
import os
from pathlib import Path
from typing import Any

import pandas
import requests


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("parser.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent


class Client:
    def __init__(self):
        self.headers = {
            'Accept': '*/*',
            'Accept-Language': 'ru-RU,ru;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
        }

    def get_request_result(self, *, query: str) -> dict[str, Any]:
        url = "https://search.wb.ru/exactmatch/ru/common/v4/search"

        params = {
            'ab_new_nm_vectors': 'true',
            'appType': 1,
            'curr': 'rub',
            'dest': 123585477,
            'query': query,
            'resultset': 'catalog',
            'sort': 'popular',
            'spp': 30
        }

        logger.info(f"Запуск поиска по запросу: '{query}'")

        try:
            response = requests.get(url, params=params, headers=self.headers)
            logger.info(f"Запрос выполнен успешно. Статус: {response.status_code}")
            return response.json()
        except Exception as e:
            logger.error(f"Ошибка запроса '{query}': {e}")
            return {}

    def parse_products_with_details(self, *, json_response: dict[str, Any]) -> list:

        if not json_response:
            return []

        products = json_response.get("products")
        parsed_data = []

        for item in products:

            sizes = item.get("sizes", [{}])
            price_data = sizes[0].get("price", {}) if sizes else 0
            sale_price = price_data.get("product", 0) / 100

            info = {
                "id": item.get("id"),
                "name": item.get("name"),
                "brand": item.get("brand"),
                "rating": item.get("reviewRating", 0),
                "feedbacks": item.get("feedbacks", 0),
                "price": sale_price,
                "url": f"https://www.wildberries.ru/catalog/{item.get('id')}/detail.aspx"
            }

            parsed_data.append(info)

        return parsed_data

    def get_product_details(self, articles: list[int]) -> None:
        pass

    def filter_products(
            self,
            data: list[dict[str, Any]],
            *,
            min_rating: float = 4.5,
            max_price: int = 10000) -> list:

        filtered = [item for item in data if item.get('rating', 0) >= min_rating and item.get('price', 0) <= max_price]

        return filtered

    def save_to_excel(self, data: list[dict[str, Any]], *, filename: str = "data.wb_results.xlsx") -> None:
        if not data:
            logger.warning("Данные отсутствуют")
            return

        try:
            data_frame = pandas.DataFrame(data)
            folder_name = "data"

            main_dir = os.path.join(BASE_DIR, folder_name)

            if not os.path.exists(main_dir):
                os.makedirs(main_dir)
                logger.info(f"Папка '{folder_name}' была создана.")

            full_path = os.path.join(main_dir, filename)

            column_mapping = {
                "id": "Артикул",
                "name": "Название",
                "brand": "Бренд",
                "rating": "Рейтинг",
                "feedbacks": "Отзывы",
                "price": "Цена (руб)",
                "url": "Ссылка"
            }

            data_frame = data_frame.rename(columns=column_mapping)
            data_frame.to_excel(full_path, index=False)
            logger.info(f"Файл {filename} успешно сохранен. Найдено: {len(data)}")

        except Exception as e:
            logger.error(f"Ошибка при сохранении в Excel: {e}")


if __name__ == "__main__":
    client = Client()

    json_response = client.get_request_result(query="пальто из натуральной шерсти")
    # items = json_response.get("products", {})
    # articles = [item.get("id") for item in items]
    # json_details = client.get_product_details(articles=articles)
    # print(json_details)
    cleaned_data = client.parse_products_with_details(json_response=json_response)
    filtered_data = client.filter_products(cleaned_data, min_rating=4.5, max_price=10000)

    client.save_to_excel(filtered_data, filename="filtered_data.xlsx")
