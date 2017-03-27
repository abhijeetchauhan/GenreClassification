import os
import sys
import nltk
import re
from nltk.corpus import wordnet as wn
from nltk import word_tokenize
from nltk.corpus import stopwords
from pywsd.baseline import random_sense, first_sense
from pywsd.baseline import max_lemma_count as most_frequent_sense
from collections import Counter
from pandas import Series, DataFrame
from time import time

# ------------------------------------ TO DO -----------------------------------------
'''
  1. Normalize word occurance value(will do this in modeling process, save file length as a feature)
'''
# ------------------------------------------------------------------------------------

startTime = time() 

# ------------------------------------- Declaring variables -------------------------
path = str(os.getcwd()) + '/' + str(sys.argv[1]) + '/'
allGenre = {'Crime':1,'Children':2,'Fiction':3,'Geography':4,'History':5,'Psychology':6,'Religion':7}
genre = allGenre[str(sys.argv[1])]

startString = "START OF THIS PROJECT GUTENBERG EBOOK"
endString = "END OF THIS PROJECT GUTENBERG EBOOK"
startString = startString.lower()
endString = endString.lower()

stop = set(stopwords.words('english'))

text_files= [f for f in os.listdir(path) if f.endswith('.txt')]
bookId = []
n= 2 # len(text_files) # No of text files
wordnet = []
features = {}
totalWords = []
temp =[0]*n
for text in text_files:
  bookId.append(text[:-4])
features['genre'] = [str(genre)]*n
features['bookId'] = bookId[:n]
wordnet.append('genre')
wordnet.append('bookId')
# -----------------------------------------------------------------------------------

# ------------------------------------- List of features -----------------------------
wordnet.append('entity.n.01') # root
features['entity.n.01'] = temp
for i in wn.synset('entity.n.01').hyponyms():
    wordnet.append(i.name()) # level 1
    features[i.name()] = temp
    
def incWordnet(root,excep=""): # function to add all words upto 2 levels from root, excep won't be checked
    for lev1 in wn.synset(str(root)).hyponyms():
        wordnet.append(lev1.name())
        features[str(lev1.name())] = temp
        if lev1.name() != str(excep):
            for lev2 in wn.synset(str(lev1.name())).hyponyms():
                if lev2.name() != "null_set.n.01":
                    wordnet.append(lev2.name())
                    features[str(lev2.name())] = temp
                    
# Adding selected features
incWordnet('abstraction.n.06') 
incWordnet('thing.n.08')
incWordnet('Physical_entity.n.01','object.n.01')
incWordnet('object.n.01','whole.n.02')
incWordnet('whole.n.02','artifact.n.01')
incWordnet('artifact.n.01','instrumentality.n.03')
incWordnet('instrumentality.n.03')
# ------------------------------------------------------------------------------------

# ----------------------------- Preprocessing functions ------------------------------
def PlusOneIfPossible(length,i,path): #Checking down upto 2 levels
    DistanceBottom = length - i;
    if DistanceBottom == 1:
        return path[i+1].name()
    elif DistanceBottom > 1:
        return path[i+2].name()
    
def transform(synsetName):  # updating synset to related synset
    result = []
    paths = wn.synset(synsetName).hypernym_paths()
    number = len(paths)
    for path in paths:
        length = len(path) -1
        i=0;
        if path[i].name() == 'entity.n.01' and length>i:
            i = i + 1
            if length == i: # if leaf node occurs
                result.append(path[i].name())
            elif path[i].name() == 'physical_entity.n.01':
                i = i + 1
                if length == i:
                    result.append(path[i].name())
                elif path[i].name() == 'object.n.01':
                    i = i + 1
                    if length == i:
                        result.append(path[i].name())
                    elif path[i].name() == 'whole.n.02':
                        i = i + 1
                        if length == i:
                            result.append(path[i].name())
                        elif path[i].name() == 'artifact.n.01':
                            i = i + 1
                            if length == i:
                                result.append(path[i].name())
                            elif path[i].name() == 'instrumentality.n.03':
                                i = i + 1
                                if length == i:
                                    result.append(path[i].name())
                                else:
                                    result.append(PlusOneIfPossible(length,i-1,path)) 
                            else:
                                result.append(PlusOneIfPossible(length,i-1,path)) 
                        else:
                            result.append(PlusOneIfPossible(length,i-1,path)) 
                    else:
                        result.append(PlusOneIfPossible(length,i-1,path))
                else:
                    result.append(PlusOneIfPossible(length,i-1,path))
            else:
                result.append(PlusOneIfPossible(length,i,path))
        else:
            result.append(path[i].name())
    return result

def preprocess(text,fileno):
    sentences = re.findall(r"\w+(?:[-']\w+)*|'|[-.(]+|\S\w*", text.lower())
    totalWords.append(len(sentences))
    print totalWords
    sentences = [sent for sent in sentences if re.compile("^\w+").match(sent) and re.compile("^[^0-9]").match(sent)]
    sentences = [sent for sent in sentences if sent not in stop and len(sent)>2]
    words = Counter(sentences).keys() # equals to list(set(words))
    frequency = Counter(sentences).values() # counts the elements' frequency
    uniqueSet = {}
    for i in range(0,len(words)):
        uniqueSet[words[i]] = frequency[i]
    result = []
    for sent in uniqueSet:
        try:
            answer = most_frequent_sense(str(sent))
            transformed = transform(answer.name())[0]
            result.append((sent,transformed))
            features[str(transformed)] = [item+uniqueSet[sent] if x==fileno else item for x,item in enumerate(features[str(transformed)])]
        except:
            pass
    return result
# ------------------------------------------------------------------------------------

# ---------------------------- Parse data and save to .csv file -----------------------
for itr,file in enumerate(text_files[:n]):

  statinfo = os.stat(path+str(file))

  if statinfo.st_size > 100:

    startIndex = 0
    endIndex = sum(1 for line in open(path + str(file)))
    count = 0

    print "#", str(file), startIndex, endIndex

    text = open(path + str(file), 'r')

    for line in text:
      line = line.decode('utf-8')
      if startString in line.lower():
        startIndex = count + 1

      if endString in line.lower():
        endIndex = count - 1
      count += 1
    print "*", startIndex, endIndex
    
    text.seek(startIndex)

    count = startIndex
	cleanedText = ""
	for line in text:
		if count <= endIndex:
			cleanedText += line
		count += 1

    # print text.read().decode('utf-8')
    preprocess(cleanedText.read().decode('utf-8'),itr)
# -----------------------------------------------------------------------------------------

wordnet.append('totalWords')
features['totalWords'] = totalWords
result = DataFrame(features,columns=wordnet)
result.to_csv( str(sys.argv[1]) + '.csv')

print time() - startTime
