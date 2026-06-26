import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'
import { Line } from 'react-chartjs-2'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler)

export default function MetricChart({ title, labels, data, color, unit = '' }) {
  const chartData = {
    labels,
    datasets: [
      {
        label: title,
        data,
        borderColor: color,
        backgroundColor: `${color}33`,
        fill: true,
        tension: 0.35,
        pointRadius: 2,
      },
    ],
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: (ctx) => `${ctx.parsed.y}${unit}`,
        },
      },
    },
    scales: {
      x: {
        ticks: { color: '#94a3b8', maxTicksLimit: 8 },
        grid: { color: '#1e293b' },
      },
      y: {
        ticks: { color: '#94a3b8' },
        grid: { color: '#1e293b' },
      },
    },
    animation: { duration: 800 },
  }

  return (
    <div className="card h-72">
      <h3 className="text-sm font-semibold text-slate-300 mb-3">{title}</h3>
      <div className="h-56">
        <Line data={chartData} options={options} />
      </div>
    </div>
  )
}
