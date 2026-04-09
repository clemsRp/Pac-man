
import json


class Parser:

    def __init__(self) -> None:
        self._config = dict()
        self._scores = dict()

    def parse_config(self, filename: str) -> None:
        '''
        Parse a given file to get the config

        Args:
            filename: str = The file to parse for the config
        Return:
            None
        '''
        with open(filename, 'r') as f:
            final_lines: list[str] = []
            lines: list[str] = f.readlines()

            for line in lines:
                if "#" in line:
                    final_lines.append(line.split("#")[0])
                else:
                    final_lines.append(line)

            res: dict
            try:
                res = json.loads("\n".join(final_lines))[0]
            except Exception:
                raise Exception("Invalid json")

            is_valid: dict = self._is_valid_config(res, filename)
            if not is_valid["state"]:
                self._config = dict()
                raise Exception(is_valid["message"])

            self._config = res

    def parse_scores(self, filename) -> None:
        '''
        Parse a given file to get the scores

        Args:
            filename: str = The file to parse for the scores
        Return:
            None
        '''
        with open(filename, 'r') as f:
            final_lines: list[str] = []
            lines: list[str] = f.readlines()

            for line in lines:
                if "#" in line:
                    final_lines.append(line.split("#")[0])
                else:
                    final_lines.append(line)

            res: dict
            try:
                res = json.loads("\n".join(final_lines))[0]
            except Exception:
                raise Exception("Invalid json")

            is_valid: dict = self._are_valid_scores(res, filename)
            if not is_valid["state"]:
                self._scores = dict()
                raise Exception(is_valid["message"])

            self._scores = res

    def get_config(self) -> dict:
        return self._config

    def get_scores(self) -> dict:
        return self._scores

    def _is_valid_config(
                self,
                config: dict, filename: str
            ) -> dict:
        '''
        Check if the config is valid or not

        Args:
            config: dict = The config
            filename: str = The filename
        Return:
            None
        '''
        errors: list[str] = []

        mandatory_keys: list[str] = [
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

        if not all([key in config for key in mandatory_keys]):
            return {
                "state": False,
                "message": f"ERROR: {filename}\n\t-\
Missing keys"
            }

        elif len(config) > len(mandatory_keys):
            return {
                "state": False,
                "message": f"ERROR: {filename}\n\t-\
Too many keys"
            }

        # highscore_filename
        if not isinstance(config["highscore_filename"], str):
            errors.append(
                "highscore_filename must be a str"
            )
        else:
            try:
                with open(config["highscore_filename"], 'r'):
                    self.parse_scores(config["highscore_filename"])
            except PermissionError:
                errors.append(
                    f"Permission error '{config['highscore_filename']}'"
                )
            except FileNotFoundError:
                errors.append(
                    f"File doesn't exist or is spell wrong \
'{config['highscore_filename']}'"
                )

        # levels
        if not isinstance(config["levels"], list) or \
                len(config["levels"]) == 0:
            errors.append(
                "levels must be a non-empty list of dict"
            )
        else:
            additional_keys: list[str] = [
                "name", "width", "height"
            ]
            for level in config["levels"]:
                if not all([key in level for key in additional_keys]):
                    errors.append(
                        "Missing keys for level"
                    )
                elif len(level) > len(additional_keys):
                    errors.append(
                        "Too many keys for level"
                    )

                if not isinstance(level["name"], str):
                    errors.append(
                        "level name must be a str"
                    )

                if not isinstance(level["width"], int) or\
                        level["width"] < 2 or level["width"] > 20:
                    errors.append(
                        "level width must be an int between 2 and 20"
                    )

                if not isinstance(level["height"], int) or\
                        level["height"] < 2 or level["height"] > 20:
                    errors.append(
                        "level height must be an int between 2 and 20"
                    )

        for key in mandatory_keys[2:]:
            if not isinstance(config[key], int) or \
                    config[key] < 1:
                errors.append(
                    f"{key} must be a positive int"
                )

        state: bool = True
        message: str = "Everything is alright"

        if len(errors) != 0:
            state = False
            message = f"ERROR: {filename}"
            for error in errors:
                message += "\n\t- " + error

        return {
            "state": state,
            "message": message
        }

    def _are_valid_scores(
                self,
                scores: dict, filename: str
            ) -> dict:
        '''
        Check if the scores is valid or not

        Args:
            scores: dict = The scores
            filename: str = The filename
        Return:
            None
        '''
        errors: list[str] = []

        mandatory_keys: list[str] = [
            "players"
        ]

        if not all([key in scores for key in mandatory_keys]):
            return {
                "state": False,
                "message": f"ERROR: {filename}\n\t-\
Missing keys"
            }

        elif len(scores) > len(mandatory_keys):
            return {
                "state": False,
                "message": f"ERROR: {filename}\n\t-\
Too many keys"
            }

        # players
        """ if not isinstance(scores["players"], list) or \
                len(scores["players"]) == 0:
            errors.append(
                "players must be a non-empty list of dict"
            ) """
        additional_keys: list[str] = [
            "pseudo", "score"
        ]
        for player in scores["players"]:
            if not all([key in player for key in additional_keys]):
                errors.append(
                    "Missing keys for player"
                )
            elif len(player) > len(additional_keys):
                errors.append(
                    "Too many keys for player"
                )

            if not isinstance(player["pseudo"], str):
                errors.append(
                    "player pseudo must be a str"
                )
            elif not player["pseudo"].replace(" ", "").isalpha() or \
                    len(player["pseudo"]) > 10:
                errors.append(
                    f"Invalid pseudo '{player['pseudo']}'"
                )

            if not isinstance(player["score"], int) or\
                    player["score"] < 0:
                errors.append(
                    "player score must be a positive int"
                )

        state: bool = True
        message: str = "Everything is alright"

        if len(errors) != 0:
            state = False
            message = f"ERROR: {filename}"
            for error in errors:
                message += "\n\t- " + error

        return {
            "state": state,
            "message": message
        }
