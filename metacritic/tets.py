import multiprocessing as mp
import signal
import sys
import time
from crawler import CrawlerMP

def main():
	
	arr = [0 for i in range(5)]
	'''
	for i in range(5):
		arr[0] = i
		for j in range(5):
			arr[1] = j
			for k in range(5):
				arr[2] = k
				for l in range(5):
					arr[3] = l
					for m in range(5):
						arr[4] = m
						for item in arr: print(item, ' ', end = '')
						print()
	'''
	def func(i = 0, arr = arr):
		if arr[i] < len(arr):
			arr[i] += 1
			i = 0
		#	func(0, arr)
		elif i + 1 < len(arr):
			arr[i] = 0
			arr[i + 1] += 1
			i += 1
		#	arr[i + 1] += 1
		#	func(i + 1, arr)
		for item in arr: print(item, ' ', end = '')
		print()
		func(i, arr)
	
	func()		

if __name__ == '__main__':
    main()
