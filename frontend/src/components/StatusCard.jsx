export default function StatusCard({ title, value, subtitle, accent = 'text-blue-400' }) {
  return (
    <div className="card">
      <p className="text-sm text-slate-400">{title}</p>
      <p className={`text-3xl font-bold mt-2 ${accent}`}>{value}</p>
      {subtitle && <p className="text-xs text-slate-500 mt-1">{subtitle}</p>}
    </div>
  )
}
