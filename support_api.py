from __future__ import annotations
import requests
from bs4 import BeautifulSoup
import json

from FunPayAPI import Account


class FunPaySupportAPI:
    def __init__(self, funpay_account: Account):
        self.funpay_account: Account = funpay_account
        self.golden_key = funpay_account.golden_key
        self.user_agent = funpay_account.user_agent
        self.requests_timeout = funpay_account.requests_timeout

        self.app_data = {}

        self.csrf_token = ""
        self.phpsessid = ""

    def method(self, method, url, headers={}, payload={}, exclude_phpsessid=False) -> requests.Response:
        headers["Cookie"] = f"golden_key={self.golden_key}; cookie_prefs=1"
        headers["Cookie"] += f"; PHPSESSID={self.phpsessid}" if self.phpsessid and not exclude_phpsessid else ""
        if self.user_agent:
            headers["User-Agent"] = self.user_agent

        for _ in range(10):
            response: requests.Response = getattr(requests, method)(
                url=url, 
                headers=headers, 
                data=payload, 
                timeout=self.requests_timeout, 
                allow_redirects=False
            )
            if not (300 <= response.status_code < 400) or not response.headers.get('Location') or response.headers.get('Location') == '/':
                break
            url = response.headers['Location']
        else:
            response = getattr(requests, method)(
                url=url, 
                headers=headers, 
                data=payload,
                timeout=self.requests_timeout
            )
        return response
        
    def get(self) -> FunPaySupportAPI:
        r = self.method("get", "https://support.funpay.com/", {}, {}, True)
        cookies = r.cookies.get_dict()
        self.phpsessid = cookies.get("PHPSESSID", self.phpsessid)
        r = self.method("get", "https://support.funpay.com/", {}, {}, False)

        html_response = r.content.decode()
        parser = BeautifulSoup(html_response, "lxml")
        self.app_data = json.loads(parser.find("body").get("data-app-config"))

        self.csrf_token = self.app_data["csrfToken"]
        return self
        
    def get_ticket_token(self) -> str:
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
        
    def create_ticket(self, order_id: str | None, comment: str) -> dict:
        ticket_token = self.get_ticket_token()
        headers = {
            "Origin": "https://support.funpay.com",
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest"
        }
        payload = {
            "ticket[fields][1]": self.funpay_account.username,
            "ticket[fields][2]": order_id if order_id else "",
            "ticket[fields][3]": "2",
            "ticket[fields][5]": "201",
            "ticket[comment][body_html]": f"<p>{comment}</p>",
            "ticket[comment][attachments]": "",
            "ticket[_token]": ticket_token
        }
        r = self.method("post", "https://support.funpay.com/tickets/create/1", headers, payload)
        return r.json()