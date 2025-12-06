from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Index, String, Text

from core.db.mixins import TimestampMixin
from core.db.session import Base


class Phone(Base, TimestampMixin):
    __tablename__ = "phones"

    __table_args__ = (Index("uq_phones_phone", "phone", unique=True),)

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False, autoincrement=True)
    phone: Mapped[str] = mapped_column(String(32), nullable=False)

    addresses: Mapped[list["Address"]] = relationship(
        "Address",
        back_populates="phone",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __init__(self, phone: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.phone = phone


class Address(Base, TimestampMixin):
    __tablename__ = "addresses"

    __table_args__ = (Index("ix_addresses_phone_id", "phone_id"),)

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False, autoincrement=True)
    phone_id: Mapped[int] = mapped_column(ForeignKey("phones.id", ondelete="CASCADE"), nullable=False)
    address: Mapped[str] = mapped_column(Text, nullable=False)

    phone: Mapped["Phone"] = relationship("Phone", back_populates="addresses")

    def __init__(self, phone_id: int, address: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.phone_id = phone_id
        self.address = address
