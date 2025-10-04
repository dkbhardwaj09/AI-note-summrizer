import os
import json
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin import credentials, auth
from dotenv import load_dotenv

load_dotenv()

# --- Firebase Admin SDK Initialization ---
# This logic supports both local development (using a file path) and
# cloud deployment (using a JSON string in an environment variable).

if not firebase_admin._apps:
    cred_json_str = os.getenv("FIREBASE_CREDENTIALS_JSON")
    cred_path = os.getenv("FIREBASE_ADMIN_SDK_SERVICE_ACCOUNT_KEY_PATH")

    cred_obj = None
    if cred_json_str:
        # For cloud deployment: load credentials from the JSON string.
        try:
            cred_obj = credentials.Certificate(json.loads(cred_json_str))
        except json.JSONDecodeError:
            raise ValueError("Failed to parse FIREBASE_CREDENTIALS_JSON.")
    elif cred_path:
        # For local development: load credentials from the file path.
        cred_obj = credentials.Certificate(cred_path)

    if cred_obj:
        firebase_admin.initialize_app(cred_obj)
    else:
        # If neither is set, the application cannot start.
        raise ValueError(
            "Firebase credentials not found. Set either FIREBASE_CREDENTIALS_JSON "
            "or FIREBASE_ADMIN_SDK_SERVICE_ACCOUNT_KEY_PATH."
        )

oauth2_scheme = HTTPBearer()

async def get_current_user(token: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    """
    Dependency to verify Firebase ID token and get user data.

    Intercepts the Authorization: Bearer <ID_TOKEN> header, verifies the token,
    and returns the user's decoded token data.

    Raises:
        HTTPException: 401 Unauthorized if the token is invalid, expired, or missing.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # Verify the token against the Firebase Auth API.
        decoded_token = auth.verify_id_token(token.credentials)
        return decoded_token
    except auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ID token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid ID token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during token verification: {e}",
        )