from fastapi import FastAPI
from .api.endpoints import router as api_router
from .avro.endpoints import router as backup_router
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import FastAPI

app = FastAPI()

# Routers
app.include_router(api_router)
app.include_router(backup_router)


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
    return {"message": "Welcome to the HR Transactions API"}
