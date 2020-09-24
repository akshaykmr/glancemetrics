build:
	docker build -t glancemetrics .

test: build
	docker run -it --entrypoint pytest glancemetrics -s

format:
	black .