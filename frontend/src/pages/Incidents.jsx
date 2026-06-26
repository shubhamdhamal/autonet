import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import StatusBadge from '../components/StatusBadge'
import { formatDate } from '../utils/helpers'

export default function Incidents() {
  const [incidents, setIncidents] = useState([])
  const [filter, setFilter] = useState('')

  const load = async () => {
    const res = await api.getIncidents(filter || undefined)
    setIncidents(res.data)
  }

  useEffect(() => { load() }, [filter])

  useEffect(() => {
    const interval = setInterval(load, 15000)
    return () => clearInterval(interval)
  }, [filter])

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold">Incident Management</h2>
          <p className="text-slate-400 text-sm">View, resolve, and close network incidents</p>
        </div>
        <select
          className="bg-slate-900 border border-noc-border rounded-lg px-3 py-2 text-sm"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        >
          <option value="">All Statuses</option>
          <option value="Open">Open</option>
          <option value="Resolved">Resolved</option>
          <option value="Closed">Closed</option>
          <option value="Auto Closed">Auto Closed</option>
        </select>
      </div>

      <div className="card overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="text-slate-400 text-left">
            <tr>
              <th className="pb-2">Incident #</th>
              <th>Device ID</th>
              <th>Severity</th>
              <th>Status</th>
              <th>Packet Loss</th>
              <th>Latency</th>
              <th>Created</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {incidents.map((inc) => (
              <tr key={inc.id} className="table-row">
                <td className="py-2 font-medium">{inc.incident_number}</td>
                <td>{inc.device_id}</td>
                <td><StatusBadge status={inc.severity} /></td>
                <td><StatusBadge status={inc.status} /></td>
                <td>{inc.packet_loss}%</td>
                <td>{inc.latency}ms</td>
                <td>{formatDate(inc.created_at)}</td>
                <td>
                  <Link to={`/incidents/${inc.id}`} className="text-blue-400 hover:underline">View</Link>
                </td>
              </tr>
            ))}
            {incidents.length === 0 && (
              <tr><td colSpan={8} className="py-6 text-slate-500 text-center">No incidents found</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
