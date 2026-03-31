from importlib.metadata import PackageNotFoundError, version

def get_app_version() -> str:
    try:
        return version("predictor-backend")
    except PackageNotFoundError:
        return "unknown"