from bs4 import BeautifulSoup as bs
import urllib
import re
import sys
import numpy
import json

# List of urls present which contain link to books specific to one genre
urls = [
	"https://www.gutenberg.org/wiki/Technology_(Bookshelf)"
	   ]

# To store book name and number pair for specific genre
bookNoList = {}

for url in urls:
	html = urllib.urlopen(url).read()
	soup = bs(html, "lxml")

	# To find the a tags with href and iterate over that list
	for a in soup.find_all('a', href=True):
	    bookNo = re.findall(r'[0-9]+',a['href'])
	    
	    if len(bookNo) == 1:
	    	bookNo = str(bookNo)
	    	#print bookNo
	    	bookNoList[a.text] = bookNo[2:len(bookNo) - 2]
	    	# a.text for name of the book

with open('Technology.txt', 'w') as outfile:
    json.dump(bookNoList, outfile)
