# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?= -j auto
SPHINXBUILD   ?= pdm run sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

ROOT_DIR := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))

.PHONY: html
html:
	pdm sync -G web
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)
	@echo "$$(hg id -R $(ROOT_DIR) -q)" > $(BUILDDIR)/html/version
	@echo "file://$(ROOT_DIR)$(BUILDDIR)/html/index.html"

.PHONY: clean
clean:
	rm -rf source/help
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)

.PHONY: sphinx-help
sphinx-help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: lock
lock:
	pdm lock

.PHONY: format
format:
	pdm sync -G format
	pdm format

.PHONY: format-check
format-check:
	pdm sync -G format
	pdm format-check

.PHONY: test
test:
	pdm sync -G web -G test
	pdm test
