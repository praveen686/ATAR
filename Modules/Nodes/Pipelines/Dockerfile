# Use the miniconda3 as base image
FROM continuumio/miniconda3

# Pass build arguments
ARG YML_ENV_NAME
ARG GITHUB_KEY

# Set the working directory to /app
WORKDIR /app

COPY app.py /app

# Create the environment:
COPY ${YML_ENV_NAME}.yml .
RUN conda env create -f ${YML_ENV_NAME}.yml && rm ${YML_ENV_NAME}.yml

ENV YML_ENV_NAME=${YML_ENV_NAME}

# Install additional packages
#...

# Make port 80 available to the world outside this container
EXPOSE ${PORT}

# Run main.py when the container launches
ENTRYPOINT ["/bin/bash", "-c", "conda run --no-capture-output -n ${YML_ENV_NAME} uvicorn app:app --host 0.0.0.0 --port ${PORT}"]
