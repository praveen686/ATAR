Setting up separate environments using Docker, Conda, and Pip involves creating several configuration files that define the necessary dependencies and setup steps for each environment. Below, I'll provide examples of what each file might contain.

1. **Dockerfile**: The Dockerfile is used to create a Docker image of your environment. Here's a very simple example of a Dockerfile that creates a Python environment with pip:

```Dockerfile
# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Run app.py when the container launches
CMD ["python", "app.py"]
```

In a Conda-based Dockerfile, you might include instructions for setting up a Conda environment:

```Dockerfile
# Use an official miniconda3 as base image
FROM continuumio/miniconda3

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

# Create and activate the conda environment
RUN conda env create -f environment.yml
SHELL ["conda", "run", "-n", "myenv", "/bin/bash", "-c"]

EXPOSE 80
CMD ["python", "app.py"]
```

2. **requirements.txt**: This file is used by pip to install Python packages. Here's a simple example:

```requirements.txt
numpy==1.21.2
pandas==1.3.2
scikit-learn==0.24.2
```

3. **environment.yml**: This file is used by Conda to create a new environment. Here's a simple example:

```environment.yml
name: myenv
channels:
  - defaults
dependencies:
  - numpy=1.21.2
  - pandas=1.3.2
  - scikit-learn=0.24.2
  - pip:
    - some-pip-package==1.0.0
```

To create and use these files, you would:

1. Create a Dockerfile in the root directory of your application.
2. Create either `requirements.txt` or `environment.yml` depending on whether you are using pip or Conda.
3. Build the Docker image from the Dockerfile with `docker build -t your-image-name .`.
4. Run the Docker container with `docker run -p 4000:80 your-image-name`.

Please replace the example Python packages and versions with the ones you actually need. You should also replace `app.py` with the script you want to run when the Docker container launches.