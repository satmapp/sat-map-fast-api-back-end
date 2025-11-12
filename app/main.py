from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app.models import Base
from app.routers import commerces, users, rewards

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SatMap API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://sat-map-hackhaton.netlify.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(commerces.router, prefix="/api", tags=["commerces"])
app.include_router(rewards.router, prefix="/api", tags=["rewards"])

@app.get("/")
def read_root():
    return {"message": "SatMap API v1.0", "status": "running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

