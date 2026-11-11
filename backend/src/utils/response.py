def success_response(data=None, message="Operation completed successfully"):
    return {"success": True, "data": data, "message": message, "errors": None}
