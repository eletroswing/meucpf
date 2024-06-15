import "dotenv/config";
import Redis from "ioredis";
import {WebSocketServer} from "ws";

const redisPublisher = new Redis(process.env.REDIS_URL);
const redisSubscriber = new Redis(process.env.REDIS_URL);

const users = {
  "usuario1": 1
};

const wss = new WebSocketServer({ port: 8080 });

const userConnections = new Map();

wss.on('connection', function connection(ws, req) {
    const token = (req.headers['authorization'] || req.headers['Authorization']).replace('Bearer ', '');

    if(!token || !users[token]) {
        ws.send(JSON.stringify({error: {message: "missing or invalid authorization header", code: 403}}))
        ws.close(4000,"missing authorization header")
        return
    }
    
    userConnections.set(users[token], ws)

    ws.on('message', function incoming(message) {
        try {
          const data = JSON.parse(message);
          const { event, payload } = data;
          if (event === 'cpf') {
            const { cpf, data_de_nascimento, id } = payload;
            redisPublisher.publish('incoming_events', JSON.stringify({ cpf, date: data_de_nascimento, id: `${id}-${users[token]}` }));
          }
        } catch (error) {
          ws.send(JSON.stringify({ error: 'Erro ao processar mensagem' }));
        }
      });

      
    ws.on('close', function close() {
        userConnections.forEach((connection, userId) => {
            if (connection === ws) {
              userConnections.delete(userId);
            }
          });
    })
});

redisSubscriber.subscribe('processed_events', (err, count) => {
  if (err) {
    console.error('Erro ao se inscrever no canal Redis:', err);
    return;
  }
  console.log(`Inscrito no canal Redis: processed_events`);
});

redisSubscriber.on('message', (channel, message) => {
  if (channel === 'processed_events') {
    const { id, data } = JSON.parse(message);
    const parsedId = id.split("-")
    
    const ws = userConnections.get(Number(parsedId[1]));
    if (ws) {
      ws.send(JSON.stringify({ event: 'processed_event', id: parsedId[0], data: data}));
    } 
  }
});

console.log('Servidor WebSocket iniciado na porta 8080.');
