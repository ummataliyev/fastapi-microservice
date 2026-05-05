"""
MongoDB repository for users.
"""

from typing import Any

from datetime import datetime
from datetime import timezone

from pymongo import ASCENDING
from pymongo import ReturnDocument
from pymongo.database import Database
from pymongo.errors import PyMongoError
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError

from src.schemas.users import UserCreateSchema
from src.schemas.users import UserUpdateSchema
from src.schemas.users import UserInternalSchema

from src.exceptions.repository.users import UserNotFoundRepoException
from src.exceptions.repository.base import CannotAddObjectRepoException
from src.exceptions.repository.base import CannotUpdateObjectRepoException
from src.exceptions.repository.base import CannotDeleteObjectRepoException
from src.exceptions.repository.users import UserAlreadyExistsRepoException
from src.exceptions.repository.base import InvalidRepositoryInputRepoException


class MongoUsersRepository:
    """
    Mongo implementation compatible with service expectations.
    """

    def __init__(self, database: Database):
        """
          init  .

        :param database: TODO - describe database.
        :type database: Database
        :return: None.
        :raises Exception: If the operation fails.
        """
        self.database = database
        self.collection: Collection = database["users"]
        self.counters: Collection = database["counters"]
        self._indexes_ready = False

    async def _ensure_indexes(self) -> None:
        """
         ensure indexes.

        :return: None.
        :raises Exception: If the operation fails.
        """
        if self._indexes_ready:
            return
        await self.collection.create_index([("email", ASCENDING)], unique=True)
        await self.collection.create_index([("deleted_at", ASCENDING)])
        self._indexes_ready = True

    async def _next_id(self) -> int:
        """
         next id.

        :return: TODO - describe return value.
        :rtype: int
        :raises Exception: If the operation fails.
        """
        counter = await self.counters.find_one_and_update(
            {"_id": "users_id"},
            {"$inc": {"seq": 1}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        return int(counter["seq"])

    @staticmethod
    def _to_schema(doc: dict[str, Any]) -> UserInternalSchema:
        """
         to schema.

        :param doc: TODO - describe doc.
        :type doc: dict[str, Any]
        :return: TODO - describe return value.
        :rtype: UserInternalSchema
        :raises Exception: If the operation fails.
        """
        normalized = {
            "id": int(doc["id"]),
            "email": doc["email"],
            "password": doc["password"],
            "created_at": doc["created_at"],
            "updated_at": doc["updated_at"],
        }
        return UserInternalSchema.model_validate(normalized)

    async def get_one(self, **filter_by) -> UserInternalSchema:
        """
        Get one.

        :param filter_by: TODO - describe filter_by.
        :return: TODO - describe return value.
        :rtype: UserInternalSchema
        :raises UserNotFoundRepoException: If the operation cannot be completed.
        """
        self._validate_filter_fields(filter_by)
        doc = await self.collection.find_one({**filter_by, "deleted_at": None})
        if not doc:
            raise UserNotFoundRepoException
        return self._to_schema(doc)

    async def get_one_or_none(self, **filter_by) -> UserInternalSchema | None:
        """
        Get one or none.

        :param filter_by: TODO - describe filter_by.
        :return: TODO - describe return value.
        :rtype: UserInternalSchema | None
        :raises Exception: If the operation fails.
        """
        self._validate_filter_fields(filter_by)
        doc = await self.collection.find_one({**filter_by, "deleted_at": None})
        if not doc:
            return None
        return self._to_schema(doc)

    async def get_all(
            self,
            limit: int = 10,
            offset: int = 0,
            **filter_by
    ) -> list[UserInternalSchema]:
        """
        Get all.

        :param limit: TODO - describe limit.
        :type limit: int
        :param offset: TODO - describe offset.
        :type offset: int
        :param filter_by: TODO - describe filter_by.
        :return: TODO - describe return value.
        :rtype: list[UserInternalSchema]
        :raises InvalidRepositoryInputRepoException: If the operation cannot be completed.
        """
        if limit < 0 or offset < 0:
            raise InvalidRepositoryInputRepoException("Limit and offset must be non-negative.")
        self._validate_filter_fields(filter_by)
        cursor = (
            self.collection.find({**filter_by, "deleted_at": None})
            .skip(offset)
            .limit(limit)
        )
        docs = await cursor.to_list(length=limit)
        return [self._to_schema(doc) for doc in docs]

    async def count(self, filters: dict | None = None) -> int:
        """
        Count.

        :param filters: TODO - describe filters.
        :type filters: dict | None
        :return: TODO - describe return value.
        :rtype: int
        :raises Exception: If the operation fails.
        """
        query = {"deleted_at": None}
        if filters:
            self._validate_filter_fields(filters)
            query.update(filters)
        return int(await self.collection.count_documents(query))

    async def add(self, data: UserCreateSchema) -> UserInternalSchema:
        """
        Add.

        :param data: TODO - describe data.
        :type data: UserCreateSchema
        :return: TODO - describe return value.
        :rtype: UserInternalSchema
        :raises UserAlreadyExistsRepoException: If the operation cannot be completed.
        :raises CannotAddObjectRepoException: If the operation cannot be completed.
        """
        await self._ensure_indexes()
        now = datetime.now(timezone.utc)
        payload = {
            "id": await self._next_id(),
            "email": data.email,
            "password": data.password,
            "created_at": now,
            "updated_at": now,
            "deleted_at": None,
        }
        try:
            await self.collection.insert_one(payload)
        except DuplicateKeyError as ex:
            raise UserAlreadyExistsRepoException from ex
        except PyMongoError as ex:
            raise CannotAddObjectRepoException from ex
        return self._to_schema(payload)

    async def update_one(self, data: UserUpdateSchema, partially: bool = False, **filter_by) -> UserInternalSchema:
        """
        Update one.

        :param data: TODO - describe data.
        :type data: UserUpdateSchema
        :param partially: TODO - describe partially.
        :type partially: bool
        :param filter_by: TODO - describe filter_by.
        :return: TODO - describe return value.
        :rtype: UserInternalSchema
        :raises InvalidRepositoryInputRepoException: If the operation cannot be completed.
        :raises UserAlreadyExistsRepoException: If the operation cannot be completed.
        :raises CannotUpdateObjectRepoException: If the operation cannot be completed.
        :raises UserNotFoundRepoException: If the operation cannot be completed.
        """
        self._validate_filter_fields(filter_by)
        update_payload = data.model_dump(exclude_unset=partially, exclude_none=True)
        if not update_payload:
            raise InvalidRepositoryInputRepoException("No fields provided for update.")
        update_payload["updated_at"] = datetime.now(timezone.utc)
        try:
            updated = await self.collection.find_one_and_update(
                {**filter_by, "deleted_at": None},
                {"$set": update_payload},
                return_document=ReturnDocument.AFTER,
            )
        except DuplicateKeyError as ex:
            raise UserAlreadyExistsRepoException from ex
        except PyMongoError as ex:
            raise CannotUpdateObjectRepoException from ex
        if not updated:
            raise UserNotFoundRepoException
        return self._to_schema(updated)

    async def delete_one(self, **filter_by) -> UserInternalSchema:
        """
        Delete one.

        :param filter_by: TODO - describe filter_by.
        :return: TODO - describe return value.
        :rtype: UserInternalSchema
        :raises CannotDeleteObjectRepoException: If the operation cannot be completed.
        :raises UserNotFoundRepoException: If the operation cannot be completed.
        """
        self._validate_filter_fields(filter_by)
        now = datetime.now(timezone.utc)
        try:
            updated = await self.collection.find_one_and_update(
                {**filter_by, "deleted_at": None},
                {"$set": {"deleted_at": now, "updated_at": now}},
                return_document=ReturnDocument.AFTER,
            )
        except PyMongoError as ex:
            raise CannotDeleteObjectRepoException from ex
        if not updated:
            raise UserNotFoundRepoException
        return self._to_schema(updated)

    async def restore_one(self, **filter_by) -> UserInternalSchema:
        """
        Restore one.

        :param filter_by: TODO - describe filter_by.
        :return: TODO - describe return value.
        :rtype: UserInternalSchema
        :raises UserNotFoundRepoException: If the operation cannot be completed.
        """
        self._validate_filter_fields(filter_by)
        updated = await self.collection.find_one_and_update(
            {**filter_by, "deleted_at": {"$ne": None}},
            {"$set": {"deleted_at": None, "updated_at": datetime.now(timezone.utc)}},
            return_document=ReturnDocument.AFTER,
        )
        if not updated:
            raise UserNotFoundRepoException
        return self._to_schema(updated)

    @staticmethod
    def _validate_filter_fields(filters: dict[str, Any]) -> None:
        """
         validate filter fields.

        :param filters: TODO - describe filters.
        :type filters: dict[str, Any]
        :return: None.
        :raises InvalidRepositoryInputRepoException: If the operation cannot be completed.
        """
        allowed = {"id", "email", "deleted_at", "created_at", "updated_at"}
        for field in filters:
            if field not in allowed:
                raise InvalidRepositoryInputRepoException(f"Unknown filter field: {field}") # noqa
