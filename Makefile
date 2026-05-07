ARGS ?= config.json

install:
	uv sync

run:
	uv run python3 pacman.py $(ARGS)

debug:
	@echo "   Starting debugger..."
	@echo "   Useful commands:"
	@echo "   n (next)       - Execute next line"
	@echo "   s (step)       - Step into function"
	@echo "   c (continue)   - Continue until next breakpoint"
	@echo "   p <var>        - Print variable"
	@echo "   l (list)       - Show source code"
	@echo "   q (quit)       - Quit debugger"
	@echo ""
	uv run python3 -m pdb pacman.py $(ARGS)

lint:
	uv run flake8 . --exclude=.venv
	uv run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

clean:
	rm -rf .mypy_cache
	rm -rf .venv
	rm -rf src/__pycache__
	rm -rf __pycache__
	rm -rf .vscode
	rm -rf build dist
	rm -f pacman.spec

package:
	uv run pyinstaller --noconfirm --onedir --windowed pacman.py
	cp -r assets dist/pacman/
	mkdir -p dist/pacman/src
	cp src/lighting.fs dist/pacman/src/
	cp config.json dist/pacman/
	cp scores.json dist/pacman/
	cp pacman_style.rgs dist/pacman/
	cp README_PACKAGE.md dist/pacman/README.md

.PHONY: install run debug lint clean fclean package                                        