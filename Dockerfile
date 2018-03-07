FROM quay.io/keboola/docker-custom-python:latest

RUN pip3 install --upgrade --force-reinstall git+git://github.com/keboola/python-docker-application.git@2.1.0
COPY . /code/
WORKDIR /data/
CMD ["python", "-u", "/code/main.py"]
