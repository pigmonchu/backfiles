import datetime
from functools import wraps
from http import HTTPStatus

from flask import current_app as app
from flask import make_response, jsonify
from flask import request
from flask.views import MethodView
from flask_babel import _

from app import db
from app.auth.models import User, BlacklistToken
from app.utils.mailing import sendConfirmationMail, confirm_token
from app.utils.validators import ResponseJSON, public_attr_to_dict, validate_form
from . import auth

def extract_token():
    auth_header = request.headers.get('Authorization')
    if auth_header:
        auth_header = auth_header
        auth_token = auth_header.split(" ")
        auth_token = auth_token[1] if len(auth_token) > 1 else ''
    else:
        auth_token = ''
    return auth_token


def is_authorized():
    auth_header = request.headers.get('Authorization')
    if auth_header:
        auth_header = auth_header
        auth_token = auth_header.split(" ")
        if len(auth_token) > 1:
            auth_token = auth_token[1] if len(auth_token) > 1 else ''
        else:
            return False, _('Bad authentication. Please try again')
    else:
        return False, _('Bad authentication. Please try again')

    if auth_token:
        try:
            resp = User.decode_auth_token(auth_token)
        except Exception as e:
            return False, str(e)

        return True, resp

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        authorized, add_info = is_authorized()
        if not authorized:
            responseObject = ResponseJSON(add_info)
            return make_response(jsonify(public_attr_to_dict(responseObject))), HTTPStatus.FORBIDDEN

        if not kwargs.get('__user_auth'):
            kwargs['__user_auth'] = add_info
        return f(*args, **kwargs)
    return decorated


class RegisterAPI(MethodView):
    def post(self):

        post_data = request.get_json()
        form_is_ok, form = validate_form(auth.import_name, "RegistrationForm", post_data)

        if form_is_ok:
            try:
                user = User(
                    email=post_data.get('email'),
                    first_name=post_data.get('first_name'),
                    last_name=post_data.get('last_name'),
                    password=post_data.get('password'),
                    is_administrator=post_data.get('is_administrator')
                )

                db.session.add(user)
                sendConfirmationMail(user.email)
                db.session.commit()
                messages = [
                    _('Successfully registered.'),
                    _('Confirmation email sended.')
                ]

                responseObject = ResponseJSON({'messages': messages}, True)
                return make_response(jsonify(public_attr_to_dict(responseObject))), HTTPStatus.CREATED
            except Exception as e:
                responseObject = {
                    'status': 'fail',
                    'message': _('Some error ocurred. Please try again.')
                }
                app.logger.error(e)
                return make_response(jsonify(responseObject)), HTTPStatus.BAD_REQUEST
        else:
            responseObject = ResponseJSON(form.errors)
            return make_response(jsonify(public_attr_to_dict(responseObject))), HTTPStatus.BAD_REQUEST

class ConfirmEmailAPI(MethodView):
    def get(self, token):
        try:
            email = confirm_token(token)
            if not email:
                responseObject = ResponseJSON(_("Incorrect or expired confirmation link"))
                return make_response(jsonify(public_attr_to_dict(responseObject))), HTTPStatus.BAD_REQUEST
        except Exception as e:
            app.logger.error("**** ERROR: {} ****".format(e))
            responseObject = ResponseJSON(_("Incorrect or expired confirmation link"))
            return make_response(jsonify(public_attr_to_dict(responseObject))), HTTPStatus.BAD_REQUEST

        user = User.query.filter_by(email=email).first()
        if user is None:
            responseObject = ResponseJSON(_("Incorrect or expired confirmation link"))
            return make_response(jsonify(public_attr_to_dict(responseObject))), HTTPStatus.BAD_REQUEST
        elif user.confirmed:
            responseObject = ResponseJSON(_("Mail already confirmed. Please log in."), True)
        else:
            user.confirmed = True
            user.confirmed_on = datetime.datetime.now()
            user.is_active = True
            db.session.add(user)
            db.session.commit()
            responseObject = ResponseJSON(_("Mail properly confirmed, thank you. Please log in."), True)

        return make_response(jsonify(public_attr_to_dict(responseObject))), HTTPStatus.OK

