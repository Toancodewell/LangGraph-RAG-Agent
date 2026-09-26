# Jenkins LTS + Docker CLI + docker compose plugin
# Cần Docker CLI bên trong Jenkins để pipeline chạy `docker compose build/up`
# (nói chuyện với Docker của máy host qua docker.sock).
FROM jenkins/jenkins:lts-jdk17

USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates curl gnupg lsb-release \
    && install -m 0755 -d /etc/apt/keyrings \
    && curl -fsSL https://download.docker.com/linux/debian/gpg \
        | gpg --dearmor -o /etc/apt/keyrings/docker.gpg \
    && chmod a+r /etc/apt/keyrings/docker.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" \
        > /etc/apt/sources.list.d/docker.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        docker-ce-cli docker-compose-plugin \
    && rm -rf /var/lib/apt/lists/*

# Chạy như root để truy cập docker.sock của host dễ dàng (phù hợp môi trường học/local).
USER root
