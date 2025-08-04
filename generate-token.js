const jwt = require('jsonwebtoken');

const apiKey = 'devkey';
const apiSecret = 'secret';

const payload = {
  video: {
    room: 'voice-agent-room',
    roomJoin: true,
    canPublish: true,
    canSubscribe: true
  },
  metadata: JSON.stringify({ name: 'Test User' }),
  iss: apiKey,
  sub: 'test-user',
  exp: Math.floor(Date.now() / 1000) + 86400 // 24 hours
};

const token = jwt.sign(payload, apiSecret);
console.log(token); 