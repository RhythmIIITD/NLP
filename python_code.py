import sys
import nltk
import re
from collections import defaultdict
#import spacy
#from spacy import *
#nlp=spacy.load('en')
from nltk import word_tokenize, pos_tag, ne_chunk
from nltk.corpus import stopwords
import xml.dom.minidom as minidom
lines = sys.stdin.readlines()
if lines[0].strip() == '1':
    content = open('xmlFiles/xmlFromWiki.xml','r').read() 
    doc = minidom.parse('xmlFiles/xmlFromWiki.xml')   
else:
    content = open('xmlFiles/xmlFromFile.xml','r').read()    
    doc = minidom.parse('xmlFiles/xmlFromFile.xml')
#################################################COPYING THE CODE HERE###########################################


itemlist = doc.getElementsByTagName('text')
AnsQues=defaultdict(list)

#finds segments in a string, identifying using comma
def findsegments(string):
    segments=[]
    for seg in string.split(', '):
        segments.append(seg)
    return segments

#use it for finding any chunk by giving the grammar and input string
def findChunk(string,grammar,grtag):
    text=nltk.word_tokenize(string)
    sentence=nltk.pos_tag(text)
    cp = nltk.RegexpParser(grammar)
    result = cp.parse(sentence)
    tree = cp.parse(sentence)
    c=0
    for subtree in tree.subtrees():
        if subtree.label() == grtag: 
            c=1
            #print("findchunksubtree",subtree)
            return 1,subtree
    if(c==0):
        return 0,""

def findChunkwithPOSTags(sentence,grammar,grtag):
    cp = nltk.RegexpParser(grammar)
    tree = cp.parse(sentence)
    c=0
    for subtree in tree.subtrees():
        if subtree.label() == grtag:
#             print("subtree",subtree)
            c=1
            return 1,subtree
    if(c==0):
        return 0,""
    
# identify if a segment is a clause or not.
def clauseOrNot(string):
#     print("clauseOrNot")
    grammar = "chunk:{<DT>?<JJ.?>*<NN.?|PRP|PRP$|POS|IN|DT|CC|VBG|VBN>+<RB.?|VB.?|MD|RP>+}"
    res,resstring=findChunk(string,grammar,"chunk")
    return res,resstring

def verbphrase(cstr):
    X=""
    Y=""
#     for subtree in cstr.subtrees():
    grammar = "verb:{<VBG|VBN|VB.?|MD|RP>+}"
    res,sentence=findChunkwithPOSTags(cstr,grammar,"verb")
    #print("res",res,"sentence",sentence)
    if(len(sentence)>0):
        for subtree in sentence.subtrees():
            if subtree.label() == 'verb': 
                #print("subtree",subtree,len(subtree))
                verbLen=len(subtree)
                #print("verbLen",verbLen)
                if(verbLen==1):
    #                 print(subtree[0][1])
                    if(subtree[0][1]=="VBD"):
                        X="did"
                        Y=subtree[0][0]
                    elif(subtree[0][1]=="VBP" or subtree[0][1]=="VB"):
                        X="do"
                        Y=subtree[0][0]
                    elif(subtree[0][1]=="VBZ"):
                        X="does"
                elif(verbLen==2):
                    if(subtree[0][0]=="am"):
                        X="is"
                        Y=subtree[1][0]
                    else:
                        X=subtree[0][0]
                        Y=subtree[1][0]
                else:
                    X=subtree[0][0]
                    for i in range(1,verbLen):
                        Y+=subtree[i][0]+" "
        #print("X",X,"Y",Y)
        return X,Y
    else:
        return 0,0

def nounphrase(tree):
    stopwords=[]
    querywords=[]
    grammar = "verb:{<VBG|VBN|VB.?|MD|RP>+}"
    res,verbtree=findChunkwithPOSTags(cstr,grammar,"verb")
#     print("res",res,"sentence",verbtree)
    #print(len(verbtree))
    if(len(verbtree)>0):
        for subtree in verbtree.subtrees():
            for words in subtree:
                stopwords.append(words[0]) 
        for subtree in tree.subtrees():
                for words in subtree:
                    querywords.append(words[0])
    #             print("querywords",querywords)
        resultwords  = [word for word in querywords if word not in stopwords]
        resultwords = ' '.join(str(e) for e in resultwords)
        #print("rs",str(resultwords))
        return 1,resultwords
    else:
        return 0,""

    
def ques1(entiresentence,string):
    stopwords=[]
    querywords = string.split()
