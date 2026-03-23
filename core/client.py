import requests

class Client:
    def __init__(self):
        self.headers = {
            'Accept': '*/*',
            'Accept-Language': 'ru-RU,ru;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
        }

    def get_request_result(self, query):
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

    def parse_products(self, json_response) -> list:

        if not json_response:
            return []

        products = json_response.get("products")
        parsed_data = []

        for item in products:

            sizes = item.get("sizes", [{}])
            price_data = sizes[0].get("price", {})

            sale_price = price_data.get("product", 0) / 100

            info = {
                "id": item.get("id"),
                "name": item.get("name"),
                "brand": item.get("brand"),
                "rating": item.get("reviewRating"),
                "feedbacks": item.get("feedbacks"),
                "price": sale_price,
                "url": f"https://www.wildberries.ru/catalog/{item.get('id')}/detail.aspx"
            }

            parsed_data.append(info)

        return parsed_data



client = Client()
json_response = client.get_request_result(query="пальто из натуральной шерсти")
cleaned_data = client.parse_products(json_response)

for product in cleaned_data:
    print(f"Название: {product['name']} | Цена: {product['price']}")

