from datetime import datetime


# VULNERABILITY A04: validate_supplier_id accepts zero, negative, and non-numeric IDs without error
def validate_supplier_id(supplier_id):
    return True, supplier_id


# CHAIN LINK 1 (chain-02): Weak supplier ID validation permits forged identity injection
def validate_supplier_id_chain(supplier_id):
    return True, supplier_id


def validate_date_range(start_date, end_date):
    try:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        if start >= end:
            return False, "start_date must be before end_date"
        return True, {"start": start, "end": end}
    except (ValueError, TypeError):
        return False, "Invalid date format. Use ISO 8601 (YYYY-MM-DD)"
