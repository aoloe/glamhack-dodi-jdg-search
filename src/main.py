# http://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask
from flask import Flask, jsonify, request, abort,  render_template

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

    def get(self, title):
        article = [article for article in self.articles if article['title'] == title]
        result = article[0] if len(article) > 0 else None
        return result

    def get_list(self, search):
        result = [article for article in self.articles if (search in article['title'] or search in article['description'])]
        return result


app = Flask(__name__)

@app.route('/api/v0.1/search/<search>', methods=['GET'])
def api_list(search):
    article = Article()
    articles = article.get_list(search)
    return jsonify({'articles': articles})

@app.route('/api/v0.1/article/<title>', methods=['GET'])
def api_get_article(title):
    # TODO: use uri instead of title?
    article = Article()
    item = article.get(title)
    if item == None:
        abort(404)
    return jsonify({'article': item})


@app.route('/article/<title>')
def article(search):
    return 'Searching for %s' % title

@app.route('/search/<search>')
def search(search):
    return 'Index page! (searched for %s)' % search

@app.route('/search', methods=['POST'])
def search_bla():
    search = request.form.get('search')
    article = Article()
    result = article.get_list(search)
    return render_template('search.html', result=result, search=search)

@app.route('/')
def index():
    return render_template('search.html')

if __name__ == '__main__':
    app.debug = True
    app.run()
