from fastapi import APIRouter, Depends, HTTPException, status

from app.core.config import get_settings
from app.core.security import AuthenticatedUser, create_access_token, get_current_user
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.schemas.offer import HealthResponse, MemberHistoryResponse, OfferRequest, OfferResponse
from app.services.member_store import member_store
from app.services.orchestrator import orchestrator
from app.services.user_store import InvalidCredentialsError, UserAlreadyExistsError, user_store

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["health"])
def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(status="ok", service=settings.app_name, environment=settings.environment)


@router.post("/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED, tags=["auth"])
def register(request: RegisterRequest) -> TokenResponse:
    settings = get_settings()
    if settings.auth_mode != "demo_jwt":
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Registration is managed by the configured OAuth/OIDC identity provider in production mode.",
        )
    try:
        user = user_store.create_user(username=request.username, password=request.password)
    except UserAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    token = create_access_token(user.username)
    return TokenResponse(
        access_token=token,
        expires_in_seconds=settings.jwt_access_token_minutes * 60,
        username=user.username,
    )


@router.post("/auth/login", response_model=TokenResponse, tags=["auth"])
def login(request: LoginRequest) -> TokenResponse:
    settings = get_settings()
    if settings.auth_mode != "demo_jwt":
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="External OAuth/OIDC login is configured at the identity provider layer. Use a provider-issued JWT.",
        )
    try:
        user = user_store.authenticate(username=request.username, password=request.password)
    except InvalidCredentialsError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    token = create_access_token(user.username)
    return TokenResponse(
        access_token=token,
        expires_in_seconds=settings.jwt_access_token_minutes * 60,
        username=user.username,
    )


@router.get("/auth/me", response_model=UserResponse, tags=["auth"])
def read_current_user(
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> UserResponse:
    return UserResponse(
        username=current_user.username,
        auth_provider=current_user.auth_provider,
        role=current_user.role,
    )


@router.post("/offers", response_model=OfferResponse, tags=["offers"])
async def create_offer(
    request: OfferRequest,
    _: AuthenticatedUser = Depends(get_current_user),
) -> OfferResponse:
    return await orchestrator.generate_offer(request)


@router.get("/members/{member_id}/transactions", response_model=MemberHistoryResponse, tags=["members"])
def get_member_transactions(
    member_id: str,
    _: AuthenticatedUser = Depends(get_current_user),
) -> MemberHistoryResponse:
    transactions = member_store.list_transactions(member_id)
    if not transactions:
        raise HTTPException(status_code=404, detail="No transactions found for member")
    return MemberHistoryResponse(member_id=member_id, transactions=transactions)
