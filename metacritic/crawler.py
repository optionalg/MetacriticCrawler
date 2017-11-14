from lxml import html
import time
import requests
import json
import signal
import sys
import re
from game_item import Game
import multiprocessing as mp

class GameCrawler:

	def __init__(self, path = 'output.json'):
		self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
		self.backup_interval = 300
		self.current_time = time.time()
		self.games_counter = 0
		self.cache = []
		self.path = path
		self.output = open(path, 'w')
		self.max_attempts = 10
		self.current_attemps = 0

		self.debug_log = open('log.txt', 'w')
		
	def request(self, url, callback):
                print ('%d: %s' %(self.games_counter, url))
                try:
                        page = requests.get(url, headers = self.headers)
                        if page.status_code == requests.codes.ok:
                                tree = html.fromstring(page.content)
                                tmp = callback(tree, self)
                                if tmp is not None:
                                        self.games_counter += 1
                                        self.cache.append(callback(tree, self))
                                self.current_attempts = 0
                                if time.time() - self.current_time > self.backup_interval:
                                        print ('Backing everything up...')
                                        self.serialize()
                        elif self.current_attempts <= self.max_attempts:
                                self.current_attempts += 1
                                self.request(url, callback)
                                self.debug_log.write('\nWarning: bad response code\n%s\n' %url)
                        else:
                                print ('Warning: bad response code. Dropping the request')
                                self.debug_log.write ('\nBad response code %d times in a row. Dropping this request\n%s\n' %(self.max_attempts, url))
                                self.current_attempts = 0
                                
                except requests.exceptions.RequestException as e:
                        self.debug_log.write('\nrequests exception raised: %s\n%s\n' %(e, url))
                        if self.current_attempts <= self.max_attempts:
                                self.debug_log.write('\nBut I still have attempts left\n')
                                self.current_attempts += 1
                                self.request(url, callback)
                        else:
                                self.debug_log.write('\nNo attempts left. Dropping the request\n' %url)
                                self.current_attempts = 0
                                print ('Error: unsolvable exception')
                                
	def serialize(self):
		self.current_time = time.time()
		json.dump(self.cache, self.output, indent = 4)
		del self.cache[:]
		print ('Data saved to: "%s"' %self.path)
		
	def exit(self):
		self.serialize()
		self.output.close()
		self.debug_log.close()
		sys.exit()

class CrawlerMP:
        
        def __init__(self, list_queue = None, game_queue = None):
                self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
                self.counter = 0
                self.list_queue = list_queue
                self.game_queue = game_queue
                
        def download(self, url, attempts_left, callback = None):

                signal.signal(signal.SIGINT, signal.SIG_IGN)
                
                print ('downloading %s ...' %url)
                try:
                        page = requests.get(url, headers = self.headers)
                        if page.status_code == requests.codes.ok:
                                if callback is not None:
                                        callback(html.fromstring(page.content), self)
                                else:
                                        print('downloaded %s ... and what now?' %url)
                        elif attempts_left > 0:
                                sys.exit(1)
                                self.download(url, attempts_left - 1, callback)
                        else:
                                print ('Warning: bad response code. Dropping the request')
                                
                except requests.exceptions.RequestException as e:
                        if attempts_left > 0:
                                sys.exit(1)
                                self.download(url, attempts_left - 1, callback)
                        else:
                                print ('Error: unsolvable exception:\n"%s"\n' %e)
        
        def game_list_parse(self, response, downloader = None):

                if response is None:
                        return
                
                for item in response.xpath('//div[@class="product_wrap"]'):
                        page = item.xpath('div[@class="basic_stat product_title"]/a/@href')      
                        if page and self.list_queue is not None:
                                self.list_queue.put('http://www.metacritic.com' + page[0].strip())
                        else:
                                sys.exit(1)
                                
                next_page = response.xpath('//span[@class="flipper next"]/a/@href')
                if next_page and downloader is not None:
                        downloader.download(url = 'http://www.metacritic.com' + next_page[0].strip(), attempts_left = 100, callback = self.game_list_parse)
                else:
                        sys.exit(1)

        def game_page_parse(self, response, downloader = None):

                if response is None:
                        return
                        
                def check(path):
                        tmp = response.xpath(path)
                        return tmp[0].strip() if len(tmp) > 0 else 'tbd'
		
                game = Game()
                
                game.title = check('//div[@class="product_title"]/a/span/h1/text()')
                game.platform = check('//div[@class="product_title"]/span/a/span/text()|//div[@class="product_title"]/span/span/text()')
                game.released = check('//li[contains(@class, "release_data")]/span[@class="data"]/text()')	
                game.reviews_count = check('//div[@class="section product_scores"]/div[@class="details main_details"]/div/div/div[@class="summary"]/p/span[@class="count"]/a/span/text()')
                game.metascore = check('//div[@class="section product_scores"]/div[@class="details main_details"]/div/div/a/div/span/text()')
                game.userscore = check('//div[@class="section product_scores"]/div[@class="details side_details"]/div[@class="score_summary"]/div/a/div/text()')
                game.user_count = check('//div[@class="section product_scores"]/div[@class="details side_details"]/div[@class="score_summary"]/div/div[@class="summary"]/p/span[@class="count"]/a/text()')	
                game.user_count = '0' if game.user_count == 'tbd' else re.findall('\d+', game.user_count)[0]
                game.developer = check('//li[@class="summary_detail developer"]/span[@class="data"]/text()')
                game.rating = check('//li[@class="summary_detail product_rating"]/span[@class="data"]/text()')
                game.genres = response.xpath('//li[@class="summary_detail product_genre"]/span[@class="data"]/text()')

                self.game_queue.put(json.dumps(game.__dict__, indent = 4))
