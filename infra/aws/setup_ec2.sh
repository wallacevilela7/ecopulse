#!/usr/bin/env bash
# ==============================================================================
# EcoPulse - Script de Inicialização da Instância AWS EC2 (Ubuntu 24.04 LTS)
# ==============================================================================
set -e

echo "[1/4] Atualizando pacotes do sistema..."
sudo apt update && sudo apt upgrade -y

echo "[2/4] Instalando Docker e Docker Compose..."
sudo apt install -y ca-certificates curl gnupg lsb-release
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

echo "[3/4] Configurando permissões do usuário ubuntu..."
sudo usermod -aG docker ubuntu

echo "[4/4] Verificando instalação..."
docker --version
docker compose version

echo "=============================================================================="
echo "Instalação concluída com sucesso! Faça logout e login novamente para ativar o Docker sem sudo."
echo "=============================================================================="
