# Use an official Python runtime as a parent image
FROM python:3.10
ENV PYTHONDONTWRITEBYTECODE=1

# Set the working directory in the container
WORKDIR /app

# Install any needed packages specified in pyproject.toml
RUN pip install poetry
RUN poetry config virtualenvs.create false

COPY . .

RUN poetry install
# Run app.py when the container launches
CMD ["poetry", "run", "pytest"]
