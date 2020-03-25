from typing import Tuple

from app import app


@app.errorhandler(400)
def bad_request_error(error: str) -> Tuple[dict, int]:
    return {
               'message': error
           }, 400


@app.errorhandler(401)
def unauthorized_error(error: str) -> Tuple[dict, int]:
    return {
               'message': error
           }, 401


@app.errorhandler(404)
def not_found_error(error: str) -> Tuple[dict, int]:
    return {
               'message': error
           }, 404


@app.errorhandler(408)
def request_timeout_error(error: str) -> Tuple[dict, int]:
    return {
               'message': error
           }, 408
