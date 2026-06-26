import { useEffect, useState } from 'react'
import { api } from '../api/client'
import StatusBadge from '../components/StatusBadge'
import { formatDate } from '../utils/helpers'

export default function Logs() {
  const [logs, setLogs] = useState([])
  const [devices, setDevices] = useState([])
  const [deviceId, setDeviceId] = useState('')

  const load = async () => {
    const [logsRes, devicesRes] = await Promise.all([
      api.getMonitoringLogs({ limit: 200, device_id: deviceId || undefined }),
      api.getDevices(),
    ])
    setLogs(logsRes.data)
    setDevices(devicesRes.data)
  }

  useEffect(() => { load() }, [deviceId])

  useEffect(() => {
    const interval = setInterval(load, 15000)
    return () => clearInterval(interval)
  }, [deviceId])

  const deviceMap = Object.fromEntries(devices.map((d) => [d.id, d.name]))

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold">Monitoring Logs</h2>
          <p className="text-slate-400 text-sm">Historical monitoring cycles stored in the database</p>
        </div>
        <select
          className="bg-slate-900 border border-noc-border rounded-lg px-3 py-2 text-sm"
          value={deviceId}
          onChange={(e) => setDeviceId(e.target.value)}
        >
          <option value="">All Devices</option>
          {devices.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
        </select>
      </div>

      <div className="card overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="text-slate-400 text-left">
            <tr>
              <th className="pb-2">Timestamp</th>
              <th>Device</th>
              <th>Status</th>
              <th>Packet Loss</th>
              <th>Latency</th>
              <th>Jitter</th>
              <th>Response Time</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log) => (
              <tr key={log.id} className="table-row">
                <td className="py-2">{formatDate(log.created_at)}</td>
                <td>{deviceMap[log.device_id] || log.device_id}</td>
                <td><StatusBadge status={log.status} /></td>
                <td>{log.packet_loss}%</td>
                <td>{log.avg_latency}ms</td>
                <td>{log.jitter}ms</td>
                <td>{log.response_time}ms</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
