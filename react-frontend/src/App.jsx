
import { useState, useRef, useEffect } from "react";

const PIXEL_FONT = "'Press Start 2P', monospace";
const BODY_FONT = "'Lato', sans-serif";

const SDV_COLORS = {
  skyBlue: "#87CEEB",
  dirtBrown: "#8B5E3C",
  grassGreen: "#5D8A3C",
  leafGreen: "#4A7A2E",
  sunYellow: "#F4C542",
  warmCream: "#FFF5DC",
  parchment: "#F2E8C8",
  darkBrown: "#3B2A1A",
  medBrown: "#6B4C2A",
  logBrown: "#7A5230",
  windowBlue: "#6AACDC",
  starPink: "#FF8FAB",
  purple: "#9B72CF",
  red: "#C94040",
  tileGray: "#C8B89A",
  shadowBrown: "#2C1A0E",
  uiGold: "#D4A017",
  uiBorder: "#5C3D1E",
  uiLight: "#F7EDD5",
  uiDark: "#3E2B14",
  uiMid: "#A87B4A",
  menuBg: "#F0E0B0",
  dialogBg: "#FDF6E3",
  heartRed: "#FF4466",
  energyGreen: "#44CC44",
  starGold: "#FFD700",
};

const pixelBorder = `4px solid ${SDV_COLORS.uiBorder}`;
const pixelShadow = `4px 4px 0px ${SDV_COLORS.shadowBrown}`;
const innerShadow = `inset 2px 2px 0px rgba(255,255,255,0.3), inset -2px -2px 0px rgba(0,0,0,0.2)`;

const SDV_PERSONAS = [
  { name: "Farmer Claude", portrait: "🧑‍🌾", color: SDV_COLORS.grassGreen, desc: "Your helpful farm assistant" },
  { name: "Robin", portrait: "👩‍🔧", color: SDV_COLORS.logBrown, desc: "Carpenter & builder" },
  { name: "Willy", portrait: "🎣", color: SDV_COLORS.windowBlue, desc: "The old fisherman" },
  { name: "Wizard", portrait: "🧙", color: SDV_COLORS.purple, desc: "Mysterious & wise" },
];

const SEASON_THEMES = {
  Spring: { bg: "#D4F0A0", sky: "#A8D8EA", accent: SDV_COLORS.starPink, icon: "🌸" },
  Summer: { bg: "#B8E08C", sky: "#87CEEB", accent: SDV_COLORS.sunYellow, icon: "☀️" },
  Fall: { bg: "#E8C57A", sky: "#C4956A", accent: "#D2691E", icon: "🍂" },
  Winter: { bg: "#D0E8F0", sky: "#B0CCE0", accent: "#8EB4D0", icon: "❄️" },
};

const SEASONS = ["Spring", "Summer", "Fall", "Winter"];

const INITIAL_MESSAGES = [
  {
    role: "assistant",
    content: "Howdy, neighbor! Welcome to Stardew Valley. I'm here to help with anything you need — farming tips, cooking recipes, or just a friendly chat. What's on your mind today?",
    persona: SDV_PERSONAS[0],
  },
];

function PixelHeart({ filled }) {
  return (
    <span style={{ fontSize: 12, color: filled ? SDV_COLORS.heartRed : SDV_COLORS.tileGray }}>
      {filled ? "♥" : "♡"}
    </span>
  );
}

function PortraitBox({ persona, size = 64, animate = false }) {
  return (
    <div style={{
      width: size, height: size,
      background: `linear-gradient(135deg, ${persona.color}88, ${persona.color}44)`,
      border: `3px solid ${SDV_COLORS.uiBorder}`,
      borderRadius: 4,
      display: "flex", alignItems: "center", justifyContent: "center",
      fontSize: size * 0.45,
      flexShrink: 0,
      boxShadow: `2px 2px 0 ${SDV_COLORS.shadowBrown}`,
      position: "relative",
      overflow: "hidden",
      animation: animate ? "portraitBob 2s ease-in-out infinite" : "none",
    }}>
      <span style={{ filter: "drop-shadow(1px 1px 0 rgba(0,0,0,0.4))" }}>{persona.portrait}</span>
      <div style={{
        position: "absolute", bottom: 0, left: 0, right: 0, height: 4,
        background: `linear-gradient(90deg, ${persona.color}, ${SDV_COLORS.sunYellow}, ${persona.color})`,
        opacity: 0.7,
      }} />
    </div>
  );
}

