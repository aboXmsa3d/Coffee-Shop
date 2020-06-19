import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth 

'''
cd backend/src
set FLASK_APP=api.py
$env:FLASK_APP = "api.py"
flask run --reload
'''

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ endpoints ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

'''
@TODO implement endpoint GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def drinks():

    all_drinks = Drink.query.all()
    drinks=[]

    for drink in all_drinks:
        drinks.append(drink.short())

    return jsonify({
        'success': True,
        "drinks": drinks
    })

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
'''
@TODO implement endpoint GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def drinks_detail(payload):

    all_drinks = Drink.query.all()
    drinks=[]

    for drink in all_drinks:
        drinks.append(drink.long())

    return jsonify({
        'success': True,
        "drinks": drinks
    })

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
'''
@TODO implement endpoint POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(payload):

    body = request.get_json()

    new_title = body.get('title', None)
    new_recipe = body.get('recipe', None)

    try:
        drink = Drink(
            title=new_title,
            recipe=json.dumps(new_recipe) # write it as String
            )

        drink.insert()

        return jsonify({
            'success': True,
            "drinks": drink.long()
        })

    except BaseException:
        abort(422)
   

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
'''
@TODO implement endpoint PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(payload , drink_id):

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
            drink.recipe = json.dumps(new_recipe) # write it as String

        drink.update()

        return jsonify({
            'success': True,
            "drinks": [drink.long()]
        })

    except BaseException:
        abort(422)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
'''
@TODO implement endpoint DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload , drink_id):

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
def Unauthorized (error):
    return jsonify({
        'success': False,
        'error': 401,
        'message': 'Unauthorized'
    }), 401


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response



if __name__ == '__main__':
    app.run()