#     print("querywords",querywords)
#     print("ques1")
    grammar = "chunk:{<DT>?<JJ.?>*<NN.?|PRP|PRP$|POS|IN|DT|CC|VBG|VBN>+<RB.?|VB.?|MD|RP>+}"
    res,sentence=findChunk(string,grammar,"chunk")
    #print("res",res,"sentence",sentence)
    if(res!=0):
        #find part to be replaced with who
        grammar = "Who:{<DT>?<JJ.?>*<NN.?|PRP|PRP$|POS|IN|DT|CC>+}"
        cp = nltk.RegexpParser(grammar)
        result = cp.parse(sentence)
        tree = cp.parse(sentence)
        #print("WHO",tree)
        if(len(tree)>0):
            for subtree in tree.subtrees():
                if subtree.label() == 'Who': 
                    for words in subtree:
                        stopwords.append(words[0])
            #print("stopwords",stopwords)
            resultwords  = [word for word in querywords if word not in stopwords]
            resultwords = ' '.join(str(e) for e in resultwords)
    #             print("resultwords",resultwords)
            whoQues ="Who "+str(resultwords)+"?"
    #             print (whoQues)
            AnsQues[entiresentence].append(whoQues)

def ques2(entiresentence,string,np,x,y):
    stopwords=[]
    querywords = string.split()
    #print("querywords",querywords)
    grammar = "chunk:{<TO>+<DT>?<RB.?>*<JJ.?>*<NN.?|PRP|PRP$|VBG|DT|POS|CD|VBN>}"
    res,sentence=findChunk(string,grammar,"chunk")
    #print("res",res,"sentence",sentence)
#     for subtree in sentence.subtrees():
#         if subtree.label() == 'chunk':
#             print(subtree)
    if(len(sentence)>0):
        for words in sentence:
            stopwords.append(words[0])
        #print("sp",stopwords)
        stopwords.append(np)
        stopwords.append(x)
        stopwords.append(y)
        stopwords=set(stopwords)
        #print(stopwords)
        
        resultwords  = [word for word in querywords if word not in stopwords]
        resultwords = ' '.join(str(e) for e in resultwords)
        #print(resultwords)
        toWhatQues="To what "+x+" "+np+" "+y+resultwords+"?"
        #print(toWhatQues)
def ques2_2(entiresentence,string,np,x,y):
    np=""
    stopwords=[]
    querywords = string.split()
    grammar =  "chunk:{<IN>+<DT>?<RB.?>*<JJ.?>*<NN.?|PRP|PRP$|POS|VBG|DT|CD|VBN>+}"
    res,sentence=findChunk(string,grammar,"chunk")
    if(res!=0):
        for words in sentence:
            stopwords.append(words[0])
        #print("sp",stopwords)
        stopwords.append(np)
        stopwords.append(x)
    #     stopwords.append(y)
        #print(stopwords)
        ########FIND THE PREPOSTION
        preposition=""
        for words in sentence:
                #print("words in sentence",words)
                if(words[1]=='IN'):
                        #print("prep found",words[0])
                        preposition=words[0]
                        #print("preposition is",preposition)
                        #print("///////////////////////////////////")
        resultwords  = [word for word in querywords if word not in stopwords]
        resultwords = ' '.join(str(e) for e in resultwords)
        #print(resultwords)
        prepques=preposition+" what "+x+np+" "+resultwords+"?"
        #print(prepques)
        AnsQues[entiresentence].append(prepques)
    
def ques23(entiresentence,string,np,x,y):
    stopwords=[]
    querywords = string.split()
    #print("querywords",querywords)
    grammar = "chunk:{<VB.?|MD|RP|RB.?>+<DT>?<RB.?>*<JJ.?>*<NN.?|PRP|PRP$|POS|VBG|DT|CD|VBN>+}"
    res,sentence=findChunk(string,grammar,"chunk")
    #print("res",res,"sentence",sentence)
#     for subtree in sentence.subtrees():
#         if subtree.label() == 'chunk':
#             print(subtree)
#     for pr in np:
#         if()
    if(len(sentence)>0):
        for words in sentence:
            stopwords.append(words[0])
        #print("sp",stopwords)
        stopwords.append(np)
        stopwords.append(x)
        stopwords.append(y)
        stopwords=set(stopwords)
        #print(stopwords)
        resultwords  = [word for word in querywords if word not in stopwords]
        resultwords = ' '.join(str(e) for e in resultwords)
        #print("rs",resultwords)
        WhatQues="What "+x+" "+np+" "+y+" "+resultwords+"?"
        #print(WhatQues)
        AnsQues[entiresentence].append(WhatQues)
