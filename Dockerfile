FROM python:3.7.5

RUN pip install pipenv

WORKDIR /app

ADD Pipfile /app
ADD Pipfile.lock /app
RUN pipenv install --system --dev --deploy --ignore-pipfile

# Add these files AFTER pipenv install so that rebuilds are quick if Pipfile
# hasn't changed
ADD . /app

RUN chmod 755 /app/app.py

ENTRYPOINT ["python", "/app/app.py"]