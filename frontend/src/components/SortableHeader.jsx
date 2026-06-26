export default function SortableHeader({ label, column, sortColumn, sortDirection, onSort, className = '' }) {
  const active = sortColumn === column

  return (
    <th className={`pb-2 ${className}`}>
      <button
        type="button"
        onClick={() => onSort(column)}
        className="inline-flex items-center gap-1.5 hover:text-slate-200 transition-colors group"
        title={`Sort by ${label}`}
      >
        <span>{label}</span>
        <span className="inline-flex flex-col text-[9px] leading-[0.65rem]">
          <span className={active && sortDirection === 'asc' ? 'text-blue-400' : 'text-slate-600 group-hover:text-slate-400'}>
            ▲
          </span>
          <span className={active && sortDirection === 'desc' ? 'text-blue-400' : 'text-slate-600 group-hover:text-slate-400'}>
            ▼
          </span>
        </span>
      </button>
    </th>
  )
}
