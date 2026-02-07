from fastapi import FastAPI
from app.routes import auth, users

app = FastAPI(title="Backend API", version="1.0.0")

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(users.router, prefix="/users", tags=["Users"])

@app.get("/")
def root():
    return {"message": "API funcionando correctamente"}
