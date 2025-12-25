# ?? Production Deployment Guide

## Overview

WhereSpace can be deployed to a production server using the built-in deployment wizard. This guide covers the complete deployment process.

---

## Prerequisites

### Local Machine Requirements
- Python 3.8+
- SSH client
- Git (for version control)
- Access to your production server

### Production Server Requirements
- Linux server (Ubuntu 20.04+ recommended)
- Python 3.8+
- PostgreSQL 14+ with pgvector extension
- Ollama installed and running
- Nginx or Apache (for reverse proxy)
- SSL certificate (for HTTPS)
- At least 4GB RAM, 20GB disk space

---

## Quick Start

### 1. Access Deployment Menu

```bash
python main.py
# Select option: 6. ?? Deploy naar productie
```

### 2. Configure Parameters

The deployment wizard will guide you through configuring:

#### Server Configuration
- **server_host**: Production server hostname or IP
- **server_port**: SSH port (default: 22)
- **server_user**: SSH username
- **server_ssh_key**: Path to SSH private key

#### Database Configuration
- **db_host**: PostgreSQL hostname
- **db_port**: PostgreSQL port (default: 5432)
- **db_name**: Database name (default: vectordb)
- **db_user**: Database username
- **db_password**: Database password

#### Ollama Configuration
- **ollama_host**: Ollama API hostname
- **ollama_port**: Ollama API port (default: 11434)
- **ollama_models**: Models to install (comma-separated)

#### Application Configuration
- **app_domain**: Your domain name
- **app_port**: Application port (default: 5000)
- **app_secret_key**: Flask secret key (can auto-generate)
- **use_https**: Enable HTTPS

#### Deployment Settings
- **deployment_path**: Server directory (e.g., /opt/wherespace)
- **backup_enabled**: Create backup before deployment
- **auto_restart**: Auto-restart services after deployment
- **notification_email**: Email for notifications (optional)

---

## Step-by-Step Deployment

### Step 1: Prepare Server

On your production server:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3 python3-pip python3-venv -y

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Install pgvector extension
sudo apt install postgresql-14-pgvector -y

# Install Ollama
curl https://ollama.ai/install.sh | sh

# Start Ollama
ollama serve &

# Pull required models
ollama pull llama3.1
ollama pull nomic-embed-text
```

### Step 2: Setup Database

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE vectordb;
CREATE USER wherespace_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE vectordb TO wherespace_user;

# Enable pgvector
\c vectordb
CREATE EXTENSION vector;

\q
```

### Step 3: Configure SSH Access

On your local machine:

```bash
# Generate SSH key if you don't have one
ssh-keygen -t ed25519 -f ~/.ssh/wherespace_deploy

# Copy public key to server
ssh-copy-id -i ~/.ssh/wherespace_deploy.pub user@your-server.com

# Test connection
ssh -i ~/.ssh/wherespace_deploy user@your-server.com
```

### Step 4: Run Deployment Wizard

```bash
# Start the application
python main.py

# Select option 6: Deploy to production
# Follow the interactive prompts to configure all parameters
```

### Step 5: Configure Parameters

In the deployment wizard:

1. **Select each parameter by number** (1-20)
2. **Enter the value** when prompted
3. **Validation happens automatically**
4. **Save configuration** by typing `s`
5. **Deploy** by typing `d` when all parameters are set

### Step 6: Pre-Deployment Checks

The system automatically runs these checks:

- ? SSH key accessibility
- ? Local dependencies installed
- ? Configuration completeness
- ? Server connectivity test

### Step 7: Deploy

If all checks pass:

1. System shows deployment summary
2. Type `DEPLOY` to confirm
3. Deployment proceeds automatically
4. Monitor progress in terminal

---

## Configuration Management

### Save Configuration

Configuration is automatically saved to:
```
config/deployment_config.json
```

### Load Previous Configuration

The deployment wizard automatically loads saved configuration on startup.

### Backup Configuration

```bash
# Backup configuration
cp config/deployment_config.json config/deployment_config.backup.json

# Restore from backup
cp config/deployment_config.backup.json config/deployment_config.json
```

---

## Parameter Reference

### Server Configuration

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| server_host | string | Yes | Production server hostname or IP |
| server_port | int | Yes | SSH port (default: 22) |
| server_user | string | Yes | SSH username for deployment |
| server_ssh_key | string | Yes | Path to SSH private key file |

### Database Configuration

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| db_host | string | Yes | PostgreSQL hostname or IP |
| db_port | int | No | PostgreSQL port (default: 5432) |
| db_name | string | No | Database name (default: vectordb) |
| db_user | string | Yes | Database username |
| db_password | string | Yes | Database password (min 8 chars) |

### Ollama Configuration

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| ollama_host | string | Yes | Ollama API hostname or IP |
| ollama_port | int | No | Ollama API port (default: 11434) |
| ollama_models | list | No | Models to install (default: llama3.1, nomic-embed-text) |

### Application Configuration

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| app_domain | string | Yes | Application domain (e.g., wherespace.example.com) |
| app_port | int | No | Application port (default: 5000) |
| app_secret_key | string | Yes | Flask secret key (can auto-generate) |
| use_https | bool | No | Enable HTTPS (default: true) |

