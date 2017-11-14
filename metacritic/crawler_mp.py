import multiprocessing as mp
import signal
import sys
import time
from crawler import CrawlerMP

def get_free(array):
    r = []
    i = 0
    while i < len(array) - 1:
        if not array[i].is_alive():
            r.append(array.pop(i))
        i += 1
    return r

def main():

    global counter
    counter = 0
    out = open('output.json', 'w')
    out.write('[\n')
    
    mp.set_start_method('spawn')
    manager = mp.Manager()
    list_queue = manager.Queue()
    game_queue = manager.Queue()
    crawler = CrawlerMP(list_queue = list_queue, game_queue = game_queue)
    workers = []
    
    def output():
        out.write(game_queue.get() + ',\n')
        global counter
        counter += 1
        print('%4d games scrapped' %counter)
        
    def exit(signum, frame):
        while not game_queue.empty():
            output()
        out.write('\n]')
        for proc in workers:
            proc.terminate()
        list_queue.close()
        game_queue.close()
        
    signal.signal(signal.SIGINT, exit)

    urls = [
            'http://www.metacritic.com/browse/games/release-date/available/dreamcast/date',
            'http://www.metacritic.com/browse/games/release-date/available/ps/date',
            'http://www.metacritic.com/browse/games/release-date/available/ps2/date'
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
        
    for url in urls:
        proc = mp.Process(target=crawler.download, args=(url, 100, crawler.game_list_parse,))
        workers.append(proc)
        proc.start()
    
    while len(workers) > 0:
        if not game_queue.empty():
            output()
        free = get_free(workers)
        for proc in free:
             while not list_queue.empty() and len(workers) < 8:
                proc = mp.Process(target=crawler.download, args=(list_queue.get(), 5, crawler.game_page_parse,))
                workers.append(proc)
                proc.start()

    exit()

if __name__ == '__main__':
    main()
