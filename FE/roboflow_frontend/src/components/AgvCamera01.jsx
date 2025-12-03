// src/components/AgvCamera01.jsx
import React, { useEffect, useRef } from "react";

const API_BASE = (process.env.REACT_APP_API_BASE || "http://k13e103.p.ssafy.io").replace(/\/+$/, "");
const PI_OFFER_URL = `${API_BASE}/api/cam/agv1/offer`;

function AgvCamera01({ height = 300 }) {
  const videoRef = useRef(null);

  useEffect(() => {
    const pc = new RTCPeerConnection({
      iceServers: [{ urls: "stun:stun.l.google.com:19302" }],
    });

    // 영상만 받는 recvonly 트랜시버
    pc.addTransceiver("video", { direction: "recvonly" });

    pc.ontrack = (event) => {
      console.log("AGV01 ontrack", event.streams);
      if (videoRef.current) {
        videoRef.current.srcObject = event.streams[0];
      }
    };

    pc.oniceconnectionstatechange = () => {
      console.log("AGV01 ICE state:", pc.iceConnectionState);
    };

    const start = async () => {
      try {
        const offer = await pc.createOffer();
        await pc.setLocalDescription(offer);

        console.log("AGV01 local SDP:", pc.localDescription.sdp);

        const res = await fetch(PI_OFFER_URL, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            sdp: pc.localDescription.sdp,
            type: pc.localDescription.type,
          }),
        });

        if (!res.ok) {
          const text = await res.text();
          console.error(
            "AGV01 WebRTC 연결 실패 (HTTP 에러)",
            "status=",
            res.status,
            "body=",
            text
          );
          throw new Error(`Pi offer 에러: ${res.status} - ${text}`);
        }

        const data = await res.json();
        await pc.setRemoteDescription(new RTCSessionDescription(data));
      } catch (err) {
        console.error("AGV01 WebRTC 연결 실패:", err);
      }
    };

    start();

    return () => {
      try {
        if (videoRef.current) {
          videoRef.current.srcObject = null;
        }
        pc.ontrack = null;
        pc.oniceconnectionstatechange = null;
        pc.close();
      } catch (e) {
        console.warn("AGV01 cleanup error:", e);
      }
    };
  }, []);

  return (
    <div className="rounded-xl overflow-hidden bg-black" style={{ height }}>
      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted
        className="w-full h-full object-cover"
      />
    </div>
  );
}

export default AgvCamera01;
