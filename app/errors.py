from app import app


@app.errorhandler(404)
def not_found_error(error: str):
    return error, 404


@app.errorhandler(400)
def bad_request_error(error: str):
    return error, 400


@app.errorhandler(401)
def unauthorized_error(error: str):
    return error, 401

