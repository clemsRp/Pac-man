from src.parser import Parser


if __name__ == "__main__":
    try:

        parser = Parser()
        parser.parse_config("test.json")

    except Exception as e:
        print(e)
