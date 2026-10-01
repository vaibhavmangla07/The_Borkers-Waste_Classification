import React, { useState, useRef } from 'react';
import { UploadCloud, Image as ImageIcon, X, AlertCircle, Loader2, Sparkles } from 'lucide-react';
import './UploadBox.css';

const MAX_FILE_SIZE_MB = 5;
const ACCEPTED_TYPES = ['image/jpeg', 'image/png', 'image/webp'];

export function UploadBox({ onAnalyze, loading = false, externalError = null }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [localError, setLocalError] = useState(null);
  const inputRef = useRef(null);

  const validateAndSetFile = (file) => {
    setLocalError(null);
    if (!file) return;

    if (!ACCEPTED_TYPES.includes(file.type)) {
      setLocalError('Please upload a JPG, PNG or WEBP image.');
      return;
    }

    if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
      setLocalError(`File size exceeds ${MAX_FILE_SIZE_MB} MB limit.`);
      return;
    }

    setSelectedFile(file);
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const handleRemove = (e) => {
    e.stopPropagation();
    setSelectedFile(null);
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
      setPreviewUrl(null);
    }
    setLocalError(null);
    if (inputRef.current) {
      inputRef.current.value = '';
    }
  };

  const handleAnalyzeClick = () => {
    if (selectedFile && onAnalyze && !loading) {
      onAnalyze(selectedFile);
    }
  };

  const displayError = (typeof externalError === 'string' ? externalError : externalError?.message) || localError;

  return (
    <div className="upload-container">
      {displayError && (
        <div className="upload-error-alert" role="alert">
          <AlertCircle size={18} />
          <span>{displayError}</span>
        </div>
      )}

      <div
        className={`upload-dropzone ${dragActive ? 'drag-active' : ''} ${selectedFile ? 'has-file' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => !selectedFile && inputRef.current?.click()}
        role="button"
        tabIndex={0}
        aria-label="Upload waste item image dropzone. Click or press Enter to browse files or snap a photo."
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            if (!selectedFile) inputRef.current?.click();
          }
        }}
      >
        <input
          ref={inputRef}
          type="file"
          accept="image/jpeg,image/png,image/webp"
          capture="environment"
          onChange={handleChange}
          style={{ display: 'none' }}
          id="waste-image-input"
        />

        {!selectedFile ? (
          <div className="upload-prompt">
            <div className="upload-icon-wrapper">
              <UploadCloud size={36} />
            </div>
            <h3 className="upload-title">Drop your waste photo here</h3>
            <p className="upload-desc">
              or <span className="browse-link">browse from files</span> / use camera
            </p>
            <div className="upload-spec-tags">
              <span className="spec-tag">JPG, PNG, WEBP</span>
              <span className="spec-tag">Max 5 MB</span>
            </div>
          </div>
        ) : (
          <div className="preview-card">
            <div className="preview-image-container">
              <img src={previewUrl} alt="Waste item preview" className="preview-image" />
              <button
                type="button"
                className="remove-btn"
                onClick={handleRemove}
                title="Remove image"
                aria-label="Remove image"
                disabled={loading}
              >
                <X size={18} />
              </button>
            </div>
            <div className="preview-meta">
              <div className="preview-file-info">
                <ImageIcon size={16} className="file-icon" />
                <span className="preview-filename">{selectedFile.name}</span>
                <span className="preview-filesize">
                  ({(selectedFile.size / (1024 * 1024)).toFixed(2)} MB)
                </span>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="upload-action-bar">
        <button
          type="button"
          className="btn btn-primary btn-analyze"
          disabled={!selectedFile || loading}
          onClick={handleAnalyzeClick}
        >
          {loading ? (
            <>
              <Loader2 size={18} className="spinner" />
              <span>Analyzing with PyTorch Model...</span>
            </>
          ) : (
            <>
              <Sparkles size={18} />
              <span>Analyze Waste Item</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}

export default UploadBox;
