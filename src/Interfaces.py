import pyray as pr
from typing import Callable
from abc import ABC, abstractmethod


from pyray import ffi


class Checkbox:
    def __init__(self,
                 x: int,
                 y: int,
                 size: int,
                 text: str,
                 text_color: pr.Color = pr.WHITE):
        self.rect: pr.Rectangle = pr.Rectangle(x, y, size, size)
        self.text: str = text
        self.text_color: pr.Color = text_color

        # bool Pointer used by raygui to store the state
        # default value = False
        self._checked_ptr = ffi.new('bool *', False)

    # property allows to use Checkbox.checked
    @property
    def checked(self) -> bool:
        return self._checked_ptr[0]

    # setter allows to use Checkbox.checked = True
    @checked.setter
    def checked(self, value: bool):
        self._checked_ptr[0] = value

    def update(self):
        """draws the checkbox using pyray's gui_check_box and its text
        by default the text is at the right so change it"""
        font_size = int(self.rect.height)
        text_width = pr.measure_text(self.text, font_size)

        text_x = int(self.rect.x) - text_width - int(font_size * 0.2)
        text_y = int(self.rect.y)
        pr.draw_text(self.text, text_x, text_y, font_size, self.text_color)

        pr.gui_check_box(self.rect, "", self._checked_ptr)


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


class Spinner:
    def __init__(self,
                 x: int,
                 y: int,
                 width: int,
                 height: int,
                 text: str,
                 min_value: int,
                 max_value: int,
                 default_value: int = 0,
                 text_color: pr.Color = pr.WHITE):
        self.rect: pr.Rectangle = pr.Rectangle(x, y, width, height)
        self.text: str = text
        self.text_color: pr.Color = text_color
        self.min_value: int = min_value
        self.max_value: int = max_value

        # int Pointer used by raygui to store the state
        # default value = default_value
        self._value_ptr = ffi.new('int *', default_value)
        self.edit_mode: bool = False

    # property allows to use Spinner.value
    @property
    def value(self) -> int:
        return self._value_ptr[0]

    # setter allows to use Spinner.value = 5
    @value.setter
    def value(self, val: int):
        self._value_ptr[0] = val

    def update(self):
        """draws the spinner using pyray's gui_spinner and its text
        by default the text is at the right so change it"""
        font_size = int(self.rect.height)
        text_width = pr.measure_text(self.text, font_size)

        text_x = int(self.rect.x) - text_width - int(font_size * 0.2)
        text_y = int(self.rect.y)

        if self.text != "":
            pr.draw_text(self.text, text_x, text_y, font_size, self.text_color)

        if pr.gui_spinner(self.rect, "",
                          self._value_ptr,
                          self.min_value,
                          self.max_value,
                          self.edit_mode):
            self.edit_mode = not self.edit_mode


class Interface(ABC):
    """class for the interfaces.
    we need to specify where buttons are and what they do """

    def __init__(self) -> None:
        self.buttons: list[Button] = []
        self.checkboxes: list[Checkbox] = []
        self.spinners: list[Spinner] = []

    def get_rotation_from_str(self, direction: str) -> int:
        if direction == "right":
            return 90
        elif direction == "left":
            return -90
        elif direction == "up":
            return 0
        elif direction == "down":
            return 180
        return 90

    def add_button(self, button: Button) -> None:
        """This function adds a button to the interface"""
        self.buttons.append(button)

    def remove_button(self, button: Button) -> None:
        """This function removes a button from the interface"""
        self.buttons.remove(button)

    def add_checkbox(self, checkbox: Checkbox) -> None:
        """This function adds a checkbox to the interface"""
        self.checkboxes.append(checkbox)

    def remove_checkbox(self, checkbox: Checkbox) -> None:
        """This function removes a checkbox from the interface"""
        self.checkboxes.remove(checkbox)

    def add_spinner(self, spinner: Spinner) -> None:
        """This function adds a spinner to the interface"""
        self.spinners.append(spinner)

    def remove_spinner(self, spinner: Spinner) -> None:
        """This function removes a spinner from the interface"""
        self.spinners.remove(spinner)

    def set_assets(self, assets: dict) -> None:
        """This function sets the assets for the interface"""
        self.assets = assets

    @abstractmethod
    def update(self) -> str:
        """function for the logic of this interface
        returns the name of the next state"""
        for button in self.buttons:
            button.update()
        for checkbox in self.checkboxes:
            checkbox.update()
        for spinner in self.spinners:
            spinner.update()
        return ""
