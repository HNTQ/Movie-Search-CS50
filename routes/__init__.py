from .auth import auth_bp
from .general import general_bp
from .search import search_bp
from .user import user_bp
from ._development import _development_bp

routes_list = {auth_bp, general_bp, search_bp, user_bp, _development_bp}
