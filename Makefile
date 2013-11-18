.PHONY: pull_deploy pull restart push_deploy push kick_server

pull_deploy: pull restart

pull:
	git pull

restart:
	sudo /usr/local/bin/allah restart umad_gunicorn

push_deploy: push kick_server

push:
	git push

kick_server:
	ssh umad.anchor.net.au -- sudo -u umad make -C /home/umad/app

