sassy: $(patsubst static/style/%.scss,static/style/%.css,$(wildcard static/style/*.scss))

%.css: %.scss
	python -mscss.tool --no-compress $< > $@
