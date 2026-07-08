# Provision redis on local computer

docker run -p 6379:6379 --name redis -d redis

# URL

https://flutter.ottawastem.com/chat/
https://flutter.ottawastem.com/chat/lobby/

# Test WebSocket

## wss

curl -H 'Upgrade: websocket' \
 -H "Sec-WebSocket-Key: `openssl rand -base64 16`" \
 -H 'Sec-WebSocket-Version: 13' \
 --http1.1 \
 -sSv \
 https://ws.ifelse.io

curl -H 'Upgrade: websocket' \
 -H "Sec-WebSocket-Key: `openssl rand -base64 16`" \
 -H 'Sec-WebSocket-Version: 13' \
 --http1.1 \
 -sSv \
 https://flutter.ottawastem.com/ws/chat/lobby/
