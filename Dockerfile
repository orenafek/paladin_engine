## Backend
### Install poetry
#RUN curl -sSL https://install.python-poetry.org | python3 -
#RUN echo "export PATH=$PATH:$HOME/.local/bin" >> $HOME/.bashrc
#
## Download and build backend libs.
#RUN poetry install
#
## Frontend
### Download nvm & node.
#RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash
#RUN nvm install node
#
## build wabsite.
#RUN make all

# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

RUN ls /app

# Install curl and other necessary packages
RUN apt-get update && \
    apt-get install -y curl && \
    apt-get install -y build-essential

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="~/.local/bin:${PATH}"

# Install dependencies using Poetry
RUN ~/.local/bin/poetry install --no-root --no-interaction

# Install Node.js and npm
RUN curl -sL https://deb.nodesource.com/setup_21.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g npm@latest

# Install nvm (Node Version Manager)
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash

# Use nvm to install the desired Node.js version
RUN bash -c "source $HOME/.nvm/nvm.sh && nvm install 21.7.1 && nvm use 21.7.1"

# Install Vue CLI
RUN npm install -g @vue/cli

# Change directory to frontend and install dependencies
WORKDIR /app/PaladinUI/paladin_server
RUN npm install

# Change directory back to the root of the app
WORKDIR /app

# Build the Vue.js frontend
RUN make all

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV FLASK_APP=app.py

# Run the script to start the application
CMD ["./run_paladin.sh"]
