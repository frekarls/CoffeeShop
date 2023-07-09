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

    @on(Button.Pressed, "#prod-trans-list")
    def show_prod_trans_screen(self):
        self.push_screen(ProductTransactionsListScreen())

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
                    yield ProductTransactionsList(order_no = 1)
    
    def on_data_table_row_selected(self, message: message.Message):
        order_no = message.row_key.value

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
        yield Header()
        yield Footer()

        with HorizontalScroll():
            yield MainMenu(id = "main-menu")
            with VerticalScroll(id = "main-options"):
                yield Input(placeholder = "Client", id = "order-client")

                yield SelectActiveProduct(id = "select-product")
                yield Input(placeholder = "How many", id = "product-quantity")
                
        

# Tables / Lists

class SelectActiveProduct(Select):

    def __init__(self, options, prompt :str = "Choose product", allow_blank :bool = False, value, name , id, classes, disabled) -> None:

        super().__init__(self, options, prompt, allow_blank, value, name, id, classes, disabled)
        sql_stmt = select(Products).where(Products.active == True)

        with db_session() as session:
            menu_products = session.scalars(sql_stmt)
            self.options = menu_products

    def on_mount(self) -> None:
        pass


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

    """ def __init__(self, *children :Widget, name :str | None = None, id :str | None = None, classes :str | None = None, disabled :bool = False, order_no :int | None = None):
        super().__init__(self, *children, name, id, classes, disabled)
        self.order_no = order_no """
    
    def __init__(self, order_no :int | None = None):
        super().__init__()
        self.order_no = order_no

    def compose(self) -> ComposeResult:
        yield DataTable(zebra_stripes=True)

    def on_mount(self) -> None:
        
        if self.order_no is None:
            sql_stmt = None
        elif self.order_no is not None:
            sql_stmt = select(ProductTransactions).where(ProductTransactions.order_id == self.order_no)

        
        table = self.query_one(DataTable)
        table.add_columns("Order #", "Product", "Quantity", "Price", "Client")

        with db_session() as session:
            if sql_stmt is not None:
                transactions = session.scalars(sql_stmt)
                for transaction in transactions:
                    table.add_row(transaction.order_id, transaction.product.name, transaction.quantity, transaction.price, transaction.order.order_client)


if __name__ == "__main__":
    app = CoffeeShopAdminApp()
    app.run()