FROM python:3.12-slim

WORKDIR tasks/

COPY requirements.txt /tasks/

RUN pip install -r requirements.txt

COPY . /tasks/

RUN ["chmod", "+x", "./docker-entrypoint.sh"]
ENTRYPOINT ["bash", "-c"]
CMD ["./docker-entrypoint.sh"]