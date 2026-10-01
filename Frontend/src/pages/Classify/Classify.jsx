import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ScanLine, Shield, Info, Sparkles } from 'lucide-react';
import UploadBox from '../../components/UploadBox/UploadBox';
import useClassify from '../../hooks/useClassify';
import './Classify.css';

export function Classify() {
  const navigate = useNavigate();
  const { classify, loading, error } = useClassify();

  const handleAnalyze = async (file) => {
    try {
      const result = await classify(file);
      const resultId = result?.classification_id || result?.id;
      if (result && resultId) {
        navigate(`/result/${resultId}`, { state: { result } });
      }
    } catch {
      // Error is tracked in hook state and displayed in UploadBox
    }
  };

  return (
    <div className="classify-page container">
      <div className="classify-header">
        <span className="badge badge-emerald">
          <ScanLine size={14} /> AI Waste Classifier
        </span>
        <h1 className="classify-title">Classify Waste Item</h1>
        <p className="classify-subtitle">
          Upload an image of packaging, food waste, bottles, or discarded items. 
          Our neural network will detect the category and provide strict disposal instructions.
        </p>
      </div>

      <div className="classify-content-grid">
        <div className="classify-main-panel glass-panel">
          <UploadBox
            onAnalyze={handleAnalyze}
            loading={loading}
            externalError={error}
          />
        </div>

        <div className="classify-side-info">
          <div className="glass-panel info-card">
            <div className="info-icon-wrapper">
              <Sparkles size={20} />
            </div>
            <h3 className="info-card-title">PyTorch Local Engine</h3>
            <p className="info-card-text">
              Images are processed via our custom-trained PyTorch model deployed locally without 
              external cloud latency or telemetry.
            </p>
          </div>

          <div className="glass-panel info-card">
            <div className="info-icon-wrapper">
              <Shield size={20} />
            </div>
            <h3 className="info-card-title">Confidence Guardrails</h3>
            <p className="info-card-text">
              Predictions include confidence score metrics. Low-confidence scans will prompt you 
              to verify before sorting to avoid stream contamination.
            </p>
          </div>

          <div className="glass-panel info-card">
            <div className="info-icon-wrapper">
              <Info size={20} />
            </div>
            <h3 className="info-card-title">Supported Formats</h3>
            <p className="info-card-text">
              Standard JPG, PNG, and modern WEBP image formats under 5 MB are supported. 
              Mobile devices can take direct camera photos.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Classify;
