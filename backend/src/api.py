import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth, get_token_auth_header

DRINKS_PER_SHELF = 8


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    '''
    @TODO uncomment the following line to initialize the datbase
    !! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
    !! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
    !! Running this function will add one
    '''
    #db_drop_and_create_all()



    # ROUTES
    '''
    @TODO implement endpoint
        GET /drinks
            it should be a public endpoint
            it should contain only the drink.short() data representation
        returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
            or appropriate status code indicating reason for failure
    '''
    @app.route('/drinks', methods=['GET'])
    def get_drinks():
        drinks = Drink.query.order_by(Drink.id).all()
        formatted_drinks = [drink.short() for drink in drinks]

        if len(formatted_drinks) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'drinks': formatted_drinks,
            'total_drinks': len(Drink.query.all())
        })

    '''
    @TODO implement endpoint
        GET /drinks-detail
            it should require the 'get:drinks-detail' permission
            it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
            or appropriate status code indicating reason for failure
    '''
    @app.route('/drinks-details', methods=['GET'])
    @requires_auth('get:drinks-detail')
    def get_drinks_details(token):
        drinks = Drink.query.order_by(Drink.id).all()
        formatted_drinks = [drink.long() for drink in drinks]

        if len(formatted_drinks) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'drinks': formatted_drinks,
            'total_drinks': len(Drink.query.all())
        })


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
    def create_drinks(token):
        body = request.get_json()

        title = body['title']
        recipe = json.dumps(body['recipe'])
        drink = Drink(title=title, recipe=recipe)
        try:
            drink.insert()
            return jsonify({
                'success': True,
                'created': drink.id,
                'drink': drink.long(),
                'total_drinks': len(drink.query.all())

            })
        except:
            abort(422)



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
    @app.route('/drinks/<int:id>', methods=['PATCH'])
    @requires_auth('patch:drinks')
    # @cross_origin
    def update_drinks(token, id):
        body = request.get_json()
        drink = Drink.query.filter(Drink.id == id).one_or_none()

        if 'recipe' not in body:
            title = body['title']
            recipe = drink.recipe
        elif 'title' not in body:
            title = drink.title
            recipe = json.dumps(body['recipe'])
        else:
            title = body['title']
            recipe = json.dumps(body['recipe'])

        if drink is None:
            abort(404)
        else:
            drink.recipe = recipe
            drink.title = title
            try:
                drink.update()
                return jsonify({
                    'success': True,
                    'drink': list(drink.long().items())
                })
            except:
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
    # @cross_origin
    def delete_drinks(token, id):
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        if drink is None:
            abort(404)
        else:
            try:
                drink.delete()
                return jsonify({
                    'success': True,
                    'drink': drink.long()
                })
            except:
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

    '''
    @TODO implement error handler for 404
        error handler should conform to general task above
    '''
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    '''
    @TODO implement error handler for AuthError
        error handler should conform to general task above
    '''

    @app.errorhandler(AuthError)
    def unauthorized(AuthError):
        return jsonify({
            "success": False,
            "error": AuthError.error,
        }), AuthError.status_code

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            "success": False,
            "error": 401,
            "message": "unauthorized"
        }), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            "success": False,
            "error": 403,
            "message": "forbidden"
        }), 403

    return app

if __name__ == "__main__":
    app.debug = True
    app.run()
