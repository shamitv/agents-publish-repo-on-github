from flask import Blueprint

from ..controllers.report_controller import list_definitions, sales_report, inventory_health, data_quality

report_bp = Blueprint("report", __name__, url_prefix="/v1/reports")


@report_bp.route("/definitions", methods=["GET"])
def definitions():
    return list_definitions()


@report_bp.route("/sales", methods=["GET"])
def sales():
    return sales_report()


@report_bp.route("/inventory-health", methods=["GET"])
def inventory():
    return inventory_health()


@report_bp.route("/data-quality", methods=["GET"])
def quality():
    return data_quality()
