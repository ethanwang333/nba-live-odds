import { useState, useEffect } from "react"
import WinProbabilityChart from "./WinProbabilityChart"
import ChatPanel from "./ChatPanel"

function PlayerTable({ players, tricode, side }) {
  if (!players || players.length === 0) return null
  const accent = side === "home" ? "#00d4aa" : "#ff6b6b"

  return (
    <div style={{ flex: 1, minWidth: 0 }}>
      <div style={{
        fontSize: "12px", fontWeight: 600, color: accent,
        marginBottom: "8px", letterSpacing: "0.05em", textTransform: "uppercase"
      }}>
        {tricode}
      </div>
      <div style={{ overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px" }}>
          <thead>
            <tr style={{ color: "#4a5568", borderBottom: "1px solid #1e1e2e" }}>
              <th style={{ textAlign: "left", padding: "4px 6px", fontWeight: 500 }}>Player</th>
              <th style={{ textAlign: "center", padding: "4px 6px", fontWeight: 500 }}>PTS</th>
              <th style={{ textAlign: "center", padding: "4px 6px", fontWeight: 500 }}>REB</th>
              <th style={{ textAlign: "center", padding: "4px 6px", fontWeight: 500 }}>AST</th>
              <th style={{ textAlign: "center", padding: "4px 6px", fontWeight: 500 }}>FL</th>
            </tr>
          </thead>
          <tbody>
            {players.map((p, i) => (
              <tr key={i} style={{ borderBottom: "1px solid #111827" }}>
                <td style={{ padding: "5px 6px", color: "#cbd5e0" }}>{p.name}</td>
                <td style={{ padding: "5px 6px", textAlign: "center", color: "white", fontWeight: 600 }}>{p.points}</td>
                <td style={{ padding: "5px 6px", textAlign: "center", color: "#94a3b8" }}>{p.rebounds}</td>
                <td style={{ padding: "5px 6px", textAlign: "center", color: "#94a3b8" }}>{p.assists}</td>
                <td style={{ padding: "5px 6px", textAlign: "center", color: p.fouls >= 4 ? "#f59e0b" : "#94a3b8" }}>{p.fouls}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function GameCard({ game, history }) {
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768)

  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < 768)
    window.addEventListener("resize", handleResize)
    return () => window.removeEventListener("resize", handleResize)
  }, [])

  const homePct = (game.home_win_probability * 100).toFixed(1)
  const awayPct = (100 - game.home_win_probability * 100).toFixed(1)
  const homeWidth = Math.max(parseFloat(homePct), 5)
  const awayWidth = Math.max(parseFloat(awayPct), 5)

  return (
    <div style={{
      backgroundColor: "#0f0f1a",
      border: "1px solid #1e1e2e",
      borderRadius: "12px",
      padding: isMobile ? "14px" : "24px",
      marginBottom: "24px",
      boxSizing: "border-box",
      width: "100%",
      overflow: "hidden",
    }}>
      {/* score header */}
      <div style={{ textAlign: "center", marginBottom: "20px" }}>
        <div style={{
          display: "flex", alignItems: "center",
          justifyContent: "center", gap: isMobile ? "12px" : "24px", marginBottom: "6px"
        }}>
          <div style={{ textAlign: "right" }}>
            <div style={{ fontSize: "12px", color: "#64748b", marginBottom: "2px" }}>{game.awayTeam}</div>
            <div style={{ fontSize: isMobile ? "30px" : "42px", fontWeight: 700, color: "#ff6b6b", lineHeight: 1 }}>{game.scoreAway}</div>
          </div>
          <div style={{ color: "#2d3748", fontSize: "18px", fontWeight: 300 }}>@</div>
          <div style={{ textAlign: "left" }}>
            <div style={{ fontSize: "12px", color: "#64748b", marginBottom: "2px" }}>{game.homeTeam}</div>
            <div style={{ fontSize: isMobile ? "30px" : "42px", fontWeight: 700, color: "#00d4aa", lineHeight: 1 }}>{game.scoreHome}</div>
          </div>
        </div>
        <div style={{
          fontSize: "12px", color: "#4a5568",
          backgroundColor: "#161625", display: "inline-block",
          padding: "4px 14px", borderRadius: "99px", marginTop: "8px"
        }}>
          Q{game.period} &nbsp;·&nbsp; {game.gameClockFormatted} left
        </div>
      </div>

      {/* probability bar */}
      <div style={{ marginBottom: "6px" }}>
        <div style={{
          display: "flex", height: "36px",
          borderRadius: "6px", overflow: "hidden",
          backgroundColor: "#161625"
        }}>
          <div style={{
            width: `${awayWidth}%`,
            backgroundColor: "#ff6b6b22",
            borderRight: "1px solid #ff6b6b44",
            display: "flex", alignItems: "center",
            justifyContent: "center",
            fontSize: isMobile ? "11px" : "13px",
            fontWeight: 600, color: "#ff6b6b",
            transition: "width 0.5s ease",
            minWidth: "36px",
            overflow: "hidden",
          }}>
            {awayPct}%
          </div>
          <div style={{
            width: `${homeWidth}%`,
            backgroundColor: "#00d4aa22",
            display: "flex", alignItems: "center",
            justifyContent: "center",
            fontSize: isMobile ? "11px" : "13px",
            fontWeight: 600, color: "#00d4aa",
            transition: "width 0.5s ease",
            minWidth: "36px",
            overflow: "hidden",
          }}>
            {homePct}%
          </div>
        </div>
        <div style={{ display: "flex", justifyContent: "space-between", marginTop: "4px", fontSize: "11px" }}>
          <span style={{ color: "#ff6b6b" }}>{game.awayTeam} win prob</span>
          <span style={{ color: "#00d4aa" }}>{game.homeTeam} win prob</span>
        </div>
      </div>

      {/* chart */}
      <div style={{ margin: "20px 0", overflow: "hidden", width: "100%" }}>
        <WinProbabilityChart
          history={history}
          homeTeam={game.homeTeam}
          awayTeam={game.awayTeam}
        />
      </div>

      {/* player stats */}
      {game.players && (
        <div style={{ marginTop: "20px", borderTop: "1px solid #1e1e2e", paddingTop: "20px" }}>
          <div style={{
            fontSize: "12px", color: "#4a5568", marginBottom: "12px",
            fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em"
          }}>
            Player Stats
          </div>
          <div style={{
            display: "flex",
            gap: "16px",
            flexDirection: isMobile ? "column" : "row",
          }}>
            <PlayerTable players={game.players.awayTeam} tricode={game.awayTeam} side="away" />
            <div style={{
              width: isMobile ? "100%" : "1px",
              height: isMobile ? "1px" : "auto",
              backgroundColor: "#1e1e2e",
              flexShrink: 0,
            }} />
            <PlayerTable players={game.players.homeTeam} tricode={game.homeTeam} side="home" />
          </div>
        </div>
      )}

      <ChatPanel gameId={game.gameId} />
    </div>
  )
}

export default GameCard