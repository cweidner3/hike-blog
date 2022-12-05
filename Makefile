.PHONY: default
default: up

.PHONY: up
up:
	docker-compose up --build -d

.PHONY: down
down:
	docker-compose down $(ARGS)

.PHONY: build
build:
	docker-compose build

.PHONY: logs
logs:
	docker-compose logs -f $(CONT)

.PHONY: status
status:
	docker-compose ps

.PHONY: stat
stat: status

.PHONY: localup
localup: .prod-local.yml
	docker-compose -f $< up --build -d

.PHONY: localdown
localdown: .prod-local.yml
	docker-compose -f $< down $(ARGS)

.PHONY: locallogs
locallogs: .prod-local.yml
	docker-compose -f $< logs -f $(CONT)

################################################################################

.PHONY: clean
clean:
	rm -rf .prod-local.yml

.prod-local.yml: docker-compose.yml prod-local.yml
	@python ./utils/dc_merge.py $@ $^
