

#
# HAVE TO BE IN VIRTUAL ENVIRONMENT TO LAUNCH SERVER.
#
# backend/app> uvicorn main:app --reload
#

# -----------------------------------------------------------------------------
#                                  IMPORTS 
# -----------------------------------------------------------------------------

import os
import sys

# ---------------------------------------------------------------------
# Add the parent directory to the system path to allow for relative
# imports.
# ---------------------------------------------------------------------
PARENT_DIR = os.path.dirname( os.path.dirname( os.path.abspath( __file__ ) ) )
sys.path.append( PARENT_DIR )

from fastapi                 import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles     import StaticFiles
from pathlib                 import Path

from routes.analyze          import router as analyze_router
from routes.health           import router as health_router

# -----------------------------------------------------------------------------
#                                 CONSTANTS
# -----------------------------------------------------------------------------

# ---------------------------------------------------------------------
# Initialize our FastAPI app
# ---------------------------------------------------------------------
app = FastAPI()

# ---------------------------------------------------------------------
# Resolve a relative path to the shared directory so it can be reached
# regardless of where the server is launched from.
# ---------------------------------------------------------------------
BASE_DIR   = Path( __file__ ).resolve().parent.parent.parent
SHARED_DIR = BASE_DIR / "shared"

# -----------------------------------------------------------------------------
#                                 PROCEDURES
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
#                                  CLASSES
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
#                                 EXECUTION 
# -----------------------------------------------------------------------------

# ---------------------------------------------------------------------
# CORS for frontend
# ---------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ "*" ],
    allow_methods=[ "*" ],
    allow_headers=[ "*" ],
)

# ---------------------------------------------------------------------
# Static directory (processed videos)
# ---------------------------------------------------------------------
app.mount(
    path="/shared",
    app=StaticFiles( directory=SHARED_DIR ),
    name="shared"
)

# ---------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------
app.include_router( router=analyze_router )
app.include_router( router=health_router )
