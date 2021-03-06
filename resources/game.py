import uuid
import string

from flask import (
    jsonify,
    Blueprint,
    abort,
    make_response,
    redirect,
    url_for
)
from flask_restful import (
    Resource, Api, reqparse
)
from hangman import loadWords, chooseWord
from models import Game, LetterGuessed
from peewee import DataError


def valid_letter(value):
    user_input = value.lower().strip()
    if not user_input:
        raise ValueError("You didn't provide a letter")
    elif len(user_input) > 1:
        raise ValueError('You provided more than 1 letter')
    elif user_input not in string.ascii_lowercase:
        raise ValueError("You didn't provide a letter from %s" %
                         string.ascii_lowercase)
    return user_input


MAX_ATTEMPTS = 8


class Word(Resource):
    '''
    Used once per game when the game is initialized.
    '''

    def post(self):
        '''
        Generates random word, game UUID and creates a DB entry for a new game.
        '''
        word = chooseWord(loadWords())
        game_uuid = uuid.uuid4()
        Game.create(
            game_uuid=game_uuid,
            word=word,
            word_length=len(word)
        )

        output = jsonify(
            word_length=len(word),
            representation='_' * len(word),
            attempts_left=MAX_ATTEMPTS,
            available_letters=string.ascii_lowercase
        )

        resp = make_response(output)
        # Cookie expires in 24 hours
        resp.set_cookie('hangman_game_id', str(game_uuid), 86400)
        return resp


class Letter(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser(bundle_errors=True)
        self.reqparse.add_argument(
            'letter',
            required=False,
            type=valid_letter,
            help='Letter not provided',
            location=['form', 'json']
        )

        self.reqparse.add_argument(
            'hangman_game_id',
            required=True,
            help='No game_identifier provided',
            location=['cookies']
        )
        super().__init__()

    def get_representation(self, letters_guessed, word):
        return ''.join(map(
            lambda l: l if l in letters_guessed else '_',
            word
        ))

    def get_available_letters(self, letters_guessed, letter_guessed=None):
        if letter_guessed:
            letters_guessed.add(letter_guessed)

        return ''.join(map(
            lambda l: l if l not in letters_guessed else '',
            string.ascii_lowercase
        )
        )

    def get(self):
        args = self.reqparse.parse_args()
        # Get game object using uuid from the cookie
        try:
            game = Game.get(Game.game_uuid == args['hangman_game_id'])
        except (Game.DoesNotExist, DataError):
            resp = make_response(redirect(url_for('index')))
            resp.set_cookie('hangman_game_id', '', expires=0)
            return resp

        word = game.word
        letters = list(
            game.letters.select().order_by(
                LetterGuessed.create_time.desc()
            )
        )
        if not letters:
            return jsonify(
                word_length=len(word),
                representation=''.join('_' for _ in word),
                attempts_left=MAX_ATTEMPTS,
                available_letters=string.ascii_lowercase
            )
        else:
            letters_guessed = {l.letter for l in letters}
            last_letter = letters[0]

            representation = self.get_representation(letters_guessed, word)
            available_letters = self.get_available_letters(letters_guessed)

            return jsonify(
                word_length=len(word),
                representation=representation,
                attempts_left=last_letter.attempts_left,
                available_letters=available_letters
            )

    def post(self):
        args = self.reqparse.parse_args()
        # Get game object using uuid from the cookie
        try:
            game = Game.get(Game.game_uuid == args['hangman_game_id'])
        except (Game.DoesNotExist, DataError):
            resp = make_response(redirect(url_for('index')))
            resp.set_cookie('hangman_game_id', '', expires=0)
            return resp

        word = game.word
        letter_guessed = args['letter'].lower()

        def update_game_result(representation):
            if representation == word:
                game.result = 'won'

            elif attempts_left == 0:
                game.result = 'lost'

            game.save()

            return game.result

        def create_letter(message):
            return LetterGuessed.create(
                game=game.id,
                letter=letter_guessed,
                attempts_left=attempts_left,
                message=message
            )

        letters = list(
            game.letters.select().order_by(
                LetterGuessed.create_time.desc()
            )
        )
        letters_guessed = {l.letter for l in letters}

        try:
            last_letter = letters[0]
        except IndexError:
            attempts_left = MAX_ATTEMPTS
        else:
            attempts_left = last_letter.attempts_left

        if game.result in ('won', 'lost'):
            return abort(
                400, '{"message": "this game is already over"}'
            )

        elif letter_guessed in letters_guessed:
            message = 'already_guessed'

        elif letter_guessed in word:
            letters_guessed.add(letter_guessed)
            message = 'correct_guess'

        else:
            attempts_left = attempts_left - 1
            message = 'incorrect_guess'

        representation = self.get_representation(letters_guessed, word)
        result = update_game_result(representation)

        letter = create_letter(message)
        letter.available_letters = self.get_available_letters(
            letters_guessed, letter_guessed)
        letter.representation = representation
        letter.word_length = len(word)

        # send back the original word if game is over
        result = game.result
        if result in ('won', 'lost'):
            original_word = game.word
        else:
            original_word = None

        return jsonify(
            word_length=len(word),
            letter=letter.letter,
            representation=representation,
            available_letters=letter.available_letters,
            attempts_left=attempts_left,
            result=result,
            message=message,
            original_word=original_word
        )


game_api = Blueprint('resources.game', __name__)
api = Api(game_api)
api.add_resource(
    Word,
    '/api/v1/word'
)

api.add_resource(
    Letter,
    '/api/v1/letter'
)
