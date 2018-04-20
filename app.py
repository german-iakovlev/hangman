from flask import Flask, render_template, make_response, request
import base64
import sys
import logging
import uuid

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
    campaign = request.args.get('utm_campaign')
    content = request.args.get('utm_content')

    app.logger.info('utm_campaign_log', campaign)
    app.logger.info('utm_content_log', content)

    
    if request.cookies.get('foo'):
        return "You have a cookie"
    else:
        gif = 'R0lGODlhAQABAIAAAP///////yH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=='
        res = make_response(base64.b64decode(gif))

        res.set_cookie('foo', str(uuid.uuid4()), max_age=60 * 60 * 24 * 365 * 2)
        return res

@app.errorhandler(404)
def page_not_found(e):
    return 'Page not found'
