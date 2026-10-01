import React from 'react';
import { Link } from 'react-router-dom';
import { 
  Sparkles, 
  ArrowRight, 
  Cpu, 
  Recycle, 
  UploadCloud
} from 'lucide-react';
import StatCard from '../../components/StatCard/StatCard';
import './Landing.css';

export function Landing() {
  return (
    <div className="landing-page">
      {/* Hero Section */}
      <section className="hero-section">
        {/* Subtle Ambient Atmosphere */}
        <div className="hero-atmosphere" aria-hidden="true">
          <div className="atmosphere-orb orb-primary" />
          <div className="atmosphere-orb orb-secondary" />
          <div className="hero-scanner" />
          <div className="hero-particles">
            <span className="particle p-1" />
            <span className="particle p-2" />
            <span className="particle p-3" />
            <span className="particle p-4" />
            <span className="particle p-5" />
            <span className="particle p-6" />
            <span className="particle p-7" />
          </div>
        </div>

        <div className="container hero-container">
          <div className="hero-badge badge badge-emerald animate-hero-badge">
            <Sparkles size={14} />
            <span>Next-Gen Waste Intelligence • PyTorch Powered</span>
          </div>

          <h1 className="hero-title animate-hero-title">
            Smart Waste Classification <br />
            <span className="text-gradient-animated">For a Cleaner Planet</span>
          </h1>

          <p className="hero-subtitle animate-hero-desc">
            Instantly identify recyclable, organic, and hazardous waste with high-precision 
            computer vision. EcoVision AI transforms municipal and domestic sorting with real-time 
            disposal intelligence.
          </p>

          <div className="hero-cta-group animate-hero-cta">
            <Link to="/classify" className="btn btn-primary btn-hero">
              <Sparkles size={18} />
              <span>Analyze Waste Now</span>
              <ArrowRight size={18} className="btn-arrow" />
            </Link>

            <Link to="/about" className="btn btn-secondary btn-hero-secondary">
              <span>Explore AI Architecture</span>
            </Link>
          </div>

          {/* Quick Metrics (Benchmark Goals & Stream Scope) */}
          <div className="hero-stats-grid">
            <StatCard
              className="animate-card-1"
              label="Model Target Accuracy"
              value="94.6%"
              subtext="Validation benchmark target"
              change="Target"
              trend="up"
            />
            <StatCard
              className="animate-card-2"
              label="Avg Inference Goal"
              value="<80ms"
              subtext="PyTorch local runtime goal"
              change="Goal"
              trend="up"
            />
            <StatCard
              className="animate-card-3"
              label="Waste Streams"
              value="6 Streams"
              subtext="Plastic, Organic, Glass, Metal, etc."
              change="6 Classes"
              trend="neutral"
            />
          </div>
        </div>
      </section>

      {/* How it Works */}
      <section className="how-it-works-section">
        <div className="container">
          <div className="section-header">
            <span className="badge badge-cyan">Workflow</span>
            <h2 className="section-title">How EcoVision AI Works</h2>
            <p className="section-desc">From image upload to compliant disposal in milliseconds</p>
          </div>

          <div className="steps-grid">
            <div className="glass-panel step-card">
              <div className="step-number">01</div>
              <div className="step-icon-wrap">
                <UploadCloud size={24} />
              </div>
              <h3 className="step-title">Upload Photo</h3>
              <p className="step-text">Snap or upload a photo of your waste item from mobile or desktop.</p>
            </div>

            <div className="glass-panel step-card">
              <div className="step-number">02</div>
              <div className="step-icon-wrap">
                <Cpu size={24} />
              </div>
              <h3 className="step-title">Local Vision Model</h3>
              <p className="step-text">PyTorch deep learning model classifies material type and calculates confidence.</p>
            </div>

            <div className="glass-panel step-card">
              <div className="step-number">03</div>
              <div className="step-icon-wrap">
                <Recycle size={24} />
              </div>
              <h3 className="step-title">Disposal Guidance</h3>
              <p className="step-text">Get bin color, preparation steps, and contamination avoidance rules.</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Banner */}
      <section className="cta-banner-section">
        <div className="container">
          <div className="glass-panel cta-banner">
            <div className="cta-content">
              <h2 className="cta-title">Ready to Classify Your First Item?</h2>
              <p className="cta-text">
                Experience real-time AI classification with zero external API dependencies.
              </p>
            </div>
            <Link to="/classify" className="btn btn-primary cta-btn">
              <span>Start Classification</span>
              <ArrowRight size={18} />
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Landing;
