# -*- coding: utf-8 -*-
"""
Projet: Le Temps

Suisse Hackaton Berne 2015
"""
__author__ = """Giovanni Colavizza"""
from flask import Flask, jsonify, request, abort,  render_template

import os, codecs, string, pickle
from collections import OrderedDict
from gensim import corpora, models, similarities
from nltk.corpus import stopwords
from bs4 import BeautifulSoup

class Corpus :
    def initalize(self):
        # load required data structures
        self.revind = pickle.load(open("../data/revind_gensim.p", "rb")) #reverse index for article ids
        self.dictionary = corpora.Dictionary.load('../data/letemps.dict') #dictionary
        self.corpus = corpora.MmCorpus('../data/letemps.mm') #corpus of articles
        self.tfidf = models.TfidfModel.load('../data/model.tfidf') #tfidf model
        self.lsi = models.LsiModel.load('../data/model.lsi') #lsi model
        self.index_tfidf = similarities.MatrixSimilarity.load('../data/tfidf.index') #tfidf index
        self.index_lsi = similarities.MatrixSimilarity.load('../data/lsi.index') #lsi index

    def preprocess(self, doc):
        """
        :param doc: a string of text
        :return: a list of filtered tokens
        """
        # remove punctuation
        for p in string.punctuation:
            doc = doc.replace(p, "")
        # remove common words and tokenize
        doc = [word for word in doc.lower().split() if word not in set(stopwords.words('french'))]
        # remove numbers and short words
        tokens_to_remove = set(word for word in set(doc) if word.isdigit() or len(word) < 4)
        doc = [word for word in doc if word not in tokens_to_remove]

        return doc

    def search_sorted_tfidf(self, doc, n=20):
        """
        Takes a list of tokens and returns a sorted list of tuples of article ids with scores, according to tfidf similarity
        :param doc: list of tokens to search for
        :param n: number of results to return
        :return: sorted list of tuples with article id and matching score
        """
        vec_bow = self.dictionary.doc2bow(doc)
        vec_tfidf = self.tfidf[vec_bow]
        sims_tfidf = self.index_tfidf[vec_tfidf]
        results = sorted(enumerate(sims_tfidf), key=lambda item: -item[1])[:n]

        return [(self.revind[x[0]], x[1]) for x in results]

    def search_tfidf(self, doc):
        """
        Takes a list of tokens and returns a list of tuples of article ids with scores, according to tfidf similarity
        :param doc: list of tokens to search for
        :return: list of tuples with article id and matching score
        """
        vec_bow = dictionary.doc2bow(doc)
        vec_tfidf = tfidf[vec_bow]

        return [(revind[x[0]], x[1]) for x in index_tfidf[vec_tfidf]]

    def search_sorted_lsi(self, doc, n=20):
        """
        Takes a list of tokens and returns a sorted list of tuples of article ids with scores, according to lsi similarity
        :param doc: list of tokens to search for
        :param n: number of results to return
        :return: sorted list of tuples with article id and matching score
        """
        vec_bow = dictionary.doc2bow(doc)
        vec_lsi = lsi[vec_bow]
        sims_lsi = index_lsi[vec_lsi]
        results = sorted(enumerate(sims_lsi), key=lambda item: -item[1])[:n]

        return [(revind[x[0]], x[1]) for x in results]

    def search_lsi(self, doc):
        """
        Takes a list of tokens and returns a list of tuples of article ids with scores, according to lsi similarity
        :param doc: list of tokens to search for
        :return: list of tuples with article id and matching score
        """
        vec_bow = dictionary.doc2bow(doc)
        vec_lsi = lsi[vec_bow]

        return [(revind[x[0]], x[1]) for x in index_lsi[vec_lsi]]

    def article_crawler(self, base_dir="CHANGE TO LOCAL SYSTEM OR MAKE RELATIVE TO WORKING DIR/Le Temps/Hackaton/data", dirs_r=["GDL/raw/1914", "JDG/raw/1914"], first_month=7, last_month=9):
        """
        Crawls a Le Temps directory and returns articles with full text
        :param base_dir: path to Le Temps data
        :param dirs_r: what journals and years to parse. This is a list of subdirectories
        :param first_month: first month to consider, e.g. January = 1
        :param last_month: last month to consider
        :return: dictionary of articles with id on key and full text as value
        """
        articles = OrderedDict()

        for directory in dirs_r:
            processDir = os.path.join(base_dir, directory)
            if not os.path.exists(processDir):
                continue
            print("processing directory: "+processDir)
            months = sorted(next(os.walk(processDir))[1])
            for month_dir in months[first_month-1:last_month]:
                days = sorted(next(os.walk(os.path.join(processDir, month_dir)))[1])
                for day_dir in days:
                    newspaper = directory.split("/")[0]
                    year = directory.split("/")[2]
                    type_of_data = directory.split("/")[1]
                    month = month_dir
                    day = day_dir
                    root = os.path.join(processDir, os.path.join(month_dir, day_dir))
                    files = sorted(next(os.walk(root))[2])

                    for file_name in files:
                        if ".xml" in file_name:
                            identifier = newspaper+"-"+year+"-"+month+"-"+day+"-"+file_name
                            print("processing article: "+identifier)
                            f = codecs.open(os.path.join(root, file_name), encoding = 'utf-8')
                            original = f.read()
                            f.close()
                            soup = BeautifulSoup(original)

                            text = ""
                            for entity in soup.find_all("entity"):
                                text += entity.full_text.string

                            articles[identifier] = text

        return articles

