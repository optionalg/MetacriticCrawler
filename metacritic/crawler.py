from lxml import html
import time
import requests
import json
import sys

class GameCrawler:

	def __init__(self, path = 'output.json'):
		self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
		self.backup_interval = 300
		self.current_time = time.time()
		self.games_counter = 0
		self.cache = []
		self.path = path
		
	def request(self, url, callback):
		print ('%d: %s' %(self.games_counter, url))
		page = requests.get(url, headers = self.headers)
		if page.status_code == requests.codes.ok:
			tree = html.fromstring(page.content)
			self.cache.append(callback(tree, self))
			self.games_counter = len(self.cache)
			if time.time() - self.current_time > self.backup_interval:
				print ('Backing everything up...')
				self.serialize()
		else:
			print ('Error: bad responce code')
			self.serialize()
	
	def serialize(self):
		self.current_time = time.time()
		with open(self.path, 'w') as outfile:  
			json.dump(self.cache, outfile, indent = 4)
		print ('Data saved to: "%s"' %self.path)
		
	def exit(self):
		self.serialize()
		sys.exit()
		
