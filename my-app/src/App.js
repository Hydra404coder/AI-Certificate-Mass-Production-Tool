import React, { useEffect, useRef, useState } from 'react';
import './App.css';
import ChatBot from './ChatBot';

function App() {
  const [scrollY, setScrollY] = useState(0);
  const [showScrollHint, setShowScrollHint] = useState(true);
  const [showEmailTooltip, setShowEmailTooltip] = useState({ hero: false, cta: false });
  const sectionsRef = useRef([]);
  const autoScrollRef = useRef(null);

  const handleEmailClick = (location) => {
    setShowEmailTooltip(prev => ({ ...prev, [location]: !prev[location] }));
  };

  const copyEmail = () => {
    navigator.clipboard.writeText('akhilshibu2710@gmail.com');
    alert('Email copied to clipboard! 📧');
  };

  useEffect(() => {
    const handleScroll = () => {
      setScrollY(window.scrollY);
      // Hide scroll hint after user scrolls
      if (window.scrollY > 50) {
        setShowScrollHint(false);
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    // Auto-scroll effect with hint animation
    let scrollTimeout;
    let hintTimeout;
    
    const startAutoScroll = () => {
      // Show hint for 3 seconds, then start slow scroll
      hintTimeout = setTimeout(() => {
        if (window.scrollY === 0) { // Only auto-scroll if user hasn't moved
          autoScrollRef.current = setInterval(() => {
            if (window.scrollY < 100) { // Scroll down slowly for first 100px
              window.scrollBy(0, 1);
            } else {
              clearInterval(autoScrollRef.current);
            }
          }, 50); // Slow scroll speed (50ms intervals)
        }
      }, 3000);
      
      // Stop auto-scroll after 8 seconds total
      scrollTimeout = setTimeout(() => {
        if (autoScrollRef.current) {
          clearInterval(autoScrollRef.current);
        }
        setShowScrollHint(false);
      }, 8000);
    };

    // Start after component mounts
    const initTimeout = setTimeout(startAutoScroll, 1000);

    return () => {
      clearTimeout(initTimeout);
      clearTimeout(scrollTimeout);
      clearTimeout(hintTimeout);
      if (autoScrollRef.current) {
        clearInterval(autoScrollRef.current);
      }
    };
  }, []);

  const handleStartClick = () => {
    // Execute main.py
    fetch('/start', {
      method: 'POST',
    })
      .then(response => response.json())
      .then(data => {
        console.log('Main.py executed:', data);
        // Alternative: window.location.href = 'http://localhost:5000/start';
      })
      .catch(error => {
        console.error('Error:', error);
        alert('Starting Certificate Mass Production Tool...');
      });
  };

  return (
    <div className="App">
      {/* Hero Section */}
      <section className="hero-section" style={{ transform: `translateY(${scrollY * 0.5}px)` }}>
        <div className="hero-content">
          <h1 className="hero-title" style={{ opacity: 1 - scrollY / 500 }}>
            Certificate Mass Production Tool
          </h1>
          <p className="hero-subtitle" style={{ opacity: 1 - scrollY / 400 }}>
            Automate the creation of personalized certificates with ease and precision
          </p>
          <button className="cta-button" onClick={handleStartClick}>
            Start It
          </button>
          
          {/* Connect Section */}
          <div className="connect-section-hero">
            <p className="connect-label">Connect with me</p>
            <div className="connect-links">
              <div className="email-container">
                <button onClick={() => handleEmailClick('hero')} className="connect-link">
                  <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                    <polyline points="22,6 12,13 2,6"/>
                  </svg>
                  Email
                </button>
                {showEmailTooltip.hero && (
                  <div className="email-tooltip">
                    <div className="email-tooltip-content">
                      <span className="email-text">akhilshibu2710@gmail.com</span>
                      <button onClick={copyEmail} className="copy-btn" title="Copy email">
                        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2">
                          <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                          <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                        </svg>
                      </button>
                    </div>
                  </div>
                )}
              </div>
              <a href="https://www.linkedin.com/in/akhil-dev404" className="connect-link" target="_blank" rel="noopener noreferrer">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                  <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
                </svg>
                LinkedIn
              </a>
              <a href="https://github.com/Hydra404coder/AI-Certificate-Mass-Production-Tool" className="connect-link" target="_blank" rel="noopener noreferrer">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                  <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                </svg>
                GitHub
              </a>
            </div>
          </div>
        </div>
        
        {/* Animated Scroll Hint */}
        {showScrollHint && (
          <div className="scroll-hint">
            <div className="scroll-hint-text">
              Scroll down to see how to use
            </div>
            <div className="scroll-hint-arrow">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M7 10L12 15L17 10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
          </div>
        )}
        
        <div className="hero-decoration" style={{ transform: `translateY(${scrollY * 0.3}px)` }}>
          <svg viewBox="0 0 800 600" className="hero-svg">
            <defs>
              <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style={{ stopColor: '#6366f1', stopOpacity: 1 }} />
                <stop offset="100%" style={{ stopColor: '#8b5cf6', stopOpacity: 1 }} />
              </linearGradient>
            </defs>
            <rect x="100" y="100" width="600" height="400" rx="20" fill="url(#grad1)" opacity="0.2" />
            <circle cx="400" cy="300" r="150" fill="none" stroke="#6366f1" strokeWidth="2" opacity="0.3" />
            <path d="M 300 250 L 350 300 L 500 200" stroke="#8b5cf6" strokeWidth="4" fill="none" strokeLinecap="round" />
          </svg>
        </div>
      </section>

      {/* Step 1: Drag/Drop */}
      <section className="step-section" ref={el => sectionsRef.current[0] = el}>
        <div className="step-container" style={{ transform: `translateX(${Math.max(0, 200 - scrollY / 3)}px)` }}>
          <div className="step-number">01</div>
          <div className="step-content">
            <h2 className="step-title">Drag/Drop</h2>
            <p className="step-description">
              Start by dragging and dropping your certificate template. Our intelligent system automatically detects variable regions where personalized data will be placed.
            </p>
            <div className="step-features">
              <div className="feature-item">✓ Support for PNG, JPG, and more</div>
              <div className="feature-item">✓ Automatic mask detection</div>
              <div className="feature-item">✓ Instant template preview</div>
            </div>
          </div>
          <div className="step-illustration">
            <svg viewBox="0 0 400 300" className="illustration-svg">
              <defs>
                <linearGradient id="dragGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style={{ stopColor: '#6366f1', stopOpacity: 0.8 }} />
                  <stop offset="100%" style={{ stopColor: '#8b5cf6', stopOpacity: 0.8 }} />
                </linearGradient>
              </defs>
              {/* Drop zone */}
              <rect x="50" y="50" width="300" height="200" rx="15" fill="#1e293b" stroke="#6366f1" strokeWidth="3" strokeDasharray="10,5" />
              {/* Document icon */}
              <rect x="150" y="90" width="100" height="120" rx="8" fill="url(#dragGrad)" />
              <line x1="170" y1="110" x2="230" y2="110" stroke="white" strokeWidth="3" />
              <line x1="170" y1="130" x2="230" y2="130" stroke="white" strokeWidth="3" />
              <line x1="170" y1="150" x2="210" y2="150" stroke="white" strokeWidth="3" />
              {/* Arrow pointing down */}
              <path d="M 200 30 L 200 70" stroke="#8b5cf6" strokeWidth="4" strokeLinecap="round" />
              <path d="M 190 60 L 200 70 L 210 60" stroke="#8b5cf6" strokeWidth="4" strokeLinecap="round" fill="none" />
            </svg>
          </div>
        </div>
      </section>

      {/* Step 2: Setup Masked Area */}
      <section className="step-section alt">
        <div className="step-container" style={{ transform: `translateX(${Math.min(0, -200 + scrollY / 4)}px)` }}>
          <div className="step-illustration">
            <svg viewBox="0 0 400 300" className="illustration-svg">
              <defs>
                <linearGradient id="maskGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" style={{ stopColor: '#8b5cf6', stopOpacity: 0.8 }} />
                  <stop offset="100%" style={{ stopColor: '#ec4899', stopOpacity: 0.8 }} />
                </linearGradient>
              </defs>
              {/* Certificate template */}
              <rect x="50" y="50" width="300" height="200" rx="10" fill="#1e293b" stroke="#475569" strokeWidth="2" />
              {/* Masked areas */}
              <rect x="80" y="80" width="120" height="30" rx="5" fill="none" stroke="#8b5cf6" strokeWidth="2" strokeDasharray="5,5" />
              <rect x="220" y="80" width="60" height="30" rx="5" fill="none" stroke="#ec4899" strokeWidth="2" strokeDasharray="5,5" />
              <rect x="80" y="130" width="240" height="30" rx="5" fill="none" stroke="#6366f1" strokeWidth="2" strokeDasharray="5,5" />
              {/* Selection handles */}
              <circle cx="80" cy="80" r="5" fill="#8b5cf6" />
              <circle cx="200" cy="80" r="5" fill="#8b5cf6" />
              {/* Cursor */}
              <path d="M 160 100 L 160 115 L 165 110 L 170 118 L 174 116 L 169 108 L 176 108 Z" fill="white" stroke="#1e293b" strokeWidth="1" />
            </svg>
          </div>
          <div className="step-content">
            <div className="step-number">02</div>
            <h2 className="step-title">Setup Masked Area</h2>
            <p className="step-description">
              Define or manually adjust variable regions (masks) where personalized data will appear. Select, move, resize, or rotate masks with precision.
            </p>
            <div className="step-features">
              <div className="feature-item">✓ Manual mask drawing</div>
              <div className="feature-item">✓ Drag to reposition masks</div>
              <div className="feature-item">✓ Resize and rotate controls</div>
            </div>
          </div>
        </div>
      </section>

      {/* Step 3: Mapping */}
      <section className="step-section">
        <div className="step-container" style={{ transform: `translateX(${Math.max(0, 200 - scrollY / 3.5)}px)` }}>
          <div className="step-number">03</div>
          <div className="step-content">
            <h2 className="step-title">Mapping</h2>
            <p className="step-description">
              Assign labels to each masked area and link them to your Excel column headers. Ensure every variable is properly mapped for accurate certificate generation.
            </p>
            <div className="step-features">
              <div className="feature-item">✓ Label each mask (a, b, c...)</div>
              <div className="feature-item">✓ Link to Excel columns</div>
              <div className="feature-item">✓ Validation checks</div>
            </div>
          </div>
          <div className="step-illustration">
            <svg viewBox="0 0 400 300" className="illustration-svg">
              <defs>
                <linearGradient id="mapGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" style={{ stopColor: '#6366f1', stopOpacity: 0.8 }} />
                  <stop offset="100%" style={{ stopColor: '#06b6d4', stopOpacity: 0.8 }} />
                </linearGradient>
              </defs>
              {/* Left side - masks */}
              <rect x="30" y="60" width="80" height="25" rx="5" fill="#1e293b" stroke="#6366f1" strokeWidth="2" />
              <text x="70" y="78" fontSize="14" fill="white" textAnchor="middle">Mask A</text>
              <rect x="30" y="110" width="80" height="25" rx="5" fill="#1e293b" stroke="#8b5cf6" strokeWidth="2" />
              <text x="70" y="128" fontSize="14" fill="white" textAnchor="middle">Mask B</text>
              <rect x="30" y="160" width="80" height="25" rx="5" fill="#1e293b" stroke="#ec4899" strokeWidth="2" />
              <text x="70" y="178" fontSize="14" fill="white" textAnchor="middle">Mask C</text>
              
              {/* Connecting lines */}
              <path d="M 110 72 L 150 72 Q 170 72 170 92 L 170 115 Q 170 125 180 125" stroke="#6366f1" strokeWidth="2" fill="none" />
              <line x1="110" y1="122" x2="180" y2="122" stroke="#8b5cf6" strokeWidth="2" />
              <path d="M 110 172 L 150 172 Q 170 172 170 152 L 170 129 Q 170 119 180 119" stroke="#ec4899" strokeWidth="2" fill="none" />
              
              {/* Right side - columns */}
              <rect x="180" y="55" width="150" height="80" rx="8" fill="url(#mapGrad)" opacity="0.9" />
              <text x="255" y="78" fontSize="12" fill="white" textAnchor="middle" fontWeight="bold">NAME</text>
              <text x="255" y="98" fontSize="12" fill="white" textAnchor="middle" fontWeight="bold">DATE</text>
              <text x="255" y="118" fontSize="12" fill="white" textAnchor="middle" fontWeight="bold">SCORE</text>
              
              {/* Checkmarks */}
              <circle cx="350" cy="72" r="12" fill="#10b981" />
              <path d="M 345 72 L 348 75 L 355 68" stroke="white" strokeWidth="2" fill="none" strokeLinecap="round" />
            </svg>
          </div>
        </div>
      </section>

      {/* Step 4: Format */}
      <section className="step-section alt">
        <div className="step-container" style={{ transform: `translateX(${Math.min(0, -200 + scrollY / 4.5)}px)` }}>
          <div className="step-illustration">
            <svg viewBox="0 0 400 300" className="illustration-svg">
              <defs>
                <linearGradient id="formatGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" style={{ stopColor: '#ec4899', stopOpacity: 0.8 }} />
                  <stop offset="100%" style={{ stopColor: '#f59e0b', stopOpacity: 0.8 }} />
                </linearGradient>
              </defs>
              {/* Format panel */}
              <rect x="50" y="40" width="300" height="220" rx="12" fill="#1e293b" stroke="#475569" strokeWidth="2" />
              <text x="200" y="70" fontSize="16" fill="white" textAnchor="middle" fontWeight="bold">Text Formatting</text>
              
              {/* Bold button */}
              <rect x="80" y="90" width="50" height="40" rx="6" fill="url(#formatGrad)" />
              <text x="105" y="116" fontSize="20" fill="white" textAnchor="middle" fontWeight="bold">B</text>
              
              {/* Italic button */}
              <rect x="145" y="90" width="50" height="40" rx="6" fill="url(#formatGrad)" />
              <text x="170" y="116" fontSize="20" fill="white" textAnchor="middle" fontStyle="italic">I</text>
              
              {/* Underline button */}
              <rect x="210" y="90" width="50" height="40" rx="6" fill="url(#formatGrad)" />
              <text x="235" y="116" fontSize="20" fill="white" textAnchor="middle" textDecoration="underline">U</text>
              
              {/* Color picker */}
              <rect x="275" y="90" width="50" height="40" rx="6" fill="url(#formatGrad)" />
              <circle cx="300" cy="110" r="12" fill="#ef4444" stroke="white" strokeWidth="2" />
              
              {/* Preview text */}
              <rect x="80" y="150" width="245" height="90" rx="8" fill="#0f172a" stroke="#475569" strokeWidth="1" />
              <text x="202" y="185" fontSize="18" fill="#ef4444" textAnchor="middle" fontWeight="bold">John Doe</text>
              <text x="202" y="215" fontSize="14" fill="#8b5cf6" textAnchor="middle" fontStyle="italic">Certificate Preview</text>
            </svg>
          </div>
          <div className="step-content">
            <div className="step-number">04</div>
            <h2 className="step-title">Format</h2>
            <p className="step-description">
              Customize the appearance of each variable with rich text formatting options. Apply bold, italic, underline, and choose colors to match your brand.
            </p>
            <div className="step-features">
              <div className="feature-item">✓ Bold, Italic, Underline styles</div>
              <div className="feature-item">✓ Custom color selection</div>
              <div className="feature-item">✓ Real-time preview</div>
            </div>
          </div>
        </div>
      </section>

      {/* Step 5: Upload XL Sheet */}
      <section className="step-section">
        <div className="step-container" style={{ transform: `translateX(${Math.max(0, 200 - scrollY / 4)}px)` }}>
          <div className="step-number">05</div>
          <div className="step-content">
            <h2 className="step-title">Upload XL Sheet</h2>
            <p className="step-description">
              Upload your Excel spreadsheet with recipient data. The first row must contain column headers that match your assigned variable names.
            </p>
            <div className="step-features">
              <div className="feature-item">✓ XLSX and XLS support</div>
              <div className="feature-item">✓ Automatic validation</div>
              <div className="feature-item">✓ Instant data processing</div>
            </div>
            <div className="caution-box">
              <strong>⚠️ Important:</strong> Column headers in your Excel file must exactly match the variable names (e.g., NAME, DATE, SCORE) you assigned in the mapping step.
            </div>
          </div>
          <div className="step-illustration">
            <svg viewBox="0 0 400 300" className="illustration-svg">
              <defs>
                <linearGradient id="excelGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style={{ stopColor: '#10b981', stopOpacity: 0.8 }} />
                  <stop offset="100%" style={{ stopColor: '#06b6d4', stopOpacity: 0.8 }} />
                </linearGradient>
              </defs>
              {/* Excel icon */}
              <rect x="100" y="60" width="200" height="180" rx="10" fill="url(#excelGrad)" />
              {/* Grid lines */}
              <line x1="130" y1="90" x2="270" y2="90" stroke="white" strokeWidth="2" />
              <line x1="130" y1="120" x2="270" y2="120" stroke="white" strokeWidth="1" opacity="0.7" />
              <line x1="130" y1="150" x2="270" y2="150" stroke="white" strokeWidth="1" opacity="0.7" />
              <line x1="130" y1="180" x2="270" y2="180" stroke="white" strokeWidth="1" opacity="0.7" />
              <line x1="130" y1="210" x2="270" y2="210" stroke="white" strokeWidth="1" opacity="0.7" />
              
              <line x1="170" y1="90" x2="170" y2="210" stroke="white" strokeWidth="1" opacity="0.7" />
              <line x1="220" y1="90" x2="220" y2="210" stroke="white" strokeWidth="1" opacity="0.7" />
              
              {/* Header row */}
              <text x="150" y="108" fontSize="10" fill="white" textAnchor="middle" fontWeight="bold">NAME</text>
              <text x="195" y="108" fontSize="10" fill="white" textAnchor="middle" fontWeight="bold">DATE</text>
              <text x="245" y="108" fontSize="10" fill="white" textAnchor="middle" fontWeight="bold">ID</text>
              
              {/* Data rows */}
              <circle cx="150" cy="135" r="3" fill="white" opacity="0.6" />
              <circle cx="195" cy="135" r="3" fill="white" opacity="0.6" />
              <circle cx="245" cy="135" r="3" fill="white" opacity="0.6" />
              
              {/* Upload arrow */}
              <path d="M 200 260 L 200 250" stroke="#f59e0b" strokeWidth="4" strokeLinecap="round" />
              <path d="M 190 260 L 200 270 L 210 260" stroke="#f59e0b" strokeWidth="4" strokeLinecap="round" fill="none" />
            </svg>
          </div>
        </div>
      </section>

      {/* Step 6: Output */}
      <section className="step-section alt final-section">
        <div className="step-container" style={{ transform: `translateX(${Math.min(0, -200 + scrollY / 5)}px)` }}>
          <div className="step-illustration">
            <svg viewBox="0 0 400 300" className="illustration-svg">
              <defs>
                <linearGradient id="outputGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style={{ stopColor: '#8b5cf6', stopOpacity: 0.9 }} />
                  <stop offset="100%" style={{ stopColor: '#6366f1', stopOpacity: 0.9 }} />
                </linearGradient>
              </defs>
              {/* Stack of certificates */}
              <rect x="120" y="100" width="160" height="120" rx="8" fill="#1e293b" stroke="#475569" strokeWidth="2" transform="rotate(-5 200 160)" />
              <rect x="120" y="100" width="160" height="120" rx="8" fill="#1e293b" stroke="#6366f1" strokeWidth="2" transform="rotate(3 200 160)" />
              <rect x="120" y="100" width="160" height="120" rx="8" fill="url(#outputGrad)" stroke="#8b5cf6" strokeWidth="2" />
              {/* Certificate content */}
              <line x1="140" y1="130" x2="260" y2="130" stroke="white" strokeWidth="2" />
              <line x1="150" y1="150" x2="250" y2="150" stroke="white" strokeWidth="1.5" opacity="0.7" />
              <line x1="150" y1="165" x2="250" y2="165" stroke="white" strokeWidth="1.5" opacity="0.7" />
              <circle cx="200" cy="190" r="15" fill="none" stroke="white" strokeWidth="2" />
              <path d="M 193 190 L 197 194 L 207 184" stroke="white" strokeWidth="2" fill="none" strokeLinecap="round" />
              {/* Counter badge */}
              <circle cx="320" cy="80" r="35" fill="#10b981" />
              <text x="320" y="85" fontSize="24" fill="white" textAnchor="middle" fontWeight="bold">N</text>
              <text x="320" y="100" fontSize="10" fill="white" textAnchor="middle">Certificates</text>
            </svg>
          </div>
          <div className="step-content">
            <div className="step-number">06</div>
            <h2 className="step-title">Output</h2>
            <p className="step-description">
              Generate N number of personalized certificates in seconds. Download individual certificates or export all at once in high-quality JPG format.
            </p>
            <div className="step-features">
              <div className="feature-item">✓ Bulk certificate generation</div>
              <div className="feature-item">✓ Individual downloads</div>
              <div className="feature-item">✓ Batch export to folder</div>
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section className="final-cta-section">
        <div className="cta-content">
          <h2 className="cta-title">Ready to Create Certificates?</h2>
          <p className="cta-description">
            Transform hours of manual work into minutes of automated precision
          </p>
          <button className="cta-button large" onClick={handleStartClick}>
            Start It Now
          </button>
          
          {/* Connect Section */}
          <div className="connect-section-cta">
            <p className="connect-label">Connect with me</p>
            <div className="connect-links">
              <div className="email-container">
                <button onClick={() => handleEmailClick('cta')} className="connect-link">
                  <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                    <polyline points="22,6 12,13 2,6"/>
                  </svg>
                  Email
                </button>
                {showEmailTooltip.cta && (
                  <div className="email-tooltip">
                    <div className="email-tooltip-content">
                      <span className="email-text">akhilshibu2710@gmail.com</span>
                      <button onClick={copyEmail} className="copy-btn" title="Copy email">
                        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2">
                          <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                          <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                        </svg>
                      </button>
                    </div>
                  </div>
                )}
              </div>
              <a href="https://www.linkedin.com/in/akhil-dev404" className="connect-link" target="_blank" rel="noopener noreferrer">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                  <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
                </svg>
                LinkedIn
              </a>
              <a href="https://github.com/Hydra404coder/AI-Certificate-Mass-Production-Tool" className="connect-link" target="_blank" rel="noopener noreferrer">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                  <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                </svg>
                GitHub
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <p>Made by Akhil Shibu ✌️😊</p>
      </footer>

      {/* ChatBot */}
      <ChatBot />
    </div>
  );
}

export default App;
