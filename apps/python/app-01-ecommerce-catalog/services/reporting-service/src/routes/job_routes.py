"""Async job queue routes for the reporting service."""

from flask import Blueprint

from ..controllers.job_controller import enqueue_job, get_job_status

job_bp = Blueprint("jobs", __name__, url_prefix="/v1/reports")


@job_bp.route("/jobs", methods=["POST"])
def enqueue():
    return enqueue_job()


@job_bp.route("/jobs/<job_id>", methods=["GET"])
def status(job_id: str):
    return get_job_status(job_id)
