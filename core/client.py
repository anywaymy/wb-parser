import os
import requests
import pandas

from pathlib import Path

from typing import List, Dict, Any


BASE_DIR = Path(__file__).resolve().parent.parent


class Client:
    def __init__(self):
        self.headers = {
            'Accept': '*/*',
            'Accept-Language': 'ru-RU,ru;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
        }

    def get_request_result(self, *, query: str) -> dict:
        url = f"https://search.wb.ru/exactmatch/ru/common/v4/search"
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

        try:
            response = requests.get(url, params=params, headers=self.headers)
            return response.json()
        except Exception as e:
            print(f"Ошибка запроса: {e}")

    def parse_products(self, *, json_response) -> list:

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

    def filter_products(
            self,
            data,
            *,
            min_rating: float=4.5,
            max_price: int =10000) -> list:

        filtered = [item for item in data if item.get('rating', 0) >= min_rating and item.get('price', 0) <= max_price]

        return filtered

    def save_to_excel(self, data, *, filename: str = "data.wb_results.xlsx"):
        if not data:
            print("Данные отсутствуют")
            return

        try:
            data_frame = pandas.DataFrame(data)
            folder_name = "data"

            main_dir = os.path.join(BASE_DIR, folder_name)

            if not os.path.exists(main_dir):
                os.makedirs(main_dir)
                print(f"Папка '{folder_name}' была создана.")

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
            print(f"Успешно сохранено! Файл: {filename} | Строк: {len(data_frame)}")

        except Exception as e:
            print(f"Ошибка при сохранении в Excel: {e}")


if __name__ == "__main__":
    client = Client()
    json_response = client.get_request_result(query="пальто из натуральной шерсти")
    cleaned_data = client.parse_products(json_response=json_response)
    filtered_data = client.filter_products(cleaned_data, min_rating=4.5, max_price=10000)

    client.save_to_excel(filtered_data, filename="filtered_data.xlsx")


