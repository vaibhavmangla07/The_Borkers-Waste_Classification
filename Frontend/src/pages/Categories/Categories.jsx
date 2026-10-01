import React from 'react';
import { BookOpen, CheckCircle2 } from 'lucide-react';
import { MOCK_DATA } from '../../services/api';
import './Categories.css';

export function Categories() {
  const categories = MOCK_DATA.categories;

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

      <div className="categories-grid">
        {categories.map((cat) => (
          <div key={cat.id} className="glass-panel glass-panel-hover category-card">
            <div className="category-card-top">
              <span className="badge badge-emerald">{cat.group}</span>
              <span className="category-id">Stream #{cat.id}</span>
            </div>

            <h3 className="category-name">{cat.name}</h3>
            <p className="category-desc">{cat.description}</p>

            <div className="category-guidance-preview">
              <div className="preview-label">
                <CheckCircle2 size={14} className="check-icon" /> Disposal Rule
              </div>
              <p className="guidance-summary">
                {cat.group === 'Recyclable' && 'Clean, rinse, and place in dry recyclable container.'}
                {cat.group === 'Compostable' && 'Segregate into wet bio-degradable green container.'}
                {cat.group === 'Special Disposal' && 'Requires specialized e-waste or hazard drop-off facility.'}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Categories;
