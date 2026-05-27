"""Download routes for completed report exports."""

from flask import Blueprint

from ..controllers.download_controller import download_report

download_bp = Blueprint("download", __name__, url_prefix="/v1/reports")


@download_bp.route("/<job_id>/download", methods=["GET"])
def download(job_id: str):
    return download_report(job_id)
