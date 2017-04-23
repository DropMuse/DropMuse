import sys
#from MyScraper import Scraper(artistImport)
from MyScraper import *


userInput = input("Please enter something: ")
print(userInput)
if(userInput == 'file'):
	text_file = open("Artists.txt", "r")											#txt file containing artists, 1 per line
	Artists = text_file.readlines()
	text_file.close()
	for i in range(0, len(Artists)):
		Scraper(Artists[i])
else:
	Scraper(userInput)