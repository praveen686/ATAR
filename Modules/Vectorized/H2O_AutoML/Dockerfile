# Use a Python base image
FROM python:3.8-slim-buster
#FROM openjdk:11

# Set the working directory in the container
WORKDIR /app

# Copy the code to the container
COPY . /app

# Build the wheel
RUN apt-get update \
        && apt-get install -y openjdk-11-jre-headless \
    && apt-get install -y zip \
    && rm -rf /var/lib/apt/lists/*
RUN zip -r --exclude=".git/*" --exclude="/venv/*" --exclude="*.csv" --exclude="*__pycache__/*" $(basename $(pwd)).qz .

# Set up the virtual environment and install dependencies
RUN python3 -m venv venv
RUN ./venv/bin/pip install -U pip
RUN ./venv/bin/pip install wheel
RUN ./venv/bin/pip install -r requirements.txt

# Install dependencies on the active python environment
RUN pip install -r requirements.txt

# Clean up
RUN rm -rf dist venv *.whl *.qz

EXPOSE ${PORT}

# Set the default command to run the application
CMD ./venv/bin/wave run src/app.py
