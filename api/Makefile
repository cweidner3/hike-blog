REV = head

.PHONY: default
default: test

.PHONY: help
help:
	@echo "ACTIONS"
	@echo "  test               [default] Run unittests."
	@echo "  upgrade   [REV=]   Migrate database upwards to REV [default head]"
	@echo "  downgrade [REV=]   Migrate database downwards to REV."
	@echo "  testhike           Upload test data for viewing the hike page."

.PHONY: test
test:
	python -m unittest $(TESTS)

.PHONY: upgrade
upgrade:
	alembic upgrade $(REV)

.PHONY: downgrade
downgrade:
	alembic downgrade $(REV)

.PHONY: testhike
testhike:
	python -m tests.scripts.upload_test_hike $(REPLACE)
