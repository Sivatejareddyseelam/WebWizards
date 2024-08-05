from flask import Blueprint
from flask_restx import Api, Resource, Namespace

bp = Blueprint('api', __name__)
api = Api(bp, version='1.0', title='My API',
          description='A simple demonstration API',
          doc='/')

from app.api import users, errors, tokens, tags
