import os
import json
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
import google_auth_oauthlib.flow
from backend.app.core import config
from backend.app.core.logger import logger

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/login")
async def login():
    """Initiate Google OAuth2 flow."""
    if not os.path.exists(config.GOOGLE_CLIENT_SECRETS_FILE):
        raise HTTPException(
            status_code=500, 
            detail="credentials.json not found. Please follow the instructions in AUTOMATION.md to set up Gmail API."
        )

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        str(config.GOOGLE_CLIENT_SECRETS_FILE),
        scopes=config.GOOGLE_SCOPES
    )
    flow.redirect_uri = config.GOOGLE_REDIRECT_URI

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    
    return {"url": authorization_url}

@router.get("/callback")
async def callback(request: Request):
    """Handle Google OAuth2 callback."""
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        str(config.GOOGLE_CLIENT_SECRETS_FILE),
        scopes=config.GOOGLE_SCOPES
    )
    flow.redirect_uri = config.GOOGLE_REDIRECT_URI
    
    flow.fetch_token(code=code)
    credentials = flow.credentials

    # Save credentials to token.json
    with open(config.GOOGLE_TOKEN_FILE, 'w') as token:
        token.write(credentials.to_json())

    logger.info("✅ Google credentials saved successfully")
    return {"status": "success", "message": "Google authentication successful"}

@router.get("/status")
async def get_auth_status():
    """Check if Google authentication is active."""
    if os.path.exists(config.GOOGLE_TOKEN_FILE):
        return {"authenticated": True}
    return {"authenticated": False}