class Article:
    articles = [
        {
            'uri': u'my-first-result',
            'title': u'My first result',
            'description': u'This is my first result', 
        },
        {
            'uri': u'my-second-result',
            'title': u'My second result',
            'description': u'This is my second result', 
        }
    ]

    def get(self, article_id):
        result = {}
        filename = article_id.replace('-NER', '')
        filename = filename.replace('GDL-', 'GDL-raw-')
        filename = filename.replace('JDG-', 'JDG-raw-')
        filename="../data/data/"+"/".join(filename.split('-'))
        content = open(filename).read()
        soup = BeautifulSoup(content)
        entity = soup.find_all("entity")[0]
        print(entity)
        result = {"filename" : filename, "id" : article_id, "newspaper" : entity.meta.publication.string, "title" : entity.meta.find("name").string, "date" : entity.meta.issue_date.string.replace("/", "."), "content" : entity.full_text.string.replace(". ", ".\n")}
        
        # article = [article for article in self.articles if article['title'] == title]
        # result = article[0] if len(article) > 0 else None
        return result

    def get_search_result(self, search):
        search_type = "text" # TODO: set it to the radio button value
        search_limit = 15 # TODO: set it to the radio button value
        corpus = Corpus()
        corpus.initalize() # TODO: do it when loading the application
        print(search)
        doc = corpus.preprocess(search)
        print(doc)
        if search_type == "text" :
            result = []
            for item in corpus.search_sorted_tfidf(doc, search_limit) :
                filename = item[0].replace('-NER', '')
                filename = filename.replace('GDL-', 'GDL-raw-')
                filename = filename.replace('JDG-', 'JDG-raw-')
                # list.insert(index,object)
                filename="../data/data/"+"/".join(filename.split('-'))
                # print(filename)
                content = open(filename).read()
                soup = BeautifulSoup(content)
                entity = soup.find_all("entity")[0]
                result.append({"filename" : filename, "id" : item[0], "newspaper" : entity.meta.publication.string, "title" : entity.meta.find("name").string, "date" : entity.meta.issue_date.string.replace("/", "."), "score" : item[1]})
                # print(result)
        else :
            return

        #result = [article for article in self.articles if (search in article['title'] or search in article['description'])]
        return result


app = Flask(__name__)

@app.route('/api/v0.1/search/<search>', methods=['GET'])
def api_list(search):
    article = Article()
    articles = article.get_search_result(search)
    return jsonify({'articles': articles})

@app.route('/api/v0.1/article/<title>', methods=['GET'])
def api_get_article(title):
    # TODO: use uri instead of title?
    article = Article()
    item = article.get(title)
    if item == None:
        abort(404)
    return jsonify({'article': item})


@app.route('/article/<article_id>')
def article(article_id):
    article = Article()
    result = article.get(article_id)
    return render_template('search.html', result=result, list=False)

@app.route('/search/<search>')
def search(search):
    article = Article()
    result = article.get_search_result(search)
    return render_template('search.html', result=result, search=search)

@app.route('/search', methods=['POST'])
def search_bla():
    search = request.form.get('search')
    article = Article()
    result = article.get_search_result(search)
    return render_template('search.html', result=result, list=True)

@app.route('/')
def index():
    return render_template('search.html')

if __name__ == '__main__':
    app.debug = True
    app.run()
