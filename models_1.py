import urllib.parse as urlparse
import os
import psycopg2
from peewee import *
from hangman import loadWords, chooseWord
import time
from datetime import datetime


# URL = urlparse.urlparse(os.environ['DATABASE_URL'])
# DBNAME = URL.path[1:]
# USER = URL.username
# PASSWORD = URL.password
# HOST = URL.hostname
# PORT = URL.port

db = PostgresqlDatabase(
    'local_db',
    user='germaniakovlev',
    password='',
    host='localhost',
    autorollback=True
)


class Result(Model):
    '''
    Creates Result table
    '''
    word = CharField(max_length=256)
    attempts = IntegerField()
    result = BooleanField()

    class Meta:
        database = db


class user(Model):
    nickname = CharField(max_length=256, unique=True)

    class Meta:
        database = db

    @classmethod
    def create_user(cls, nickname):
        try:
            cls.create(nickname=nickname)
        except IntegrityError:
            raise ValueError('User already exists')


class word_created(Model):
    word = CharField(max_length=256)
    language = CharField(max_length=10)
    #create_time = DateTimeField(default=datetime.datetime.now)
    user = ForeignKeyField(user)

    class Meta:
        database = db


class Letter(Model):
    '''
    Contains letters submitted by user during the game
    '''
    letter = CharField(max_length=1, unique=True)

    class Meta:
        database = db


class Game(Model):
    '''
    '''
    game_uuid = UUIDField(unique=True)
    word = CharField(max_length=256)
    word_length = IntegerField()
    result = CharField(max_length=16, default='in_progress')
    create_time = DateTimeField(default=datetime.utcnow)
    update_time = DateTimeField(default=datetime.utcnow)
    

    class Meta:
        database = db
    
    def save(self, *args, **kwargs):
        self.update_time = datetime.utcnow()
        return super(Game, self).save(*args, **kwargs)

    # @classmethod
    # def create_game(cls, game_uuid, word, word_length):
    #     '''
    #     '''
    #     cls.create(game_uuid=game_uuid,
    #                word=word, word_length=word_length)


class LetterGuessed(Model):
    '''
    '''
    game = ForeignKeyField(Game, related_name='letters')
    letter = CharField(max_length=1)
    #representation = CharField(max_length=500)
    #letters_guessed = CharField(max_length=1000)
    attempts_left = IntegerField()
    message = CharField(max_length=256)
    create_time = DateTimeField(default=datetime.utcnow)

    class Meta:
        database = db
        order_by = ['-create_time']

    @classmethod
    def create_letter(cls, game, letter, representation, letters_guessed, attempts_left, message):
        '''
        '''
        return cls.create(
            game=game, letter=letter, representation=representation,
            letters_guessed=letters_guessed,attempts_left=attempts_left,
            message=message
        )


def create_result(word, attempts, result):
    '''
    Creates an entry with the game result
    '''
    Result.create(word=word, attempts=attempts, result=result)


def create_word(word, user_id):
    word_created.create(word=word, user=user_id, language='')
