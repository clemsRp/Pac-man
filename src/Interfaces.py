import pyray as pr
from typing import Callable
from abc import ABC, abstractmethod


class Button:
    def __init__(self,
                 x: int,
                 y: int,
                 width: int,
                 height: int,
                 text: str,
                 color: pr.Color,
                 triggered_function: Callable):
        self.rect: pr.Rectangle = pr.Rectangle(x, y, width, height)

        self.color: pr.Color = color
        self.text: str = text
        self.triggered_function: Callable = triggered_function

    def update(self):
        """draws the button on the screen and checks if it was clicked"""
        if pr.gui_button(self.rect, self.text):
            self.triggered_function()


class Interface(ABC):
    """class for the interfaces.
    we need to specify where buttons are and what they do """

    def __init__(self) -> None:
        self.buttons: list[Button] = []

    def add_button(self, button: Button) -> None:
        """This function adds a button to the interface"""
        self.buttons.append(button)

    def remove_button(self, button: Button) -> None:
        """This function removes a button from the interface"""
        self.buttons.remove(button)

    @abstractmethod
    def update(self) -> str:
        """function for the logic of this interface
        returns the name of the next state"""
        for button in self.buttons:
            button.update()
        return ""
