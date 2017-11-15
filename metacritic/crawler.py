from lxml import html
import time
import requests
import json
import signal
import re
from game_item import Game

class Crawler:
	
	def __init__(self):
		self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
		self.urls = [
			'http://www.metacritic.com/browse/games/release-date/available/dreamcast/date',
			'http://www.metacritic.com/browse/games/release-date/available/ps/date',
			'http://www.metacritic.com/browse/games/release-date/available/ps2/date',
			'http://www.metacritic.com/browse/games/release-date/available/ps3/date',
			'http://www.metacritic.com/browse/games/release-date/available/ps4/date',
			'http://www.metacritic.com/browse/games/release-date/available/xbox/date',
			'http://www.metacritic.com/browse/games/release-date/available/xbox360/date',
			'http://www.metacritic.com/browse/games/release-date/available/xboxone/date',
			'http://www.metacritic.com/browse/games/release-date/available/n64/date',
			'http://www.metacritic.com/browse/games/release-date/available/gamecube/date',
			'http://www.metacritic.com/browse/games/release-date/available/wii/date',
			'http://www.metacritic.com/browse/games/release-date/available/wii-u/date',
			'http://www.metacritic.com/browse/games/release-date/available/switch/date',
			'http://www.metacritic.com/browse/games/release-date/available/gba/date',
			'http://www.metacritic.com/browse/games/release-date/available/ds/date',
			'http://www.metacritic.com/browse/games/release-date/available/3ds/date',
			'http://www.metacritic.com/browse/games/release-date/available/psp/date',
			'http://www.metacritic.com/browse/games/release-date/available/vita/date',
			'http://www.metacritic.com/browse/games/release-date/available/pc/date'
			]
		self.game_links = []
		self.games = []
		self.game_counter = 0
		self.startup = time.time()
		
	def collect_links(self, result):
		if not isinstance(result, str):
			if result['next'] is not None:
				self.urls.append(result['next'])
			self.game_links += result['links']
		else:
			self.urls.append(result)
			
	def collect_games(self, result):
		if not isinstance(result, str):
			self.games.append(json.dumps(result, indent = 4))
		else:
			self.game_links.append(result)

	def output(self, file):
		while self.games:
			file.write((',\n' if self.game_counter > 0 else '') + self.games.pop())
			self.game_counter += 1
			print('%4d games scrapped' %self.game_counter)
			print('current execution time: %f' %(time.time() - self.startup))			

	def print_list_links(self):
		for i in range(len(self.urls)):
                        print('%3d: %s' %(i, self.urls[i]))

	def print_game_links(self):
		for i in range(len(self.game_links)):
                        print('%3d: %s' %(i, self.game_links[i]))

	def download(self, url, retries = 0, callback = None):
		signal.signal(signal.SIGINT, signal.SIG_IGN)
		print ('downloading %s' %url)
		try:
			page = requests.get(url, headers = self.headers)
			if page.status_code == requests.codes.ok:
				if callback is not None:
					return callback(html.fromstring(page.content), url)
				else:
					print('downloaded %s. and what now?' %url)
			elif retries > 0:
				time.sleep(0.1)
				return self.download(url, retries - 1, callback)
			else:
				print ('Warning: bad response code. Dropping the request')
				return url
		except requests.exceptions.RequestException as e:
			if retries > 0:
				time.sleep(0.1)
				return self.download(url, retries - 1, callback)
			else:
				print ('Error: unsolvable exception:\n"%s"\n' %e)
				return url
	
	def game_list_parse(self, response, url):
		if response is None:
			return url
		
		ret = {'links': [], 'next': None}
		
		for item in response.xpath('//div[@class="product_wrap"]'):
			page = item.xpath('div[@class="basic_stat product_title"]/a/@href')
			if page:
				ret['links'].append('http://www.metacritic.com' + page[0].strip())
			else:
				print('invalid page')
				return url
		
		next_page = response.xpath('//span[@class="flipper next"]/a/@href')
		if next_page:
			ret['next'] = 'http://www.metacritic.com' + next_page[0].strip()
		return ret
			
	def game_page_parse(self, response, url):
		if response is None:
			return url
		
		main = response.xpath('//div[@id="main"]/div')[0]
		if len(main) > 0: main = main[0]
		else: return url
                
                head = main.xpath('div[@class="content_head product_content_head game_content_head"]')[0]
                if len(head) > 0: head = head[0]
		else: return url
		
                scores = main.xpath('div[@class="module product_data product_data_summary"]/div/div[@class="summary_wrap"]/div[@class="section product_scores"]')[0]
                if len(scores) > 0: scores = scores[0]
		else: return url

                details = main.xpath('div[@class="module product_data product_data_summary"]/div/div[@class="summary_wrap"]/div[@class="section product_details"]/div[@class="details side_details"]/ul')[0]
                if len(details) > 0: details = details[0]
		else: return url
		
		def check(root, path):
			tmp = root.xpath(path)
			return tmp[0].strip() if len(tmp) > 0 else 'tbd'
		
		game = Game()
                
		game.title = check(head, 'div[@class="product_title"]/a/span/h1/text()')
		game.platform = check(head, 'div[@class="product_title"]/span/a/span/text() | div[@class="product_title"]/span/span/text()')
		game.released = check(head, 'div[@class="product_data"]/ul/li[@class="summary_detail release_data"]/span[@class="data"]/text()')	

		game.metascore = check(scores, 'div[@class="details main_details"]/div/div/a/div/span/text()')
		game.reviews_count = check(scores, 'div[@class="details main_details"]/div/div/div[@class="summary"]/p/span[@class="count"]/a/span/text()')
		game.userscore = check(scores, 'div[@class="details side_details"]/div/div/a/div/text()')
		game.user_count = check(scores, 'div[@class="details side_details"]/div/div/div[@class="summary"]/p/span[@class="count"]/a/text()')	
		game.user_count = '0' if game.user_count == 'tbd' else re.findall('\d+', game.user_count)[0]

		game.developer = check(details, 'li[@class="summary_detail developer"]/span[@class="data"]/text()')
		game.rating = check(details, 'li[@class="summary_detail product_rating"]/span[@class="data"]/text()')
		game.genres = details.xpath('li[@class="summary_detail product_genre"]/span[@class="data"]/text()')
							
		return game.__dict__

