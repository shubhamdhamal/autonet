export const APP_TIMEZONE = 'Asia/Kolkata'

export const statusColor = (status) => {
  const map = {
    Healthy: 'text-emerald-400 bg-emerald-400/10 border-emerald-400/30',
    Warning: 'text-yellow-400 bg-yellow-400/10 border-yellow-400/30',
    Major: 'text-orange-400 bg-orange-400/10 border-orange-400/30',
    Critical: 'text-red-400 bg-red-400/10 border-red-400/30',
    Open: 'text-red-400 bg-red-400/10 border-red-400/30',
    Resolved: 'text-blue-400 bg-blue-400/10 border-blue-400/30',
    Closed: 'text-slate-400 bg-slate-400/10 border-slate-400/30',
    'Auto Closed': 'text-emerald-400 bg-emerald-400/10 border-emerald-400/30',
  }
  return map[status] || 'text-slate-300 bg-slate-700/40 border-slate-600'
}

export const healthScoreColor = (score) => {
  if (score >= 80) return 'text-emerald-400'
  if (score >= 60) return 'text-yellow-400'
  if (score >= 40) return 'text-orange-400'
  return 'text-red-400'
}

export const formatDate = (value) => {
  if (!value) return '—'
  const normalized = typeof value === 'string' && !value.endsWith('Z') && !value.includes('+')
    ? `${value}Z`
    : value
  return new Date(normalized).toLocaleString('en-IN', {
    timeZone: APP_TIMEZONE,
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: true,
  })
}

export const formatTime = (value) => {
  if (!value) return '—'
  const normalized = typeof value === 'string' && !value.endsWith('Z') && !value.includes('+')
    ? `${value}Z`
    : value
  return new Date(normalized).toLocaleTimeString('en-IN', {
    timeZone: APP_TIMEZONE,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: true,
  })
}

export const simulationProfiles = [
  { value: 'normal', label: 'Normal (Real Ping)' },
  { value: 'packet_loss_20', label: '20% Packet Loss' },
  { value: 'high_latency', label: 'High Latency' },
  { value: 'high_jitter', label: 'High Jitter' },
  { value: 'device_down', label: 'Device Down' },
  { value: 'random_issues', label: 'Random Network Issues' },
]

export const deviceTypes = ['Router', 'Switch', 'Firewall', 'Access Point', 'Server', 'Load Balancer']

export const formatDeviceDetail = (incident) => {
  if (!incident?.device_name) return 'Unknown device'
  const ip = incident.device_ip ? ` (${incident.device_ip})` : ''
  const location = incident.device_location ? ` — ${incident.device_location}` : ''
  return `${incident.device_name}${ip}${location}`
}
