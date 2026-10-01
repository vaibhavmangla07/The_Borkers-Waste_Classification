import React, { useState, useEffect } from 'react';
import { BookOpen, CheckCircle2, AlertCircle } from 'lucide-react';
import { api } from '../../services/api';
import './Categories.css';

export function Categories() {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadCategories() {
      try {
        const data = await api.getCategories();
        setCategories(data);
        setError(null);
      } catch (err) {
        console.error('Failed to load categories', err);
        setError('Unable to load waste categories. Please try again later.');
      } finally {
        setLoading(false);
      }
    }
    loadCategories();
  }, []);

  if (loading) {
    return (
      <div className="categories-page container">
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading waste categories...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="categories-page container">
        <div className="error-panel">
          <AlertCircle size={24} className="error-icon" />
          <p>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="categories-page container">
      <div className="page-header">
        <div className="badge badge-emerald">
          <BookOpen size={14} /> Waste Directory
        </div>
        <h1 className="page-title">Waste Categories & Sorting Guide</h1>
        <p className="page-subtitle">
          Explore all standard waste streams classified by the EcoVision AI PyTorch neural network.
        </p>
      </div>

      {categories.length === 0 ? (
        <div className="empty-state">
          <BookOpen size={48} className="empty-icon" />
          <h3>No categories found</h3>
          <p>The waste directory is currently empty.</p>
        </div>
      ) : (
        <div className="categories-grid">
          {categories.map((cat) => (
            <div key={cat.id} className="glass-panel glass-panel-hover category-card">
              <div className="category-card-top">
                <span className="badge badge-emerald">Category</span>
                <span className="category-id">Stream #{cat.id}</span>
              </div>

              <h3 className="category-name">{cat.name}</h3>
              <p className="category-desc">{cat.description}</p>

              <div className="category-guidance-preview">
                <div className="preview-label">
                  <CheckCircle2 size={14} className="check-icon" /> Disposal Rule
                </div>
                <p className="guidance-summary">
                  {cat.guidelines ? cat.guidelines.title : 'General disposal guidelines apply.'}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Categories;
