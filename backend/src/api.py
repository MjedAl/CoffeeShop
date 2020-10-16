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
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''


# db_drop_and_create_all()

# ROUTES

'''
@implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
     where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['GET'])
def get_drinks():
    try:
        drinks = Drink.query.all()
        return jsonify({
            'success': True,
            'drinks': [drink.short() for drink in drinks]
        })
    except Exception:
        abort(500)

'''
@implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
     where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def drinks_details(payload):
    try:
        drinks = Drink.query.order_by(Drink.id).all()
        return jsonify({
            'success': True,
            'drinks': [drink.long() for drink in drinks]
        })
    except Exception:
        return jsonify({
            'success': False
        })

'''
@implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
     where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drink(payload):
    JSON_body = request.get_json()
    title = JSON_body.get('title')
    recipe = JSON_body.get('recipe')
    drink = Drink(title=title, recipe=json.dumps(recipe))
    drink.insert()
    return jsonify({
        'success': True,
        'drinks': drink.long()
    })

'''
@implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
     where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):
    drink = Drink.query.filter_by(id=id).one_or_none()
    if drink is None:
        abort(404)
    else:
        JSON_body = request.get_json()
        title = JSON_body.get('title')
        recipe = JSON_body.get('recipe')
        if title is not None:
            drink.title = title
        if recipe is not None:
            drink.recipe = json.dumps(recipe)
        drink.update()
        return jsonify({
            'success': True,
            'drinks': drink.long()
        })

'''
@implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id}
     where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    drink = Drink.query.filter_by(id=id).one_or_none()
    if drink is None:
        abort(404)
    else:
        drink.delete()
        return jsonify({
            'success': True,
            'delete': drink.id
        })


# Error Handling


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad request"
    }), 400


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Not found"
    }), 404


@app.errorhandler(422)
def unprocessable_entity(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Un-processable Entity"
    }), 422


@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal Server Error"
    }), 500

'''
@implement error handler for AuthError CHANGE
    error handler should conform to general task above
'''


@app.errorhandler(AuthError)
def auth_error(exception):
    """
    Receive the raised authorization error and propagates it as response
    """
    return jsonify(exception.error), exception.status_code
