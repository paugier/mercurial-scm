all:: serve

serve: .env
	HGWEBSITE_DEBUG=1 .env/bin/python hgwebsite.py

.env:
	python -m virtualenv .env
	.env/bin/pip install flask

.PHONY: build serve
