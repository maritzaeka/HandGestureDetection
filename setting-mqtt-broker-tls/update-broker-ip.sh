#!/bin/bash

NEW_IP=$(hostname -I | awk '{print $1}')
echo "Current IP: $NEW_IP"

# Update SAN config
sudo sed -i "s/^IP\.2 = .*/IP.2 = $NEW_IP/" /etc/mosquitto/certs/san.cnf

# Backup old cert
sudo cp /etc/mosquitto/certs/server.crt /etc/mosquitto/certs/server.crt.backup-$(date +%Y%m%d-%H%M%S)
sudo cp /etc/mosquitto/certs/server.key /etc/mosquitto/certs/server.key.backup-$(date +%Y%m%d-%H%M%S)

# Regenerate certificate
cd /etc/mosquitto/certs
sudo openssl genrsa -out server.key 2048
sudo openssl req -new -key server.key -out server.csr -config san.cnf
sudo openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 3650 -extensions v3_req -extfile san.cnf

# Set permissions
sudo chown root:mosquitto server.key
sudo chmod 640 server.key
sudo chmod 644 server.crt

# Restart Mosquitto
sudo systemctl restart mosquitto

echo "Certificate updated with IP: $NEW_IP"
echo "Remember to update ESP8266 code with new IP and re-upload!"