function MessageBubble({ msg, isLatest }) {
  const isUser = msg.role === "user";
  return (
    <div style={{
      display: "flex", gap: 12, alignItems: "flex-start",
      flexDirection: isUser ? "row-reverse" : "row",
      marginBottom: 20,
      animation: isLatest ? "fadeSlideIn 0.3s ease-out" : "none",
    }}>
      {!isUser && (
        <PortraitBox persona={msg.persona || SDV_PERSONAS[0]} size={56} />
      )}
      {isUser && (
        <div style={{
          width: 56, height: 56, flexShrink: 0,
          background: `linear-gradient(135deg, ${SDV_COLORS.windowBlue}88, ${SDV_COLORS.windowBlue}44)`,
          border: `3px solid ${SDV_COLORS.uiBorder}`, borderRadius: 4,
          display: "flex", alignItems: "center", justifyContent: "center",
          fontSize: 28, boxShadow: `2px 2px 0 ${SDV_COLORS.shadowBrown}`,
        }}>
          🧑‍🌾
        </div>
      )}
      <div style={{ maxWidth: "72%", minWidth: 80 }}>
        {!isUser && (
          <div style={{
            fontFamily: PIXEL_FONT, fontSize: 8, color: SDV_COLORS.uiGold,
            marginBottom: 4, textShadow: `1px 1px 0 ${SDV_COLORS.shadowBrown}`,
            letterSpacing: 1,
          }}>
            {msg.persona?.name || "Farmer Claude"}
          </div>
        )}
        <div style={{
          background: isUser
            ? `linear-gradient(135deg, ${SDV_COLORS.windowBlue}22, ${SDV_COLORS.windowBlue}44)`
            : SDV_COLORS.dialogBg,
          border: `3px solid ${SDV_COLORS.uiBorder}`,
          borderRadius: 0,
          padding: "12px 16px",
          boxShadow: `3px 3px 0 ${SDV_COLORS.shadowBrown}`,
          position: "relative",
          fontFamily: BODY_FONT,
          fontSize: 14,
          lineHeight: 1.7,
          color: SDV_COLORS.darkBrown,
        }}>
          <div style={{
            position: "absolute",
            top: 0, left: 0, right: 0, height: 3,
            background: `linear-gradient(90deg, ${SDV_COLORS.uiGold}88, transparent, ${SDV_COLORS.uiGold}44)`,
          }} />
          {msg.role === "assistant" && msg.content === "..." ? (
            <div style={{ display: "flex", gap: 6, alignItems: "center", padding: "4px 0" }}>
              {[0, 1, 2].map(i => (
                <div key={i} style={{
                  width: 8, height: 8, borderRadius: "50%",
                  background: SDV_COLORS.grassGreen,
                  animation: `typingDot 1.2s ease-in-out ${i * 0.2}s infinite`,
                }} />
              ))}
            </div>
          ) : msg.content}
        </div>
        <div style={{
          display: "flex", gap: 4, marginTop: 4,
          justifyContent: isUser ? "flex-end" : "flex-start",
        }}>
          {[1,2,3,4,5].map(i => (
            <PixelHeart key={i} filled={i <= Math.floor(Math.random() * 3) + 3} />
          ))}
        </div>
      </div>
    </div>
  );
}

function SeasonDecorations({ season }) {
  const theme = SEASON_THEMES[season];
  const icons = {
    Spring: ["🌸","🌷","🐝","🌻","🌱"],
    Summer: ["🌻","🍓","⭐","🌊","🦋"],
    Fall: ["🍂","🎃","🍄","🌾","🦊"],
    Winter: ["❄️","⛄","🎄","✨","🌨️"],
  };
  return (
    <div style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0, pointerEvents: "none", overflow: "hidden" }}>
      {icons[season].map((icon, i) => (
        <div key={i} style={{
          position: "absolute",
          top: `${10 + i * 18}%`,
          left: i % 2 === 0 ? `${2 + i * 2}%` : "auto",
          right: i % 2 === 1 ? `${2 + i * 2}%` : "auto",
          fontSize: 18, opacity: 0.35,
          animation: `float${i % 3} ${3 + i * 0.5}s ease-in-out infinite`,
          animationDelay: `${i * 0.7}s`,
        }}>{icon}</div>
      ))}
    </div>
  );
}



