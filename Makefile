# Build each model, models/<name>/<name>.py, to build/<name>.stl and
# build/<name>.step. Any other .py file in a model's folder is a helper.
#
#   make           build every model that is out of date
#   make <name>    build one model
#   make list      list model names
#   make lint      lint and check formatting with ruff
#   make clean     remove build/

RUN ?= uv run

NAMES := $(foreach dir,$(wildcard models/*/),$(if $(wildcard $(dir)$(notdir $(dir:/=)).py),$(notdir $(dir:/=))))
OUTPUTS := $(NAMES:%=build/%.step)

# Python cannot report what a model imports, so every model is treated as
# depending on all of common/ and on every file in its own folder.
COMMON := $(wildcard common/*.py)

.PHONY: all list lint clean $(NAMES)

all: $(OUTPUTS)

$(NAMES): %: build/%.step

.SECONDEXPANSION:
build/%.step: models/$$*/$$*.py $$(wildcard models/$$*/*.py) $(COMMON)
	$(RUN) python $<

list:
	@printf '%s\n' $(NAMES)

lint:
	$(RUN) ruff check .
	$(RUN) ruff format --check .

clean:
	rm -rf build
