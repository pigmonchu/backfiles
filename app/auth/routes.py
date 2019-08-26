from app.auth.views import RegisterAPI, LoginAPI, ConfirmEmailAPI, ReconfirmEmailAPI, LogoutAPI, UserAPI
from . import auth
from app.utils.routes import enroute
registration_view = RegisterAPI.as_view('register_api')
auth.add_url_rule(
    enroute('register'),
    view_func=registration_view,
    methods=['POST']
)

login_view = LoginAPI.as_view('login_api')
auth.add_url_rule(
    enroute('login'),
    view_func=login_view,
    methods=['POST']
)

confirm_view = ConfirmEmailAPI.as_view('confirm_email_api')
auth.add_url_rule(
    enroute('confirm/<token>'),
    view_func=confirm_view
)

reconfirm_view = ReconfirmEmailAPI.as_view('reconfirm_user_api')
auth.add_url_rule(
    enroute('reconfirm'),
    view_func=reconfirm_view,
    methods=['POST']
)

logout_view = LogoutAPI.as_view('logout_api')
auth.add_url_rule(
    enroute('logout'),
    view_func=logout_view,
    methods=['POST']
)

user_view = UserAPI.as_view('user_api')
auth.add_url_rule(
    enroute('user'),
    view_func=user_view
)
