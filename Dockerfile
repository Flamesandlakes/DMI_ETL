FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1

# ?
WORKDIR /app

# ?
COPY . /app

# install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5432

# for data persistence
# VOLUME /var/lib/postgresql/data 

# ?
ENV PYTHONPATH=/app/src
CMD ["python", "src/dmi_etl/main.py"]

