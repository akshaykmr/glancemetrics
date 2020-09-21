 FROM python:3.7.9

 RUN pip install pipenv

 WORKDIR /app

 ADD Pipfile /app
 ADD Pipfile.lock /app
 # ignore-pipfile will install  versions present in lock file and deploy would prevent any re-lock.
 RUN pipenv install --system --dev --deploy --ignore-pipfile

 # Add these files AFTER pipenv install so that rebuilds are quick if Pipfile
 # hasn't changed
 ADD . /app

 EXPOSE 5000
 CMD ["python", "glancemetrics"]