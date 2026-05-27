def parse_pagination(request_args):
    try:
        page = int(request_args.get("page", 1))
    except (ValueError, TypeError):
        page = 1
    try:
        limit = int(request_args.get("limit", 20))
    except (ValueError, TypeError):
        limit = 20

    page = max(page, 1)
    limit = max(1, min(limit, 100))

    offset = (page - 1) * limit
    return {"page": page, "limit": limit, "offset": offset}
