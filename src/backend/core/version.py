from importlib.metadata import version, PackageNotFoundError

def get_app_version() -> str:
    try:
        return version("predictor-backend")
    except PackageNotFoundError:
        return "unknown"
