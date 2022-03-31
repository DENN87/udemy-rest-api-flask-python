import hmac

from flask_jwt_extended import create_access_token, create_refresh_token
from flask_restful import Resource, reqparse
from models.user import UserModel


_user_parser = reqparse.RequestParser()
_user_parser.add_argument('username',
                          type = str,
                          required = True,
                          help = "This field cannot be blank."
                          )
_user_parser.add_argument('password',
                          type = str,
                          required = True,
                          help = "This field cannot be blank."
                          )


class UserRegister(Resource):
    def post(self):
        data = _user_parser.parse_args()
        
        if UserModel.find_by_username(data['username']):
            return {"message": "A user with that username already exists."}, 400
        
        user = UserModel(data['username'], data['password'])  # (**data) unpacking data
        user.save_to_db()
        
        return {"message": "User created successfully."}, 201


class User(Resource):
    @classmethod
    def get(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User not found.'}, 404
        return user.json()
    
    @classmethod
    def delete(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User not found.'}, 404
        user.delete_from_db()
        return {'message': 'User was deleted.'}, 200


class UserLogin(Resource):
    def post(self):
        data = _user_parser.parse_args()
        
        user = UserModel.find_by_username(data['username'])
        
        if user and hmac.compare_digest(user.password, data['password']):
            access_token = create_access_token(identity = user.id, fresh = True)
            refresh_token = create_refresh_token(user.id)
            return {
                       'access_token': access_token,
                       'refresh_token': refresh_token
                       }, 200
        
        return {'message': 'Invalid credentials.'}, 401


# TO IMPLEMENT FOR ADMIN USER ONLY
# from flask_jwt import jwt_required, current_identity
# class User(Resource):
#     @jwt_required()
#     def get(self):   # view all users
#         user = current_identity
#         # then implement admin auth method
