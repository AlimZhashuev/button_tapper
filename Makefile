
install:
	python -m pip install -e ".[dev]"

run:
	python src/main.py com.example.buttontest

demo:
	python src/demo.py

lint:
	ruff check . --fix
	ruff format .
	mypy src
