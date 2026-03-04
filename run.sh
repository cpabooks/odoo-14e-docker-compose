#!/bin/bash
DESTINATION=$1
PORT=$2
CHAT=$3

# Clone Odoo directory
git clone --depth=1 https://github.com/cpabooks/odoo-14e-docker-compose $DESTINATION
rm -rf $DESTINATION/.git

# Create PostgreSQL directory
mkdir -p $DESTINATION/postgresql

# Change ownership to current user and set restrictive permissions for security
sudo chown -R $USER:$USER $DESTINATION
sudo chmod -R 700 $DESTINATION  # Only the user has access

# Check if running on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
  echo "Running on macOS. Skipping inotify configuration."
else
  # System configuration
  if grep -qF "fs.inotify.max_user_watches" /etc/sysctl.conf; then
    echo $(grep -F "fs.inotify.max_user_watches" /etc/sysctl.conf)
  else
    echo "fs.inotify.max_user_watches = 524288" | sudo tee -a /etc/sysctl.conf
  fi
  sudo sysctl -p
fi

# Set ports in docker-compose.yml
# Update docker-compose configuration
if [[ "$OSTYPE" == "darwin"* ]]; then
  # macOS sed syntax
  sed -i '' 's/10014/'$PORT'/g' $DESTINATION/docker-compose.yml
  sed -i '' 's/20014/'$CHAT'/g' $DESTINATION/docker-compose.yml
else
  # Linux sed syntax
  sed -i 's/10014/'$PORT'/g' $DESTINATION/docker-compose.yml
  sed -i 's/20014/'$CHAT'/g' $DESTINATION/docker-compose.yml
fi

# Set file and directory permissions after installation
find $DESTINATION -type f -exec chmod 644 {} \;
find $DESTINATION -type d -exec chmod 755 {} \;

chmod +x $DESTINATION/entrypoint.sh

# Run Odoo
if docker compose version &>/dev/null 2>&1; then
  docker compose -f $DESTINATION/docker-compose.yml up -d
elif command -v docker-compose &>/dev/null; then
  docker-compose -f $DESTINATION/docker-compose.yml up -d
else
  echo "Error: Neither 'docker compose' nor 'docker-compose' found."
  exit 1
fi
ETH0_IP=$(ip addr show eth0 | grep 'inet ' | head -1 | awk '{print $2}' | cut -d'/' -f1)

RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m' # No Color / Reset

echo -e "Odoo started at ${RED}${BOLD}http://$ETH0_IP:$PORT${NC} | Live chat port: ${RED}${BOLD}$CHAT${NC}"
echo -e "Odoo Database Manager: ${RED}${BOLD}http://$ETH0_IP:$PORT/web/database/manager${NC} | Master Password: ${RED}${BOLD}CnvvV46UGZb2=N${NC}"
docker ps -a | grep "$DESTINATION-odoo14-1"


#echo "Odoo started at http://$ETH0_IP:$PORT | Live chat port: $CHAT"
#echo "Odoo Database Manager can be found http://$ETH0_IP:$PORT/web/database/manager | Master Password: CnvvV46UGZb2=N"
#docker ps -a | grep "$DESTINATION-odoo14-1"
