from textual import on, events, message, messages
from textual.app import *
from textual.containers import *
from textual.screen import *
from textual.widgets import *

from db.db_create import engine, db_session
from models.db_models import Products, Orders, ProductTransactions, ProductMenuCategories

from sqlalchemy import select, func

class Header(Header):
    pass


class Footer(Footer):
    pass


class CoffeeShopApp(App):

    CSS_PATH = "static/coffee_shop_textual_app.css"
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode"), ("q", "quit", "Quit"),
                ("o", "add_order", "Add order")]


    def on_ready(self) -> None:
        self.push_screen(MainScreen())

    @on(Button.Pressed, "#main-screen")
    def activate_main_screen(self):
        self.push_screen(MainScreen())

    @on(Button.Pressed, "#pop-start-values")
    def populate_start_values(self):
        import startvalues_db

    @on(Button.Pressed, "#quit-button")
    def quit(self):
        app.exit()
    
    @on(DataTable.RowSelected, "#product-list")
    def selected_product_from_menu(self, message: message.Message):
        global active_product
        active_product = message.row_key.value
        print(active_product)
    
    @on(DataTable.RowSelected, "#shopping-cart")
    def selected_product_from_shopping_cart(self, message: message.Message):
        global active_cart_product
        active_cart_product = message.row_key.value


    @on(Button.Pressed, "#add-to-cart")
    def add_selected_product_to_cart(self) -> None:
        shopping_cart.add_to_cart(active_product, 1)
        self.push_screen(MainScreen())
    
    @on(Button.Pressed, "#remove-from-cart")
    def remove_selected_product_from_cart(self) -> None:
        shopping_cart.remove_from_cart(active_cart_product,1)
        self.push_screen(MainScreen())


class MainScreen(Screen):
    def compose(self) -> ComposeResult:

        yield Header(show_clock=True)

        with HorizontalScroll():
            yield MainMenu(id = "main-menu")
            yield Welcome(id = "welcome-text")
            yield ProductMenu(id = "product-menu")

        yield Footer()


class MainMenu(Vertical):
    
    def compose(self) -> ComposeResult:
        yield Button(label = "Main screen", id = "main-screen", classes = "main_menu_buttons")
        yield Button(label = "Populate start values", id="pop-start-values", classes = "main_menu_buttons")
        # yield Button(classes = "main_menu_buttons")
        yield Button(label = "Leave", classes = "main_menu_buttons", id="quit-button", variant="error")


class Welcome(Vertical):
    def compose(self) -> ComposeResult:
        yield Static("WELCOME", id="welcome-heading", classes="headings")
        yield Static(
            "Welcome to our Coffee Shop!! This is a brilliant shop. You will find our menu to the right"
        )


class ProductMenu(Vertical):
    
    def compose(self) -> ComposeResult:
        

        yield Static("OUR MENU", id="menu-heading", classes="headings")

        with db_session() as session:
            categories = session.scalars(select(ProductMenuCategories))
            option_categories = tuple(
                (category.name, category.id)
                for category in categories
            )
            print(option_categories)
            yield Select(
                options=option_categories,
                prompt="Select producttype",
                id="select-menu-category"
                )
        self.product_list = ProductList(id="product-list")
        yield self.product_list

        yield Static("SHOPPING CART", id="shopping-cart-heading", classes="headings")
        
        yield ShoppingCartList(id = "shopping-cart")

        with Horizontal(id="cart-buttons-container"):
            yield Button(label="Add to cart", id="add-to-cart")
            yield Button(label="Remove from cart", id="remove-from-cart", variant="error")
            yield Button(label="Order", id="submit-order", variant="success")

    @on(Select.Changed, "#select-menu-category")
    def alter_productlist_table(self, event: Select.Changed):
        self.product_list.update_menu_category(event.value)


class ShoppingCartList(VerticalScroll):

    def compose(self) -> ComposeResult:
        yield DataTable(id="shopping-cart")
    
    def on_mount(self) -> None:

        table = self.query_one("#shopping-cart", DataTable)
        table.add_columns("Product", "Price", "Quantity", "Total")
        table.cursor_type = "row"

        self.fill_table(table)
    
    def fill_table(self, table) -> None:
        grand_total = 0
        with db_session() as session:
            for product_id, quantity in shopping_cart.order_items.items():
                product = session.scalar(select(Products).where(Products.id == product_id))
                table.add_row(product.name, product.price, quantity, product.price * quantity, key=product.id)
                grand_total = grand_total + (product.price * quantity)
            
            if grand_total != 0:
                table.add_row("Grand total","", "", grand_total)


class ProductList(VerticalScroll):

    sql_stmt = select(Products).where(Products.active == True)
    #table = DataTable(id = "product-list")

    def compose(self) -> ComposeResult:
        yield DataTable(id = "product-list")

    def on_mount(self) -> None:

        table = self.query_one("#product-list", DataTable)
        table.add_columns("Product", "Description", "Price")
        table.cursor_type = "row"

        self.fill_table(table)

    
    def fill_table(self, table):
            
        with db_session() as session:
            products = session.scalars(self.sql_stmt)
            for product in products:
                table.add_row(product.name, product.description, product.price, key=product.id)

    def update_menu_category(self, menu_category_id):
        
        if menu_category_id is not None:
            self.sql_stmt = select(Products).where(Products.active == True, Products.menu_category_id == menu_category_id)
            print("Endret sql-statement")
            table = self.query_one("#product-list", DataTable)
            table.clear()
            self.fill_table(table)
        else:
            self.sql_stmt = select(Products).where(Products.active == True)
            table = self.query_one("#product-list", DataTable)
            table.clear()
            self.fill_table(table)            


class ShoppingCart():
    
    def __init__(self) -> None:
        self.order_items = {}
    
    def add_to_cart(self, product_id :int, quantity :int):

        if product_id in self.order_items.keys():
            self.order_items[product_id] = self.order_items[product_id] + quantity
        else:
            self.order_items[product_id] = quantity
    
    def remove_from_cart(self, product_id :int, quantity :int):
        print(f"From remove_from_cart {product_id}")
        if product_id in self.order_items.keys():
            if self.order_items[product_id] > quantity:
                self.order_items[product_id] = self.order_items[product_id] - quantity
            else:
                self.order_items.pop(product_id)
    
    def cart_list(self) -> List:

        cart_list =[]

        with db_session() as session:
            for product_id, quantity in self.order_items.items():
                product = session.scalar(select(Products).where(Products.id == product_id))
                cart_object = {"product_id": product_id, "name": product.name, "quantity": quantity, "price": product.price}
                cart_list.append(cart_object)
            
        return cart_list
    
    def order_cart_items(self) -> None:
        with db_session() as session:
            



# Global variables

shopping_cart = ShoppingCart()
active_product = 0
active_cart_product = 0


def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    from models.db_models import Base
    
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    app = CoffeeShopApp()
    app.run()