export default function StatusBadge({ status }) {
  const color = {
    Healthy: 'bg-emerald-500',
    Warning: 'bg-yellow-500',
    Major: 'bg-orange-500',
    Critical: 'bg-red-500',
    Open: 'bg-red-500',
    Resolved: 'bg-blue-500',
    Closed: 'bg-slate-500',
    'Auto Closed': 'bg-emerald-500',
  }[status] || 'bg-slate-500'

  return (
    <span className={`inline-flex items-center gap-2 px-2.5 py-1 rounded-full text-xs font-medium border border-white/10`}>
      <span className={`w-2 h-2 rounded-full ${color} animate-pulseSlow`} />
      {status}
    </span>
  )
}
