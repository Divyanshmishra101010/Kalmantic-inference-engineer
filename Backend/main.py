from fastapi import FastAPI
from api import router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="PDF Analyzer")

origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # <-- URLs that can access the API
    allow_credentials=True,
    allow_methods=["*"],    # <-- HTTP methods to allow (POST, GET, etc.)
    allow_headers=["*"],    # <-- HTTP Headers to allow
)

app.include_router(router)
