import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api/v1'

const client = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
})

export const api = {
  getDashboard: () => client.get('/dashboard'),
  getStatistics: () => client.get('/statistics'),
  getDevices: () => client.get('/devices'),
  getDevice: (id) => client.get(`/devices/${id}`),
  createDevice: (data) => client.post('/devices', data),
  updateDevice: (id, data) => client.put(`/devices/${id}`, data),
  deleteDevice: (id) => client.delete(`/devices/${id}`),
  getIncidents: (status) => client.get('/incidents', { params: { status_filter: status } }),
  getIncident: (id) => client.get(`/incidents/${id}`),
  resolveIncident: (id, notes) => client.post(`/incidents/${id}/resolve`, { resolution_notes: notes }),
  closeIncident: (id, notes) => client.post(`/incidents/${id}/close`, { resolution_notes: notes }),
  getMonitoringLogs: (params) => client.get('/monitoring/logs', { params }),
  getNotifications: () => client.get('/notifications'),
}

export default client
