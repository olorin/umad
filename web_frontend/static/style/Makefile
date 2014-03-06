sassy: $(patsubst %.scss,%.css,$(wildcard *.scss))

%.css: %.scss
	python -mscss.tool --no-compress $< > $@
