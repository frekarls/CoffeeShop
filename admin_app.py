from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Static, DataTable, Placeholder, ContentSwitcher, Input, SelectionList, Select
from textual.containers import ScrollableContainer, Container, Vertical, HorizontalScroll, VerticalScroll
from textual.screen import Screen
from textual import on, events, message, messages
from textual.widget import Widget

from db.db_create import engine, db_session
from models.db_models import Products, Orders, ProductTransactions

from sqlalchemy import select, func

class Header(Header):
    pass

class Footer(Footer):
    pass

class CoffeeShopAdminApp(App):

    CSS_PATH = "static/admin_app.css"
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode"), ("q", "quit", "Quit"), ("p", "add_product", "Add Product"),
                ("o", "add_order", "Add order")]

    def on_ready(self) -> None:
        self.push_screen(MainScreen())
        self.dark = not self.dark

    @on(Button.Pressed, "#exit")
    def exit_app(self) -> None:
        exit()


    @on(Button.Pressed, "#product-list")
    def show_product_screen(self) -> None:
        self.push_screen(ProductListScreen())

    @on(Button.Pressed, "#order-list")
    def show_order_screen(self):
        self.push_screen(OrderListScreen())

    @on(Button.Pressed, "#add-product-button")
    def open_add_product_screen(self):
        self.push_screen(AddProductScreen())

    @on(Button.Pressed, "#submit-product")
    def submit_and_validate_product(self):
        
        name = self.query_one("#product-name", Input).value
        price = self.query_one("#product-price", Input).value
        description = self.query_one("#product-description", Input).value

        product = Products(name, price, description)

        with db_session() as session:
            session.add(product)
            session.commit()
        
        self.push_screen(ProductListScreen())

    @on(Button.Pressed, "#submit-order")
    def submit_and_validate_order(self):
        
        client = self.query_one("#order-client", Input).value
        sel_product = self.query_one("#order-product", Select).value
        sel_quantity = int(self.query_one("#order-quantity", Input).value)
        print(sel_product)

        order = Orders(order_client = client)

        with db_session() as session:
            price = session.scalar(select(Products.price).where(Products.id == sel_product))

        with db_session() as session:
            session.add(order)
            session.flush()
            order_id = order.id
            transaction = ProductTransactions(order_id, sel_product, sel_quantity, price)
            
            session.add(transaction)
            session.commit()
        
        self.push_screen(MainScreen())

    
    def action_add_product(self) -> None:
        self.push_screen(AddProductScreen())
    
    def action_add_order(self) -> None:
        self.push_screen(AddOrderScreen())


class MainMenu(Vertical):
    
    def compose(self) -> ComposeResult:
        
        buttons = [
            ("Products", "product-list", "primary"),
            ("Orders", "order-list", "primary"),
            #("Transactions", "prod-trans-list", "primary"),
            ("Exit", "exit", "error"),
            ]

        for button in buttons:
            yield Button(label=button[0], id=button[1], variant=button[2])

# SCREENS ###########################################################################
class MainScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

        with HorizontalScroll():
            yield MainMenu(id = "main-menu")

class ProductListScreen(Screen):
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

        with HorizontalScroll():
            yield MainMenu(id = "main-menu")
            with Container(id = "main-options"):
                yield ProductList()
                yield Button(label = "Add product", id = "add-product-button", variant="success")


class OrderListScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

        with HorizontalScroll():
            yield MainMenu(id = "main-menu")
            with Container(id = "main-options"):
                yield OrderList(id = "main-data-list")
                with HorizontalScroll():
                    order_transactions = ProductTransactionsList()
                    yield order_transactions
    
    def on_data_table_row_selected(self, message: message.Message):
        order_no = message.row_key.value
        ProductTransactionsList.selected_order(order_id = order_no)


""" class ProductTransactionsListScreen(Screen):

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

        with HorizontalScroll():
            yield MainMenu(id = "main-menu")
            with Container(id = "main-options"):
                yield ProductTransactionsList(order_no=None) """

class AddProductScreen(Screen):

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

        with HorizontalScroll():
            yield MainMenu(id = "main-menu")
            with VerticalScroll(id = "main-options"):
                yield Input(placeholder="Product name", id="product-name")
                yield Input(placeholder="Price", id="product-price")
                yield Input(placeholder="Description", id="product-description")
                yield Button(label="Add product", variant="success", id="submit-product")

class AddOrderScreen(Screen):
    def compose(self) -> ComposeResult:

        # get active products for select-field
        with db_session() as session:
            active_products = session.scalars(select(Products.name).where(Products.active == True))

        yield Header()
        yield Footer()

        with HorizontalScroll():
            yield MainMenu(id = "main-menu")
            with VerticalScroll(id = "main-options"):
                yield Input(placeholder = "Client", id = "order-client")

                # get active products for select-field
                with db_session() as session:
                    active_products = session.scalars(select(Products).where(Products.active == True))
                    

                    active_products_tuple = tuple(
                        ((f"{menu_product.name} @{menu_product.price}"),
                         menu_product.id) 
                         for menu_product in active_products
                         )

                    yield Select(
                        options = active_products_tuple,
                        prompt = "Select Product",
                        allow_blank = False,
                        id = "order-product"
                        )
                
                yield Input(placeholder = "How many", id = "order-quantity")
                yield Button(label = "Add order", id = "submit-order", variant = "success")
                    

# Tables / Lists

class ProductList(Vertical):

    def compose(self) -> ComposeResult:
        yield DataTable(zebra_stripes=True)

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("#", "Product", "Description", "Price", "Active", "Created", "Updated")
        table.cursor_type = "row"

        with db_session() as session:
            menu_products = session.scalars(select(Products).where(Products.active == True))
            for product in menu_products:
                table.add_row(product.id, product.name, product.description, product.price, product.active, product.created.strftime("%x"), product.updated.strftime("%x"))
            #self.add_rows(menu_products)


class OrderList(Vertical):

    def compose(self) -> ComposeResult:
        yield DataTable(zebra_stripes=True)

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("Order #", "Client", "Created", "Updated")
        table.cursor_type = "row"

        with db_session() as session:
            orders = session.scalars(select(Orders))
            for order in orders:
                table.add_row(order.id, order.order_client, order.created.strftime("%x"), order.updated.strftime("%x"), key=order.id)


class ProductTransactionsList(Vertical):

    def compose(self) -> ComposeResult:
        yield DataTable(zebra_stripes=True)
        
        table = self.query_one(DataTable)
        table.add_columns("Order #", "Product", "Quantity", "Price", "Client")
        table.cursor_type = "row"

        sql_stmt = select(ProductTransactions)

        with db_session() as session:
            if sql_stmt is not None:
                transactions = session.scalars(sql_stmt)
                for transaction in transactions:
                    table.add_row(transaction.order_id, transaction.product.name, transaction.quantity, transaction.price, transaction.order.order_client)

    def selected_order(self, order_id) -> None:
        table = self.query_one(DataTable)
        for row in table.rows.keys:
            table.remove_row(row)
        
        sql_stmt = select(ProductTransactions).where(ProductTransactions.order_id == order_id)

        with db_session() as session:
            transactions = session.scalars(sql_stmt)
            for transaction in transactions:
                table.add_row(transaction.order_id, transaction.product.name, transaction.quantity, transaction.price, transaction.order.order_client)


if __name__ == "__main__":
    app = CoffeeShopAdminApp()
    app.run()