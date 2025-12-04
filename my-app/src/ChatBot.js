import React, { useState, useRef, useEffect } from 'react';
import './ChatBot.css';

const GEMINI_API_KEY = 'AIzaSyD_9ohSE8klHLlHc8O-_2u4ROQCprRxUUU';

const SYSTEM_CONTEXT = `You are CertiBot 🤖, a friendly, joyful, and slightly sarcastic AI assistant for the Certificate Mass Production Tool. Always keep replies in plain text, short (max 5 sentences), upbeat, and packed with helpful emojis. Write each sentence on its own line instead of one big paragraph.

Rules:
- ONLY answer questions related to this certificate maker project.
- Keep language simple and easy to skim; no **bold** formatting.
- When explaining a process or procedure, use clear step lines like "Step 1:" or "Tip:" on separate lines to make it feel like bullet points.
- If someone asks about anything else, give a playful sarcastic nudge and steer them back to certificates.
- You know EVERYTHING about the project:

PROJECT KNOWLEDGE:
- The tool creates bulk certificates from a template image + Excel data
- Users drag/drop a certificate template (PNG, JPG, etc.)
- The system auto-detects "masked regions" (blank areas for text)
- Users can manually draw masks using "Manual Masking" mode
- Each mask gets a letter (a, b, c...) and users assign labels like NAME, DATE, SCORE
- Formatting options: Bold (B), Italic (I), Underline (U), Color picker, Font size, Font family dropdown
- Users upload an Excel file (.xlsx or .xls) with column headers matching the assigned labels
- Validation checks: column count must match mask count, column names must match labels exactly
- Preview shows sample certificate with first Excel row data
- "Go back and edit" returns to template view
- "Continue" generates all certificates
- Output: Download individual certificates or "Download All" to a folder
- Files are saved as high-quality JPG images
- Red boundary shows around selected mask only; clicking elsewhere hides it
- Rotation handle (⟳) above masks for rotating text areas
- Resize handles at corners and edges
- Move by dragging center handle

COMMON ISSUES:
- "Column and mask variable number mismatch error" = Excel columns ≠ number of masks
- "Mask variable corresponding string and column name error" = Column headers don't match assigned labels exactly
- Manual masking stays ON after returning from preview? No! It's now OFF by default
- Status bar shows "Manual Masking: ON/OFF" when toggled

Tone reminders:
- Use cheerful sarcasm sparingly, never rude.
- Emojis are welcome but keep sentences short and clear.
- Always end with a quick offer to help or next-step hint when appropriate.`;

const SAMPLE_QUESTIONS = [
  "How do I add a masked region? 🎯",
  "Why am I getting column mismatch error? ⚠️"
];

// Intro message will be defined after helpers are available

const sentenceRegex = /[^.!?]+[.!?]?/g;

const isStructuredLine = (line) => /^(step\s*\d+|tip|pro tip|reminder|heads up|note)[:\-\s]/i.test(line);

const formatBotReply = (text) => {
  if (!text) return '';
  const cleaned = text.replace(/\r\n/g, '\n').trim();
  if (!cleaned) return '';

  const output = [];
  cleaned.split(/\n+/).forEach(rawLine => {
    const line = rawLine.trim();
    if (!line) return;
    if (isStructuredLine(line)) {
      output.push(line);
      return;
    }
    const segments = line.match(sentenceRegex);
    if (segments) {
      segments.forEach(segment => {
        const sentence = segment.trim();
        if (sentence) {
          output.push(sentence);
        }
      });
    } else {
      output.push(line);
    }
  });

  return output.join('\n');
};

const INTRO_MESSAGE = formatBotReply(
  "Hey there, certificate wizard! 🧙‍♂️✨ I'm CertiBot, your friendly guide to mass-producing awesome certificates! Ask me anything about masks, templates, Excel magic, or formatting sorcery! 🎓🚀 Need a hand right away? I'm all circuits!"
);

