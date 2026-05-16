import { useState, useEffect } from "react"

function App() {
  const [games, setGames] = useState([])
  const [connected, setConnected] = useState(false)

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws/games")

    ws.onopen = () => setConnected(true)
    ws.onclose = () => setConnected(false)

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      setGames(data.games)
    }

    return () => ws.close()
  }, [])

  return (
    <div style={{ backgroundColor: "#0f0f0f", minHeight: "100vh", color: "white", padding: "20px", fontFamily: "sans-serif" }}>
      <h1 style={{ color: "#00d4aa" }}>NBA Live Odds</h1>
      <p style={{ color: connected ? "#00d4aa" : "red" }}>
        {connected ? "Connected" : "Disconnected"}
      </p>

      {games.length === 0 && <p>No live games right now</p>}

      {games.map(game => (
        <div key={game.gameId} style={{ border: "1px solid #333", borderRadius: "8px", padding: "20px", marginBottom: "20px" }}>
          
          <h2>{game.awayTeam} @ {game.homeTeam}</h2>
          <h3>{game.scoreAway} - {game.scoreHome} | Q{game.period}</h3>
          
          <div style={{ marginTop: "16px" }}>
            <p>{game.awayTeam} win probability: {((1 - game.home_win_probability) * 100).toFixed(1)}%</p>
            <p>{game.homeTeam} win probability: {(game.home_win_probability * 100).toFixed(1)}%</p>
          </div>

        </div>
      ))}
    </div>
  )
}

export default App