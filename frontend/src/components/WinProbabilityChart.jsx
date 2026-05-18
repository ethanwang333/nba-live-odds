import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ReferenceLine, ResponsiveContainer } from "recharts"

function WinProbabilityChart({ history, homeTeam, awayTeam }) {
  if (!history || history.length === 0) {
    return (
      <div style={{
        height: "200px", display: "flex", alignItems: "center",
        justifyContent: "center", color: "#2d3748", fontSize: "13px",
        border: "1px dashed #1e1e2e", borderRadius: "8px"
      }}>
        Waiting for data...
      </div>
    )
  }

  const chartData = history.map(point => ({
    time: Math.round(point.time),
    home: parseFloat((point.home * 100).toFixed(1)),
    away: parseFloat((point.away * 100).toFixed(1)),
  }))

  const formatXAxis = (seconds) => {
    if (seconds >= 2880) return "Tip"
    if (seconds >= 2160) return "Q1"
    if (seconds >= 1440) return "Q2"
    if (seconds >= 720) return "Q3"
    if (seconds > 0) return "Q4"
    return "Final"
  }

  const formatTooltipLabel = (seconds) => {
    if (seconds >= 2880) return "Tipoff"
    const q = seconds >= 2160 ? 1 : seconds >= 1440 ? 2 : seconds >= 720 ? 3 : 4
    const rem = seconds % 720
    const mins = Math.floor(rem / 60)
    const secs = rem % 60
    return `Q${q}  ${mins}:${secs.toString().padStart(2, "0")} remaining`
  }

  return (
    <div>
      <div style={{ fontSize: "12px", color: "#4a5568", marginBottom: "8px", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em" }}>
        Win Probability History
      </div>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={chartData} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1a1a2e" vertical={false} />

          <XAxis
            dataKey="time"
            type="number"
            domain={[0, 2880]}
            reversed={true}
            ticks={[2880, 2160, 1440, 720, 0]}
            tickFormatter={formatXAxis}
            stroke="#2d3748"
            tick={{ fill: "#4a5568", fontSize: 12 }}
            axisLine={{ stroke: "#1e1e2e" }}
          />

          <YAxis
            domain={[0, 100]}
            ticks={[0, 25, 50, 75, 100]}
            tickFormatter={(v) => `${v}%`}
            stroke="#2d3748"
            tick={{ fill: "#4a5568", fontSize: 12 }}
            axisLine={{ stroke: "#1e1e2e" }}
            width={42}
          />

          <Tooltip
            formatter={(value, name) => [`${value}%`, name === "home" ? homeTeam : awayTeam]}
            labelFormatter={formatTooltipLabel}
            contentStyle={{
              backgroundColor: "#0d0d1a",
              border: "1px solid #1e1e2e",
              borderRadius: "8px",
              fontSize: "13px",
            }}
            labelStyle={{ color: "#94a3b8", marginBottom: "4px" }}
          />

          <Legend
            formatter={(value) => (
              <span style={{ color: value === "home" ? "#00d4aa" : "#ff6b6b", fontSize: "12px" }}>
                {value === "home" ? homeTeam : awayTeam}
              </span>
            )}
          />

          <ReferenceLine y={50} stroke="#2d3748" strokeDasharray="4 4" />

          <Line
            type="monotone"
            dataKey="away"
            stroke="#ff6b6b"
            dot={false}
            strokeWidth={2}
            isAnimationActive={false}
          />
          <Line
            type="monotone"
            dataKey="home"
            stroke="#00d4aa"
            dot={false}
            strokeWidth={2}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

export default WinProbabilityChart