''' 
def ques5(entiresentence,string,np,x,y):
    stopwords=[]
    querywords=[]
    querywords = string.split()
    #print("querywords",querywords)
    #print("ques5")
    #print("x",x,"y",y)
    #print("np",np)
    grammar = "when:{<DT>?<JJ.?>?<RB>?<IN|TO|RP>+<DT>*<NN.?>+}"
    res,sentence=findChunk(string,grammar,"when")
    #print("res",res,"sentence",sentence)
    if(len(sentence)>0):
        for words in sentence:
            stopwords.append(words[0])
        #print("sp",stopwords)
        stopwords.append(np)
        stopwords.append(x)
        stopwords.append(y)
        stopwords=set(stopwords)
        #print(stopwords)
        resultwords  = [word for word in querywords if word not in stopwords]
        resultwords = ' '.join(str(e) for e in resultwords)
        #print("rs",resultwords)
    if(res==1):
        grammar = "NN:{<NN|NN.?>+}"
        resNN,NN=findChunk(string,grammar,"NN")
        #print("resNN",resNN,"NN",NN)
        whentags=""
        for words in NN:
            #print(words[0])
            whentags=words[0]
            
        res = nlp(string)
        NERTags={}
        for j in res.ents:
            NERTags.update({str(j):j.label_})
        #print(NERTags)
        
        if(NERTags.get(whentags)=='DATE' or NERTags.get(whentags)=='TIME'):
            whenQues="When "+x+" "+np+" "+y+" "+resultwords+"?"
            #print(whenQues)
            AnsQues[entiresentence].append(whenQues)
'''
def ques63(entiresentence,string,np,x,y):
    nounphrase = []
    verbphrase = []
    text=nltk.word_tokenize(string)
    sentence=nltk.pos_tag(text)
    
    grammar = "chunk:{<MD>?<VB|VBD|VBG|VBP|VBN|VBZ>+<IN>?<NN|NNS|NNP|NNPS|PRP|PRP$>?<$>*<CD>+}"
    cp = nltk.RegexpParser(grammar)
#     result = cp.parse(sentence)
#     print("result1",result)
    tree = cp.parse(sentence)
#     print("tree1",tree)
    if(len(tree)>0):
        grammar = "chunk:{<DT>?<JJ.?>*<NN.?|PRP|PRP$|POS|IN|DT|CC|VBG|VBN>+<RB.?|VB.?|MD|RP>+}"
        cp = nltk.RegexpParser(grammar)
        rule1 = cp.parse(sentence)
    #     rule1.draw()
    #     print("checked by rule1",rule1)
        tree = cp.parse(sentence)
    #     print("tree2",tree)
    #     tree.draw()
        question_generated = ' '
        c=0
        for subtree in tree.subtrees():
            if subtree.label() == 'chunk': 
                c=1
                for t in subtree:
                    if t[1] == 'VB' or t[1] == "VBG" or t[1] == "VBN":
                        verbphrase.append(t[0])
    #                     print("verbphrase",verbphrase)
                        break

                    if t[1] == 'NP' or t[1] == 'NNP' or t[1] == 'NNPS' or t[1] == 'NN':
                        nounphrase.append(t[0])
        if(len(nounphrase)>0 and len(verbphrase)>0):
            question_generated = 'How much ' + " ".join(str(n) for n in nounphrase)+" " +  " ".join(str(v) for v in set(verbphrase)) + "?" 
            #print(question_generated)
            AnsQues[entiresentence].append(question_generated)

def quesHMany(entiresentence,string):
    verbphrase=[]
    nounphrase=[]
    currency=[]
    text=nltk.word_tokenize(string)
    sentence=nltk.pos_tag(text)
    grammar = "chunk:{<DT>?<CD>+<RB>?<JJ|JJR|JJS>?<NN|NNS|NNP|NNPS|VBG>+}"
    cp = nltk.RegexpParser(grammar)
    result = cp.parse(sentence)
