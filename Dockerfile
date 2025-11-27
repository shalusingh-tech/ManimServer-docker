FROM python:3.11-slim

WORKDIR /app

# Install system dependencies required by Manim + LaTeX + OpenGL
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libcairo2-dev \
    libpango1.0-dev \
    build-essential \
    pkg-config \
    # ---- LaTeX for Manim ----
    texlive-latex-base \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-science \
    texlive-xetex \
    dvisvgm \
    latexmk \
    # ---- OpenGL system libs (for GPU renderer) ----
    libgl1 \
    libgl-dev \
    libglu1-mesa \
    libglu1-mesa-dev \
    freeglut3-dev \
    # -----------------------------------------------
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirement.txt .

# Install Python dependencies
# NOTE: manim[opengl] installs extra Python libs for GPU/OpenGL rendering
RUN pip install --no-cache-dir fastmcp "manim[opengl]"

# Copy the server file
COPY manim_server.py .

# Create media directory for Manim output
RUN mkdir -p /app/media /app/media/manim_tmp

# Ensure unbuffered output for stdio
ENV PYTHONUNBUFFERED=1

# Run the server
CMD ["python", "manim_server.py"]
