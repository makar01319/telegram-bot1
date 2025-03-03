FROM python:3.11-slim AS install

ENV PATH="/root/.local/bin:${PATH}"
ENV PYTHONUNBUFFERED=1

WORKDIR /root
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN apt-get update && \
    apt-get install curl -y --no-install-recommends

COPY requirements.txt .


FROM python:3.11-slim AS base

ENV PYTHONPATH="/app"

WORKDIR /app

RUN groupadd -g 5000 container && useradd -d /app -m -g container -u 5000 container
COPY --from=install /root/requirements.txt ./
RUN pip --no-cache-dir install -U pip && \
    pip --no-cache-dir install -r requirements.txt dumb-init==1.2.5.post1
COPY . .

FROM base AS final

RUN chown -R 5000:5000 /app
USER container

CMD ["dumb-init", "python", "bot_42.py"]
