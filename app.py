from translation import i18n_set_file
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

# Set i18n file to use
i18n_set_file("main")

# Import and register all routes
from routes import routes_list

for route in routes_list:
    app.register_blueprint(route)

# Go go go !
if __name__ == "__main__":
    app.run()
