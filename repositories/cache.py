from core.cache.pool import get_redis_pool as redis


class CacheRepository:
    _KEY_PREFIX = "helpdesk:phone:"

    @classmethod
    def _make_key(cls, phone: str) -> str:
        # TODO: вынести нормализацию номера?
        normalized = phone.strip()
        return f"{cls._KEY_PREFIX}{normalized}"

    @classmethod
    async def get_address(cls, phone: str) -> str | None:
        key = cls._make_key(phone)
        value = await redis().get(key)
        if value is None:
            return None

        if isinstance(value, bytes):
            value = value.decode("utf-8")

        return value

    @classmethod
    async def create_or_update(
        cls,
        phone: str,
        address: str,
        *,
        ttl: int | None = None,
        overwrite: bool = False,
    ) -> bool:
        """
        Создаёт/обновляет запись в Redis.

        :param phone: номер телефона
        :param address: адрес
        :param ttl: время жизни ключа в секундах (опционально)
        :param overwrite: если False — не перезаписывать существующий ключ
        :return: True, если запись создана/перезаписана, False — если не создали из-за overwrite=False и ключ уже был
        """

        key = cls._make_key(phone)
        if not overwrite:
            if ttl is not None:
                result = await redis().set(key, address, ex=ttl, nx=True)
            else:
                result = await redis().set(key, address, nx=True)
            return bool(result)

        if ttl is not None:
            await redis().set(key, address, ex=ttl)
        else:
            await redis().set(key, address)
        return True

    @classmethod
    async def delete_address(cls, phone: str) -> bool:
        """
        Удаляет запись из Redis.

        :return: True, если ключ был и удалён, False — если ключа не было.
        """
        key = cls._make_key(phone)
        deleted = await redis().delete(key)
        return deleted > 0

    @classmethod
    async def ping(cls):
        await redis().ping()
