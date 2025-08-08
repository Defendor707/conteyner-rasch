FROM python:3.11-slim

# R dasturini o'rnatish
RUN apt-get update && apt-get install -y \
    r-base \
    r-base-dev \
    libcurl4-openssl-dev \
    libssl-dev \
    libxml2-dev \
    libgdal-dev \
    libproj-dev \
    libgeos-dev \
    && rm -rf /var/lib/apt/lists/*

# R paketlarini o'rnatish
RUN R -e "install.packages(c('ltm', 'ggplot2', 'dplyr', 'reshape2'), repos='https://cran.rstudio.com/')"

# Ish papkasini yaratish
WORKDIR /app

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Loyiha fayllarini ko'chirish
COPY . .

# Ma'lumotlar va log papkalarini yaratish
RUN mkdir -p data logs

# Port ochish
EXPOSE 8000

# Ishga tushirish
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
