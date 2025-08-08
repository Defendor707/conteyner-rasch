FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive

# Sistem paketlari: R, curl va kerakli dev kutubxonalar
RUN apt-get update && apt-get install -y \
    r-base \
    r-base-dev \
    libcurl4-openssl-dev \
    libssl-dev \
    libxml2-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# R paketlari (faqat keraklilari)
RUN R -e "install.packages(c('ltm', 'ggplot2', 'dplyr'), repos='https://cran.rstudio.com/')"

# Ish papkasi
WORKDIR /app

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Loyiha fayllari
COPY . .

# Ma'lumotlar va loglar
RUN mkdir -p data logs

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
