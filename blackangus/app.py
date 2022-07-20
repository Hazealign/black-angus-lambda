from flask import Flask

app = Flask(__name__)


@app.route("/")
def index_route():
    return {
        "result": {
            "success": False,
            "message": "Not Found",
        }
    }, 404


@app.errorhandler(404)
def not_found_route(error):
    return {
        "result": {
            "success": False,
            "message": "Not Found",
            "error": f"{error}",
        }
    }


# We only need this for local development.
if __name__ == "__main__":
    app.run(port=8000, debug=True)
