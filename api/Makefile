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