function QuickActions({ onAction }) {
  const actions = [
    { label: "🌽 Crop Tips", prompt: "What crops should I plant this season?" },
    { label: "🎣 Fishing", prompt: "Give me some fishing tips for beginners!" },
    { label: "💌 Gifts", prompt: "What are the best gifts for villagers?" },
    { label: "⚔️ Mine", prompt: "How do I survive deeper mine levels?" },
    { label: "🍳 Recipe", prompt: "What's a good cooking recipe I can make on the farm?" },
    { label: "⭐ Events", prompt: "Tell me about upcoming festivals and events!" },
  ];
  return (
    <div style={{
      display: "flex", gap: 8, flexWrap: "wrap",
      padding: "8px 16px",
      background: `${SDV_COLORS.parchment}88`,
      borderBottom: `2px solid ${SDV_COLORS.uiBorder}`,
    }}>
      {actions.map(a => (
        <button key={a.label} onClick={() => onAction(a.prompt)} style={{
          fontFamily: BODY_FONT, fontSize: 12, fontWeight: 700,
          padding: "5px 10px",
          background: SDV_COLORS.warmCream,
          border: `2px solid ${SDV_COLORS.uiBorder}`,
          color: SDV_COLORS.medBrown,
          cursor: "pointer",
          boxShadow: `2px 2px 0 ${SDV_COLORS.shadowBrown}`,
          borderRadius: 0,
          transition: "all 0.1s",
        }}
        onMouseEnter={e => { e.target.style.transform = "translate(-1px,-1px)"; e.target.style.boxShadow = `3px 3px 0 ${SDV_COLORS.shadowBrown}`; }}
        onMouseLeave={e => { e.target.style.transform = "none"; e.target.style.boxShadow = `2px 2px 0 ${SDV_COLORS.shadowBrown}`; }}>
          {a.label}
        </button>
      ))}
    </div>
  );
}



