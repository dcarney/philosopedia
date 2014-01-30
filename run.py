import sys
import httplib
httplib.HTTPConnection.debuglevel = 1
import urllib2
import re
from BeautifulSoup import BeautifulSoup
import parens
import getopt
import simplejson as json
import pickle

# EXAMPLE:
# soup = BeautifulSoup(urllib2.urlopen('http://www.timeanddate.com/worldclock/astronomy.html?n=78').read())

# for row in soup('table', {'class' : 'spad'})[0].tbody('tr'):
  # tds = row('td')
  #print tds[0].string, tds[1].string
  # will print date and sunrise

MAX_RECURSE_DEPTH = 25
TARGET_WORD = "philosophy"

tempWordDepths = {}
wordDepths = {}
badWords = []

def printUsage():
	print("run.py -s <start_word> -t <target_word> -n <max_depth>")
	print("\tEx: run.py -s castle -t philosophy -n 25")
	print("\t    Trys to arrive at the entry 'Philosophy' in 25 links or less, starting at the entry 'Castle'")
	print("\n\t<target_word> defaults to 'philosophy'")
	print("\n\t<max_depth> defaults to 25")

def followWikiLinks(article, depth):
	print str(depth) + " --> " + article

	original_article = article
	article = article.lower()

	# We've already seen this word, and know it's good
	if article in wordDepths:
		return depth + wordDepths[article]

	# We've already seen this word, and know it's not going to work
	if article in badWords:
		return -1

	if (article == TARGET_WORD):
		return depth

	if (depth > MAX_RECURSE_DEPTH):
		print "*** max recursion depth reached"
		return -1

	# We've hit a "cycle", e.g. foo -> bar -> baz -> foo
	# All these words are "bad"
	if article in tempWordDepths:
		print "*** Cycle detected. Word will not reach " + TARGET_WORD
		return -1

	tempWordDepths[article] = depth

	try:
		# It appears that Wikipedia has some broken 303/302 redirects, and therefore
		# the case-sensitivity of the URL actuall matters.  Who knew?
		request = urllib2.Request('http://en.wikipedia.org/wiki/' + original_article)
		# Wikipedia filters out requests that have the default urllib2 user agent!
		request.add_header('User-Agent', 'OpenAnything/1.0 +http://diveintopython.org/')
		# debugHandler = urllib2.HTTPHandler(debuglevel=1)
		feeddata = urllib2.build_opener().open(request).read()
	except urllib2.HTTPError as ex:
		print ex, request.get_full_url()
		return -1

	# parse that junk
	soup = BeautifulSoup(feeddata)

	# most pages have a main article div
	mainArticleDiv = soup('div', {'id' : "bodyContent"})

	if ((mainArticleDiv is None) or (len(mainArticleDiv) < 1)):
		print "*** main article div not found"
		return -1

	# some pages have <p> elements before the one we're interested in, but
	# they're not direct children of the mainArticleDiv
	linkContainerTags = ['p', 'ul']
	linkContainer = None

	for elem in linkContainerTags:
		linkContainerElem = mainArticleDiv[0].findAll(elem, recursive=True) #limit=1
		#if ((linkContainerElem is not None) and (len(linkContainerElem) > 0)) :
			#linkContainer = linkContainerElem[0]
		#	break
		for linkContainer in linkContainerElem:

			if ((linkContainer is not None) and (len(linkContainer('a')) > 0)) :
				for link in linkContainer('a'):

					# print "link: ", link.string, link['href']

					# Check that it's a valid Wikipedia link that doesn't point to a citation or pronunciation guide
					if ((re.search(r"/wiki/", link['href'])) and not
						(re.search(r"/wiki/Wikipedia:", link['href'])) and not
						(re.search(r"\.ogg$", link['href'])) and not
						(re.search(r"#cite_note", link['href']))) :

						# Now, find the link in the complete page text using a regex.  We need to check
						# whether or not it's in parens.

						match = re.search(str(link['href']).replace("(", r"\(").replace(")", r"\)"), linkContainer.renderContents());
#						match = re.search(str(link['href']).replace("(", r"\(").replace(")", r"\)"), feeddata);
						if (match):
							# If the parens match, then we're not inside a pair of them...
							if (parens.checkParentheses(linkContainer.renderContents()[0:match.start()])):
							#if (parens.checkParentheses(feeddata[0:match.start()])):
								# Get the new article to look up
								newArticle = link['href'].replace('/wiki/', '')

								# recurse
								return followWikiLinks(newArticle, depth + 1)
								break
								break
						else:
							print "*** link not found in article text"
							return -1

def initWordLists():
	try:
		with open('good.pickle', 'rb') as f:
			return pickle.load(f)

	#	with open('bad.pickle', 'rb') as f:
	#		badWords = pickle.load(f)
	#		f.close()
	except IOError as ex:
		print ex, 'no file'


def saveWordLists():
	with open('good.pickle', 'wb') as f:
		#f.write(json.dumps(sorted(wordDepths.items())))
		pickle.dump(wordDepths, f)
		f.close()

	with open('bad.pickle', 'wb') as f:
		#f.write(json.dumps(sorted(badWords)))
		pickle.dump(badWords, f)
		f.close()

def printWordLists():
	print "word Depths: "
	for k, v in sorted(wordDepths.items()):
		print k, ":", v

	print "bad words:"
	print "\n", json.dumps(sorted(badWords), sort_keys=True, indent=3)


if __name__ == "__main__":

	try:
		# sys.argv[0] is just the name of the script
		if (len(sys.argv[1:]) < 1):
			printUsage()
			sys.exit(2)

		options, arguments = getopt.getopt(sys.argv[1:], "s:t:n:", ["start=", "target=", "depth="])

	except getopt.GetoptError:
		printUsage()
		sys.exit(2)

	# print("ARGUMENTS/OPTIONS: ")
	for opt, arg in options:
		# print("\t" + opt + " : " + arg)
		if (opt == "-s"):
			startWords = arg
		elif (opt == "-t"):
			TARGET_WORD = arg
		elif (opt == "-n"):
		 	MAX_RECURSE_DEPTH = arg

	print("")

	#wordDepths = initWordLists()
	if wordDepths is None: wordDepths = {}

	#printWordLists()

	#followFirstLink('Subject_(philosophy)', 0)
	#followFirstLink('Cultural_heritage')
	#followFirstLink('Psychophysiological', 0)
	#followFirstLink('math', 0)

	for startWord in startWords.split(','):
		tempWordDepths = {}
		foo = followWikiLinks(startWord, 0)

		if (foo != -1):
			print startWord + " is " + str(foo) + " Wikipedia hops from " + TARGET_WORD
			for word in tempWordDepths.keys():
				if not tempWordDepths[word] is None:
					tempWordDepths[word] = foo - tempWordDepths[word]

			# merge the temp dictionary, with the real dictionary. values in the
			# temporary dictionary will override those in the real dictionary
			wordDepths = dict(wordDepths.items() + tempWordDepths.items())
		else:
			for word in tempWordDepths.keys():
				if not word in badWords:
					badWords.append(word)
			print TARGET_WORD, "was not reached from", startWord

	saveWordLists()
	#printWordLists()

