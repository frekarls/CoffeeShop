from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Static, DataTable
from textual.containers import ScrollableContainer


class CoffeeShopApp(App):
    """A Textual app to manage my coffee shop."""

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode"), ("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield ScrollableContainer(MainMenu())

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark
    
    def action_quit() -> None:
        exit()


class MainMenu(Static):

    def compose(self) -> ComposeResult:
        menu_buttons = [
            ("Show menu", "menu", "default"),
            ("Exit", "exit", "error")]

        for button in menu_buttons:
            yield Button(label=button[0], id = button[1], variant=button[2]) 

        def on_button_pressed(self, event: Button.Pressed) -> None:
            button_id = button.event.id
            
            if button_id == "exit":
                exit()
            


class ProductMenu(Static):

    def compose(self) -> ComposeResult:

        menu_table = DataTable()

        menu_table.addcolumns("#", "Product", "Desc")



if __name__ == "__main__":
    app = CoffeeShopApp()
    app.run()