export default function StardewChatbot() {
  const [messages, setMessages] = useState(INITIAL_MESSAGES);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);
  const theme = SEASON_THEMES["Spring"];

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async (text) => {
    const userText = text || input.trim();
    if (!userText || loading) return;
    setInput("");

    const newMessages = [...messages, { role: "user", content: userText }];
    setMessages(newMessages);
    setLoading(true);

    const typingMsg = { role: "assistant", content: "..." };
    setMessages([...newMessages, typingMsg]);

    try {
      // Send the request to our local FastAPI RAG backend
      const apiUrl = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/chat";
      const res = await fetch(apiUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userText }),
      });

      const data = await res.json();
      const reply = data.answer || "Hmm, the wind seems to have blown my words away...";
      setMessages([...newMessages, { role: "assistant", content: reply }]);
    } catch {
      setMessages([...newMessages, {
        role: "assistant",
        content: "Oh my, seems like the power went out! Give me a moment to collect my thoughts...",
      }]);
    }
    setLoading(false);
  };

  const handleKey = e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); } };

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Lato:wght@400;700&display=swap');
        @keyframes fadeSlideIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }
        @keyframes typingDot { 0%,80%,100% { transform: scale(0.6); opacity: 0.4; } 40% { transform: scale(1); opacity: 1; } }
        @keyframes portraitBob { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-3px); } }
        @keyframes float0 { 0%,100% { transform: translateY(0) rotate(0deg); } 50% { transform: translateY(-8px) rotate(5deg); } }
        @keyframes float1 { 0%,100% { transform: translateY(0) rotate(0deg); } 50% { transform: translateY(-12px) rotate(-5deg); } }
        @keyframes float2 { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-6px); } }
        @keyframes starTwinkle { 0%,100% { opacity: 0.3; } 50% { opacity: 1; } }
        @keyframes grassWave { 0%,100% { transform: scaleX(1); } 50% { transform: scaleX(1.02); } }
        .sdv-input:focus { outline: none; box-shadow: 0 0 0 3px ${SDV_COLORS.sunYellow}88 !important; }
        .sdv-send:active { transform: translate(2px,2px) !important; box-shadow: 1px 1px 0 ${SDV_COLORS.shadowBrown} !important; }
        .sdv-send:hover { background: ${SDV_COLORS.sunYellow} !important; }
        ::-webkit-scrollbar { width: 10px; }
        ::-webkit-scrollbar-track { background: ${SDV_COLORS.parchment}; border-left: 2px solid ${SDV_COLORS.uiBorder}; }
        ::-webkit-scrollbar-thumb { background: ${SDV_COLORS.uiMid}; border: 2px solid ${SDV_COLORS.uiBorder}; border-radius: 0; }
      `}</style>

      <div style={{
        fontFamily: BODY_FONT,
        background: theme.sky,
        border: `4px solid ${SDV_COLORS.uiBorder}`,
        boxShadow: `6px 6px 0 ${SDV_COLORS.shadowBrown}`,
        borderRadius: 0,
        overflow: "hidden",
        display: "flex", flexDirection: "column",
        height: 640,
        position: "relative",
      }}>

        {/* Sky background */}
        <div style={{
          position: "absolute", inset: 0, pointerEvents: "none",
          background: `linear-gradient(180deg, ${theme.sky} 0%, ${theme.bg}66 100%)`,
          zIndex: 0,
        }} />
        <SeasonDecorations season="Spring" />

        {/* Header */}
        <div style={{
          background: SDV_COLORS.uiDark,
          padding: "12px 20px",
          display: "flex", alignItems: "center", gap: 12,
          borderBottom: `4px solid ${SDV_COLORS.uiBorder}`,
          position: "relative", zIndex: 10,
        }}>
          <div style={{
            fontFamily: PIXEL_FONT, fontSize: 13, color: SDV_COLORS.sunYellow,
            textShadow: `2px 2px 0 ${SDV_COLORS.shadowBrown}, -1px -1px 0 ${SDV_COLORS.dirtBrown}`,
            letterSpacing: 2, flex: 1,
          }}>
            ⭐ STARDEW CHAT ⭐
          </div>
          <div style={{
            fontFamily: PIXEL_FONT, fontSize: 7, color: SDV_COLORS.tileGray,
            textAlign: "right", lineHeight: 2,
          }}>
            <div style={{ color: SDV_COLORS.uiGold }}>{theme.icon} Spring</div>
          </div>
        </div>

        {/* Quick actions */}
        <div style={{ position: "relative", zIndex: 10 }}>
          <QuickActions onAction={sendMessage} />
        </div>

        {/* Chat area */}
        <div style={{
          flex: 1, overflowY: "auto",
          padding: "20px 20px 10px",
          position: "relative", zIndex: 5,
          background: `${SDV_COLORS.warmCream}99`,
        }}>
          {messages.map((msg, i) => (
            <MessageBubble key={i} msg={msg} isLatest={i === messages.length - 1} />
          ))}
          <div ref={chatEndRef} />
        </div>

        {/* Ground strip */}
        <div style={{
          height: 12, position: "relative", zIndex: 10,
          background: `repeating-linear-gradient(90deg, ${SDV_COLORS.grassGreen} 0px, ${SDV_COLORS.grassGreen} 8px, ${SDV_COLORS.leafGreen} 8px, ${SDV_COLORS.leafGreen} 16px)`,
          borderTop: `3px solid ${SDV_COLORS.uiBorder}`,
          borderBottom: `2px solid ${SDV_COLORS.dirtBrown}`,
        }} />

        {/* Input area */}
        <div style={{
          background: SDV_COLORS.menuBg,
          borderTop: `4px solid ${SDV_COLORS.uiBorder}`,
          padding: "12px 16px",
          display: "flex", gap: 10, alignItems: "flex-end",
          position: "relative", zIndex: 10,
        }}>
          <div style={{ flex: 1, position: "relative" }}>
            <textarea
              className="sdv-input"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKey}
              placeholder="Talk to a villager... (Enter to send)"
              rows={2}
              style={{
                width: "100%", resize: "none",
                background: SDV_COLORS.dialogBg,
                border: `3px solid ${SDV_COLORS.uiBorder}`,
                borderRadius: 0,
                padding: "8px 12px",
                fontFamily: BODY_FONT, fontSize: 14, color: SDV_COLORS.darkBrown,
                boxShadow: innerShadow,
                boxSizing: "border-box",
                lineHeight: 1.6,
              }}
            />
          </div>
          <button
            className="sdv-send"
            onClick={() => sendMessage()}
            disabled={loading || !input.trim()}
            style={{
              background: loading ? SDV_COLORS.tileGray : SDV_COLORS.grassGreen,
              border: `3px solid ${SDV_COLORS.uiBorder}`,
              color: "white",
              fontFamily: PIXEL_FONT, fontSize: 9,
              padding: "12px 16px",
              cursor: loading ? "not-allowed" : "pointer",
              boxShadow: `3px 3px 0 ${SDV_COLORS.shadowBrown}`,
              transition: "all 0.1s",
              letterSpacing: 1,
              whiteSpace: "nowrap",
            }}
          >
            {loading ? "..." : "SEND ▶"}
          </button>
        </div>
      </div>
    </>
  );
}
