from flask import Flask, render_template, make_response, request, Response
import base64
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

@app.route('/fb.gif')
def fb():
    campaign = request.args.get('utm_campaign')
    content = request.args.get('utm_content')
    term = request.args.get('utm_term')

    GIF = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=')


    if request.cookies.get('viewtrack'):
        user_id = request.cookies.get('viewtrack')
        
        print([user_id, campaign, content, term, "exists"])
        
        return Response(GIF, mimetype="image/gif")

    else:
        # Generate user id for the cookie
        user_id = uuid.uuid4()
        
        print([str(user_id), campaign, content, term, "new"])

        res = Response(GIF, mimetype="image/gif")
        res.set_cookie('viewtrack', str(user_id), max_age=60 * 60 * 24 * 365 * 2)
        return res

@app.errorhandler(404)
def page_not_found(e):
    return 'Page not found'
