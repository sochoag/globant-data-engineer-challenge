from fastapi import FastAPI
from .api.endpoints import router as api_router
from .avro.endpoints import router as backup_router
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.status import HTTP_401_UNAUTHORIZED
import secrets
import os

security = HTTPBasic()

USERS = {
    os.getenv("API_USER"): os.getenv("API_PASS")
}


def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username not in USERS:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    if not secrets.compare_digest(credentials.password, USERS[credentials.username]):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


# Create data folder if it doesn't exist
if not os.path.exists("./.data"):
    os.makedirs("./.data")

app = FastAPI()

# Routers
app.include_router(api_router, dependencies=[Depends(authenticate_user)])
app.include_router(backup_router, dependencies=[Depends(authenticate_user)])


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    errors = [
        {
            "field": ".".join(map(str, error["loc"])),
            "message": error["msg"],
        }
        for error in exc.errors()
    ]

    return JSONResponse(
        status_code=422,
        content={"message": "Validation failed", "errors": errors},
    )


@app.get("/")
def read_root():
    import os
    return {"message": f"Welcome to the HR Transactions API {os.getcwd()}"}
