from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Static, DataTable, Placeholder, ContentSwitcher
from textual.containers import ScrollableContainer, Container, Horizontal, VerticalScroll
from textual.screen import Screen
from textual import on
from db.db_create import engine, db_session
from models.db_models import Products, Orders
from sqlalchemy import select, func

class Header(Placeholder):
    pass

class Footer(Placeholder):
    pass


class CoffeeShopApp(App):
    """A Textual app to manage my coffee shop."""

    CSS_PATH = "static/app_textual.css"
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode"), ("q", "quit", "Quit")]

    global active_table
    active_table = "products"

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""

        yield Header("Admin-tool", id="Header")

        yield DatabaseTableSwitch(id="app-layout")

        yield Placeholder(label="Sub datatable", id="sub-data")
        

        yield Footer(id="Footer")

    #main menu button press actions

    @on(Button.Pressed, "#products")
    def activate_products_list(self):
        pass

    @on(Button.Pressed, "#orders")
    def activate_orders_list(self):
        pass

    @on(Button.Pressed, "#exit")
    def exit_app(self):
        exit()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark
    
    def action_quit(self) -> None:
        exit()

class MainScreen(Screen):
    


class ProductList(Static):

    def compose(self) -> ComposeResult:
        yield DataTable(zebra_stripes=True)

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("#", "Product", "Description", "Price", "Active", "Created", "Updated")

        with db_session() as session:
            menu_products = session.scalars(select(Products).where(Products.active == True))
            for product in menu_products:
                table.add_row(product.id, product.name, product.description, product.price, product.active, product.created.strftime("%x"), product.updated.strftime("%x"))
            #self.add_rows(menu_products)

class DatabaseTableSwitch(Static):

    def compose(self) -> ComposeResult:

        main_buttons = [
            ("Products", "product-list", "primary"),
            ("Orders", "order-list", "primary"),
            ("Categories", "category-list", "primary"),
            ("Exit", "exit", "error"),
        ]
        with VerticalScroll(id = "main-menu"):
            for button in main_buttons:
                yield Button(label=button[0], id=button[1], variant=button[2])

        with ContentSwitcher(id="main-data"):
            yield ProductList(id="product-list")
            yield OrderList(id="order-list")


        @on(Button.Pressed, "#order-list")
        def activate_orders_list(self):
            print(event.button.id)
            self.query.one(ContentSwitcher).current = event.button.id

"""
        def on_button_pressed(self, event: Button.Pressed) -> None:
            self.query_one(ContentSwitcher).current = event.button.id 

"""     
            


class OrderList(Static):

    def compose(self) -> ComposeResult:
        yield DataTable(zebra_stripes=True)

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("Order #", "Client", "Created", "Updated")

        with db_session() as session:
            orders = session.scalars(select(Orders))
            for order in orders:
                table.add_row(order.id, order.order_client, order.created.strftime("%x"), order.updated.strftime("%x"))
            #self.add_rows(menu_products)

if __name__ == "__main__":
    app = CoffeeShopApp()
    print(app.run())