.PHONY: pull_deploy pull restart

pull_deploy: pull restart

pull:
	git pull

restart:
	sudo /usr/local/bin/allah restart umad_gunicorn

