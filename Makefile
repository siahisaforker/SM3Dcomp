PYTHON ?= python3
NINJA ?= ninja

.PHONY: all check configure all_source verify progress tools ghidra clean

all: check build.ninja
	$(NINJA)

check:
	$(PYTHON) tools/validate_splits.py

configure: check
	$(PYTHON) configure.py

build.ninja: configure.py tools/validate_splits.py config/US/config.yml config/US/build.sha256 \
	config/US/splits.txt config/US/symbols.txt \
	config/US/undefined_funcs.txt config/US/undefined_syms.txt \
	config/US/imports/gx2.txt CMakeLists.txt tools/download_tool.py \
	tools/wiiurpxtool/wiiurpxtool.cpp
	$(PYTHON) configure.py

all_source verify progress tools: check build.ninja
	$(NINJA) $@

ghidra:
	$(PYTHON) tools/setup_ghidra.py

clean:
	$(NINJA) -t clean
