FROM python:3.10-slim
RUN apt update
RUN echo y | apt install gcc
RUN pip install --trusted-host pypi.python.org discord

FROM python:3.10-slim
COPY --from=0 /usr/local/lib/python3.10 /usr/local/lib/python3.10
WORKDIR /app
ADD main.py bot-database.db /app/
CMD ["python", "/app/main.py"]
