from flask import Flask, render_template, make_response, request
import io
import base64

from resources.game import game_api

app = Flask(__name__, static_url_path='/static')
app.register_blueprint(game_api)


@app.route('/hangman')
def hangman():
    return render_template('hangman.html')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fb')
def fb():
    
    if request.cookies.get('cookie_fb'):
        return "You have a cookie"
    else:
        gif = 'R0lGODlhAQABAIAAAP///////yH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=='
        res = make_response(base64.b64decode(gif))
        res.set_cookie('cookie_fb', '12345', max_age=60 * 60 * 24 * 365 * 2)
        return res
    
    
@app.route('/game_over')
def game_over():
    return render_template('game_over.html')


@app.errorhandler(404)
def page_not_found(e):
    return 'Page not found'


if __name__ == '__main__':
    app.debug = True
