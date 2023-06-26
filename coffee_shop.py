from db.db_create import engine, db_session
from rich import print as rprint
from rich.table import Table,Column
from rich.console import Console
from os import system
from models.db_models import Products, Orders, ProductTransactions
from sqlalchemy import select, func
import os

console = Console()

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    from models.db_models import Base
    
    Base.metadata.create_all(bind=engine)


def get_menu_response():

    response = int(input("What do you want to do? ---> "))

    return response


def main_menu():

    run_main_menu = True

    while run_main_menu == True:
        
        table = Table(title="Main menu")
        table.add_column("#", justify="right", style="cyan")
        table.add_column("Description", style="magenta")

        table.add_row("1", "See Coffee-Shop menu")
        table.add_row("2", "")
        table.add_row("3", "List my orders")
        table.add_row("4", "")
        table.add_row("5", "Play Snake")
        table.add_row("6", "")
        table.add_row("7", "")
        table.add_row("8", "Admin menu")
        table.add_row("9", "Exit program")

        console.print(table)

        choice_main_menu = get_menu_response()

        if choice_main_menu == 9:
            run_main_menu = False
            exit()
        elif choice_main_menu == 1:
            run_main_menu = False
            product_menu()
        elif choice_main_menu == 3:
            print_orders_with_spec(input("What's your name? ---> "))
        elif choice_main_menu == 5:
            import snake
        elif choice_main_menu == 8:
            main_admin_menu()
        else:
            print("Wrong option, choose again")


def main_admin_menu():

    run_menu = True

    while run_menu == True:
        
        table = Table(title="Admin Menu")
        table.add_column("#", justify="right", style="cyan")
        table.add_column("Description", style="magenta")

        table.add_row("1", "List products")
        table.add_row("2", "Add products")
        table.add_row("3", "Edit products")
        table.add_row("4", "Delete products")
        table.add_row("5", "List orders")
        table.add_row("8", "Main menu")
        table.add_row("9", "Exit program")

        console.print(table)

        choice_main_menu = get_menu_response()

        if choice_main_menu == 9:
            run_menu = False
            exit()
        elif choice_main_menu == 1:
            print_products()
        elif choice_main_menu == 2:
            add_product()
        elif choice_main_menu == 3:
            edit_product(choose_product("edit"))
        elif choice_main_menu == 4:
            delete_product(choose_product("delete"))
        elif choice_main_menu == 5:
            print_orders_with_spec(None)
        elif choice_main_menu == 8:
            main_menu()
        else:
            print("Wrong option, choose again")
        

def product_menu():

    os.system('clear')

    run_menu = True

    while run_menu == True:
        with db_session() as session:
            products = db_session.scalars(select(Products))

            table = Table(title = "Coffee-shop menu")

            table.add_column("#")
            table.add_column("Product")
            table.add_column("Price", justify="right", style = "cyan")
            table.add_column("Description", style="magenta")

            for product in products:
                table.add_row(str(product.id), product.name, str(product.price), product.description)
        
        console.print(table)

        print("You can now order (1) or go back to main menu (2)")

        user_choice = get_menu_response()

        if user_choice == 1:
            new_order()
        elif user_choice == 2:
            run_menu = False
            main_menu()


def new_order():
    client_name = input("What's your name? ---> ")

    order = Orders(order_client=client_name) #Create new order
    with db_session() as session:
        session.add(order)
        session.flush()
        order_id = order.id
        order_client = order.order_client
        session.commit()

    add_order_line(order_id, order_client)

    more_products = True
    while more_products == True:
        if input(f"{order_client}, do you want anything else? (Yes/No) ---> ").lower() == "yes":
            add_order_line(order_id, order_client)
        else:
            sum_order(order_id)
            more_products = False
            product_menu()


def print_orders_with_spec(client):

    os.system('clear')

    if client == None:
        sql_stmt = select(Orders)
    else:
        sql_stmt = select(Orders).where(Orders.order_client == client)

    with db_session() as session:
        order_data = session.scalars(sql_stmt)

        order_table = Table(title = "Coffee-Shop orders", show_lines=True)

        order_table.add_column("Order #")
        order_table.add_column("Client")
        order_table.add_column("Prod./Qty/Price")



        for order in order_data:

            order_lines = session.scalars(select(ProductTransactions).where(ProductTransactions.order_id == order.id))
            order_total = 0

            for line in order_lines:
                order_total += (line.quantity * line.price)

            order_lines = session.scalars(select(ProductTransactions).where(ProductTransactions.order_id == order.id))

            order_lines_table = Table(show_header=False, show_edge=False, show_footer=True)

            order_lines_table.add_column(footer="Sum")
            order_lines_table.add_column()
            order_lines_table.add_column(footer=str(order_total))


            for line in order_lines:
                order_lines_table.add_row(line.product.name, str(line.quantity), str(line.quantity * line.price))

            order_table.add_row(str(order.id),
                                order.order_client,
                                order_lines_table,
                                )
    
    console.print(order_table)


