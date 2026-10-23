PYTHON ?= python3
NINJA ?= ninja

.PHONY: all check configure all_source verify progress tools ghidra clean format format-check

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

CLANG_FORMAT ?= clang-format
CPP_FILES := tools/wiiurpxtool-compat/io.h $(shell find include src -type f \( -name '*.cpp' -o -name '*.h' \) | LC_ALL=C sort)
JAVA_FILES := $(shell find tools/ghidra_scripts -type f -name '*.java' | LC_ALL=C sort)

format:
	$(CLANG_FORMAT) -i $(CPP_FILES) $(JAVA_FILES)

format-check:
	$(CLANG_FORMAT) --dry-run --Werror $(CPP_FILES) $(JAVA_FILES)
