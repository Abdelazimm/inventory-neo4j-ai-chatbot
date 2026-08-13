import React, { useState, useRef, useEffect } from 'react';
import { Send, Network, User, Sparkles, Loader2 } from 'lucide-react';
import { Message } from '../types';
import { DebugPanel } from './DebugPanel';
import { GraphVisualization } from './GraphVisualization';

interface ChatWindowProps {
  messages: Message[];
  isLoading: boolean;
  onSendMessage: (text: string) => void;
  debugMode: boolean;
}

const EXAMPLE_GRAPH_QUESTIONS = [
  "Which sites contain assets supplied by TechSupply Inc?",
  "Which vendors supply items stored in more than one site?",
  "Where is asset TAG-1001 located?",
  "Show the relationship path from TechSupply Inc to Headquarters.",
  "Which customers placed orders containing items supplied by TechSupply Inc?",
  "What is the most expensive asset in our graph?"
];

export const ChatWindow: React.FC<ChatWindowProps> = ({
  messages,
  isLoading,
  onSendMessage,
  debugMode
}) => {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    onSendMessage(input.trim());
    setInput('');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100%', position: 'relative', overflow: 'hidden' }}>
      <div className="chat-scroll-padding" style={{ flex: 1, overflowY: 'auto', padding: '24px 32px' }}>
        {messages.length === 0 ? (
          <div style={{ maxWidth: '640px', margin: '20px auto', textAlign: 'center' }}>
            <div style={{
              width: '54px',
              height: '54px',
              borderRadius: '16px',
              background: 'var(--accent-gradient)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 16px auto',
              boxShadow: 'var(--accent-glow)'
            }}>
              <Network size={28} color="#fff" />
            </div>
            <h2 style={{ fontSize: '20px', fontWeight: 600, marginBottom: '6px' }}>
              Welcome to Inventory Knowledge Graph
            </h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginBottom: '20px' }}>
              Explore multi-hop relationships, vendor dependencies, and asset locations across your supply chain.
            </p>

            <div style={{ textAlign: 'left' }}>
              <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '10px' }}>
                Multi-Hop Graph Queries:
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '8px' }}>
                {EXAMPLE_GRAPH_QUESTIONS.map((q, idx) => (
                  <button
                    key={idx}
                    onClick={() => onSendMessage(q)}
                    style={{
                      padding: '10px 14px',
                      background: 'rgba(30, 41, 59, 0.4)',
                      border: '1px solid var(--border-color)',
                      borderRadius: 'var(--radius-md)',
                      color: 'var(--text-primary)',
                      textAlign: 'left',
                      fontSize: '12px',
                      cursor: 'pointer',
                      transition: 'all 0.2s ease'
                    }}
                    onMouseEnter={(e) => (e.currentTarget.style.borderColor = 'rgba(16, 185, 129, 0.5)')}
                    onMouseLeave={(e) => (e.currentTarget.style.borderColor = 'var(--border-color)')}
                  >
                    "{q}"
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div style={{ maxWidth: '800px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {messages.map((msg) => {
              const isUser = msg.sender === 'user';
              return (
                <div
                  key={msg.id}
                  className="animate-fade-in chat-message-bubble"
                  style={{
                    display: 'flex',
                    gap: '12px',
                    alignSelf: isUser ? 'flex-end' : 'flex-start',
                    maxWidth: '85%',
                    width: '100%'
                  }}
                >
                  {!isUser && (
                    <div style={{
                      width: '32px',
                      height: '32px',
                      borderRadius: '8px',
                      background: 'var(--accent-gradient)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      flexShrink: 0
                    }}>
                      <Network size={17} color="#fff" />
                    </div>
                  )}

                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{
                      padding: '12px 16px',
                      borderRadius: isUser ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
                      background: isUser ? 'var(--accent-gradient)' : 'rgba(30, 41, 59, 0.6)',
                      border: isUser ? 'none' : '1px solid var(--border-color)',
                      color: '#fff',
                      fontSize: '14px',
                      whiteSpace: 'pre-wrap',
                      lineHeight: 1.5,
                      wordBreak: 'break-word'
                    }}>
                      {msg.text}
                    </div>

                    {/* Interactive Force Graph Visualization */}
                    {!isUser && msg.graph_data && (
                      <div className="table-responsive" style={{ marginTop: '10px' }}>
                        <GraphVisualization graphData={msg.graph_data} />
                      </div>
                    )}

                    {/* Cypher Debug & Multi-Hop Telemetry Panel */}
                    {!isUser && debugMode && (
                      <div className="table-responsive">
                        <DebugPanel metadata={msg.metadata} />
                      </div>
                    )}
                  </div>

                  {isUser && (
                    <div style={{
                      width: '32px',
                      height: '32px',
                      borderRadius: '8px',
                      background: 'var(--bg-tertiary)',
                      border: '1px solid var(--border-color)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      flexShrink: 0
                    }}>
                      <User size={17} color="var(--text-secondary)" />
                    </div>
                  )}
                </div>
              );
            })}

            {isLoading && (
              <div style={{ display: 'flex', gap: '12px', alignSelf: 'flex-start', maxWidth: '90%' }}>
                <div style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '8px',
                  background: 'var(--accent-gradient)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0
                }}>
                  <Network size={17} color="#fff" />
                </div>
                <div style={{
                  padding: '12px 16px',
                  borderRadius: '16px 16px 16px 4px',
                  background: 'rgba(30, 41, 59, 0.6)',
                  border: '1px solid var(--border-color)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  fontSize: '13px',
                  color: 'var(--text-secondary)'
                }}>
                  <Loader2 size={15} className="animate-spin" />
                  Traversing knowledge graph & executing Cypher...
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      <div className="chat-input-wrapper" style={{
        padding: '14px 20px',
        borderTop: '1px solid var(--border-color)',
        background: 'rgba(7, 11, 18, 0.95)',
        zIndex: 10
      }}>
        <form onSubmit={handleSubmit} style={{ maxWidth: '800px', margin: '0 auto', display: 'flex', gap: '8px' }}>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a graph query (e.g., 'Where is asset TAG-1001 located?')..."
            rows={1}
            style={{
              flex: 1,
              padding: '10px 14px',
              borderRadius: 'var(--radius-md)',
              background: 'var(--bg-secondary)',
              border: '1px solid var(--border-color)',
              color: '#fff',
              fontSize: '14px',
              resize: 'none',
              outline: 'none',
              fontFamily: 'inherit'
            }}
            onFocus={(e) => (e.target.style.borderColor = 'var(--accent-primary)')}
            onBlur={(e) => (e.target.style.borderColor = 'var(--border-color)')}
          />
          <button
            type="submit"
            className="btn btn-primary"
            disabled={!input.trim() || isLoading}
            style={{ opacity: !input.trim() || isLoading ? 0.5 : 1, padding: '0 16px', flexShrink: 0 }}
          >
            <Send size={15} />
          </button>
        </form>
      </div>
    </div>
  );
};
