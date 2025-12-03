package com.ssafy.roboflow.config;

import org.springframework.web.socket.WebSocketHandler;
import org.springframework.web.socket.WebSocketSession;
import org.springframework.web.socket.TextMessage;
import org.springframework.web.socket.handler.TextWebSocketHandler;

public class MyWebSocketHandler extends TextWebSocketHandler {

    @Override
    public void handleTextMessage(WebSocketSession session, TextMessage message) throws Exception {
        // 클라이언트로부터 메시지를 받으면 처리하고, 응답을 보냄
        String clientMessage = message.getPayload();
        System.out.println("Received message: " + clientMessage);

        // 클라이언트에게 응답 전송
        session.sendMessage(new TextMessage("Message received: " + clientMessage));
    }
}
