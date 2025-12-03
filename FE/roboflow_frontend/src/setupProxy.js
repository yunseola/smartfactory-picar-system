const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function (app) {
  app.use(
    '/api',
    createProxyMiddleware({
      target: 'http://k13e103.p.ssafy.io',
      changeOrigin: true,
      ws: true,
      logLevel: 'debug',
    })
  );

  // WebSocket 프록시를 /ws 경로로 추가
  app.use(
    '/ws',
    createProxyMiddleware({
      target: 'http://k13e103.p.ssafy.io',
      changeOrigin: true,
      ws: true,
      logLevel: 'debug',
    })
  );
};
