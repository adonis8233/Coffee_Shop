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
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks')
def get_drinks():

    try:
        drinks = Drink.query.order_by(Drink.id).all()

        if len(drinks) == 0:
            abort(404)

        else:
            formattedDrinks = [drink.short() for drink in drinks]
            return jsonify({
                'success': True,
                'drinks': formattedDrinks
            })

    except Exception as error:
        print(sys.exc_info())
        abort(404)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detailed(jwt):
    try:
        drinks = Drink.query.order_by(Drink.id).all()
        formatted_drinks = [drink.long() for drink in drinks]

        if len(result) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'drinks': formatted_drinks
        })

    except AuthError:
        abort(422)


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drinks(jwt):
    body = request.get_json()

    json.loads(request.data.decode('utf-8'))
    drink = Drink(title=body['title'], recipe=json.dumps(body['recipe']))

    return jsonify({
        'success': True,
        'drink': drink
    })


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:id>', methods=['POST'])
@requires_auth('patch:drinks')
def update_drink(jwt, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()

    try:
        body = request, get_json(force=True)
        title = body.get('title', None)
        recipe = body.get('recipe', None)

        drink = Drink.query.filter(Drink.id == id).one_or_none()

        drink.title = title
        drink.recipe = json.dumps(recipe)

        drink.update()
        return jsonify({
            'success': True,
            'drinks': [drink.long()],
            'modified_drink_id': id
        })

    except Exception as error:
        abort(422)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload, id):
    try:
        deleted_drinks = Drink.query.filter(Drink.id == id).one_or_none()

        if deleted_drinks is None:
            abort(404)

        deleted_drinks.delete()

        current_drinks = Drink.query.order_by(Drink.id).all()

        return jsonify({
            'success': True,
            'deleted_drinks_id': id,
            'drinks': current_drinks
        })

    except Exception as error:
        print(error)
        abort(422)


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


@app.errorhandler(AuthError)
def auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
