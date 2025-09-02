# Ubuntu 22.04 Deployment Guide

This guide deploys the backend with Gunicorn + Nginx and serves the frontend from Nginx. Assumes domain efarmzehunger.com.

## 1) Server prerequisites
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y nginx python3-pip python3-venv git ufw certbot python3-certbot-nginx fail2ban unattended-upgrades
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw --force enable
```

## 2) Upload project
```bash
sudo mkdir -p /opt/bsf-farm && sudo chown $USER:$USER /opt/bsf-farm
cd /opt/bsf-farm
# Clone or copy your code
# git clone YOUR_REPO_URL .
```

## 3) Backend venv and dependencies
```bash
cd /opt/bsf-farm/backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 4) Environment variables
```bash
cat > /opt/bsf-farm/backend/.env << 'EOF'
DB_HOST=YOUR_MANAGED_MYSQL_HOST
DB_USER=YOUR_DB_USER
DB_PASSWORD=YOUR_DB_PASSWORD
DB_NAME=bsf_farm
SECRET_KEY=CHANGE_ME
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=YOUR_GMAIL
EMAIL_HOST_PASSWORD=YOUR_GMAIL_APP_PASSWORD
ADMIN_EMAIL=YOUR_ADMIN_EMAIL
API_DEBUG=false
EOF
```

## 5) systemd service
```bash
sudo cp /opt/bsf-farm/nginx/bsf-farm-ubuntu.service /etc/systemd/system/bsf-farm.service
sudo systemctl daemon-reload
sudo systemctl enable --now bsf-farm
sudo systemctl status bsf-farm | cat
```

## 6) Nginx config (frontend + API proxy)
```bash
sudo mkdir -p /var/www/bsf-frontend
sudo rsync -avh /opt/bsf-farm/frontend/ /var/www/bsf-frontend/
sudo cp /opt/bsf-farm/nginx/bsf-farm-ubuntu.conf /etc/nginx/sites-available/bsf-farm.conf
sudo ln -sf /etc/nginx/sites-available/bsf-farm.conf /etc/nginx/sites-enabled/bsf-farm.conf
sudo nginx -t && sudo systemctl reload nginx
```

## 7) SSL with Let's Encrypt
Make sure DNS for efarmzehunger.com points to this server.
```bash
sudo certbot --nginx -d efarmzehunger.com -d www.efarmzehunger.com --redirect --non-interactive --agree-tos -m YOUR_EMAIL
```

## 8) Database schema (managed MySQL)
Pick latest schema file and import:
```bash
# Example using new_database_schema.sql
mysql -h $DB_HOST -u $DB_USER -p $DB_NAME < /opt/bsf-farm/backend/new_database_schema.sql
```

## 9) Updates / redeploys
```bash
cd /opt/bsf-farm
# git pull (if using git)
cd backend
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart bsf-farm
sudo rsync -avh /opt/bsf-farm/frontend/ /var/www/bsf-frontend/
sudo systemctl reload nginx
```

## 10) Logs and troubleshooting
- App logs: `journalctl -u bsf-farm -f`
- Nginx logs: `/var/log/nginx/access.log`, `/var/log/nginx/error.log`
- Test API: `curl -i http://127.0.0.1:8000/`
- Health check homepage: `curl -I https://efarmzehunger.com`