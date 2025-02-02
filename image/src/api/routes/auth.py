from fastapi import APIRouter, HTTPException, Depends
from typing import Dict
import boto3
from botocore.exceptions import ClientError
from models.user import User, SignUpUser, SignInUser
from services.mongodb_service import MongoDBService, get_mongodb_service
import os
import logging

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

# Initialize Cognito client
cognito_client = boto3.client(
    "cognito-idp",
    region_name=os.getenv("AWS_REGION_LOCAL"),
)
USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID")
CLIENT_ID = os.getenv("COGNITO_CLIENT_ID")


@router.post("/signup")
async def signup(
    user_data: SignUpUser, mongo_service: MongoDBService = Depends(get_mongodb_service)
) -> Dict:
    try:
        # Create user in Cognito
        cognito_response = cognito_client.sign_up(
            ClientId=CLIENT_ID,
            Username=user_data.email,
            Password=user_data.password,
            UserAttributes=[
                {"Name": "email", "Value": user_data.email},
            ],
        )

        # Get the Cognito user ID from the response
        cognito_user_id = cognito_response["UserSub"]

        try:
            # Auto confirm the user
            cognito_client.admin_confirm_sign_up(
                UserPoolId=USER_POOL_ID, Username=user_data.email
            )
        except ClientError as confirm_error:
            logging.error(f"Error confirming user: {str(confirm_error)}")
            # If confirmation fails, we should handle cleaning up the created user
            try:
                cognito_client.admin_delete_user(
                    UserPoolId=USER_POOL_ID, Username=user_data.email
                )
            except Exception as delete_error:
                logging.error(
                    f"Error cleaning up unconfirmed user: {str(delete_error)}"
                )
            raise HTTPException(
                status_code=500, detail=f"Failed to confirm user: {str(confirm_error)}"
            )

        # Create user in MongoDB
        user = User(
            email=user_data.email,
            cognito_id=cognito_user_id,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            age=user_data.age,
            profession=user_data.profession,
            skills=user_data.skills,
            interests=user_data.interests or [],
            university=user_data.university,
        )
        await mongo_service.create_user(user)

        return {"message": "User created successfully", "user_id": cognito_user_id}

    except ClientError as e:
        error = e.response["Error"]
        if error["Code"] == "UsernameExistsException":
            raise HTTPException(status_code=400, detail="Email already registered")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/confirm-signup")
async def confirm_signup(email: str, confirmation_code: str) -> Dict:
    """Confirm user signup with code (fallback endpoint)"""
    try:
        cognito_client.confirm_sign_up(
            ClientId=CLIENT_ID, Username=email, ConfirmationCode=confirmation_code
        )
        return {"message": "User confirmed successfully"}
    except ClientError as e:
        error = e.response["Error"]
        raise HTTPException(status_code=400, detail=str(error))


@router.post("/signin")
async def signin(user_data: SignInUser) -> Dict:
    try:
        response = cognito_client.initiate_auth(
            ClientId=CLIENT_ID,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": user_data.email,
                "PASSWORD": user_data.password,
            },
        )

        return {
            "message": "Login successful",
            "tokens": {
                "access_token": response["AuthenticationResult"]["AccessToken"],
                "refresh_token": response["AuthenticationResult"]["RefreshToken"],
                "id_token": response["AuthenticationResult"]["IdToken"],
            },
        }

    except ClientError as e:
        error = e.response["Error"]
        if error["Code"] == "UserNotConfirmedException":
            raise HTTPException(
                status_code=400,
                detail="User is not confirmed. Please confirm your email first.",
            )
        if error["Code"] in ["NotAuthorizedException", "UserNotFoundException"]:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/resend-confirmation")
async def resend_confirmation(email: str) -> Dict:
    """Resend confirmation code"""
    try:
        cognito_client.resend_confirmation_code(ClientId=CLIENT_ID, Username=email)
        return {"message": "Confirmation code resent"}
    except ClientError as e:
        error = e.response["Error"]
        raise HTTPException(status_code=400, detail=str(error))
