from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Job Search System",
    description="Tasks 1 & 2: Cyclic company coverage + open-web discovery",
    version="0.0.1",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "jobfinder-backend"}


@app.get("/")
async def root():
    return {"message": "Job Search System API v0.0.1"}
