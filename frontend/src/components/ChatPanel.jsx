import { useState, useRef, useEffect } from "react"

function ChatPanel({ gameId }) {
  const [messages, setMessages] = useState([
    { role: "bot", text: "Ask me anything about this game — probabilities, player performance, or strategy." }
  ])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  // auto scroll to bottom when new message arrives
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim() || loading) return

    const question = input.trim()
    setInput("")
    setMessages(prev => [...prev, { role: "user", text: question }])
    setLoading(true)

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, game_id: gameId })
      })
      const data = await response.json()
      setMessages(prev => [...prev, { role: "bot", text: data.answer }])
    } catch {
      setMessages(prev => [...prev, { role: "bot", text: "Couldn't connect to the server." }])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === "Enter") sendMessage()
  }

  return (
    <div style={{
      marginTop: "20px",
      borderTop: "1px solid #1e1e2e",
      paddingTop: "20px",
    }}>
      <div style={{
        fontSize: "12px", color: "#4a5568", marginBottom: "12px",
        fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em"
      }}>
        AI Analyst
      </div>

      {/* message history */}
      <div style={{
        height: "200px",
        overflowY: "auto",
        marginBottom: "12px",
        display: "flex",
        flexDirection: "column",
        gap: "10px",
        paddingRight: "4px",
      }}>
        {messages.map((msg, i) => (
          <div key={i} style={{
            display: "flex",
            justifyContent: msg.role === "user" ? "flex-end" : "flex-start",
          }}>
            <div style={{
              maxWidth: "80%",
              padding: "10px 14px",
              borderRadius: msg.role === "user" ? "12px 12px 2px 12px" : "12px 12px 12px 2px",
              backgroundColor: msg.role === "user" ? "#00d4aa22" : "#161625",
              border: msg.role === "user" ? "1px solid #00d4aa44" : "1px solid #1e1e2e",
              fontSize: "13px",
              color: msg.role === "user" ? "#00d4aa" : "#cbd5e0",
              lineHeight: "1.5",
            }}>
              {msg.text}
            </div>
          </div>
        ))}

        {loading && (
          <div style={{ display: "flex", justifyContent: "flex-start" }}>
            <div style={{
              padding: "10px 14px",
              borderRadius: "12px 12px 12px 2px",
              backgroundColor: "#161625",
              border: "1px solid #1e1e2e",
              fontSize: "13px",
              color: "#4a5568",
            }}>
              Thinking...
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* input row */}
      <div style={{ display: "flex", gap: "8px" }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about this game..."
          style={{
            flex: 1,
            backgroundColor: "#161625",
            border: "1px solid #1e1e2e",
            borderRadius: "8px",
            padding: "10px 14px",
            color: "white",
            fontSize: "13px",
            outline: "none",
          }}
        />
        <button
          onClick={sendMessage}
          disabled={loading || !input.trim()}
          style={{
            padding: "10px 18px",
            backgroundColor: loading || !input.trim() ? "#1e1e2e" : "#00d4aa",
            color: loading || !input.trim() ? "#4a5568" : "#0a0a0f",
            border: "none",
            borderRadius: "8px",
            fontSize: "13px",
            fontWeight: 600,
            cursor: loading || !input.trim() ? "not-allowed" : "pointer",
            transition: "background-color 0.2s",
          }}
        >
          Send
        </button>
      </div>
    </div>
  )
}

export default ChatPanel