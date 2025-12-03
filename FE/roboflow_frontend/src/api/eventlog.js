import { getJson } from './client';

export const fetchEventLogs = async ({ from, to, module, location, page = 0, size = 10 } = {}) => {
  return getJson('/api/eventlog', { from, to, module, location, page, size });
};

export default fetchEventLogs;
