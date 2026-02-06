"""
Authentication service for user registration, login, and token management.
"""

import time

from uuid import uuid4

from typing import Any

from datetime import datetime

from src.services.base import BaseService

from src.schemas.auth import LoginSchema
from src.schemas.users import UserReadSchema
from src.schemas.users import UserCreateSchema
from src.schemas.users import UserInternalSchema
from src.schemas.auth import TokenResponseSchema

from src.exceptions.service.auth import InvalidToken
from src.exceptions.service.users import UserNotFound
from src.exceptions.service.auth import InvalidTokenType
from src.exceptions.service.auth import InvalidCredentials
from src.exceptions.service.auth import LoginTemporarilyLocked
from src.exceptions.service.users import UserAlreadyExists
from src.exceptions.repository.users import UserNotFoundRepoException
from src.exceptions.repository.users import UserAlreadyExistsRepoException

from src.db.redis.broker import redis_client
from src.core.settings import settings
from src.core.observability.logging import logger

from src.security.exceptions.token import TokenError
from src.security.implementations.jwt_service import JWTTokenService
from src.security.implementations.bcrypt_hasher import BcryptPasswordHasher


class AuthService(BaseService):
    """
    Service for handling authentication operations.

    Attributes:
        token_service (JWTTokenService): Service for creating and verifying JWT tokens.
        password_hasher (BcryptPasswordHasher): Service for hashing and verifying passwords.
    """

    token_service = JWTTokenService()
    password_hasher = BcryptPasswordHasher()

    async def register(self, data: UserCreateSchema) -> TokenResponseSchema:
        """
        Register a new user and return tokens.

        :param data: UserCreateSchema object containing user email and password.
        :type data: UserCreateSchema
        :return: TokenResponseSchema containing access and refresh tokens.
        :rtype: TokenResponseSchema
        :raises UserAlreadyExists: If a user with the given email already exists.
        """
        normalized_email = data.email.lower()
        existing = await self.db.users.get_one_or_none(email=normalized_email)
        if existing:
            raise UserAlreadyExists("User with this email already exists")

        hashed_password = self.password_hasher.hash(data.password)
        user_data = UserCreateSchema(email=normalized_email, password=hashed_password) # noqa

        try:
            user = await self.db.users.add(user_data)
            await self.db.commit()
        except UserAlreadyExistsRepoException as ex:
            raise UserAlreadyExists.from_repo(ex)

        return await self._generate_tokens(user)

    async def login(
            self,
            credentials: LoginSchema,
            client_ip: str | None = None
    ) -> TokenResponseSchema:
        """
        Authenticate user and return tokens.

        :param credentials: LoginSchema containing email and password.
        :type credentials: LoginSchema
        :return: TokenResponseSchema containing access and refresh tokens.
        :rtype: TokenResponseSchema
        :raises InvalidCredentials: If the email does not exist or password is incorrect.
        """
        email = credentials.email.lower()
        ip = client_ip or "unknown"
        await self._ensure_login_not_locked(email=email, client_ip=ip)

        try:
            user = await self.db.users.get_one(email=email)
        except UserNotFoundRepoException:
            await self._track_failed_login(email=email, client_ip=ip)
            raise InvalidCredentials()

        if not self.password_hasher.verify(credentials.password, user.password): # noqa
            await self._track_failed_login(email=email, client_ip=ip)
            raise InvalidCredentials()

        await self._clear_failed_login_state(email=email, client_ip=ip)
        return await self._generate_tokens(user)

    async def refresh_access_token(self, refresh_token: str) -> TokenResponseSchema: # noqa
        """
        Generate a new access token using a refresh token.

        :param refresh_token: Refresh token string.
        :type refresh_token: str
        :return: TokenResponseSchema containing new access and refresh tokens.
        :rtype: TokenResponseSchema
        :raises InvalidToken: If the token is invalid or cannot be decoded.
        :raises InvalidTokenType: If the token type is not "refresh".
        :raises UserNotFound: If the user specified in the token does not exist.
        """
        try:
            payload = self.token_service.decode(refresh_token)
        except TokenError:
            raise InvalidToken()

        if payload.get("type") != "refresh":
            raise InvalidTokenType(expected="refresh", got=payload.get("type"))

        jti = payload.get("jti")
        if not jti or not isinstance(jti, str):
            raise InvalidToken("Invalid token payload")

        if await self._is_refresh_token_revoked_or_unknown(jti):
            raise InvalidToken("Refresh token has been revoked")

        user_id = payload.get("sub")
        if not user_id:
            raise InvalidToken("Invalid token payload")
        try:
            user_id = int(user_id)
        except (TypeError, ValueError):
            raise InvalidToken("Invalid token payload")

        try:
            user = await self.db.users.get_one(id=user_id)
        except UserNotFoundRepoException:
            raise UserNotFound("User not found")

        await self._revoke_refresh_token(jti, payload.get("exp"))
        return await self._generate_tokens(user)

    async def get_current_user(self, token: str) -> UserReadSchema:
        """
        Retrieve the current user from an access token.

        :param token: Access token string.
        :type token: str
        :return: UserReadSchema representing the current authenticated user.
        :rtype: UserReadSchema
        :raises InvalidToken: If the token is invalid or cannot be decoded.
        :raises InvalidTokenType: If the token type is not "access".
        :raises UserNotFound: If the user specified in the token does not exist.
        """
        try:
            payload = self.token_service.decode(token)
        except TokenError:
            raise InvalidToken()

        if payload.get("type") != "access":
            raise InvalidTokenType(expected="access", got=payload.get("type"))

        try:
            user_id = int(payload.get("sub"))
        except (ValueError, TypeError):
            raise InvalidToken("Invalid user id in token")

        try:
            user = await self.db.users.get_one(id=user_id)
        except UserNotFoundRepoException:
            raise UserNotFound("User not found")

        return user

    async def _generate_tokens(self, user: UserInternalSchema) -> TokenResponseSchema: # noqa
        """
        Generate access and refresh tokens for a user.

        :param user: UserInternalSchema object representing the user.
        :type user: UserInternalSchema
        :return: TokenResponseSchema containing access and refresh tokens.
        :rtype: TokenResponseSchema
        """
        token_data = {"sub": str(user.id), "email": user.email}

        access_token = self.token_service.create_access_token(data={**token_data}) # noqa
        refresh_jti = uuid4().hex
        refresh_token = self.token_service.create_refresh_token(
            data={**token_data, "jti": refresh_jti}
        )
        await self._store_active_refresh_jti(refresh_jti)

        return TokenResponseSchema(access_token=access_token, refresh_token=refresh_token) # noqa

    @staticmethod
    def _refresh_active_key(jti: str) -> str:
        """
         refresh active key.

        :param jti: TODO - describe jti.
        :type jti: str
        :return: TODO - describe return value.
        :rtype: str
        :raises Exception: If the operation fails.
        """
        return f"auth:refresh:active:{jti}"

    @staticmethod
    def _refresh_revoked_key(jti: str) -> str:
        """
         refresh revoked key.

        :param jti: TODO - describe jti.
        :type jti: str
        :return: TODO - describe return value.
        :rtype: str
        :raises Exception: If the operation fails.
        """
        return f"auth:refresh:revoked:{jti}"

    @staticmethod
    def _login_fail_key(scope: str, value: str) -> str:
        """
         login fail key.

        :param scope: TODO - describe scope.
        :type scope: str
        :param value: TODO - describe value.
        :type value: str
        :return: TODO - describe return value.
        :rtype: str
        :raises Exception: If the operation fails.
        """
        return f"auth:login:fail:{scope}:{value}"

    @staticmethod
    def _login_lock_key(scope: str, value: str) -> str:
        """
         login lock key.

        :param scope: TODO - describe scope.
        :type scope: str
        :param value: TODO - describe value.
        :type value: str
        :return: TODO - describe return value.
        :rtype: str
        :raises Exception: If the operation fails.
        """
        return f"auth:login:lock:{scope}:{value}"

    async def _store_active_refresh_jti(self, jti: str) -> None:
        """
         store active refresh jti.

        :param jti: TODO - describe jti.
        :type jti: str
        :return: None.
        :raises Exception: If the operation fails.
        """
        ttl_seconds = max(settings.jwt.refresh_token_expire_days * 24 * 60 * 60, 1) # noqa
        try:
            await redis_client.set(self._refresh_active_key(jti), "1", ex=ttl_seconds) # noqa
        except Exception as ex:
            logger.warning(f"Failed to store active refresh token JTI: {ex}")

    async def _is_refresh_token_revoked_or_unknown(self, jti: str) -> bool:
        """
         is refresh token revoked or unknown.

        :param jti: TODO - describe jti.
        :type jti: str
        :return: TODO - describe return value.
        :rtype: bool
        :raises Exception: If the operation fails.
        """
        try:
            is_revoked = await redis_client.get(self._refresh_revoked_key(jti))
            is_active = await redis_client.get(self._refresh_active_key(jti))
            return bool(is_revoked) or not bool(is_active)
        except Exception as ex:
            logger.warning(f"Failed to verify refresh token state in Redis: {ex}") # noqa
            return True

    async def _revoke_refresh_token(self, jti: str, exp: Any) -> None:
        """
         revoke refresh token.

        :param jti: TODO - describe jti.
        :type jti: str
        :param exp: TODO - describe exp.
        :type exp: Any
        :return: None.
        :raises Exception: If the operation fails.
        """
        try:
            await redis_client.delete(self._refresh_active_key(jti))
            ttl = self._ttl_from_exp(exp)
            if ttl > 0:
                await redis_client.set(self._refresh_revoked_key(jti), "1", ex=ttl) # noqa
        except Exception as ex:
            logger.warning(f"Failed to revoke refresh token in Redis: {ex}")

    @staticmethod
    def _ttl_from_exp(exp: Any) -> int:
        """
         ttl from exp.

        :param exp: TODO - describe exp.
        :type exp: Any
        :return: TODO - describe return value.
        :rtype: int
        :raises Exception: If the operation fails.
        """
        if isinstance(exp, datetime):
            exp_ts = int(exp.timestamp())
        else:
            try:
                exp_ts = int(exp)
            except (TypeError, ValueError):
                return 0
        return max(exp_ts - int(time.time()), 0)

    async def _ensure_login_not_locked(self, email: str, client_ip: str) -> None: # noqa
        """
         ensure login not locked.

        :param email: TODO - describe email.
        :type email: str
        :param client_ip: TODO - describe client_ip.
        :type client_ip: str
        :return: None.
        :raises LoginTemporarilyLocked: If the operation cannot be completed.
        """
        email_ttl = 0
        ip_ttl = 0
        try:
            email_ttl = int(await redis_client.ttl(self._login_lock_key("email", email)) or 0) # noqa
            ip_ttl = int(await redis_client.ttl(self._login_lock_key("ip", client_ip)) or 0) # noqa
        except Exception as ex:
            logger.warning(f"Login lock check skipped due to Redis error: {ex}") # noqa
            return

        retry_after = max(email_ttl, ip_ttl, 0)
        if retry_after > 0:
            raise LoginTemporarilyLocked(retry_after_seconds=retry_after)

    async def _track_failed_login(self, email: str, client_ip: str) -> None:
        """
         track failed login.

        :param email: TODO - describe email.
        :type email: str
        :param client_ip: TODO - describe client_ip.
        :type client_ip: str
        :return: None.
        :raises Exception: If the operation fails.
        """
        window = settings.auth_login_window_seconds
        limit = settings.auth_login_max_attempts
        lockout = settings.auth_login_lockout_seconds
        email_fail_key = self._login_fail_key("email", email)
        ip_fail_key = self._login_fail_key("ip", client_ip)
        email_lock_key = self._login_lock_key("email", email)
        ip_lock_key = self._login_lock_key("ip", client_ip)

        try:
            email_count = await redis_client.incr(email_fail_key)
            if email_count == 1:
                await redis_client.expire(email_fail_key, window)
            ip_count = await redis_client.incr(ip_fail_key)
            if ip_count == 1:
                await redis_client.expire(ip_fail_key, window)

            if int(email_count) >= limit:
                await redis_client.set(email_lock_key, "1", ex=lockout)
            if int(ip_count) >= limit:
                await redis_client.set(ip_lock_key, "1", ex=lockout)
        except Exception as ex:
            logger.warning(f"Failed to track login attempts in Redis: {ex}")

    async def _clear_failed_login_state(self, email: str, client_ip: str) -> None: # noqa
        """
         clear failed login state.

        :param email: TODO - describe email.
        :type email: str
        :param client_ip: TODO - describe client_ip.
        :type client_ip: str
        :return: None.
        :raises Exception: If the operation fails.
        """
        try:
            await redis_client.delete(
                self._login_fail_key("email", email),
                self._login_fail_key("ip", client_ip),
            )
        except Exception as ex:
            logger.warning(f"Failed to clear login failure counters: {ex}")
