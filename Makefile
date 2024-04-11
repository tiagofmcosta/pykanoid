.PHONY: all install_prerequisites package

all: package

install_prerequisites: requirements.txt
	python -m pip install -r requirements.txt

package: install_prerequisites
	pyinstaller \
		--clean \
		-n Pykanoid \
		--add-data "data:data" \
		-w \
		-p .venv/Lib/site-packages \
		pykanoid/game.py