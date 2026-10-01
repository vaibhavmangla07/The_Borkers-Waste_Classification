import React from 'react';
import { Info, Cpu, Database, Server, Layers, ShieldCheck, Terminal } from 'lucide-react';
import './About.css';

export function About() {
  return (
    <div className="about-page container">
      <div className="page-header">
        <div className="badge badge-cyan">
          <Info size={14} /> System Blueprint
        </div>
        <h1 className="page-title">About EcoVision AI</h1>
        <p className="page-subtitle">
          An end-to-end intelligent waste classification system addressing contamination in municipal recycling streams.
        </p>
      </div>

      {/* Problem & Solution Cards */}
      <div className="about-sections-grid">
        <div className="glass-panel about-card">
          <h2 className="card-heading">The Problem</h2>
          <p className="card-paragraph">
            Municipal recycling programs suffer from a contamination rate exceeding 25%. Non-recyclable items 
            and improper disposal ruin entire sorting batches, leading to unnecessary landfill overflow and high 
            processing penalties.
          </p>
        </div>

        <div className="glass-panel about-card">
          <h2 className="card-heading">The EcoVision Solution</h2>
          <p className="card-paragraph">
            EcoVision AI couples on-device or local PyTorch neural networks with strict disposal intelligence, 
            giving citizens and sorting operators immediate, deterministic guidance with confidence-guarded recommendations.
          </p>
        </div>
      </div>

      {/* Tech Stack Breakdown */}
      <div className="glass-panel tech-stack-panel">
        <h2 className="panel-title">Production Technology Stack</h2>
        <div className="tech-stack-grid">
          <div className="tech-item">
            <div className="tech-icon-wrap"><Cpu size={24} /></div>
            <div>
              <h4 className="tech-name">PyTorch Engine</h4>
              <p className="tech-desc">Custom local computer vision model inference with latency under 80ms.</p>
            </div>
          </div>

          <div className="tech-item">
            <div className="tech-icon-wrap"><Server size={24} /></div>
            <div>
              <h4 className="tech-name">FastAPI Backend</h4>
              <p className="tech-desc">High-performance asynchronous REST endpoints handling multipart uploads.</p>
            </div>
          </div>

          <div className="tech-item">
            <div className="tech-icon-wrap"><Database size={24} /></div>
            <div>
              <h4 className="tech-name">PostgreSQL</h4>
              <p className="tech-desc">Relational persistence for classification audits, analytics, and taxonomy.</p>
            </div>
          </div>

          <div className="tech-item">
            <div className="tech-icon-wrap"><Layers size={24} /></div>
            <div>
              <h4 className="tech-name">React + Vite</h4>
              <p className="tech-desc">Ultra-responsive client with pure vanilla CSS architecture and glassmorphic UI.</p>
            </div>
          </div>

          <div className="tech-item">
            <div className="tech-icon-wrap"><Terminal size={24} /></div>
            <div>
              <h4 className="tech-name">Docker & Kubernetes</h4>
              <p className="tech-desc">Containerized microservices orchestrated via Helm charts for cloud deployment.</p>
            </div>
          </div>

          <div className="tech-item">
            <div className="tech-icon-wrap"><ShieldCheck size={24} /></div>
            <div>
              <h4 className="tech-name">Strict Guardrails</h4>
              <p className="tech-desc">Low-confidence thresholding prevents accidental waste stream contamination.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default About;
