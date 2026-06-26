import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import MetricChart from '../components/MetricChart'
import StatusBadge from '../components/StatusBadge'
import StatusCard from '../components/StatusCard'
import { formatDate, healthScoreColor } from '../utils/helpers'

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')

  const load = async () => {
    try {
      const res = await api.getDashboard()
      setData(res.data)
      setError('')
    } catch {
      setError('Failed to load dashboard data')
    }
  }

  useEffect(() => {
    load()
    const interval = setInterval(load, 15000)
    return () => clearInterval(interval)
  }, [])

  if (error) return <p className="text-red-400">{error}</p>
  if (!data) return <p className="text-slate-400">Loading NOC dashboard...</p>

  const { summary, trends, recent_incidents, device_status, top_problem_devices } = data
  const labels = trends.map((t) => new Date(t.timestamp).toLocaleTimeString())

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold">NOC Dashboard</h2>
          <p className="text-slate-400 text-sm">Real-time network quality and incident overview</p>
        </div>
        <div className="card py-3 px-5">
          <p className="text-xs text-slate-400">Network Health Score</p>
          <p className={`text-3xl font-bold ${healthScoreColor(summary.network_health_score)}`}>
            {summary.network_health_score}
            <span className="text-base text-slate-500">/100</span>
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-5 gap-4">
        <StatusCard title="Total Devices" value={summary.total_devices} accent="text-blue-400" />
        <StatusCard title="Healthy" value={summary.healthy} accent="text-emerald-400" />
        <StatusCard title="Warning" value={summary.warning} accent="text-yellow-400" />
        <StatusCard title="Critical" value={summary.critical} accent="text-red-400" />
        <StatusCard title="Open Incidents" value={summary.open_incidents} accent="text-orange-400" />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
        <MetricChart title="Packet Loss Trend (%)" labels={labels} data={trends.map((t) => t.packet_loss)} color="#f59e0b" unit="%" />
        <MetricChart title="Latency Trend (ms)" labels={labels} data={trends.map((t) => t.latency)} color="#3b82f6" unit="ms" />
        <MetricChart title="Jitter Trend (ms)" labels={labels} data={trends.map((t) => t.jitter)} color="#a855f7" unit="ms" />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        <div className="card overflow-x-auto">
          <h3 className="font-semibold mb-3">Recent Incidents</h3>
          <table className="w-full text-sm">
            <thead className="text-slate-400 text-left">
              <tr>
                <th className="pb-2">Incident</th>
                <th>Device</th>
                <th>Severity</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {recent_incidents.map((inc) => (
                <tr key={inc.id} className="table-row">
                  <td className="py-2">
                    <Link to={`/incidents/${inc.id}`} className="text-blue-400 hover:underline">
                      {inc.incident_number}
                    </Link>
                  </td>
                  <td>{inc.device_name}</td>
                  <td><StatusBadge status={inc.severity} /></td>
                  <td><StatusBadge status={inc.status} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="card overflow-x-auto">
          <h3 className="font-semibold mb-3">Top Problem Devices</h3>
          <table className="w-full text-sm">
            <thead className="text-slate-400 text-left">
              <tr>
                <th className="pb-2">Device</th>
                <th>Status</th>
                <th>Loss</th>
                <th>Latency</th>
              </tr>
            </thead>
            <tbody>
              {top_problem_devices.map((d) => (
                <tr key={d.id} className="table-row">
                  <td className="py-2">{d.name}</td>
                  <td><StatusBadge status={d.status} /></td>
                  <td>{d.packet_loss}%</td>
                  <td>{d.avg_latency}ms</td>
                </tr>
              ))}
              {top_problem_devices.length === 0 && (
                <tr><td colSpan={4} className="py-4 text-slate-500">No problem devices detected</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      <div className="card overflow-x-auto">
        <h3 className="font-semibold mb-3">Device Status</h3>
        <table className="w-full text-sm">
          <thead className="text-slate-400 text-left">
            <tr>
              <th className="pb-2">Device</th>
              <th>IP</th>
              <th>Location</th>
              <th>Status</th>
              <th>Loss</th>
              <th>Latency</th>
              <th>Jitter</th>
              <th>Last Check</th>
            </tr>
          </thead>
          <tbody>
            {device_status.map((d) => (
              <tr key={d.id} className="table-row">
                <td className="py-2 font-medium">{d.name}</td>
                <td>{d.ip_address}</td>
                <td>{d.location}</td>
                <td><StatusBadge status={d.status} /></td>
                <td>{d.packet_loss}%</td>
                <td>{d.avg_latency}ms</td>
                <td>{d.jitter}ms</td>
                <td>{formatDate(d.last_check)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
