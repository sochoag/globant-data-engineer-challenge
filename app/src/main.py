# Library imports
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.status import HTTP_401_UNAUTHORIZED
import secrets
import os

# Local imports
from .api.endpoints import router as api_router
from .avro.endpoints import router as backup_router

# Authentication
security = HTTPBasic()

# User credentials
USERS = {
    os.getenv("API_USER"): os.getenv("API_PASS")
}

# Authentication function


def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)):
    """
    Authenticate the user based on the provided credentials.

    Args:
        credentials (HTTPBasicCredentials): The credentials provided by the user.

    Returns:
        str: The username of the authenticated user.
    """
    # Check if the username and password are correct
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

# Initialize the FastAPI app
app = FastAPI()

# Add the routers to the app
app.include_router(api_router, dependencies=[Depends(authenticate_user)])
app.include_router(backup_router, dependencies=[Depends(authenticate_user)])

# Exception handler for RequestValidationError


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

# Root endpoint


@app.get("/")
def read_root():
    import os
    return {"message": f"Welcome to the HR Transactions API {os.getcwd()}"}
