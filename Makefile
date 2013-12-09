.PHONY: pull_deploy pull restart rollout push kick_server

pull_deploy: pull restart

pull:
	git pull

restart:
	sudo /usr/local/bin/allah restart umad_gunicorn
	sudo /usr/local/bin/allah restart umad-indexing-listener_gunicorn


rollout: push kick_server

push:
	git push

kick_server:
	ssh umad.anchor.net.au -- sudo -u umad make -C /home/umad/app

