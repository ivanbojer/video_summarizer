import uvicorn
from app import ignoreSSL

IGNORE_SSL = False
if __name__ == "__main__":
    if IGNORE_SSL:
        with ignoreSSL.no_ssl_verification():
            import uvicorn
            uvicorn.run("app.main:app")
    else:
        uvicorn.run("app.main:app")