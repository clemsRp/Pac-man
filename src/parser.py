
import json
from typing import Any


class Parser:

    def __init__(self) -> None:
        '''
        Initialize the parser

        Args:
            None
        Return:
            None
        '''
        self._config: dict[str, Any] = dict()
        self._scores: dict[str, str | int] = dict()

    def parse_config(self, filename: str) -> None:
        '''
        Parse a given config file

        Args:
            filename: str = The name of the file to parse
        Return:
            None
        '''
        try:

            # Read the config file
            with open(filename, 'r') as f:
                final_lines: list[str] = []
                lines: list[str] = f.readlines()

                # Handle the comments
                for line in lines:
                    if "#" in line:
                        final_lines.append(line.split("#")[0])
                    else:
                        final_lines.append(line)

                # Convert to python dictionary
                content: str = "\n".join(final_lines)

                try:
                    res: dict[str, Any] = json.loads(content)[0]
                except Exception:
                    raise Exception("Invalid json")

                # Check all mandatory keys are present and valid
                is_valid: dict[str, bool | str] = self._is_valid_config(
                    res, filename
                )
                if not is_valid["state"]:
                    self._config = dict()
                    raise Exception(is_valid["message"])

                self._config = res

        # Raise customs errors
        except PermissionError:
            self._config = dict()
            raise PermissionError(f"You don't have the permission \
                                  to the file '{filename}'")
        except FileNotFoundError:
            self._config = dict()
            raise FileNotFoundError(f"Missing file or \
                                    invalid name: '{filename}'")

    def parse_scores(self, filename: str) -> None:
        '''
        Parse a given scores file

        Args:
            filename: str = The name of the file to parse
        Return:
            None
        '''
        try:

            # Read the config file
            with open(filename, 'r') as f:
                final_lines: list[str] = []
                lines: list[str] = f.readlines()

                # Handle the comments
                for line in lines:
                    if "#" in line:
                        final_lines.append(line.split("#")[0])
                    else:
                        final_lines.append(line)

                # Convert to python dictionary
                content: str = "\n".join(final_lines)

                try:
                    res: dict[str, Any] = json.loads(content)[0]
                except Exception:
                    raise Exception("Invalid json")

                # Check all mandatory keys are present and valid
                is_valid: dict[str, bool | str] = self._is_valid_scores(
                    res, filename
                )
                if not is_valid["state"]:
                    self._scores = dict()
                    raise Exception(is_valid["message"])

                self._scores = res

        # Raise customs errors
        except PermissionError:
            self._scores = dict()
            raise PermissionError(f"You don't have the permission \
                                  to the file '{filename}'")
        except FileNotFoundError:
            self._scores = dict()
            raise FileNotFoundError(f"Missing file or \
                                    invalid name: '{filename}'")

    def get_config(self) -> dict[str, Any]:
        '''
        Return the current config

        Args:
            None
        Return:
            config: dict[str, Any] = The config
        '''
        return self._config

    def get_scores(self) -> dict[str, str | int]:
        '''
        Return the current scores

        Args:
            None
        Return:
            config: dict[str, str | int] = The scores
        '''
        return self._scores

    def _is_valid_config(
                self, config: dict[str, Any], filename: str
            ) -> dict[str, bool | str]:
        '''
        Check is the config is valid or not

        Args:
            config: dict[str, Any] = The current config
            filename: str = The filename
        Return:
            None
        '''
        errors: list[str] = []

        mandatory_keys = [
            "highscore_filename",
            "levels",
            "lives",
            "pacgum",
            "points_per_pacgum",
            "points_per_super_pacgum",
            "points_per_ghost",
            "seed",
            "level_max_time"
        ]

        # Check for missing keys
        if not all([key in config.keys() for key in mandatory_keys]):
            return {
                "state": False,
                "message": "Missing mandatory keys"
            }

        elif len(config) > len(mandatory_keys):
            return {
                "state": False,
                "message": "Too many keys"
            }

        # Check for invalid values

        #  highscore_filename
        cond1: bool = not isinstance(config["highscore_filename"], str)
        if cond1:
            errors.append(
                "highscore_filename must be a valid str filename"
            )
        else:
            try:
                with open(config["highscore_filename"], 'r'):
                    pass
                self.parse_scores(config["highscore_filename"])
            except FileNotFoundError:
                errors.append(
                    f"Missing file or invalid name: \
'{config['highscore_filename']}'"
                )
            except PermissionError:
                errors.append(
                    f"You don't have the permission \
to the file '{config['highscore_filename']}"
                )

        #  levels
        cond1 = not isinstance(config["levels"], list)
        cond2 = len(config["levels"]) == 0
        if cond1 or cond2:
            errors.append(
                "levels must be a non-empty list of dict"
            )
        else:
            level_keys: list[str] = [
                "name", "width", "height"
            ]
            for level in config["levels"]:
                cond1 = not all(key in level.keys() for key in level_keys)
                cond2 = len(level) > len(level_keys)
                if cond1 or cond2:
                    errors.append(
                        """
                        levels must be a list of dict with this format:
                        {
                            "name": "level1",
                            "width": 15,
                            "height": 15
                        }
                        """
                    )
                elif not isinstance(level["name"], str):
                    errors.append(
                        f"level name ({level['name']}) must be a str"
                    )

                elif not isinstance(level["width"], int):
                    errors.append(
                        f"level width ({level['width']}) must be a int"
                    )

                elif not isinstance(level["height"], int):
                    errors.append(
                        f"level height ({level['height']}) must be a int"
                    )

                elif 2 > level["width"] or level["width"] > 20:
                    errors.append(
                        "level width must be between 2 and 20"
                    )

                elif 2 > level["height"] or level["height"] > 20:
                    errors.append(
                        "level height must be between 2 and 20"
                    )

        #  lives, pacgum, points_per_pacgum, points_per_super_pacgum,
        #  points_per_ghost, level_max_time
        additional_keys: list[str] = [
            "lives", "pacgum", "points_per_pacgum",
            "points_per_super_pacgum",
            "points_per_ghost", "level_max_time"
        ]
        for key in additional_keys:
            if not isinstance(config[key], int) or config[key] < 1:
                errors.append(
                    f"{key} must be a positive int"
                )

        message: str = "Everything is alright"
        state: bool = True
        if len(errors) != 0:
            state = False
            message = f"ERROR: {filename}"
            for error in errors:
                message += "\n\t- " + error

        return {
            "state": state,
            "message": message
        }

    def _is_valid_scores(
                self, scores: dict[str, str | int], filename: str
            ) -> dict[str, bool | str]:
        '''
        Check is the scores are valid or not

        Args:
            scores: dict[str, str | int = The current scores
            filename: str = The filename
        Return:
            None
        '''
        errors: list[str] = []

        if "players" not in scores:
            return {
                "state": False,
                "message": "Missing mandatory key"
            }

        elif len(scores) > 1:
            return {
                "state": False,
                "message": "Too many keys"
            }

        #  players
        cond1 = not isinstance(scores["players"], list)
        cond2 = len(scores["players"]) == 0
        if cond1 or cond2:
            errors.append(
                "players must be a non-empty list of dict"
            )
        else:
            player_keys: list[str] = [
                "pseudo", "score"
            ]

            pseudos: list[str] = []
            for player in scores["players"]:
                cond1 = not all(key in player.keys() for key in player_keys)
                cond2 = len(player) > len(player_keys)
                if cond1 or cond2:
                    errors.append(
                        """
                        players must be a list of dict with this format:
                        {
                            "pseudo": "crappo",
                            "score": 424242
                        }
                        """
                    )
                elif not isinstance(player["pseudo"], str):
                    errors.append(
                        f"player pseudo ({player['pseudo']}) must be a str"
                    )

                elif len(player["pseudo"]) > 10 or \
                        not all(
                            c.isalpha() or c.isspace()
                            for c in player["pseudo"]
                        ):
                    errors.append(
                        f"player pseudo ({player['pseudo']}) is invalid"
                    )

                elif player["pseudo"] in pseudos:
                    errors.append(
                        "2 players can't have the same pseudo"
                    )

                elif not isinstance(player["score"], int):
                    errors.append(
                        f"player score ({player['score']}) must be a int"
                    )

                elif 0 > player["score"]:
                    errors.append(
                        "player score must be a positive int"
                    )
                pseudos.append(player["pseudo"])

        message: str = "Everything is alright"
        state: bool = True
        if len(errors) != 0:
            state = False
            message = f"ERROR: {filename}"
            for error in errors:
                message += "\n\t- " + error

        return {
            "state": state,
            "message": message
        }
