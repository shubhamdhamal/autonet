import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api/client'
import StatusBadge from '../components/StatusBadge'
import { formatDate } from '../utils/helpers'

export default function IncidentDetail() {
  const { id } = useParams()
  const [incident, setIncident] = useState(null)
  const [notes, setNotes] = useState('')
  const [message, setMessage] = useState('')

  const load = async () => {
    const res = await api.getIncident(id)
    setIncident(res.data)
    setNotes(res.data.resolution_notes || '')
  }

  useEffect(() => { load() }, [id])

  const handleResolve = async () => {
    if (notes.length < 3) {
      setMessage('Resolution notes must be at least 3 characters')
      return
    }
    await api.resolveIncident(id, notes)
    setMessage('Incident resolved')
    load()
  }

  const handleClose = async () => {
    await api.closeIncident(id, notes || undefined)
    setMessage('Incident closed')
    load()
  }

  if (!incident) return <p className="text-slate-400">Loading incident...</p>

  return (
    <div className="space-y-6">
      <Link to="/incidents" className="text-blue-400 text-sm hover:underline">← Back to Incidents</Link>

      <div className="card">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h2 className="text-2xl font-bold">{incident.incident_number}</h2>
            <p className="text-slate-400">{incident.device_name} ({incident.device_ip}) — {incident.device_location}</p>
          </div>
          <div className="flex gap-2">
            <StatusBadge status={incident.severity} />
            <StatusBadge status={incident.status} />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6 text-sm">
          <div><span className="text-slate-400">Packet Loss:</span> {incident.packet_loss}%</div>
          <div><span className="text-slate-400">Latency:</span> {incident.latency}ms</div>
          <div><span className="text-slate-400">Jitter:</span> {incident.jitter}ms</div>
          <div><span className="text-slate-400">Created:</span> {formatDate(incident.created_at)}</div>
          <div className="md:col-span-2"><span className="text-slate-400">Root Cause:</span> {incident.root_cause}</div>
        </div>
      </div>

      <div className="card space-y-4">
        <h3 className="font-semibold">Resolution Notes</h3>
        <textarea
          className="w-full bg-slate-900 border border-noc-border rounded-lg px-3 py-2 min-h-28"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Add resolution notes..."
        />
        {message && <p className="text-sm text-emerald-400">{message}</p>}
        <div className="flex gap-3">
          {incident.status === 'Open' && (
            <button onClick={handleResolve} className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-sm">
              Resolve Incident
            </button>
          )}
          {incident.status !== 'Closed' && incident.status !== 'Auto Closed' && (
            <button onClick={handleClose} className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-sm">
              Close Incident
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
