from flask import Flask
app = Flask(__name__)

@app.route('/search/<search>')
def search(search):
    return 'Searching for %s' % search

@app.route('/list')
def list():
    return 'List page'

@app.route('/')
def index():
    return 'Index page!'

if __name__ == '__main__':
    app.debug = True
    app.run()