def add_order_line(order_id, client):

    with db_session() as session:

        product_id = int(input(f"What product would you like to order, {client}?  ---> "))
        quantity = int(input("How many?  ---> "))

        orderproduct = ProductTransactions(
            order_id = order_id,
            product_id=product_id,
            quantity=quantity,
            price = session.scalars(select(Products.price).where(Products.id == product_id)).one()
        )

        session.add(orderproduct)
        session.flush()

        print(f"Added {orderproduct.product.name} to order")
        session.commit()


def sum_order(order_id):

    with db_session() as session:

        order = session.scalars(select(Orders).where(Orders.id == order_id)).one()
        order_lines = session.scalars(select(ProductTransactions).where(ProductTransactions.order_id == order_id))
        order_total = 0

        table = Table(title = "Heres your order " + order.order_client, show_footer=True)

        for line in order_lines:
            order_total += (line.quantity * line.product.price)

        table.add_column('Line','Sum')
        table.add_column('Product')
        table.add_column('@ price', justify='right', style='cyan')
        table.add_column('Quantity', justify='right', style='cyan')
        table.add_column('Total', str(order_total), justify='right', style='cyan')

        order_lines = session.scalars(select(ProductTransactions).where(ProductTransactions.order_id == order_id))

        line_no = 1
        for line in order_lines:
            table.add_row(str(line_no), line.product.name, str(line.product.price), str(line.quantity), str(line.product.price * line.quantity))
            line_no += 1

        console.print(table)
    
    choice = int(input("New order (1), or back to main menu (2)? ---> "))
    if choice == 1: new_order()
    elif choice == 2: main_menu()


def add_product():
    product = Products(
        name = input("What is the product name? ---> "),
        price = float(input("Price? ---> ")),
        description = input("Description of the product ---> ")
    )

    with db_session() as session:
        session.add(product)
        session.commit()
    
    print(f"Added to the products list")


def delete_product(product_id):
    with db_session() as session:
        product = session.get(Products, product_id)
        session.delete(product)
        session.scalars(select(Products))
        session.commit()

def print_product(product_id):
    
    product_table = product_table_create("Existing product")

    with db_session() as session:
        product = session.execute(select(Products).where(Products.id == product_id))


        product = session.scalars(select(Products).where(Products.id == product_id)).one()
        product_table.add_row(str(product.id), product.name, str(product.price), product.description, str(product.created), str(product.updated))

    console.print(product_table)

def product_table_create(title):
        return Table(
            Column(header="ID", justify='right'),
            Column(header="Name"),
            Column(header="Price", justify='right'),
            Column(header="Description"),
            Column(header="Created"),
            Column(header="Last updated"),
            title = title
            )

def print_products():
    product_table = product_table_create("Product list")

    with db_session() as session:
        products = session.scalars(select(Products))
        for product in products:
            product_table.add_row(
                str(product.id), product.name, str(product.price),
                product.description, str(product.created), str(product.updated)
                )
    console.print(product_table)


def edit_product(product_id):
    
    print_product(product_id)
    
    with db_session() as session:

        sql_stmt = select(Products).where(Products.id == product_id)

        if input("Do you want to edit? ---> ").lower() == "yes":
        
            product = session.execute(sql_stmt).scalar_one()
            
            name = input(f"Product name: ({product.name}) ") or product.name
            print(name)
            price = input(f"Price: ({product.price}) ") or product.price
            print(price)
            description = input(f"Description: ({product.description}) ") or product.description
            print(description)

            product.name = name
            product.price = price
            product.description = description
            
            session.execute(sql_stmt).scalar_one()
            print("Product updated successfully")
            session.commit()

            main_admin_menu()

        else:
            main_admin_menu()

def choose_product(operation):
    print_products()

    return int(input(f"What product would you like to {operation}? (number) ---> "))

        


#######################################################################

init_db()


os.system('clear')
rprint("Welcome to the Coffee shop")

main_menu()







