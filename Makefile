.PHONY: distil

distil:
	python distil_some_stuff.py -v /tmp/mutt.html file:///home/barney/git/support-knowledgebase/ssh-public-key-authentication/index.markdown http://google.com/

distilRT:
	python distil_some_stuff.py -v https://rt.engineroom.anchor.net.au/Ticket/Display.html?id=1877 https://rt.engineroom.anchor.net.au/Ticket/Display.html?id=2207 https://rt.engineroom.anchor.net.au/Ticket/Display.html?id=3010 https://rt.engineroom.anchor.net.au/Ticket/Display.html?id=3084 https://rt.engineroom.anchor.net.au/Ticket/Display.html?id=3101 https://rt.engineroom.anchor.net.au/Ticket/Display.html?id=4771 https://rt.engineroom.anchor.net.au/Ticket/Display.html?id=11039

search:
	python find_some_stuff.py $@

%:
	python find_some_stuff.py $@

