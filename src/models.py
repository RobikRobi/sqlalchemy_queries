from .db import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

class User(Base):
 __tablename__ = "users"

 id:Mapped[int] = mapped_column(primary_key=True)

 username:Mapped[str]
 password:Mapped[str]
 age:Mapped[int]

 products:Mapped[list["Products"]] = relationship(uselist=True, back_populates="user")


class Products(Base):
 __tablename__ = "products"
 id:Mapped[int] = mapped_column(primary_key=True)
 name:Mapped[str]
 price:Mapped[float] # 120.4
 user_id:Mapped[int] = mapped_column(ForeignKey("users.id"), unique= False)

 user:Mapped["User"] = relationship(uselist=False,back_populates="products")