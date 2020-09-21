build:
	docker build -t glancemetrics .

run:
	docker run -it glancemetrics

build_and_run: build run

test: build
	docker run -it glancemetrics pytest

format:
	black .