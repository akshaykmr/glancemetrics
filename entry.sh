#!/bin/bash

# used as entrypoint in Dockerfile to make it an executable and pass args
# neatly
# now we can just do: docker run glancemetrics arg1 arg2
# instead of "docker run -it glancemetrics python app.py arg1 arg2"

python app.py "$@"