def make_response(data, status=200, message="success"):
    return {"data": data, "message": message}, status


def error_response(message, status=400):
    return {"message": message}, status
