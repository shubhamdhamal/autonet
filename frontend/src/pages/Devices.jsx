import { useEffect, useState } from 'react'
import { api } from '../api/client'
import Modal from '../components/Modal'
import StatusBadge from '../components/StatusBadge'
import { deviceTypes, simulationProfiles } from '../utils/helpers'

const emptyForm = {
  name: '',
  ip_address: '',
  device_type: 'Router',
  location: '',
  monitoring_enabled: true,
  simulation_profile: 'normal',
}

export default function Devices() {
  const [devices, setDevices] = useState([])
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState(emptyForm)
  const [error, setError] = useState('')

  const load = async () => {
    const res = await api.getDevices()
    setDevices(res.data)
  }

  useEffect(() => { load() }, [])

  const openCreate = () => {
    setEditing(null)
    setForm(emptyForm)
    setError('')
    setModalOpen(true)
  }

  const openEdit = (device) => {
    setEditing(device)
    setForm({
      name: device.name,
      ip_address: device.ip_address,
      device_type: device.device_type,
      location: device.location,
      monitoring_enabled: device.monitoring_enabled,
      simulation_profile: device.simulation_profile,
    })
    setError('')
    setModalOpen(true)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      if (editing) {
        await api.updateDevice(editing.id, form)
      } else {
        await api.createDevice(form)
      }
      setModalOpen(false)
      load()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save device')
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('Delete this device?')) return
    await api.deleteDevice(id)
    load()
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Device Management</h2>
          <p className="text-slate-400 text-sm">Manage monitored network devices and simulation profiles</p>
        </div>
        <button onClick={openCreate} className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-sm font-medium">
          + Add Device
        </button>
      </div>

      <div className="card overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="text-slate-400 text-left">
            <tr>
              <th className="pb-2">Name</th>
              <th>IP</th>
              <th>Type</th>
              <th>Location</th>
              <th>Status</th>
              <th>Simulation</th>
              <th>Monitoring</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {devices.map((d) => (
              <tr key={d.id} className="table-row">
                <td className="py-2 font-medium">{d.name}</td>
                <td>{d.ip_address}</td>
                <td>{d.device_type}</td>
                <td>{d.location}</td>
                <td><StatusBadge status={d.current_status} /></td>
                <td className="text-slate-300">{d.simulation_profile}</td>
                <td>{d.monitoring_enabled ? 'Enabled' : 'Disabled'}</td>
                <td className="space-x-2">
                  <button onClick={() => openEdit(d)} className="text-blue-400 hover:underline">Edit</button>
                  <button onClick={() => handleDelete(d.id)} className="text-red-400 hover:underline">Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <Modal open={modalOpen} title={editing ? 'Edit Device' : 'Add Device'} onClose={() => setModalOpen(false)}>
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && <p className="text-red-400 text-sm">{error}</p>}
          <input className="w-full bg-slate-900 border border-noc-border rounded-lg px-3 py-2" placeholder="Device Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
          <input className="w-full bg-slate-900 border border-noc-border rounded-lg px-3 py-2" placeholder="IP Address" value={form.ip_address} onChange={(e) => setForm({ ...form, ip_address: e.target.value })} required />
          <select className="w-full bg-slate-900 border border-noc-border rounded-lg px-3 py-2" value={form.device_type} onChange={(e) => setForm({ ...form, device_type: e.target.value })}>
            {deviceTypes.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
          <input className="w-full bg-slate-900 border border-noc-border rounded-lg px-3 py-2" placeholder="Location" value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} required />
          <select className="w-full bg-slate-900 border border-noc-border rounded-lg px-3 py-2" value={form.simulation_profile} onChange={(e) => setForm({ ...form, simulation_profile: e.target.value })}>
            {simulationProfiles.map((p) => <option key={p.value} value={p.value}>{p.label}</option>)}
          </select>
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" checked={form.monitoring_enabled} onChange={(e) => setForm({ ...form, monitoring_enabled: e.target.checked })} />
            Monitoring Enabled
          </label>
          <button type="submit" className="w-full py-2 bg-blue-600 hover:bg-blue-500 rounded-lg font-medium">
            {editing ? 'Update Device' : 'Create Device'}
          </button>
        </form>
      </Modal>
    </div>
  )
}
