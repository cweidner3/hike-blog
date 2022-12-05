REV = head

SRCS = alembic.ini
SRCS += $(shell find src -iname '*.py')
SRCS += $(shell find tests -iname '*.py')

.PHONY: default
default: test

.PHONY: help
help:
	@echo "ACTIONS"
	@echo "  test               [default] Run unittests."
	@echo "  upgrade   [REV=]   Migrate database upwards to REV [default head]"
	@echo "  downgrade [REV=]   Migrate database downwards to REV."
	@echo "  testhike           Upload test data for viewing the hike page."
	@echo "  cov                Show report of test coverage of the app."
	@echo "  html               Show report of test coverage of the app in html."

.PHONY: test
test:
	python -m unittest -v $(TESTS)

.PHONY: upgrade
upgrade:
	alembic upgrade $(REV)

.PHONY: downgrade
downgrade:
	alembic downgrade $(REV)

.PHONY: testhike
testhike:
	python -m tests.scripts.upload_test_hike $(REPLACE)

.PHONY: cov
cov: .coverage
	python -m coverage report

.PHONY: html
html: htmlcov

################################################################################

.PHONY: clean
clean:
	rm -rf .coverage htmlcov

htmlcov: .coverage
	python -m coverage html

.coverage: $(SRCS) Makefile
	python -m coverage run --source=src -m unittest -v
