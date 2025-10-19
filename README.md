# mc-server
 A minecraft server runner.
```
java -Xmx8G -Xms4G -jar server.jar nogui
```

# DuckDNS
1. Make directory
```
mkdir duckdns
cd duckdns
nvim duck.sh
```
2. Add to duck.sh
```
echo url="https://www.duckdns.org/update?domains=mcserverhashir&token=bdcbebe1-cd6c-48f7-90b3-ace359bfb4e8&ip=" | curl -k -o ~/duckdns/duck.log -K -
```
3. Add perms to duck.sh
```
chmod 700 duck.sh
```
4. Cron job
```
crontab -e
```
Add to bottom of the cron job
```
*/5 * * * * ~/duckdns/duck.sh >/dev/null 2>&1
```
5. Run the job
```
./duck.sh
```
6. Join Minecraft
```
mcserverhashir.duckdns.org:25565
```
# Port Forwarding
Allow firewall
```
sudo ufw allow 25565/tcp
```

