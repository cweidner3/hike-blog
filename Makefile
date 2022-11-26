.PHONY: default
default: up

.PHONY: up
up:
	docker-compose up --build -d

.PHONY: down
down:
	docker-compose down

.PHONY: logs
logs:
	docker-compose logs -f $(CONT)

.PHONY: status
status:
	docker-compose ps

.PHONY: stat
stat: status
