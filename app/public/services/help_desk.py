from dataclasses import dataclass

from api.public.v1.response.help_desk import HelpDeskResponseSchema, DeleteHelpDeskResponseSchema
from core.exceptions.service import ServiceAPIException, ServiceAPIResponseStatus
from core.exceptions.service.enum import ServiceAPIResponseMessage
from repositories.cache import CacheRepository
from repositories.help_desk import HelpDeskRepository


@dataclass
class HelpDeskService:
    cache_repository: CacheRepository
    help_desk_repository: HelpDeskRepository

    async def get_all_contacts(self) -> list[HelpDeskResponseSchema]:
        """
        Получить список всех телефонов с их последним адресом.
        """
        rows = await self.help_desk_repository.get_all_with_latest_addresses()
        return [
            HelpDeskResponseSchema(
                phone=phone_obj.phone,
                address=address_obj.address
            ) for phone_obj, address_obj in rows]

    async def filter_contact_by_phone_or_address(
            self,
            *,
            phone: str | None = None,
            address: str | None = None,
    ) -> HelpDeskResponseSchema:
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
            return await self._get_by_phone(phone=phone)

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

        return HelpDeskResponseSchema(phone=phone_obj.phone, address=address_obj.address)

    async def create_contact(self, phone: str, address: str) -> HelpDeskResponseSchema:
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

        return HelpDeskResponseSchema(phone=phone_obj.phone, address=address_obj.address)

    async def update_contact_by_address_id(
            self,
            address_id: int,
            phone: str | None,
            address: str | None
    ) -> HelpDeskResponseSchema:
        """
        Обновление контакта по id записи Address.

        Можно обновить:
        — phone,
        — address,
        — или оба поля.
        """

        if phone is None and address is None:
            raise ServiceAPIException(
                status=ServiceAPIResponseStatus.BAD_REQUEST,
                message=ServiceAPIResponseMessage.BAD_REQUEST,
                extra_data={"detail": "phone or address must be provided"},
            )

        result = await self.help_desk_repository.update_contact_by_address_id(
            address_id=address_id,
            phone=phone,
            address=address
        )
        if result is None:
            raise ServiceAPIException(
                status=ServiceAPIResponseStatus.NOT_FOUND_DATA,
                message=ServiceAPIResponseMessage.NOT_FOUND_DATA,
                extra_data={"contact_id_not_found": address_id},
            )

        phone_obj, address_obj, old_phone = result

        if phone is not None and phone != old_phone:
            await self.cache_repository.delete_address_by_phone(phone=old_phone)

        await self.cache_repository.create_or_update(
            phone=phone_obj.phone,
            address=address_obj.address,
            overwrite=True,
        )

        return HelpDeskResponseSchema(
            phone=phone_obj.phone,
            address=address_obj.address
        )

    async def delete_by_phone(self, phone: str) -> DeleteHelpDeskResponseSchema:
        """
        Удаление телефона и всех его адресов.

        1) Удаляем из БД (CASCADE на addresses).
        2) Удаляем запись из Redis (если была).
        """
        deleted_id = await self.help_desk_repository.delete_by_phone(phone=phone)
        if not deleted_id:
            raise ServiceAPIException(
                status=ServiceAPIResponseStatus.NOT_FOUND_DATA,
                message=ServiceAPIResponseMessage.NOT_FOUND_DATA,
                extra_data={"data_by_phone_not_found": phone},
            )

        await self.cache_repository.delete_address_by_phone(phone=phone)
        return DeleteHelpDeskResponseSchema(
            delete_contact_id=deleted_id
        )

    async def _get_by_phone(self, phone: str) -> HelpDeskResponseSchema:
        """
        Получить текущий адрес по телефону(основной сценарий).

        1) Сначала пытаемся прочитать из Redis.
        2) Если кэша нет — читаем из БД.
        3) При удачном чтении из БД — прогреваем кэш.
        """

        cached_address = await self.cache_repository.get_address(phone)
        if cached_address is not None:
            return HelpDeskResponseSchema(phone=phone, address=cached_address)

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

        return HelpDeskResponseSchema(phone=phone_obj.phone, address=address_obj.address)
