FROM python:3.13-slim-bookworm AS base

#
# Fetch requirements
#
FROM base AS builder
RUN apt-get -qq update \
    && apt-get install -y --no-install-recommends libpq-dev g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app/
COPY ./requirements.txt ./

RUN pip install --upgrade pip
RUN pip install --prefix="/reqs" -r requirements.txt

#
# Runtime
#
FROM base AS runtime

RUN apt-get -qq update \
    && apt-get install -y --no-install-recommends libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app/
COPY --from=builder /reqs /usr/local
COPY ./ ./

RUN opentelemetry-bootstrap -a install

EXPOSE 8080
ENTRYPOINT [ "opentelemetry-instrument", "python", "app.py" ]
