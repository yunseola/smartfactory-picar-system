// src/api/webSocketClient.js
import SockJS from "sockjs-client";
import { Client } from "@stomp/stompjs";

const createWebSocketClient = () => {
  // 🔴 기존: k13e103.p.ssafy.io 로 직접 나가고 있었음
  const socketFactory = () => new SockJS("http://k13e103.p.ssafy.io/ws");

  // ✅ 수정: 일단 로컬 백엔드로 붙이기
  //const socketFactory = () => new SockJS("http://localhost:8080/ws");

  const client = new Client({
    webSocketFactory: socketFactory,
    reconnectDelay: 5000,
    debug: (msg) => {
      console.log("[STOMP DEBUG]", msg);
    },
  });

  let kpiHandler = null;
  let envHandler = null;
  let logHandler = null;

  client.onConnect = () => {
    console.log("[STOMP] connected");

    client.subscribe("/topic/kpi-summary", (message) => {
      if (!kpiHandler) return;
      try {
        const body = JSON.parse(message.body);
        kpiHandler(body);
      } catch (e) {
        console.error("[STOMP] KPI message parse error", e);
      }
    });

    client.subscribe("/topic/environment", (message) => {
      if (!envHandler) return;
      try {
        const body = JSON.parse(message.body);
        envHandler(body);
      } catch (e) {
        console.error("[STOMP] ENV message parse error", e);
      }
    });

    client.subscribe("/topic/eventlog", (message) => {
      if (!logHandler) return;
      try {
        const body = JSON.parse(message.body);
        logHandler(body);
      } catch (e) {
        console.error("[STOMP] EVENTLOG message parse error", e);
      }
    });
  };

  client.onStompError = (frame) => {
    console.error("[STOMP] broker error:", frame.headers["message"]);
  };

  client.onWebSocketError = (event) => {
    console.error("[STOMP] websocket error:", event);
  };

  client.activate();

  return {
    onConnect: (onKpi, onEnv, onLog) => {
      kpiHandler = typeof onKpi === "function" ? onKpi : null;
      envHandler = typeof onEnv === "function" ? onEnv : null;
      logHandler = typeof onLog === "function" ? onLog : null;
    },
    deactivate: () => {
      try {
        client.deactivate();
      } catch (e) {
        console.error("[STOMP] deactivate error", e);
      }
    },
  };
};

export default createWebSocketClient;
