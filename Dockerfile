ARG PY_VERSION=3.8-slim
FROM python:${PY_VERSION}
WORKDIR /app
COPY . .
ARG PIP_CONFIG_FILE=pip.conf
RUN pip install -r requirements.txt
CMD ["python3", "app.py"]