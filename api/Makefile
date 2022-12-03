REV = head

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
