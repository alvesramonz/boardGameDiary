from crypt import methods
from datetime import datetime
from functools import wraps
from bson import ObjectId
from werkzeug.local import LocalProxy
from flask import Blueprint, redirect, render_template, url_for, session, request

from settings.db import get_db

main = Blueprint('main', __name__)

db = LocalProxy(get_db)

# Decorators    
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session or 'token' in session: 
            return f(*args, **kwargs)
        else:
            return redirect(url_for('auth.login'))

    return wrap
    
@main.route('/')
def view_index():
    return redirect(url_for('main.view_my_games'))

@main.route('/register_game')
@login_required
def view_register_game():
    return render_template('register_game.html')

@main.route('/my_games')
@login_required
def view_my_games():
    user_id = ObjectId(session['user']['_id'])
    user = db.users.find_one({'_id': user_id})
    
    my_games_ids = user.get('myGames', [])
    my_games = db.games.find({'_id': {'$in': my_games_ids}})

    return render_template('my_games.html', my_games=my_games)

@main.route('/edit_game/<my_game_id>')
@login_required
def view_edit_game(my_game_id):
    my_game = db.games.find_one({'_id': ObjectId(my_game_id)})
    return render_template('edit_game.html', my_game=my_game)


@main.route('/my_games', methods=['POST'])
def my_games():
    pass

@main.route('/register_game', methods=['POST'])
def register_game():
    user = session['user']
    
    game_system = request.form.get('game-system')
    game_players = request.form.get('game-players')
    game_description = request.form.get('game-description')

    new_game = {
        "userOwner": ObjectId(user.get('_id')),
        "gameSystem": game_system,
        "gamePlayers": game_players,
        "gameDescription": game_description,
        "createdAt": datetime.now()
    }

    my_game = db.games.insert_one(new_game)
    db.users.update_one({'_id': ObjectId(user.get('_id'))}, {"$push": {"myGames": my_game.inserted_id}})

    return redirect(url_for('main.view_my_games'))

@main.route('/edit_game/<my_game_id>', methods=['PUT', 'POST'])
def edit_my_game(my_game_id):
    game_system = request.form.get('game-system')
    game_players = request.form.get('game-players')
    game_description = request.form.get('game-description')

    payload = {
        "gameSystem": game_system,
        "gamePlayers": game_players,
        "gameDescription": game_description,
        "updatedAt": datetime.now()
    }

    db.games.update_one({'_id': ObjectId(my_game_id)}, {'$set': payload})
    return redirect(url_for('main.view_my_games'))

@main.route('/delete_game/<my_game_id>', methods=['DELETE', 'GET'])
@login_required
def delete_my_game(my_game_id):
    user_id = ObjectId(session['user']['_id'])

    db.games.delete_one({'_id': ObjectId(my_game_id)})
    db.users.update_one({'_id': user_id}, {"$pull": {"myGames": ObjectId(my_game_id)}})

    return redirect(url_for('main.view_my_games'))
