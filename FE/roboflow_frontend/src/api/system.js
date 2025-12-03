// src/api/system.js
import { getJson } from './client';

export const fetchSystemStatus = async () => {
  try {
    const response = await fetch('/api/system/status');
    if (!response.ok) {
      throw new Error('시스템 상태 로드 실패');
    }
    return await response.json();
  } catch (error) {
    console.error(error);
    throw error;
  }
};
