.PHONY: pull_deploy pull restart rollout push kick_server


# Acts on the server

pull_deploy: pull_production restart

pull_production:
	git checkout master
	git pull
	git checkout production

restart:
	sudo /usr/local/bin/allah restart umad_gunicorn
	sudo /usr/local/bin/allah restart umad-indexing-listener_gunicorn
	sudo /usr/local/bin/allah restart umad-indexing-worker
	sudo /usr/local/bin/allah restart umad-provsys-auditlog-watcher



# Acts on your local dev repo

rollout: checkout_master push kick_server

checkout_master:
	git checkout master

push:
	git push

kick_server:
	ssh umad.anchor.net.au -- sudo -u umad make -C /home/umad/app pull_deploy
