# Mosquitto MQTT Broker Configuration

This directory contains configuration files for the Mosquitto MQTT broker used by Home Assistant and other IoT devices.

## Files

- **mosquitto.conf**: Main broker configuration
- **passwd**: Password file (created during deployment, not in version control)
- **acl**: Access Control List for topic permissions (optional, not created by default)

## Initial Setup

### 1. Create Password File

The password file is required for authentication and must be created before starting the broker.

```bash
# Navigate to the configs directory
cd projects/06-homelab/PRJ-HOME-002/assets/configs/

# Create password file using Docker
docker run --rm -v $(pwd)/mosquitto:/mosquitto eclipse-mosquitto:2.0 \
  sh -c "mosquitto_passwd -c -b /mosquitto/passwd \${MQTT_USERNAME:-homeassistant} \${MQTT_PASSWORD:-changeme}"
```

**Note**: Replace `changeme` with your actual MQTT password from `.env` file.

### 2. Add Additional Users

To add more users without overwriting the existing file:

```bash
# Add user (interactive, prompts for password)
docker run --rm -v $(pwd)/mosquitto:/mosquitto eclipse-mosquitto:2.0 \
  mosquitto_passwd /mosquitto/passwd zigbee2mqtt

# Add user (non-interactive, password in command)
docker run --rm -v $(pwd)/mosquitto:/mosquitto eclipse-mosquitto:2.0 \
  mosquitto_passwd -b /mosquitto/passwd tasmota strongpassword123
```

### 3. Verify Password File

```bash
# Check password file contents
cat mosquitto/passwd

# Should show entries like:
# homeassistant:$7$101$...
# zigbee2mqtt:$7$101$...
```

## Access Control List (Optional)

For fine-grained topic permissions, create an ACL file:

```bash
cat > mosquitto/acl << 'EOF'
# Admin user (full access)
user admin
topic readwrite #

# Home Assistant (read/write to all topics)
user homeassistant
topic readwrite #

# Zigbee2MQTT (restricted to zigbee2mqtt topics)
user zigbee2mqtt
topic readwrite zigbee2mqtt/#
topic read homeassistant/#

# Tasmota devices (restricted to tasmota topics)
user tasmota
topic readwrite tasmota/#
EOF
```

Then uncomment the `acl_file` line in `mosquitto.conf`.

## Testing

### Test Connection

```bash
# Subscribe to all topics (wait for messages)
docker exec -it mosquitto mosquitto_sub -t '#' -u homeassistant -P yourpassword

# In another terminal, publish a test message
docker exec -it mosquitto mosquitto_pub -t 'test/topic' -m 'Hello MQTT' -u homeassistant -P yourpassword
```

### Monitor System Topics

```bash
# View broker statistics
docker exec -it mosquitto mosquitto_sub -t '$SYS/#' -u homeassistant -P yourpassword -C 10
```

## Common Issues

### Authentication Failures

**Symptom**: Clients can't connect, logs show "Connection refused: not authorized"

**Solutions**:
1. Verify password file exists: `ls -la mosquitto/passwd`
2. Check password is correct: Recreate password file
3. Ensure `allow_anonymous false` in `mosquitto.conf`
4. Check logs: `docker logs mosquitto | grep "refused"`

### Connection Timeouts

**Symptom**: Clients connect but disconnect immediately

**Solutions**:
1. Check firewall rules: `sudo ufw status`
2. Verify port mapping: `docker compose ps`
3. Test connection: `telnet localhost 1883`
4. Check logs: `docker logs mosquitto | grep "Error"`

### Retained Messages Not Persisting

**Symptom**: Retained messages lost after broker restart

**Solutions**:
1. Verify persistence enabled: `grep persistence mosquitto/mosquitto.conf`
2. Check volume mount: `docker inspect mosquitto | grep Mounts`
3. Check disk space: `df -h /var/lib/docker/volumes`
4. Force save: `docker exec mosquitto mosquitto_sub -t '$SYS/broker/clients/total' -C 1`

## Security Best Practices

1. **Use Strong Passwords**: Generate with `openssl rand -base64 32`
2. **Enable TLS/SSL**: Uncomment TLS listener in `mosquitto.conf` for external access
3. **Restrict Network Access**: Use firewall rules to limit port 1883 to local network
4. **Implement ACLs**: Limit topic access per user/device
5. **Rotate Passwords Annually**: Update password file and restart broker
6. **Monitor Logs**: Regularly check for failed authentication attempts
7. **Update Regularly**: Keep Mosquitto updated to latest version

## Backup and Recovery

### Backup

```bash
# Backup persistence data (retained messages, subscriptions)
docker run --rm -v mosquitto-data:/data -v $(pwd):/backup alpine \
  tar czf /backup/mosquitto-data-$(date +%Y%m%d).tar.gz -C /data .

# Backup configuration
cp -r mosquitto mosquitto-backup-$(date +%Y%m%d)
```

### Restore

```bash
# Restore persistence data
docker run --rm -v mosquitto-data:/data -v $(pwd):/backup alpine \
  tar xzf /backup/mosquitto-data-20240101.tar.gz -C /data

# Restart broker
docker compose restart mosquitto
```

## References

- [Mosquitto Documentation](https://mosquitto.org/documentation/)
- [MQTT Protocol Specification](https://mqtt.org/mqtt-specification/)
- [Home Assistant MQTT Integration](https://www.home-assistant.io/integrations/mqtt/)
- [Zigbee2MQTT Configuration](https://www.zigbee2mqtt.io/guide/configuration/)
