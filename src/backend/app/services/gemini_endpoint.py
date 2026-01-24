

# -----------------------------------------------------------------------------
#                                  IMPORTS 
# -----------------------------------------------------------------------------

from .            import config
from google       import genai
from google.genai import types
from pydantic     import BaseModel

# -----------------------------------------------------------------------------
#                                  CONSTANTS
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
#                                   CLASSES
# -----------------------------------------------------------------------------

# ---------------------------------------------------------------------
#
#   CLASS NAME: ResponseSchemaScore
#
#   DESCRIPTION:
#       Pydantic base model for structuring the Gemini API responses
#       for specific swing category scores.
#
# ---------------------------------------------------------------------
class ResponseSchemaScore( BaseModel ):
    name: str                # "Posture & Setup"
    score: int               # 0–100
    summary: str             # One-sentence explanation


# ---------------------------------------------------------------------
#
#   CLASS NAME: ResponseSchema
#
#   DESCRIPTION:
#       Pydantic base model for structuring the Gemini API responses.
#
# ---------------------------------------------------------------------
class ResponseSchema( BaseModel ):
    swingAnalysis: str
    categoryScores: list[ ResponseSchemaScore ]
    overallScore: int
    keyObservations: list[ str ]
    coachingTips: list[ str ]


# ---------------------------------------------------------------------
#
#   CLASS NAME: Client
#
#   DESCRIPTION:
#       This is the access point to the Gemini API. It's sole
#       responsibility is to manage communication with the Gemini
#       service.
#
# ---------------------------------------------------------------------
class Client():
    
    def __init__( self, api_key: str = config.GEMINI_KEY ):

        # -------------------------------------------------------------
        # Initialize with the project-specific API key.
        # -------------------------------------------------------------
        self.api_key       = api_key
        self.gemini_client = genai.Client( api_key=self.api_key )

    # -----------------------------------------------------------------
    #                        PUBLIC METHODS
    # -----------------------------------------------------------------

    # -----------------------------------------------------------------
    #
    #   PROCEDURE NAME: generate_response
    #
    #   DESCRIPTION:
    #       Public API method to generate a response from Gemini given
    #       a text prompt.
    #
    # -----------------------------------------------------------------
    def generate_response( self, prompt: str, model: str = "gemini-2.5-flash" ):
        
        # -------------------------------------------------------------
        # Return Gemini's response to the provided prompt.
        # -------------------------------------------------------------
        response = self.gemini_client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type='application/json',
                response_schema=ResponseSchema ) )
    
        return response.parsed


# -----------------------------------------------------------------------------
#                                 PROCEDURES
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
#                                  EXECUTION 
# -----------------------------------------------------------------------------
