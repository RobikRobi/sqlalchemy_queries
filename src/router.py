from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func, cast, Numeric, update, delete
from sqlalchemy.future import select
from src.models import User, Products
from src.db import get_session


app = APIRouter(prefix="/tasks", tags=["Tasks"])

# Получить всех пользователей старше 18 лет
@app.get("/users/adults")
def get_adults(session: Session = Depends(get_session)):
    stmt = select(User).where(User.age > 18)
    users = session.scalars(stmt).all()
    return [
        {"id": u.id, "username": u.username, "age": u.age}
        for u in users
    ]
# Получить всех пользователей, отсортированных по возрасту от старшего к младшему
@app.get("/users/sorted")
def get_users_sorted(session: Session = Depends(get_session)):
    stmt = select(User).order_by(User.age.desc())
    users = session.scalars(stmt).all()
    return [
        {"id": u.id, "username": u.username, "age": u.age}
        for u in users
    ]

# Получить только username всех пользователей
@app.get("/users/username")
def get_username(session: Session = Depends(get_session)):
    stmt = select(User.username)
    usersname = session.scalars(stmt).all()
    return usersname

# Найти пользователя с username == "denis"
@app.get("/users/denis")
def get_denis_name(session: Session = Depends(get_session)):
    stmt = select(User).where(User.username == "denis")
    name = session.scalar(stmt)
    if name is None:
        raise HTTPException(status_code=404, detail="User not found")
    return name

# Получить все товары дороже 1000
@app.get("/products/1000")
def get_product_1000(session: Session = Depends(get_session)):
    stmt = select(Products).where(Products.price > 1000)
    products = session.scalars(stmt).all()
    return [
        {"id": p.id, "name": p.name, "price": p.price}
        for p in products
    ]

# Получить все товары конкретного пользователя с user_id = 1
@app.get("/products/user_1")
def get_products_user_1(session: Session = Depends(get_session)):
    stmt = select(Products).where(Products.user_id == 1)
    products = session.scalars(stmt).all()
    return [
        {"id": p.id, "name": p.name, "price": p.price, "user_id": p.user_id}
        for p in products
    ]

# Получить всех пользователей, у которых есть хотя бы один товар
@app.get("/products/user_one_product")
def get_user_one_product(session:Session = Depends(get_session)):
    stmt = select(User).where(User.products.any())
    users = session.scalars(stmt).all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "age": u.age,
            "products": [
                {"id": p.id, "name": p.name, "price": p.price}
                for p in u.products
            ],
        }
        for u in users
    ]

# Получить всех пользователей, у которых есть хотя бы один товар дороже 5000
@app.get("/users/with-expensive-products")
def get_users_with_expensive_products(session: Session = Depends(get_session)):
    stmt = select(User).where(User.products.any(Products.price > 5000))
    users = session.scalars(stmt).all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "age": u.age,
            "products": [
                {"id": p.id, "name": p.name, "price": p.price}
                for p in u.products
            ],
        }
        for u in users
    ]

# Получить пользователей вместе с их товарами через selectinload
@app.get("/users/user-and-products")
def get_users_and_products(session: Session = Depends(get_session)):
    stmt = select(User).options(selectinload(User.products))
    users = session.scalars(stmt).all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "age": u.age,
            "products": [
                {"id": p.id, "name": p.name, "price": p.price}
                for p in u.products
            ],
        }
        for u in users
    ]

# Получить пары: username | product_name | price
@app.get("/users/products-pairs")
def get_users_products_pairs(session: Session = Depends(get_session)):
    stmt = (
        select(User.username, Products.name, Products.price)
        .join(Products, Products.user_id == User.id)
        .order_by(User.username, Products.name)
    )
    rows = session.execute(stmt).all()
    return [
        {"username": row.username, "product_name": row.name, "price": row.price}
        for row in rows
    ]

######################### через .options(selectinload(...)) ########################################

# Найти пользователя, у которого нет ни одного товара
@app.get("/users/without-products")
def get_users_without_products(session: Session = Depends(get_session)):
    stmt = select(User).where(User.products.any()).options(selectinload(User.products))
    users = session.scalars(stmt).all()
    return [
        {"id": u.id, "username": u.username, "age": u.age}
        for u in users
    ]

# Посчитать количество всех пользователей
@app.get("/users/count")
def count_users(session: Session = Depends(get_session)):
    total = session.scalar(select(func.count()).select_from(User))
    return {"total_users": total}

# Посчитать количество товаров у каждого пользователя
@app.get("/users/count-products")
def count_users_products(session: Session = Depends(get_session)):
    stmt = select(User).options(selectinload(User.products))
    users = session.scalars(stmt).all()
    return [
        {"username": u.username, "products_count": len(u.products)}
        for u in users
    ]

# Получить пользователей, у которых больше 1 товара
@app.get("/users/with-multiple-products")
def get_users_with_multiple_products(session: Session = Depends(get_session)):
    stmt = (
            select(User)
            .join(Products, Products.user_id == User.id)
            .group_by(User.id)
            .having(func.count(Products.id) > 1)
            .options(selectinload(User.products))
    )
    users = session.scalars(stmt).all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "products_count": len(u.products),
            "products": [
                {"id": p.id, "name": p.name, "price": p.price}
                for p in u.products
            ],
        }
        for u in users
    ]
# Найти самый дорогой товар
@app.get("/products/max-price")
def get_max_price_product(session: Session = Depends(get_session)):
    stmt = select(Products).order_by(Products.price.desc()).limit(1)
    product = session.scalars(stmt).first()
    if product is None:
        return {"message": "No products found"}
    return {
        "id": product.id,
        "name": product.name,
        "price": product.price,
        "user_id": product.user_id,
    }

# Найти среднюю цену всех товаров
@app.get("/products/avg-price")
def get_avg_price(session: Session = Depends(get_session)):
    stmt = select(
        func.round(cast(func.avg(Products.price), Numeric), 2)
    )
    avg_price = session.scalar(stmt)
    return {"avg_price": avg_price}

# Найти среднюю цену товаров для каждого пользователя
@app.get("/users/avg-price")
def get_avg_price_per_user(session: Session = Depends(get_session)):
    stmt = (
        select(
            User.id,
            User.username,
            func.avg(Products.price).label("avg_price"),
        )
        .join(Products, Products.user_id == User.id)
        .group_by(User.id, User.username)
        .order_by(User.username)
    )
    rows = session.execute(stmt).all()
    return [
        {
            "id": r.id,
            "username": r.username,
            "avg_price": round(float(r.avg_price), 2),
        }
        for r in rows
    ]

# Увеличить возраст всех пользователей младше 18 лет на 1
@app.patch("/users/increment-minors-age")
def increment_minors_age(session: Session = Depends(get_session)):
    stmt = (
        update(User)
        .where(User.age < 18)
        .values(age=User.age + 1)
    )
    result = session.execute(stmt)
    session.commit()
    return {"updated": result.rowcount}

# Увеличить цену всех товаров дешевле 1000 на 10%
@app.patch("/products/increase-cheap-prices")
def increase_cheap_prices(session: Session = Depends(get_session)):
    stmt = (
        update(Products)
        .where(Products.price < 1000)
        .values(price=Products.price * 1.1)
    )
    result = session.execute(stmt)
    session.commit()
    return {"updated": result.rowcount}

# Удалить все товары дешевле 100
@app.delete("/products/cheap")
def delete_cheap_products(session: Session = Depends(get_session)):
    stmt = delete(Products).where(Products.price < 100)
    result = session.execute(stmt)
    session.commit()
    return {"deleted": result.rowcount}