function ChatBot() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      role: 'bot',
      content: INTRO_MESSAGE
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  const sendMessage = async (text) => {
    if (!text.trim()) return;

    const userMessage = { role: 'user', content: text };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch(
        `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${GEMINI_API_KEY}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            contents: [
              {
                parts: [
                  { text: SYSTEM_CONTEXT },
                  { text: `User question: ${text}` }
                ]
              }
            ],
            generationConfig: {
              temperature: 0.8,
              maxOutputTokens: 500,
            }
          })
        }
      );

      const data = await response.json();
      
      let botReply = "Oops! 🤖💥 My circuits got tangled. Try again?";
      if (data.candidates && data.candidates[0]?.content?.parts?.[0]?.text) {
        botReply = data.candidates[0].content.parts[0].text;
      }

      setMessages(prev => [...prev, { role: 'bot', content: formatBotReply(botReply) }]);
    } catch (error) {
      console.error('Gemini API error:', error);
      const fallback = formatBotReply(
        "Yikes! 😵 Something went wrong with my neural pathways. Check your internet connection and try again! 🔌 Need me after that? I'll be here!"
      );
      setMessages(prev => [...prev, { 
        role: 'bot', 
        content: fallback 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(input);
  };

  const handleSampleClick = (question) => {
    sendMessage(question);
  };

  return (
    <>
      {/* Floating Bot Icon */}
      <div 
        className={`chatbot-trigger ${isOpen ? 'hidden' : ''}`} 
        onClick={() => setIsOpen(true)}
        title="Need help? Click me! 🤖"
      >
        <div className="bot-icon">
          <svg viewBox="0 0 100 100" className="bot-svg">
            {/* Robot head */}
            <defs>
              <linearGradient id="botGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style={{ stopColor: '#8b5cf6' }} />
                <stop offset="100%" style={{ stopColor: '#6366f1' }} />
              </linearGradient>
              <filter id="glow">
                <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
                <feMerge>
                  <feMergeNode in="coloredBlur"/>
                  <feMergeNode in="SourceGraphic"/>
                </feMerge>
              </filter>
            </defs>
            {/* Antenna */}
            <line x1="50" y1="5" x2="50" y2="18" stroke="#06b6d4" strokeWidth="3" strokeLinecap="round"/>
            <circle cx="50" cy="5" r="4" fill="#06b6d4" filter="url(#glow)"/>
            {/* Head */}
            <rect x="20" y="18" width="60" height="55" rx="12" fill="url(#botGrad)" stroke="#a78bfa" strokeWidth="2"/>
            {/* Eyes */}
            <ellipse cx="35" cy="42" rx="8" ry="10" fill="#0f172a"/>
            <ellipse cx="65" cy="42" rx="8" ry="10" fill="#0f172a"/>
            <circle cx="35" cy="40" r="4" fill="#06b6d4" className="eye-glow"/>
            <circle cx="65" cy="40" r="4" fill="#06b6d4" className="eye-glow"/>
            {/* Mouth */}
            <path d="M 35 60 Q 50 70 65 60" stroke="#06b6d4" strokeWidth="3" fill="none" strokeLinecap="round"/>
            {/* Ear panels */}
            <rect x="10" y="35" width="8" height="20" rx="3" fill="#6366f1"/>
            <rect x="82" y="35" width="8" height="20" rx="3" fill="#6366f1"/>
            {/* Neck */}
            <rect x="40" y="73" width="20" height="8" fill="#475569"/>
            {/* Body hint */}
            <rect x="30" y="81" width="40" height="15" rx="5" fill="url(#botGrad)" opacity="0.8"/>
          </svg>
        </div>
        <div className="pulse-ring"></div>
        <div className="pulse-ring delay"></div>
      </div>

      {/* Chat Window */}
      <div className={`chatbot-window ${isOpen ? 'open' : ''}`}>
        {/* Header */}
        <div className="chatbot-header">
          <div className="header-bot-info">
            <div className="header-bot-icon">🤖</div>
            <div className="header-text">
              <span className="header-name">CertiBot</span>
              <span className="header-status">
                <span className="status-dot"></span>
                Online & Ready to Help!
              </span>
            </div>
          </div>
          <button className="close-btn" onClick={() => setIsOpen(false)}>
            <svg viewBox="0 0 24 24" width="20" height="20">
              <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          </button>
        </div>

        {/* Messages */}
        <div className="chatbot-messages">
          {messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.role}`}>
              {msg.role === 'bot' && <span className="bot-avatar">🤖</span>}
              <div className="message-content">{msg.content}</div>
            </div>
          ))}
          {isLoading && (
            <div className="message bot">
              <span className="bot-avatar">🤖</span>
              <div className="message-content typing">
                <span className="dot"></span>
                <span className="dot"></span>
                <span className="dot"></span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Sample Questions */}
        {messages.length <= 1 && (
          <div className="sample-questions">
            <p className="sample-label">Quick questions to get started:</p>
            {SAMPLE_QUESTIONS.map((q, idx) => (
              <button 
                key={idx} 
                className="sample-btn"
                onClick={() => handleSampleClick(q)}
              >
                {q}
              </button>
            ))}
          </div>
        )}

        {/* Input */}
        <form className="chatbot-input" onSubmit={handleSubmit}>
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask me about certificates... 🎓"
            disabled={isLoading}
          />
          <button type="submit" disabled={isLoading || !input.trim()}>
            <svg viewBox="0 0 24 24" width="20" height="20">
              <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
            </svg>
          </button>
        </form>
      </div>
    </>
  );
}

export default ChatBot;
