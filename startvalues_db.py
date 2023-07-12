from db.db_create import engine, db_session
from models.db_models import Products, Orders, ProductTransactions, ProductMenuCategories

from sqlalchemy import select, func

def add_menu_categories() -> None:
    category1 = ProductMenuCategories(name = "Coffees")
    category2 = ProductMenuCategories(name = "Drinks")
    category3 = ProductMenuCategories(name = "Pastries")
    category4 = ProductMenuCategories(name = "Other")

    with db_session() as session:
        session.add(category1)
        session.add(category2)
        session.add(category3)
        session.add(category4)

        session.commit()

def add_products() -> None:

    product1 = Products("Coffee", 5.0, "Regular Coffee. Just regular.", 1)
    product2 = Products("Americano", 5.0, "Regular Coffee. Almost like the other one.", 1)
    product3 = Products("Frappuccino", 10.0, "FROZEN. Great.", 1)
    product4 = Products("Cappuccino", 15.0, "Coffee with skimmed milk.", 1)
    product5 = Products("Mojito", 25.0, "SOUR.", 2)
    product6 = Products("Strawberry Daiquiry", 25.0, "Frozen Strawberry. Chill.", 2)
    product7 = Products("Gin & Tonic", 20.0, "Magic happens.", 2)
    product8 = Products("Croissant", 5.0, "Pastry", 3)
    product9 = Products("Chateau Briand", 50.0, "Smooth meat. Smooth.", 4)
    product10 = Products("Shish Kebap", 30.0, "Turkish.", 4)

    with db_session() as session:
        session.add(product1)
        session.add(product2)
        session.add(product3)
        session.add(product4)
        session.add(product5)
        session.add(product6)
        session.add(product7)
        session.add(product8)
        session.add(product9)
        session.add(product10)

        session.commit()


add_menu_categories()

add_products()