import { useState, useEffect } from "react"
import GameCard from "./components/GameCard"

function App() {
  const [games, setGames] = useState([])
  const [connected, setConnected] = useState(false)

  useEffect(() => {
    let ws
    let reconnectTimer

    const connect = () => {
      const wsUrl = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace("http", "ws")
      ws = new WebSocket(`${wsUrl}/ws/games`)

      ws.onopen = () => {
        setConnected(true)
        clearTimeout(reconnectTimer)
      }

      ws.onclose = () => {
        setConnected(false)
        reconnectTimer = setTimeout(connect, 3000)
      }

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data)
        setGames(data.games)
      }
    }

    connect()

    return () => {
      clearTimeout(reconnectTimer)
      if (ws) ws.close()
    }
  }, [])

  return (
    <div style={{
      backgroundColor: "#0a0a0f",
      minHeight: "100vh",
      color: "white",
      fontFamily: "'Inter', 'Segoe UI', sans-serif",
      overflowX: "hidden",
    }}>
      <div style={{
        borderBottom: "1px solid #1e1e2e",
        padding: "16px 20px",
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

      <div style={{
        padding: "16px",
        maxWidth: "1100px",
        margin: "0 auto",
        boxSizing: "border-box",
        width: "100%",
      }}>
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