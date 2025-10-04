import os
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin import credentials, auth
from dotenv import load_dotenv

load_dotenv()

# Initialize Firebase Admin SDK
# The service account key is expected to be in a JSON file pointed to by an environment variable.
# For security, the service account key itself should not be hardcoded.
cred_path = os.getenv("FIREBASE_ADMIN_SDK_SERVICE_ACCOUNT_KEY_PATH")
if not cred_path:
    raise ValueError("The FIREBASE_ADMIN_SDK_SERVICE_ACCOUNT_KEY_PATH environment variable must be set.")

# Check if the app is already initialized to prevent errors
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

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