from __future__ import annotations
import requests
from bs4 import BeautifulSoup
import json
import html

class FunPaySupportAPI:
    """
    API сайта поддержки FunPay.

    :param golden_key: golden_key аккаунта.
    :type golden_key: `str`

    :param user_agent: user_agent браузера _(опционально)_.
    :type user_agent: `str`

    :param timeout: Максимальное длительность запроса в секундах.
    :type timeout: `int`
    """

    def __init__(self, golden_key: str, user_agent: str | None, timeout: int = 10):
        self.golden_key: str = golden_key
        """ golden_key аккаунта. """
        self.user_agent: str = user_agent
        """ user_agent браузера _(опционально)_. """
        self.timeout: int = timeout
        """ Максимальное длительность запроса в секундах. """

        self.app_data: dict = {}
        """ AppData пользователя. """

        self.csrf_token: str = ""
        """ CSRF токен. """
        self.phpsessid: str = ""
        """ PHPSESSID аккаунта. """

    def method(self, method: str, url: str, headers: dict[str, str] = {}, payload: dict = {},
               exclude_phpsessid: bool = False) -> requests.Response:
        """
        Отправляет запрос на сайт поддержки.

        :param method: Метод запроса (get или post).
        :type method: `str`

        :param url: URL запроса.
        :type url: `str`

        :param headers: Заголовки запроса.
        :type headers: `dict[str, str]`

        :param payload: Payload запроса.
        :type payload: `dict`

        :return: Ответа запроса.
        :rtype: `requests.Response`
        """
        headers["Cookie"] = f"golden_key={self.golden_key}; cookie_prefs=1"
        headers["Cookie"] += f"; PHPSESSID={self.phpsessid}" if self.phpsessid and not exclude_phpsessid else ""
        if self.user_agent:
            headers["User-Agent"] = self.user_agent

        link = url
        for i in range(10):
            response: requests.Response = getattr(requests, method)(link, headers=headers, 
                                                                    data=payload, timeout=self.timeout, 
                                                                    allow_redirects=False)
            if not (300 <= response.status_code < 400) or not response.headers.get('Location') or response.headers.get('Location') == '/':
                break
            link = response.headers['Location']
        else:
            response = getattr(requests, method)(url, headers=headers, data=payload,
                                                 timeout=self.timeout)
        return response
        
    def get(self) -> FunPaySupportAPI:
        """
        Получает и заполняет/обновляет данные аккаунта на сайте поддержки.
        """
        r = self.method("get", "https://support.funpay.com/", {}, {}, True)
        cookies = r.cookies.get_dict()
        self.phpsessid = cookies.get("PHPSESSID", self.phpsessid)
        r = self.method("get", "https://support.funpay.com/", {}, {}, False)

        html_response = r.content.decode()
        parser = BeautifulSoup(html_response, "lxml")
        self.app_data = json.loads(parser.find("body").get("data-app-config"))

        self.csrf_token = self.app_data["csrfToken"]
        return self
        
    def get_ticket_token(self):
        """
        Получает токен для создания тикета.
        """
        headers = {
            "X-CSRF-Token": self.csrf_token,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Referer": "https://support.funpay.com/",
        }
        r = self.method("get", "https://support.funpay.com/tickets/new/1", headers)
        soup = BeautifulSoup(r.text, "html.parser")
        body = soup.find("input", attrs={"name": "ticket[_token]"})
        return body.get("value")

        
    def create_ticket(self, username: str, order_id: str | None, comment: str) -> dict:
        """
        Создаёт тикет в поддержку с просьбой подтвердить заказ.

        :param username: Юзернейм аккаунта.
        :type username: `str`

        :param order_id: ID заказа.
        :type order_id: `str` or `None`

        :param comment: Комментарий заявки.
        :type comment: `str`

        :return: JSON ответ запроса.
        :rtype: `dict`
        """
        ticket_token = self.get_ticket_token()
        headers = {
            "Origin": "https://support.funpay.com",
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest"
        }
        payload = {
            "ticket[fields][1]": username,
            "ticket[fields][2]": order_id if order_id else "",
            "ticket[fields][3]": "2",
            "ticket[fields][5]": "201",
            "ticket[comment][body_html]": f"<p>{comment}</p>",
            "ticket[comment][attachments]": "",
            "ticket[_token]": ticket_token
        }
        r = self.method("post", "https://support.funpay.com/tickets/create/1", headers, payload)
        return r.json()