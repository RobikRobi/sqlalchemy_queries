from fastapi import FastAPI
from fastapi import Depends
from binascii import Error
from sqlalchemy import delete
from sqlalchemy.orm import Session
from src.db import engine, Base, get_session
from src.models import User, Products
from src.router import app as app_router


app = FastAPI()

app.include_router(app_router)

@app.get("/init")
def create_db(session: Session = Depends(get_session)):
    try:
        Base.metadata.drop_all(bind=engine)
    except Exception as e:
        print(e)
    Base.metadata.create_all(bind=engine)
    return {"msg": "db creat! =)"}


@app.post("/seed")
def seed(session: Session = Depends(get_session)):

    # Чтобы можно было запускать endpoint несколько раз
    session.execute(delete(Products))
    session.execute(delete(User))

    users = [
        User(username="denis", password="123", age=17),
        User(username="alex", password="123", age=25),
        User(username="anna", password="123", age=19),
        User(username="max", password="123", age=16),
        User(username="kate", password="123", age=31),
        User(username="ivan", password="123", age=22),
    ]

    session.add_all(users)

    # Получаем ID пользователей
    session.flush()

    products = [
        # Denis: 3 товара, сумма 15550
        Products(
            name="Mouse",
            price=550,
            user_id=users[0].id
        ),
        Products(
            name="Keyboard",
            price=5000,
            user_id=users[0].id
        ),
        Products(
            name="Monitor",
            price=10000,
            user_id=users[0].id
        ),

        # Alex: 2 дорогих товара
        Products(
            name="Laptop",
            price=90000,
            user_id=users[1].id
        ),
        Products(
            name="Headphones",
            price=7000,
            user_id=users[1].id
        ),

        # Anna: 1 товар
        Products(
            name="Book",
            price=800,
            user_id=users[2].id
        ),

        # Max: очень дешёвые товары
        Products(
            name="Pen",
            price=50,
            user_id=users[3].id
        ),
        Products(
            name="Notebook",
            price=90,
            user_id=users[3].id
        ),

        # Kate: 2 товара
        Products(
            name="Phone",
            price=50000,
            user_id=users[4].id
        ),
        Products(
            name="Charger",
            price=1500,
            user_id=users[4].id
        ),

        # Ivan специально без товаров
    ]

    session.add_all(products)

    session.commit()

    return {
        "message": "Seed completed",
        "users": len(users),
        "products": len(products)
    }