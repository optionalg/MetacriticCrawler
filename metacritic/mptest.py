import multiprocessing as mp
import signal
import sys
import time
from crawler import TestCrawler

urls = [
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
            
game_links = []
games = []
	
def product(base_list, *args):
	ret = []
	for item in base_list:
		ret.append((item,) + tuple(args))
	return ret

def collect_links(result):
	global urls
	global game_links
	if result['next'] is not None:
		urls.append(result['next'])
	game_links += result['links']

def collect_games(result):
	global games
	if result is not None:
		games.append(result)

def main():
	
	startup = time.time()
	out = open('output.json', 'w')
	out.write('[\n')
	crawler = TestCrawler()
	mp.set_start_method('fork')
	processes = 8
	pool = mp.Pool(processes = processes)
	counter = 0
	
	while True:
		for i in range(processes):
			if urls:
				pool.apply_async(crawler.download, (urls.pop(), 100, crawler.game_list_parse), callback = collect_links)
			elif game_links:
				pool.apply_async(crawler.download, (game_links.pop(), 5, crawler.game_page_parse), callback = collect_games)
			while games:
				out.write(games.pop() + ',\n')
				counter += 1
				print('%4d games scrapped' %counter)
				print('current_execution_time: %f' %(time.time() - startup))
			
			'''
			dif = len(urls) - processes
			if dif < 0:
				print('ALARM\ncounter: %d' %counter)
				#do something!
				
			results = pool.starmap(crawler.download, product(urls, 100, crawler.game_list_parse))
			urls = []
			for result in results:
				if result is not None:
					if result['next'] is not None:
						print('I have the next link')
						urls.append(result['next'])
					else:
						print('I have no next link')
					game_links += result['links']
			print('%d links crawled' %len(game_links))
			print('current execution time: %f' %(time.time() - startup))
			counter += 1
		#	50916 links crawled
		#	current execution time: 765.866702
			'''
			
		
if __name__ == '__main__':
    main()