#     print("result1",result)
    if(len(result)>0):
        for subtree in result.subtrees():
            if subtree.label() == 'chunk':
                for t in subtree:
                    if t[1] != 'CD':
                        currency.append(t[0])
        grammar = "chunk:{<DT>?<JJ.?>*<NN.?|PRP|PRP$|POS|IN|DT|CC|VBG|VBN>+<RB.?|VB.?|MD|RP>+}"
        cp = nltk.RegexpParser(grammar)
        rule1 = cp.parse(sentence)
    #     rule1.draw()
    #     print("checked by rule1",rule1)
        tree = cp.parse(sentence)
    #     print("tree2",tree)
    #     tree.draw()
        question_generated = ' '
        c=0
        for subtree in tree.subtrees():
            if subtree.label() == 'chunk': 
                c=1
                for t in subtree:
                    if t[1] == 'VB' or t[1] == "VBG" or t[1] == "VBN":
                        verbphrase.append(t[0])
                        #print("verbphrase",verbphrase)
                        break

                    if t[1] == 'NP' or t[1] == 'NNP' or t[1] == 'NNPS' or t[1] == 'NN' or t[1]:
                        nounphrase.append(t[0])
                        #print("nounphrase",nounphrase)
        if(len(nounphrase)>0 and len(verbphrase)>0):
            question_generated = 'How many ' +" ".join(str(c) for c in currency)+ " " +" ".join(str(n) for n in nounphrase)+" " +  " ".join(str(v) for v in set(verbphrase)) + "?" 
        #     print(question_generated)
            AnsQues[entiresentence].append(question_generated)
def queswhere(entiresentence,string):
    text=nltk.word_tokenize(string)
    sentence=nltk.pos_tag(text)
    grammar = "chunk:{<DT>?<JJ.?>?<RB>?<IN|TO|RP>+<DT>*<NN.?|PP|PRP|PRP$ >+<VBG|POS|CD|RB|DT>*}"
    cp = nltk.RegexpParser(grammar)
#     print("cp",cp)
    stopwords = []
    preprocessed_Sentence = cp.parse(sentence)
#     preprocessed_Sentence.draw()
#     print("Preproccessed Sentence",preprocessed_Sentence)
    Question = "Where:{<DT>?<JJ.?>?<RB>?<IN|TO|RP>+<DT>*<NN.?|PP|PRP|PRP$ >+<VBG|POS|CD|RB|DT>*}"
    after_where = nltk.RegexpParser(Question)
    sentence_generated = after_where.parse(sentence)
    #print("Sentence Generated",sentence_generated)
    segments = []
    segments = string.split()
    for subtree in sentence_generated.subtrees():
        if subtree.label() == 'Where':
            #print("Where Found!")
            for s in subtree:
                #print("words",s[0])
                stopwords.append(s[0])
                #print("stopwords",stopwords)
                resultwords  = [word for word in segments if word not in stopwords]
                resultwords = ' '.join(str(e) for e in resultwords)
                #print("resultwords",resultwords)
                whereQues ="Where "+str(resultwords)+"?"
                #print (whereQues)
                AnsQues[entiresentence].append(whereQues)
    
#read the dataset and process it
output = open('xmlFiles/questionsGenerated.txt','w')
#output=open("QuestionGenerated.txt","w")
j=0
for i in itemlist:
    j=j+1
    entiresentence=''.join( [node.data for node in i.childNodes])
    result = entiresentence[0].lower() + entiresentence[1:]
    result = result.replace(".","")
    segments=findsegments(result)
#     print(segments)
    AnsQues[entiresentence]=[]
    #print(AnsQues)
    for i in segments:
        c,cstr=clauseOrNot(i)
        if(c==1):
#             print(cstr)
            x,y=verbphrase(cstr)
            if(x!=0):
                npc,np=nounphrase(cstr)
    #             print("np",np)
                if(npc==1):
                    ques1(entiresentence,i)
                    ques2(entiresentence,i,np,x,y)
                    ques2_2(entiresentence,i,np,x,y)
                    ques23(entiresentence,i,np,x,y)
                    #ques5(entiresentence,i,np,x,y)
                    ques63(entiresentence,i,np,x,y)
                    quesHMany(entiresentence,i)
                    queswhere(entiresentence,i)
#print(AnsQues)
i=1
#output.write('Please write questions generated in this file')

for key,value in AnsQues.items():
    output.write(str(i)+". ")
    output.write(key)
    output.write("\n")
    for v in value:
        output.write(v+"\n")
    i=i+1
output.close()


# =====================================================================
# =====================================================================
# Algorithm code goes STARTS here
#questionsGenerated = open('xmlFiles/questionsGenerated.txt','w')
#questionsGenerated.write('Please write questions generated in this file')
# Algorithm code goes ENDS here
# =====================================================================
# =====================================================================


print 'Return to Node Code'
