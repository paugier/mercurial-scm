all:: serve

deploy-ssh:
	ssh selenic 'cd /home/hg/www && hg pull -u'

deploy:
	cd /home/hg/www && hg pull -u

serve: .env
	HGWEBSITE_DEBUG=1 .env/bin/python hgwebsite.py

.env:
	python -m virtualenv .env
	.env/bin/pip install flask

.PHONY: build deploy-ssh deploy serve
