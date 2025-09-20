FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYENV_ROOT=/home/computeruse/.pyenv
ENV PATH=$PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH
ENV TZ=UTC

# Create user
RUN useradd -m -s /bin/bash computeruse && \
    usermod -aG sudo computeruse && \
    echo 'computeruse ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Basic tools
    curl wget git vim nano sudo \
    build-essential software-properties-common \
    # Python
    python3-pip python3-dev python3-venv \
    # Node.js
    nodejs npm \
    # Desktop environment for computer use
    xvfb x11vnc novnc websockify \
    fluxbox xterm \
    # Computer control tools
    scrot imagemagick xdotool xclip wmctrl \
    # Development tools
    tmux htop net-tools iputils-ping \
    postgresql-client mysql-client redis-tools \
    ripgrep fd-find bat jq \
    # Libraries
    libssl-dev libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Install VS Code Server
RUN curl -fsSL https://code-server.dev/install.sh | sh

# Switch to computeruse user
USER computeruse
WORKDIR /home/computeruse

# Install Python packages
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --user -r /tmp/requirements.txt

# Install global Node packages
USER root
RUN npm install -g \
    typescript ts-node \
    eslint prettier \
    jest mocha chai \
    nodemon pm2

USER computeruse

# Copy application files
COPY --chown=computeruse:computeruse app /home/computeruse/app/

# Set up VNC password
RUN mkdir -p ~/.vnc && \
    x11vnc -storepasswd "password" ~/.vnc/passwd

# Create necessary directories
RUN mkdir -p ~/workspace ~/projects ~/logs

# Entry point
COPY --chown=computeruse:computeruse docker/entrypoint.sh /home/computeruse/
RUN chmod +x /home/computeruse/entrypoint.sh

EXPOSE 5900 6080 8080 8000 8443 9090

ENTRYPOINT ["/home/computeruse/entrypoint.sh"]
