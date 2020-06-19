import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth


app = Flask(__name__)
setup_db(app)
CORS(app)

'''
    uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ endpoints ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #


@app.route('/drinks', methods=['GET'])
def drinks():

    all_drinks = Drink.query.all()
    drinks = []

    for drink in all_drinks:
        drinks.append(drink.short())

    return jsonify({
        'success': True,
        "drinks": drinks
    })


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def drinks_detail(payload):

    all_drinks = Drink.query.all()
    drinks = []

    for drink in all_drinks:
        drinks.append(drink.long())

    return jsonify({
        'success': True,
        "drinks": drinks
    })


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(payload):

    body = request.get_json()

    new_title = body.get('title', None)
    new_recipe = body.get('recipe', None)

    try:
        drink = Drink(
            title=new_title,
            recipe=json.dumps(new_recipe)  # write it as String
        )

        drink.insert()

        return jsonify({
            'success': True,
            "drinks": drink.long()
        })

    except BaseException:
        abort(422)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(payload, drink_id):

    drink = Drink.query.get(drink_id)

    if drink is None:
        abort(404)

    body = request.get_json()

    new_title = body.get('title', None)
    new_recipe = body.get('recipe', None)

    try:

        if new_title is not None:
            drink.title = new_title
        if new_recipe is not None:
            drink.recipe = json.dumps(new_recipe)  # write it as String

        drink.update()

        return jsonify({
            'success': True,
            "drinks": [drink.long()]
        })

    except BaseException:
        abort(422)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):

    drink = Drink.query.get(drink_id)

    if drink is None:
        abort(404)

    try:

        drink.delete()

        return jsonify({
            'success': True,
            "drinks": drink.long()
        })

    except BaseException:
        abort(422)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Error Handlers ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        'success': False,
        'error': 422,
        'message': 'unprocessable'
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'resource not found'
    }), 404


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': 'bad request'
    }), 400


@app.errorhandler(401)
def Unauthorized(error):
    return jsonify({
        'success': False,
        'error': 401,
        'message': 'Unauthorized'
    }), 401


@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response


if __name__ == '__main__':
    app.run()
