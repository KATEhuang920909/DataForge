"""DataForge — Professional Data Management Tool"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text
from app.core.config import get_settings
from app.core.database import engine, Base
from app.api import sources_router, files_router, logs_router, root_router

settings = get_settings()

def _ensure_activity_log_status_column():
    inspector = inspect(engine)
    if 'activity_logs' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('activity_logs')]
        if 'status' not in columns:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE activity_logs ADD COLUMN status VARCHAR(16) DEFAULT 'success'"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    _ensure_activity_log_status_column()
    print(f"\n🚀 {settings.APP_NAME} v{settings.APP_VERSION} started\n")
    yield
    print(f"\n👋 {settings.APP_NAME} shutting down\n")

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION,
              description="Professional data management platform", lifespan=lifespan)

app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS,
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(root_router)
app.include_router(sources_router, prefix="/api/v1")
app.include_router(files_router, prefix="/api/v1")
app.include_router(logs_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