### Deployment Settings

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| deployment_path | string | No | Server directory (default: /opt/wherespace) |
| backup_enabled | bool | No | Create backup before deployment (default: true) |
| auto_restart | bool | No | Auto-restart services (default: true) |
| notification_email | string | No | Email for deployment notifications (optional) |

---

## Validation Rules

### Hostname/IP Validation
- Must be valid hostname or IPv4 address
- Examples: `example.com`, `192.168.1.100`

### Port Validation
- Must be integer between 1 and 65535

### SSH Key Validation
- File must exist at specified path
- Must be a regular file (not directory)

### Domain Validation
- Must be valid domain name format
- Examples: `wherespace.example.com`, `app.example.com`

### Email Validation (Optional)
- Must be valid email format
- Example: `admin@example.com`

### Password/Secret Validation
- Minimum 8 characters
- No maximum length

---

## Deployment Process

### What Happens During Deployment

1. **Pre-Deployment Checks**
   - Verify SSH connectivity
   - Check server access
   - Validate configuration

2. **Backup Creation** (if enabled)
   - Backup existing deployment
   - Store in dated directory

3. **File Upload**
   - Transfer application files
   - Upload dependencies
   - Copy configuration

4. **Dependency Installation**
   - Install Python packages
   - Setup virtual environment

5. **Database Setup**
   - Run migrations
   - Initialize schema
   - Create indexes

6. **Ollama Configuration**
   - Pull required models
   - Configure API access

7. **Web Server Setup**
   - Configure Nginx/Apache
   - Setup SSL certificates
   - Configure reverse proxy

8. **Service Management** (if auto-restart enabled)
   - Start/restart services
   - Enable auto-start on boot

9. **Health Checks**
   - Verify application is running
   - Test database connectivity
   - Check Ollama API

10. **Notifications** (if configured)
    - Send deployment success email

---

## Troubleshooting

### SSH Connection Fails

```bash
# Test SSH connection manually
ssh -i ~/.ssh/your_key user@server -v

# Check SSH key permissions
chmod 600 ~/.ssh/your_key

# Add key to SSH agent
eval $(ssh-agent)
ssh-add ~/.ssh/your_key
```

### Database Connection Fails

```bash
# Test database connection
psql -h your-db-host -U your-db-user -d vectordb

# Check PostgreSQL is running
sudo systemctl status postgresql

# Check PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-14-main.log
```

### Ollama Not Responding

```bash
# Check Ollama status
ollama list

# Restart Ollama
pkill ollama
ollama serve &

# Check Ollama logs
journalctl -u ollama -f
```

### Port Already in Use

```bash
# Find process using port
sudo lsof -i :5000

# Kill process if needed
sudo kill -9 <PID>

# Or change app_port in configuration
```

---

## Security Best Practices

### 1. SSH Key Security
- Use Ed25519 keys (recommended)
- Never share private keys
- Use passphrase-protected keys
- Restrict key file permissions (600)

### 2. Database Security
- Use strong passwords (16+ characters)
- Create dedicated database user
- Limit database user permissions
- Use SSL for database connections

### 3. Application Security
- Generate strong secret key
- Use HTTPS in production
- Keep dependencies updated
- Regular security audits

### 4. Server Security
- Keep system updated
- Configure firewall (ufw)
- Disable root SSH login
- Use fail2ban for SSH protection
- Regular backups

---

## Post-Deployment

### Verify Deployment

```bash
# Check application status
curl https://your-domain.com/api/status

# Check database
psql -h localhost -U wherespace_user -d vectordb -c "\dt"

# Check Ollama
curl http://localhost:11434/api/tags
```

### Monitor Application

```bash
# View application logs
sudo journalctl -u wherespace -f

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# View database logs
sudo tail -f /var/log/postgresql/postgresql-14-main.log
```

### Setup Monitoring (Optional)

Consider setting up:
- **Uptime monitoring** (UptimeRobot, Pingdom)
- **Error tracking** (Sentry)
- **Performance monitoring** (New Relic, Datadog)
- **Log aggregation** (ELK Stack, Splunk)

---

## Rollback Procedure

If deployment fails or issues occur:

### Automatic Rollback

```bash
# Deployment creates backups automatically
# Restore from backup:
cd /opt/wherespace
mv current current.failed
mv backup.YYYY-MM-DD current
sudo systemctl restart wherespace
```

### Manual Rollback

```bash
# Stop services
sudo systemctl stop wherespace

# Restore previous version
cd /opt/wherespace
rm -rf current
cp -r previous_version current

# Restart services
sudo systemctl start wherespace
```

---

## Update Deployment

To update an existing deployment:

```bash
# Run deployment wizard
python main.py
# Select option 6

# Load existing configuration (automatic)
# Make any necessary changes
# Deploy updates
```

---

## Support

For deployment issues:

1. Check this guide
2. Review logs on server
3. Test connectivity manually
4. Open GitHub issue: https://github.com/jwvanderstam/WhereSpace/issues

---

**Last Updated**: December 24, 2025  
**Version**: 1.0.0
