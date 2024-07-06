from flask import Blueprint
from app.config import settings
from app.helpers import ResponseHelper

bp = Blueprint("health", __name__)


@bp.route("/health", methods=["GET"])
def status():
    """
    Health check endpoint.
    """
    return ResponseHelper.parse_response(
        200,
        {
            "status": "ok",
            "version": settings.version,
        },
    )
