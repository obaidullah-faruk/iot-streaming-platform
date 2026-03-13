-include .env
export

DOCKER_COMPOSE_DIR=infrastructure/docker
KAFKA_CONTAINER=kafka
KAFKA_BIN=/opt/kafka/bin/kafka-topics.sh
KAFKA_CONSOLE_CONSUMER=/opt/kafka/bin/kafka-console-consumer.sh
POSTGRES_CONTAINER=postgres
TOPIC_NAME=$(KAFKA_TOPIC)

.PHONY: help up down restart logs ps test-db create-topic list-topics test-all build simulator-logs consume-telemetry

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

up: ## Start all docker containers in background
	docker compose -f $(DOCKER_COMPOSE_DIR)/docker-compose.yml up -d

down: ## Stop and remove all containers
	docker compose -f $(DOCKER_COMPOSE_DIR)/docker-compose.yml down

restart: ## Restart all containers
	docker compose -f $(DOCKER_COMPOSE_DIR)/docker-compose.yml restart

logs: ## Follow logs of all containers
	docker compose -f $(DOCKER_COMPOSE_DIR)/docker-compose.yml logs -f

ps: ## List running containers
	docker compose -f $(DOCKER_COMPOSE_DIR)/docker-compose.yml ps

test-db: ## Test Postgres connection
	@echo "Checking Postgres connection..."
	docker exec $(POSTGRES_CONTAINER) pg_isready -U $(POSTGRES_USER) -d $(POSTGRES_DB)

create-topic: ## Create Kafka topic: iot.telemetry
	@echo "Creating Kafka topic $(TOPIC_NAME)..."
	docker exec $(KAFKA_CONTAINER) $(KAFKA_BIN) --create --topic $(TOPIC_NAME) --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1 --if-not-exists

list-topics: ## List all Kafka topics
	@echo "Listing Kafka topics..."
	docker exec $(KAFKA_CONTAINER) $(KAFKA_BIN) --list --bootstrap-server localhost:9092

db-wipe: ## Delete database volume
	@echo "Stopping containers and removing volumes..."
	docker compose -f $(DOCKER_COMPOSE_DIR)/docker-compose.yml down -v
	@echo "Restarting containers..."
	docker compose -f $(DOCKER_COMPOSE_DIR)/docker-compose.yml up -d

test-all: test-db create-topic list-topics ## Run all infrastructure tests

build: ## Build or rebuild services
	docker compose -f $(DOCKER_COMPOSE_DIR)/docker-compose.yml build

simulator-logs: ## Follow simulator logs
	docker compose -f $(DOCKER_COMPOSE_DIR)/docker-compose.yml logs -f simulator

worker-logs: ## Follow worker logs
	docker compose -f $(DOCKER_COMPOSE_DIR)/docker-compose.yml logs -f worker

api-logs: ## Follow api logs
	docker compose -f $(DOCKER_COMPOSE_DIR)/docker-compose.yml logs -f api

migrate: ## Run database migrations
	docker exec worker alembic -c database/alembic.ini upgrade head

setup: create-topic migrate ## Setup infrastructure (topics + migrations)

consume-telemetry: ## Read messages from iot.telemetry topic
	docker exec $(KAFKA_CONTAINER) $(KAFKA_CONSOLE_CONSUMER) --topic $(TOPIC_NAME) --bootstrap-server localhost:9092 --from-beginning
