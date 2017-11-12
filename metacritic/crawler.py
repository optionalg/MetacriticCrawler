from lxml import html
import requests
import json
import sys

class GameCrawler:
	
	headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
	games_counter = 0
	cache = []
	
	def __init__(self):
		self.requests_counter = 0
		
	def request(self, url, callback):
		print ('%d: %s' %(self.games_counter, url))
		page = requests.get(url, headers = self.headers)
		if(page.status_code == requests.codes.ok):
			tree = html.fromstring(page.content)
			self.cache.append(callback(tree, self))
			self.games_counter = len(self.cache)
		else:
			print ('Error: bad responce code')
			self.serialize(self)
	
	def serialize(self, output):
		with open('output.json' if not output else output, 'w') as outfile:  
			json.dump(self.cache, outfile, indent = 4)
		
	def exit(self, output):
		self.serialize(output)
		sys.exit()
		
