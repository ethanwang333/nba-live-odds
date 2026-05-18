import { useState, useEffect } from "react"
import GameCard from "./components/GameCard"
import ChatPanel from "./components/ChatPanel"

function App() {
  const [games, setGames] = useState([])
  const [connected, setConnected] = useState(false)
  const [history, setHistory] = useState({})

  useEffect(() => {
    const wsUrl = import.meta.env.VITE_API_URL.replace("http", "ws")
    const ws = new WebSocket(`${wsUrl}/ws/games`)
    ws.onopen = () => setConnected(true)
    ws.onclose = () => setConnected(false)
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      setGames(data.games)
      setHistory(prev => {
        const updated = { ...prev }
        data.games.forEach(game => {
          const existing = updated[game.gameId] || []
          const lastPoint = existing[existing.length - 1]
          const newProb = game.home_win_probability
          const lastProb = lastPoint ? lastPoint.home : null
          if (lastProb === null || newProb !== lastProb) {
            const point = {
              time: game.total_seconds_remaining,
              home: game.home_win_probability,
              away: 1 - game.home_win_probability
            }
            updated[game.gameId] = [...existing, point]
          }
        })
        return updated
      })
    }
    return () => ws.close()
  }, [])

  return (
    <div style={{
      backgroundColor: "#0a0a0f",
      minHeight: "100vh",
      color: "white",
      fontFamily: "'Inter', 'Segoe UI', sans-serif",
    }}>
      {/* header */}
      <div style={{
        borderBottom: "1px solid #1e1e2e",
        padding: "18px 32px",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        backgroundColor: "#0d0d1a",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <span style={{ fontSize: "22px" }}>🏀</span>
          <h1 style={{ margin: 0, fontSize: "20px", fontWeight: 700, color: "#e2e8f0", letterSpacing: "-0.3px" }}>
            NBA Live Odds
          </h1>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <div style={{
            width: "8px", height: "8px", borderRadius: "50%",
            backgroundColor: connected ? "#22c55e" : "#ef4444",
            boxShadow: connected ? "0 0 8px #22c55e" : "none",
          }} />
          <span style={{ fontSize: "13px", color: connected ? "#22c55e" : "#ef4444" }}>
            {connected ? "Live" : "Disconnected"}
          </span>
        </div>
      </div>

      {/* content */}
      <div style={{ padding: "24px 32px", maxWidth: "1100px", margin: "0 auto" }}>
        {games.length === 0 ? (
          <div style={{
            textAlign: "center", padding: "80px 0",
            color: "#4a5568", fontSize: "16px"
          }}>
            <div style={{ fontSize: "40px", marginBottom: "12px" }}>🏀</div>
            <p>No live games right now</p>
          </div>
        ) : (
          games.map(game => (
            <GameCard
              key={game.gameId}
              game={game}
              history={history[game.gameId] || []}
            />
          ))
        )}
      </div>
    </div>
  )
}

export default App