class ReconfirmEmailAPI(MethodView):
    def post(self):
        post_data = request.get_json()
        form_is_ok, form = validate_form(auth.import_name, "LoginForm", post_data)
        if form_is_ok:
            user = User.query.filter_by(email=post_data.get('email')).first()
            if user is None:
                responseObject = ResponseJSON(_("A confirmation email was sent to your registration address."), True)
            elif user.confirmed:
                responseObject = ResponseJSON(_("Mail already confirmed. Please log in."), True)
            else:
                sendConfirmationMail(user.email)
                responseObject = ResponseJSON(_("A confirmation email was sent to your registration address."), True)
        else:
            responseObject = ResponseJSON(form.errors)
        return make_response(jsonify(public_attr_to_dict(responseObject))), HTTPStatus.OK

class LoginAPI(MethodView):
    def post(self):
        post_data = request.get_json()
        form_is_ok, form = validate_form(auth.import_name, "LoginForm", post_data)

        if form_is_ok:
            try:
                user = User.query.filter_by(
                    email=post_data.get("email")
                ).first()

                if user is not None and user.verify_password(post_data.get("password")):
                    if user.confirmed:
                        auth_token = user.encode_auth_token()

                        if auth_token:
                            responseObject = ResponseJSON( {'msg': _('Succesfully logged in.'), 'token': auth_token.decode()}, True)
                            response = make_response(jsonify(public_attr_to_dict(responseObject)))
                            return response
                        else:
                            raise Exception(_("Not token generated."))
                    else:
                        responseObject = ResponseJSON(_('Please confirm your email before connecting.'))
                        return make_response(jsonify(public_attr_to_dict(responseObject))), HTTPStatus.UNAUTHORIZED

                else:
                    responseObject = ResponseJSON(_('Incorrect user or password. Please try again.'))
                    return make_response(jsonify(public_attr_to_dict(responseObject))), HTTPStatus.UNAUTHORIZED

            except Exception as e:
                responseObject = ResponseJSON(_('Some error ocurred. Please try again.'))
                app.logger.error(e)
                return make_response(jsonify(public_attr_to_dict(responseObject))), HTTPStatus.BAD_REQUEST
        else:
            responseObject = ResponseJSON(form.errors)
            return make_response(jsonify(public_attr_to_dict(responseObject))), HTTPStatus.BAD_REQUEST

class LogoutAPI(MethodView):
    def post(self):
        auth_token = extract_token()
        if auth_token:
            try:
                resp = User.decode_auth_token(auth_token)
            except Exception as e:
                responseObject = ResponseJSON(str(e))
                return make_response(jsonify(public_attr_to_dict(responseObject))), HTTPStatus.FORBIDDEN

            blacklis_token = BlacklistToken(auth_token)
            blacklis_token.user_update = resp
            try:
                db.session.add(blacklis_token)
                db.session.commit()
                responseObject = ResponseJSON(_("Succesfully logged out."), True)
                return make_response(jsonify(public_attr_to_dict(responseObject))), HTTPStatus.OK
            except Exception as e:
                responseObject = ResponseJSON(_('Some error ocurred. Please try again.'))
                return make_response(jsonify(public_attr_to_dict(responseObject))), HTTPStatus.INTERNAL_SERVER_ERROR

        else:
            responseObject = ResponseJSON(_('Bad authentication. Please try again'))
            return make_response(jsonify(public_attr_to_dict(responseObject))), HTTPStatus.FORBIDDEN


class UserAPI(MethodView):
    def get(self):
        authorized, add_info = is_authorized()
        if not authorized:
            responseObject = ResponseJSON(add_info)
            return make_response(jsonify(public_attr_to_dict(responseObject))), HTTPStatus.FORBIDDEN

        user = User.query.filter_by(id=add_info).first()
        if user:
            dUser = [{'id': user.id, 'email': user.email, 'first_name': user.first_name, 'last_name': user.last_name, 'is_administrator': user.is_administrator}]
            responseObject = ResponseJSON(dUser, True)
            return make_response(jsonify(public_attr_to_dict(responseObject))), HTTPStatus.OK
        else:
            responseObject = ResponseJSON(_('Some error ocurred. Please try again.'))
            app.logger.error('*** Usuario {} inexistente'.format(resp))
            return make_response(jsonify(public_attr_to_dict(responseObject))), HTTPStatus.BAD_REQUEST

