from flask_session import Session
from dotenv import load_dotenv
from tempfile import mkdtemp
from flask import Flask

load_dotenv()


app = Flask(__name__)
# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Import all routes from modules
from routes.auth.auth import auth_bp
from routes.general.general import general_bp
from routes.user.user import user_bp
from routes.search.search import search_bp

app.register_blueprint(auth_bp)
app.register_blueprint(general_bp)
app.register_blueprint(user_bp)
app.register_blueprint(search_bp)


# Let's go baby !
if __name__ == '__main__':
    app.run()
