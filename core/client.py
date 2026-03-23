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

        response = requests.get(url, params=params, headers=self.headers)

        return response.json()



result = Client()
response_json = result.get_request_result(query="пальто из натуральной шерсти")
products = response_json.get("products")


for item in products:
    name = item.get("name")
    brand = item.get("brand")
    rating = item.get("reviewRating")
    price_raw = item.get("sizes", [{}])[0].get("price", {}).get("product", 0)
    price = price_raw / 100

    print(f"Товар: {name} | Бренд: {brand} | Цена: {price} руб. | Рейтинг: {rating}")