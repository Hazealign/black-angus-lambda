from flask import Flask, jsonify

from blackangus.routes.v1.line import search_list_route, fetch_info_route

app = Flask(__name__)


@app.route("/")
def index_route():
    return (
        jsonify(
            {
                "result": {
                    "success": False,
                    "message": "Not Found",
                }
            }
        ),
        404,
    )


@app.errorhandler(404)
def not_found_route(error):
    return (
        jsonify(
            {
                "result": {
                    "success": False,
                    "message": "Not Found",
                    "error": f"{error}",
                }
            }
        ),
        404,
    )


@app.errorhandler(500)
def internal_server_error_route(error):
    return (
        jsonify(
            {
                "result": {
                    "success": False,
                    "message": "Internal Server Error",
                    "error": f"{error}",
                }
            }
        ),
        500,
    )


@app.route("/api/v1/line/list", methods=["GET"])
async def api_v1_line_list():
    return await search_list_route()


# mypy is bullshit...
@app.route("/api/v1/line/<int:linecon_id>", methods=["GET"])  # type: ignore
async def api_v1_line_item(linecon_id: int):
    return await fetch_info_route(linecon_id)


# We only need this for local development.
if __name__ == "__main__":
    app.run(port=8000, debug=True)
