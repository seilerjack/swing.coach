

# -----------------------------------------------------------------------------
#                                  IMPORTS 
# -----------------------------------------------------------------------------

from fastapi                 import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles     import StaticFiles

from routes.analyze          import router as analyze_router
from routes.health           import router as health_router

# -----------------------------------------------------------------------------
#                                 CONSTANTS
# -----------------------------------------------------------------------------

app = FastAPI()

# -----------------------------------------------------------------------------
#                                 PROCEDURES
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
#                                  CLASSES
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
#                                 EXECUTION 
# -----------------------------------------------------------------------------

if __name__ == "__main__":

    # CORS for frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[ "*" ],
        allow_methods=[ "*" ],
        allow_headers=[ "*" ],
    )

    # Static directory (processed videos)
    app.mount(
        path="/shared",
        app=StaticFiles( directory="src/shared" ),
        name="shared"
    )

    # Routers
    app.include_router( router=analyze_router, prefix="/routes")
    app.include_router( router=health_router, prefix="/routes")
