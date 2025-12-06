from dataclasses import dataclass

from core.db.models import Phone, Address
from core.exceptions.service import ServiceAPIException, ServiceAPIResponseStatus
from core.exceptions.service.enum import ServiceAPIResponseMessage
from repositories.cache import CacheRepository
from repositories.help_desk import HelpDeskRepository


@dataclass
class HelpDeskService:
    cache_repository: CacheRepository
    help_desk_repository: HelpDeskRepository

    async def get_by_phone(self, phone: str) -> tuple[Phone, Address] | str:
        """
        Получить текущий адрес по телефону(основной сценарий).

        1) Сначала пытаемся прочитать из Redis.
        2) Если кэша нет — читаем из БД.
        3) При удачном чтении из БД — прогреваем кэш.
        """

        cached_address = await self.cache_repository.get_address(phone)
        if cached_address is not None:
            return cached_address

        result = await self.help_desk_repository.get_phone_with_latest_address_by_phone_or_address(
            phone=phone,
            address=None,
        )
        if result is None:
            raise ServiceAPIException(
                status=ServiceAPIResponseStatus.NOT_FOUND_DATA,
                message=ServiceAPIResponseMessage.NOT_FOUND_DATA,
                extra_data={"data_by_phone_not_found": phone},
            )

        phone_obj, address_obj = result

        # Прогрев кэша
        await self.cache_repository.create_or_update(phone=phone_obj.phone, address=address_obj.address, overwrite=True)

        return phone_obj, address_obj

    async def get_all(self) -> list[tuple[Phone, Address]]:
        """
        Получить список всех телефонов с их последним адресом.
        """
        rows = await self.help_desk_repository.get_all_with_latest_addresses()
        return rows

    async def search(
        self,
        *,
        phone: str | None = None,
        address: str | None = None,
    ) -> tuple[Phone, Address] | str:
        """
        Универсальный поиск:
        - если указан phone — используем get_by_phone (с кэшем);
        - иначе, если указан address — ищем в БД по адресу (ILIKE, partial);
        - если ничего не указано — ServiceAPIException(BAD_REQUEST).
        """

        if not phone and not address:
            raise ServiceAPIException(
                status=ServiceAPIResponseStatus.BAD_REQUEST,
                message=ServiceAPIResponseMessage.BAD_REQUEST,
                extra_data={"phone_must_be_provided_or_address": phone, "address_must_be_provided_or_phone": address},
            )

        if phone:
            return await self.get_by_phone(phone=phone)

        # address есть, phone нет идём сразу в БД
        assert address is not None

        result = await self.help_desk_repository.get_phone_with_latest_address_by_phone_or_address(
            phone=None,
            address=address,
            partial_address=True,
            case_insensitive_address=True,
        )
        if result is None:
            raise ServiceAPIException(
                status=ServiceAPIResponseStatus.NOT_FOUND_DATA,
                message=ServiceAPIResponseMessage.NOT_FOUND_DATA,
                extra_data={"data_by_address_not_found": address},
            )

        phone_obj, address_obj = result

        await self.cache_repository.create_or_update(phone=phone_obj.phone, address=address_obj.address, overwrite=True)

        return phone_obj, address_obj

    async def create(self, phone: str, address: str) -> tuple[Phone, Address]:
        """
        Создать новую связку телефон-адрес.

        Поведение:
        - если телефон уже существует (есть хотя бы один адрес) → ServiceAPIException(CONFLICT_DATA);
        - если нет — создаём запись в БД и обновляем кэш.
        """

        existing = await self.help_desk_repository.get_phone_with_latest_address_by_phone_or_address(
            phone=phone,
            address=None,
        )
        if existing is not None:
            raise ServiceAPIException(
                status=ServiceAPIResponseStatus.CONFLICT_DATA,
                message=ServiceAPIResponseMessage.CONFLICT_DATA,
                extra_data={"phone_already_exists": phone},
            )

        # На всякий случай проверяем существование самой сущности телефона без адресов
        if await self.help_desk_repository.phone_exists(phone):
            raise ServiceAPIException(
                status=ServiceAPIResponseStatus.CONFLICT_DATA,
                message=ServiceAPIResponseMessage.CONFLICT_DATA,
                extra_data={"phone_already_exists": phone},
            )

        phone_obj, address_obj = await self.help_desk_repository.create_phone_with_address(phone=phone, address=address)

        await self.cache_repository.create_or_update(phone=phone_obj.phone, address=address_obj.address, overwrite=True)

        return phone_obj, address_obj

    async def update(self, phone: str, address: str) -> tuple[Phone, Address]:
        """
        Обновление адреса для существующего телефона.

        Реализация через добавление новой записи Address (история адресов сохраняется).
        """
        result = await self.help_desk_repository.get_phone_with_latest_address_by_phone_or_address(
            phone=phone,
            address=None,
        )
        if result is None:
            raise ServiceAPIException(
                status=ServiceAPIResponseStatus.NOT_FOUND_DATA,
                message=ServiceAPIResponseMessage.NOT_FOUND_DATA,
                extra_data={"data_by_phone_not_found": phone},
            )

        phone_obj, _ = result

        new_address_obj = await self.help_desk_repository.add_address_to_existing_phone(
            phone_obj=phone_obj,
            address=address,
        )

        await self.cache_repository.create_or_update(
            phone=phone_obj.phone,
            address=new_address_obj.address,
            overwrite=True,
        )

        return phone_obj, new_address_obj

    async def delete(self, phone: str) -> None:
        """
        Удаление телефона и всех его адресов.

        1) Удаляем из БД (CASCADE на addresses).
        2) Удаляем запись из Redis (если была).
        """
        deleted = await self.help_desk_repository.delete_by_phone(phone=phone)
        if not deleted:
            raise ServiceAPIException(
                status=ServiceAPIResponseMessage.NOT_FOUND_DATA,
                message=ServiceAPIResponseMessage.NOT_FOUND_DATA,
                extra_data={"data_by_phone_not_found": phone},
            )

        await self.cache_repository.delete_address(phone=phone)
