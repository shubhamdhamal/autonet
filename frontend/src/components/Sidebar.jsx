import { NavLink } from 'react-router-dom'

const links = [
  { to: '/', label: 'Dashboard', icon: '📊' },
  { to: '/devices', label: 'Devices', icon: '🖧' },
  { to: '/incidents', label: 'Incidents', icon: '🚨' },
  { to: '/logs', label: 'Monitoring Logs', icon: '📋' },
]

export default function Sidebar() {
  return (
    <aside className="w-64 bg-noc-panel border-r border-noc-border min-h-screen p-5 flex flex-col">
      <div className="mb-8">
        <p className="text-xs uppercase tracking-widest text-blue-400">Enterprise NOC</p>
        <h1 className="text-xl font-bold mt-1">Network Quality Monitor</h1>
        <p className="text-xs text-slate-500 mt-1">Incident Management System</p>
      </div>
      <nav className="space-y-2 flex-1">
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg transition ${
                isActive
                  ? 'bg-blue-600/20 text-blue-300 border border-blue-500/30'
                  : 'text-slate-300 hover:bg-slate-800/60'
              }`
            }
          >
            <span>{link.icon}</span>
            <span className="text-sm font-medium">{link.label}</span>
          </NavLink>
        ))}
      </nav>
      <div className="text-xs text-slate-500 border-t border-noc-border pt-4">
        Live monitoring every 30s
      </div>
    </aside>
  )
}
