.PHONY: install test api frontend docker-up
install:
	pip install -r requirements.txt
	cd frontend && npm install

test:
	pytest backend/tests

api:
	uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	cd frontend && npm run dev

docker-up:
	docker compose up --build
