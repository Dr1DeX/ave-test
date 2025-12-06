from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select, func, delete

from core.db.models import Phone, Address


@dataclass
class HelpDeskRepository:
    _session: AsyncSession

    async def get_phone_with_latest_address_by_phone_or_address(
        self,
        *,
        phone: str | None = None,
        address: str | None = None,
        partial_address: bool = True,
        case_insensitive_address: bool = True,
    ) -> tuple[Phone, Address] | None:
        """
        Универсальный поиск:
        1) Если указан phone - ищем через get_phone_with_latest_address_by_phone.
        2) Иначе, если указан address - ищем через get_phone_with_latest_address_by_address.
        3) Если не указано ничего - возвращаем None (решение об ошибке — на уровне сервиса).
        """

        if phone:
            result = await self._get_phone_with_latest_address_by_phone(phone)
            if result is not None:
                return result
            if not address:
                return None

        if address:
            return await self._get_phone_with_latest_address_by_address(
                address=address,
                partial=partial_address,
                case_insensitive=case_insensitive_address,
            )

        return None

    async def get_all_with_latest_addresses(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> list[tuple[Phone, Address]]:
        """
        Вернуть все телефоны с их последним (по created_at) адресом.

        Используем подзапрос по max(created_at) на phone_id.
        """
        latest_subq = (
            select(
                Address.phone_id.label("phone_id"),
                func.max(Address.created_at).label("max_created_at"),
            )
            .group_by(Address.phone_id)
            .subquery()
        )

        stmt = (
            select(Phone, Address)
            .join(Address, Address.phone_id == Phone.id)
            .join(
                latest_subq,
                (Address.phone_id == latest_subq.c.phone_id) & (Address.created_at == latest_subq.c.max_created_at),
            )
            .order_by(Phone.phone)
            .offset(offset)
            .limit(limit)
        )

        result = await self._session.execute(stmt)
        rows = result.all()  # list[Row[(Phone, Address)]]

        return [(row[0], row[1]) for row in rows]

    async def phone_exists(self, phone: str) -> bool:
        stmt = select(func.count(Phone.id)).where(Phone.phone == phone)
        result = await self._session.execute(stmt)
        return result.scalar_one() > 0

    async def create_phone_with_address(
        self,
        phone: str,
        address: str,
    ) -> tuple[Phone, Address]:
        phone_obj = Phone(phone=phone)
        self._session.add(phone_obj)
        await self._session.flush()  # получаем phone_obj.id

        address_obj = Address(phone_id=phone_obj.id, address=address)
        self._session.add(address_obj)
        await self._session.commit()
        return phone_obj, address_obj

    async def add_address_to_existing_phone(
        self,
        phone_obj: Phone,
        address: str,
    ) -> Address:
        address_obj = Address(phone_id=phone_obj.id, address=address)
        self._session.add(address_obj)
        await self._session.commit()
        return address_obj

    async def delete_by_phone(self, phone: str) -> bool:
        stmt = delete(Phone).where(Phone.phone == phone).returning(Phone.id)
        result = await self._session.execute(stmt)
        deleted_id = result.scalar_one_or_none()
        await self._session.commit()
        return deleted_id is not None

    async def _get_phone_with_latest_address_by_phone(
        self,
        phone: str,
        limit: int = 10,
    ) -> tuple[Phone, Address] | None:
        """
        Поиск по телефону: возвращает телефон и его последний (по created_at) адрес.
        """
        stmt = (
            select(Phone, Address)
            .join(Address, Address.phone_id == Phone.id)
            .where(Phone.phone == phone)
            .order_by(Address.created_at.desc())
            .limit(limit)
        )

        result = await self._session.execute(stmt)
        row = result.first()
        if row is None:
            return None

        phone_obj, address_obj = row
        return phone_obj, address_obj

    async def _get_phone_with_latest_address_by_address(
        self,
        address: str,
        *,
        partial: bool = True,
        case_insensitive: bool = True,
        limit: int = 10,
    ) -> tuple[Phone, Address] | None:
        """
        Поиск телефона и последнего адреса по значению address.

        partial=True - поиск по подстроке ('%address%')
        case_insensitive=True - ILIKE, иначе LIKE
        Если один адрес привязан к нескольким телефонам, берём
        последний по времени created_at Address.
        """
        cond = Address.address
        pattern = address

        if partial:
            pattern = f"%{address}%"

        if case_insensitive:
            cond = cond.ilike(pattern)
        else:
            cond = cond.like(pattern)

        stmt = (
            select(Phone, Address)
            .join(Address, Address.phone_id == Phone.id)
            .where(cond)
            .order_by(Address.created_at.desc())
            .limit(limit)
        )

        result = await self._session.execute(stmt)
        row = result.first()
        if row is None:
            return None

        phone_obj, address_obj = row
        return phone_obj, address_obj
