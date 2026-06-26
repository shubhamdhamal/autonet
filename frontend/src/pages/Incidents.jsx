import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import SortableHeader from '../components/SortableHeader'
import StatusBadge from '../components/StatusBadge'
import { formatDate } from '../utils/helpers'

const EMPTY_FILTERS = {
  incident_number: '',
  device_id: '',
  severity: '',
  status: '',
  packet_loss: '',
  latency: '',
  created_at: '',
}

const SEVERITY_ORDER = { Critical: 0, Major: 1, Warning: 2, Healthy: 3 }
const STATUS_ORDER = { Open: 0, Resolved: 1, Closed: 2, 'Auto Closed': 3 }

function compareValues(a, b, column, direction) {
  let valA = a[column]
  let valB = b[column]

  if (column === 'created_at') {
    valA = new Date(valA).getTime()
    valB = new Date(valB).getTime()
  } else if (column === 'severity') {
    valA = SEVERITY_ORDER[valA] ?? 99
    valB = SEVERITY_ORDER[valB] ?? 99
  } else if (column === 'status') {
    valA = STATUS_ORDER[valA] ?? 99
    valB = STATUS_ORDER[valB] ?? 99
  } else if (column === 'device_id' || column === 'packet_loss' || column === 'latency') {
    valA = Number(valA)
    valB = Number(valB)
  } else {
    valA = String(valA ?? '').toLowerCase()
    valB = String(valB ?? '').toLowerCase()
  }

  if (valA < valB) return direction === 'asc' ? -1 : 1
  if (valA > valB) return direction === 'asc' ? 1 : -1
  return 0
}

function matchesFilter(value, filter, column) {
  if (!filter.trim()) return true
  const query = filter.trim().toLowerCase()

  if (column === 'device_id' || column === 'packet_loss' || column === 'latency') {
    return String(value).includes(query)
  }
  if (column === 'created_at') {
    return formatDate(value).toLowerCase().includes(query)
  }
  return String(value ?? '').toLowerCase().includes(query)
}

export default function Incidents() {
  const [incidents, setIncidents] = useState([])
  const [statusFilter, setStatusFilter] = useState('')
  const [sortColumn, setSortColumn] = useState('created_at')
  const [sortDirection, setSortDirection] = useState('desc')
  const [columnFilters, setColumnFilters] = useState(EMPTY_FILTERS)

  const load = async () => {
    const res = await api.getIncidents(statusFilter || undefined)
    setIncidents(res.data)
  }

  useEffect(() => { load() }, [statusFilter])

  useEffect(() => {
    const interval = setInterval(load, 15000)
    return () => clearInterval(interval)
  }, [statusFilter])

  const handleSort = (column) => {
    if (sortColumn === column) {
      setSortDirection((prev) => (prev === 'asc' ? 'desc' : 'asc'))
    } else {
      setSortColumn(column)
      setSortDirection('asc')
    }
  }

  const updateFilter = (column, value) => {
    setColumnFilters((prev) => ({ ...prev, [column]: value }))
  }

  const clearFilters = () => {
    setColumnFilters(EMPTY_FILTERS)
    setStatusFilter('')
    setSortColumn('created_at')
    setSortDirection('desc')
  }

  const displayedIncidents = useMemo(() => {
    let rows = incidents.filter((inc) =>
      Object.entries(columnFilters).every(([col, filter]) => matchesFilter(inc[col], filter, col)),
    )

    if (sortColumn) {
      rows = [...rows].sort((a, b) => compareValues(a, b, sortColumn, sortDirection))
    }

    return rows
  }, [incidents, columnFilters, sortColumn, sortDirection])

  const filterInputClass =
    'w-full bg-slate-900/80 border border-noc-border rounded px-2 py-1 text-xs text-slate-200 placeholder:text-slate-500'

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold">Incident Management</h2>
          <p className="text-slate-400 text-sm">View, resolve, and close network incidents</p>
        </div>
        <div className="flex items-center gap-3">
          <select
            className="bg-slate-900 border border-noc-border rounded-lg px-3 py-2 text-sm"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="">All Statuses</option>
            <option value="Open">Open</option>
            <option value="Resolved">Resolved</option>
            <option value="Closed">Closed</option>
            <option value="Auto Closed">Auto Closed</option>
          </select>
          <button
            onClick={clearFilters}
            className="px-3 py-2 text-sm border border-noc-border rounded-lg hover:bg-slate-800/60"
          >
            Clear filters
          </button>
        </div>
      </div>

      <div className="card overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="text-slate-400 text-left">
            <tr>
              <SortableHeader label="Incident #" column="incident_number" sortColumn={sortColumn} sortDirection={sortDirection} onSort={handleSort} />
              <SortableHeader label="Device ID" column="device_id" sortColumn={sortColumn} sortDirection={sortDirection} onSort={handleSort} />
              <SortableHeader label="Severity" column="severity" sortColumn={sortColumn} sortDirection={sortDirection} onSort={handleSort} />
              <SortableHeader label="Status" column="status" sortColumn={sortColumn} sortDirection={sortDirection} onSort={handleSort} />
              <SortableHeader label="Packet Loss" column="packet_loss" sortColumn={sortColumn} sortDirection={sortDirection} onSort={handleSort} />
              <SortableHeader label="Latency" column="latency" sortColumn={sortColumn} sortDirection={sortDirection} onSort={handleSort} />
              <SortableHeader label="Created" column="created_at" sortColumn={sortColumn} sortDirection={sortDirection} onSort={handleSort} />
              <th className="pb-2">Action</th>
            </tr>
            <tr className="border-b border-noc-border">
              <th className="py-2 pr-2">
                <input className={filterInputClass} placeholder="Filter..." value={columnFilters.incident_number} onChange={(e) => updateFilter('incident_number', e.target.value)} />
              </th>
              <th className="py-2 pr-2">
                <input className={filterInputClass} placeholder="Filter..." value={columnFilters.device_id} onChange={(e) => updateFilter('device_id', e.target.value)} />
              </th>
              <th className="py-2 pr-2">
                <input className={filterInputClass} placeholder="Filter..." value={columnFilters.severity} onChange={(e) => updateFilter('severity', e.target.value)} />
              </th>
              <th className="py-2 pr-2">
                <input className={filterInputClass} placeholder="Filter..." value={columnFilters.status} onChange={(e) => updateFilter('status', e.target.value)} />
              </th>
              <th className="py-2 pr-2">
                <input className={filterInputClass} placeholder="Filter..." value={columnFilters.packet_loss} onChange={(e) => updateFilter('packet_loss', e.target.value)} />
              </th>
              <th className="py-2 pr-2">
                <input className={filterInputClass} placeholder="Filter..." value={columnFilters.latency} onChange={(e) => updateFilter('latency', e.target.value)} />
              </th>
              <th className="py-2 pr-2">
                <input className={filterInputClass} placeholder="Filter..." value={columnFilters.created_at} onChange={(e) => updateFilter('created_at', e.target.value)} />
              </th>
              <th className="py-2" />
            </tr>
          </thead>
          <tbody>
            {displayedIncidents.map((inc) => (
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
            {displayedIncidents.length === 0 && (
              <tr><td colSpan={8} className="py-6 text-slate-500 text-center">No incidents found</td></tr>
            )}
          </tbody>
        </table>
        <p className="text-xs text-slate-500 mt-3">
          Showing {displayedIncidents.length} of {incidents.length} incidents · Click column headers to sort ▲▼
        </p>
      </div>
    </div>
  )
}
