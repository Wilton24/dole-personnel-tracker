from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine, SessionLocal
from .routers import auth, roles, personnel, projects, assignments
from .seed import seed_data

app = FastAPI(title="DOLE Personnel Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_data(db)
    finally:
        db.close()


app.include_router(auth.router)
app.include_router(roles.router)
app.include_router(personnel.router)
app.include_router(projects.router)
app.include_router(assignments.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
