import re
import sys
from game_item import Game
from crawler import GameCrawler

def parse_game_page(response, crawler):
	
	def check(path):
		tmp = response.xpath(path)
		return tmp[0].strip() if len(tmp) > 0 else ''
		
	game = Game()
	
	game.title = check('//div[@class="product_title"]/a/span/h1/text()')
	game.platform = check('//div[@class="product_title"]/span/a/span/text()')
	game.released = check('//li[contains(@class, "release_data")]/span[@class="data"]/text()')	
	game.reviews_count = check('//div[@class="section product_scores"]/div[@class="details main_details"]/div/div/div[@class="summary"]/p/span[@class="count"]/a/span/text()')
	game.metascore = check('//div[@class="section product_scores"]/div[@class="details main_details"]/div/div/a/div/span/text()')
	game.userscore = check('//div[@class="section product_scores"]/div[@class="details side_details"]/div[@class="score_summary"]/div/a/div/text()')
	game.user_count = check('//div[@class="section product_scores"]/div[@class="details side_details"]/div[@class="score_summary"]/div/div[@class="summary"]/p/span[@class="count"]/a/text()')	
	game.user_count = '0' if game.user_count == '' else re.findall('\d+', game.user_count)[0]
	game.developer = check('//li[@class="summary_detail developer"]/span[@class="data"]/text()')
	game.rating = check('//li[@class="summary_detail product_rating"]/span[@class="data"]/text()')
	game.genres = response.xpath('//li[@class="summary_detail product_genre"]/span[@class="data"]/text()')
	
	return game.__dict__;

def parse(response, crawler):
	
	if response[0] is None or crawler is None:
		return
	
	for item in response.xpath('//div[@class="product_wrap"]'):
		try:
			page = item.xpath('div[@class="basic_stat product_title"]/a/@href')
			
			if page:
				game = crawler.request('http://www.metacritic.com' + page[0].strip(), callback = parse_game_page)
				
		except KeyboardInterrupt:
			crawler.exit()
			
	next_page = response.xpath('//span[@class="flipper next"]/a/@href')
	if next_page:
		return crawler.request(url = 'http://www.metacritic.com' + next_page[0].strip(), callback = parse)
			
urls = ['http://www.metacritic.com/browse/games/release-date/available/ps3/date']

crawler = GameCrawler()
if len(sys.argv) > 1:
	crawler.path = sys.argv[1]

for url in urls:
	crawler.request(url, parse)
