install:
    pip install -r requirements.txt

run:
    python main.py

lint:
    flake8 main.py --max-line-length=120

test:
    pytest test_game.py -v

build:
    pyinstaller --onefile --windowed main.py

clean:
    rm -rf dist/ build/ __pycache__/ *.spec