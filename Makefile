all:: serve

serve: .venv
	HGWEBSITE_DEBUG=1 pdm run ./hgwebsite.py

.venv:
	pdm install

.PHONY: build serve
