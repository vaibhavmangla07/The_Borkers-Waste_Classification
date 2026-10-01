import React, { useState, useEffect } from 'react';
import { NavLink, Link } from 'react-router-dom';
import { 
  Sparkles, 
  ScanLine, 
  LayoutDashboard, 
  History as HistoryIcon, 
  BarChart3, 
  BookOpen, 
  Info, 
  Menu, 
  X, 
  Leaf 
} from 'lucide-react';
import './Navbar.css';

export function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Keyboard accessibility: Close mobile drawer on Escape key
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && mobileMenuOpen) {
        setMobileMenuOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [mobileMenuOpen]);

  // Lock body scroll when mobile menu is open
  useEffect(() => {
    if (mobileMenuOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [mobileMenuOpen]);

  const handleNavClick = () => {
    setMobileMenuOpen(false);
  };

  const navLinks = [
    { to: '/', label: 'Home', icon: Leaf },
    { to: '/classify', label: 'Classify', icon: ScanLine },
    { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/history', label: 'History', icon: HistoryIcon },
    { to: '/analytics', label: 'Analytics', icon: BarChart3 },
    { to: '/categories', label: 'Categories', icon: BookOpen },
    { to: '/about', label: 'About', icon: Info },
  ];

  return (
    <>
      <header className={`navbar ${scrolled ? 'navbar-scrolled' : ''}`}>
        <div className="container nav-container">
          <Link to="/" className="nav-brand" onClick={handleNavClick} aria-label="EcoVision AI Homepage">
            <div className="nav-logo-icon">
              <Leaf size={22} aria-hidden="true" />
            </div>
            <span className="brand-text">
              EcoVision <span className="text-gradient-cyan">AI</span>
            </span>
          </Link>

          {/* Navigation links & Mobile Drawer Content */}
          <nav
            id="primary-navigation"
            className={`nav-links ${mobileMenuOpen ? 'open' : ''}`}
            aria-label="Main Navigation"
          >
            {navLinks.map((item) => {
              const Icon = item.icon;
              return (
                <div key={item.to} className="nav-item">
                  <NavLink
                    to={item.to}
                    className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                    end={item.to === '/'}
                    onClick={handleNavClick}
                  >
                    <Icon size={16} className="nav-icon" aria-hidden="true" />
                    <span>{item.label}</span>
                  </NavLink>
                </div>
              );
            })}

            {/* Mobile Actions Container (Appears inside drawer on mobile) */}
            <div className="mobile-nav-actions">
              <div className="status-badge" title="AI inference system is active • Local PyTorch Engine">
                <span className="status-dot-wrapper">
                  <span className="status-dot"></span>
                  <span className="status-dot-ping"></span>
                </span>
                <span className="status-text-label">PyTorch Active</span>
              </div>

              <Link
                to="/classify"
                className="btn btn-primary mobile-cta-btn"
                onClick={handleNavClick}
              >
                <Sparkles size={16} aria-hidden="true" />
                <span>Analyze Waste</span>
              </Link>
            </div>
          </nav>

          {/* Desktop Actions & Mobile toggle button */}
          <div className="nav-actions">
            <div className="status-badge desktop-status-badge" title="AI inference system is active • Local PyTorch Engine">
              <span className="status-dot-wrapper">
                <span className="status-dot"></span>
                <span className="status-dot-ping"></span>
              </span>
              <span className="status-text-label">PyTorch Active</span>
            </div>

            <Link
              to="/classify"
              className="btn btn-primary nav-cta-btn"
              onClick={handleNavClick}
            >
              <Sparkles size={16} aria-hidden="true" />
              <span>Analyze Waste</span>
            </Link>

            <button
              type="button"
              className="mobile-toggle"
              aria-label={mobileMenuOpen ? 'Close navigation menu' : 'Open navigation menu'}
              aria-expanded={mobileMenuOpen}
              aria-controls="primary-navigation"
              onClick={() => setMobileMenuOpen((prev) => !prev)}
            >
              {mobileMenuOpen ? <X size={24} aria-hidden="true" /> : <Menu size={24} aria-hidden="true" />}
            </button>
          </div>
        </div>
      </header>

      {/* Click-outside backdrop overlay for mobile drawer */}
      {mobileMenuOpen && (
        <div
          className="mobile-backdrop"
          onClick={() => setMobileMenuOpen(false)}
          aria-hidden="true"
        />
      )}
    </>
  );
}

export default Navbar;
