def success(data=None):
    return {"status": "success", "data": data}


def fail(data=None):
    return {"status": "fail", "data": data}


def error(message, code=None):
    return {"status": "error", "message": message, "code": code}
