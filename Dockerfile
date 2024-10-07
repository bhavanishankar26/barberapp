# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /code

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /code
COPY . /code/

# Expose port 8000 to the outside world
EXPOSE 8000
ENTRYPOINT ["bash", "/code/entrypoint.sh"]

# Run the Django app using gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "provisioning.wsgi:application"]
