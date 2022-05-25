build:
	docker build -t glancemetrics .

test: build
	docker run -it --entrypoint pytest glancemetrics -s

test-ci: build
	docker run --entrypoint pytest glancemetrics -s

generate_logs:
	@docker run -it --entrypoint python glancemetrics -m test.log_generator

format:
	black .
