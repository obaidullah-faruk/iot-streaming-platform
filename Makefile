DOCKER_COMPOSE_DIR=infrastructure/docker

.PHONY: up down restart logs ps

up:
	docker compose -f $(DOCKER_COMPOSE_DIR)/docker-compose.yml up -d

down:
	docker compose -f $(DOCKER_COMPOSE_DIR)/docker-compose.yml down

restart:
	docker compose -f $(DOCKER_COMPOSE_DIR)/docker-compose.yml restart

logs:
	docker compose -f $(DOCKER_COMPOSE_DIR)/docker-compose.yml logs -f

ps:
	docker compose -f $(DOCKER_COMPOSE_DIR)/docker-compose.yml ps
