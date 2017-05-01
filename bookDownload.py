#from bs4 import BeautifulSoup as bs
#import urllib
import json
#import time
import sys
import requests
import os

json_data=open(sys.argv[1]).read()

data = json.loads(json_data)

bookName = str(sys.argv[1])
print bookName, bookName[:len(bookName)-4]


for key, value in data.iteritems():
	print key, value

	directory = str(os.getcwd()) + '/' + str(bookName[:len(bookName)-4]) + '/' + str(value) + ".txt"
	url = "http://www.gutenberg.org/cache/epub/" + str(value) + "/pg" + str(value) + ".txt"
	h = requests.head(url)

	#print directory, "\n\n\n\n"

	print h.headers['content-length']

	if int(h.headers['content-length']) < 200:
		url = "http://www.gutenberg.org/files/" + str(value) + "/" + str(value) + "-0.txt"

	h = requests.head(url)

	if int(h.headers['content-length']) > 200:
		try:
			data = requests.get(url)
			page = data.text
			f = open((directory), "w")
			f.write(str(page.encode('utf8')))
			f.close()

		except:
			print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"