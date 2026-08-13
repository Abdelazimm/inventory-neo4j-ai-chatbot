import React from 'react';
import { Network, ArrowRight, Layers, Tag } from 'lucide-react';
import { GraphDataPayload, GraphNode, GraphEdge } from '../types';

interface GraphVisualizationProps {
  graphData?: GraphDataPayload;
}

const GROUP_COLORS: Record<string, string> = {
  Asset: 'node-asset',
  Vendor: 'node-vendor',
  Item: 'node-item',
  Site: 'node-site',
  Location: 'node-location',
  Customer: 'node-asset',
  PurchaseOrder: 'node-vendor',
  SalesOrder: 'node-item',
  Category: 'node-location'
};

export const GraphVisualization: React.FC<GraphVisualizationProps> = ({ graphData }) => {
  if (!graphData || (!graphData.nodes.length && !graphData.edges.length)) {
    return null;
  }

  const nodes = graphData.nodes || [];
  const edges = graphData.edges || [];

  return (
    <div style={{
      marginTop: '12px',
      padding: '14px 18px',
      background: 'rgba(6, 78, 59, 0.25)',
      border: '1px solid rgba(16, 185, 129, 0.35)',
      borderRadius: 'var(--radius-md)',
      fontSize: '13px'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px', borderBottom: '1px solid rgba(255, 255, 255, 0.08)', paddingBottom: '6px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#6ee7b7', fontWeight: 600 }}>
          <Network size={16} />
          Knowledge Graph Subgraph Traversal
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', color: 'var(--text-muted)', fontSize: '11px' }}>
          <span>{nodes.length} Nodes</span>
          <span>{edges.length} Relationships</span>
        </div>
      </div>

      {/* Nodes Chips Grid */}
      <div style={{ marginBottom: '10px' }}>
        <div style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '6px' }}>
          Traversed Nodes:
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
          {nodes.map((node) => {
            const colorClass = GROUP_COLORS[node.group] || 'node-asset';
            return (
              <div key={node.id} className={`node-pill ${colorClass}`} title={JSON.stringify(node.properties || {})}>
                <span style={{ fontSize: '10px', opacity: 0.75 }}>({node.group})</span>
                <strong>{node.label}</strong>
              </div>
            );
          })}
        </div>
      </div>

      {/* Directed Relationships Flow */}
      {edges.length > 0 && (
        <div>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '6px' }}>
            Relationship Paths:
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {edges.map((edge, idx) => {
              const srcNode = nodes.find((n) => n.id === edge.source);
              const tgtNode = nodes.find((n) => n.id === edge.target);
              const srcLabel = srcNode ? srcNode.label : edge.source;
              const tgtLabel = tgtNode ? tgtNode.label : edge.target;

              return (
                <div
                  key={edge.id || idx}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    background: 'rgba(15, 23, 42, 0.7)',
                    padding: '6px 12px',
                    borderRadius: '6px',
                    border: '1px solid rgba(255, 255, 255, 0.05)',
                    fontSize: '12px'
                  }}
                >
                  <span style={{ color: '#93c5fd', fontWeight: 500 }}>{srcLabel}</span>
                  <span style={{ color: '#10b981', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '11px', background: 'rgba(16, 185, 129, 0.15)', padding: '2px 6px', borderRadius: '4px' }}>
                    -[:{edge.label}]-&gt;
                  </span>
                  <span style={{ color: '#fcd34d', fontWeight: 500 }}>{tgtLabel}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
