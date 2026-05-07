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
        """
        Initialize a Checkbox instance.

        Args:
            x
                int: The x coordinate of the checkbox.
            y
                int: The y coordinate of the checkbox.
            size
                int: The size (width and height) of the checkbox.
            text
                str: The label text for the checkbox.
            text_color
                pr.Color: The color of the label text.
        """
        self.rect: pr.Rectangle = pr.Rectangle(x, y, size, size)
        self.text: str = text
        self.text_color: pr.Color = text_color

        # bool Pointer used by raygui to store the state
        # default value = False
        self._checked_ptr = ffi.new('bool *', False)

    # property allows to use Checkbox.checked
    @property
    def checked(self) -> bool:
        """
        Get the current checked state of the checkbox.

        Returns:
            bool: True if checked, False otherwise.
        """
        return bool(self._checked_ptr[0])

    # setter allows to use Checkbox.checked = True
    @checked.setter
    def checked(self, value: bool) -> None:
        """
        Set the checked state of the checkbox.

        Args:
            value
                bool: The new checked state.

        Returns:
            None: No return value.
        """
        self._checked_ptr[0] = value

    def update(self) -> None:
        """
        Draw the checkbox using pyray's gui_check_box and its text.
        By default the text is at the right, so change it to the left.

        Returns:
            None: No return value.
        """
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
                 triggered_function: Callable):
        """
        Initialize a Button instance.

        Args:
            x
                int: The x coordinate of the button.
            y
                int: The y coordinate of the button.
            width
                int: The width of the button.
            height
                int: The height of the button.
            text
                str: The text displayed on the button.
            triggered_function
                Callable: The function to call when the button is clicked.
        """
        self.rect: pr.Rectangle = pr.Rectangle(x, y, width, height)

        self.text: str = text
        self.triggered_function: Callable = triggered_function

    def update(self) -> None:
        """
        Draw the button on the screen and check if it was clicked.

        Returns:
            None: No return value.
        """
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
        """
        Initialize a Spinner instance.

        Args:
            x
                int: The x coordinate of the spinner.
            y
                int: The y coordinate of the spinner.
            width
                int: The width of the spinner.
            height
                int: The height of the spinner.
            text
                str: The label text for the spinner.
            min_value
                int: The minimum allowed value.
            max_value
                int: The maximum allowed value.
            default_value
                int: The initial value of the spinner.
            text_color
                pr.Color: The color of the label text.
        """
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
        """
        Get the current integer value of the spinner.

        Returns:
            int: The current value.
        """
        return int(self._value_ptr[0])

    # setter allows to use Spinner.value = 5
    @value.setter
    def value(self, val: int) -> None:
        """
        Set the integer value of the spinner.

        Args:
            val
                int: The new integer value.

        Returns:
            None: No return value.
        """
        self._value_ptr[0] = val

    def update(self) -> None:
        """
        Draw the spinner using pyray's gui_spinner and its text.
        By default the text is at the right, so change it to the left.

        Returns:
            None: No return value.
        """
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
    """
    Base class for the user interfaces.
    """

    def __init__(self) -> None:
        """
        Initialize the interface with empty lists for UI elements.
        """
        self.buttons: list[Button] = []
        self.checkboxes: list[Checkbox] = []
        self.spinners: list[Spinner] = []

    def get_rotation_from_str(self, direction: str) -> int:
        """
        Get the rotation angle in degrees from a direction string.

        Args:
            direction
                str: The direction as a string (e.g. "right", "left",
                "up", "down").

        Returns:
            int: The rotation angle in degrees.
        """
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
        """
        Add a button to the interface.

        Args:
            button
                Button: The button instance to add.

        Returns:
            None: No return value.
        """
        self.buttons.append(button)

    def remove_button(self, button: Button) -> None:
        """
        Remove a button from the interface.

        Args:
            button
                Button: The button instance to remove.

        Returns:
            None: No return value.
        """
        self.buttons.remove(button)

    def add_checkbox(self, checkbox: Checkbox) -> None:
        """
        Add a checkbox to the interface.

        Args:
            checkbox
                Checkbox: The checkbox instance to add.

        Returns:
            None: No return value.
        """
        self.checkboxes.append(checkbox)

    def remove_checkbox(self, checkbox: Checkbox) -> None:
        """
        Remove a checkbox from the interface.

        Args:
            checkbox
                Checkbox: The checkbox instance to remove.

        Returns:
            None: No return value.
        """
        self.checkboxes.remove(checkbox)

    def add_spinner(self, spinner: Spinner) -> None:
        """
        Add a spinner to the interface.

        Args:
            spinner
                Spinner: The spinner instance to add.

        Returns:
            None: No return value.
        """
        self.spinners.append(spinner)

    def remove_spinner(self, spinner: Spinner) -> None:
        """
        Remove a spinner from the interface.

        Args:
            spinner
                Spinner: The spinner instance to remove.

        Returns:
            None: No return value.
        """
        self.spinners.remove(spinner)

    def set_assets(self, assets: dict) -> None:
        """
        Set the assets dictionary for the interface.

        Args:
            assets
                dict: The assets dictionary to store.

        Returns:
            None: No return value.
        """
        self.assets = assets

    @abstractmethod
    def update(self) -> str:
        """
        Update the logic of this interface and draw its elements.

        Returns:
            str: The name of the next state (or an empty string if staying).
        """
        for button in self.buttons:
            button.update()
        for checkbox in self.checkboxes:
            checkbox.update()
        for spinner in self.spinners:
            spinner.update()
        return ""
