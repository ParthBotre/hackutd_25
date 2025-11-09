import { useAuth0 } from '@auth0/auth0-react';
import { Cpu, Shield, Sparkles, Zap } from 'lucide-react';
import React from 'react';
import './LoginPage.css';

function LoginPage() {
  const { loginWithRedirect } = useAuth0();

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-header">
          <Sparkles className="login-logo" />
          <h1>PM Mockup Generator</h1>
          <p className="tagline">AI-Powered Mockup Generation for Product Managers</p>
          <div className="powered-by">
            <Cpu className="nvidia-icon" />
            <span>Powered by NVIDIA Nemotron</span>
          </div>
        </div>

        <div className="features-grid">
          <div className="feature">
            <Zap className="feature-icon" />
            <h3>Instant Generation</h3>
            <p>Create professional mockups in seconds with AI</p>
          </div>
          <div className="feature">
            <Shield className="feature-icon" />
            <h3>Secure & Private</h3>
            <p>Your data is protected with Auth0 authentication</p>
          </div>
          <div className="feature">
            <Sparkles className="feature-icon" />
            <h3>AI-Powered</h3>
            <p>Using NVIDIA's latest Llama 3.3 Nemotron model</p>
          </div>
        </div>

        <button 
          className="login-cta-button"
          onClick={() => loginWithRedirect()}
        >
          <Shield className="button-icon" />
          Sign In to Get Started
        </button>

        <p className="login-footer">
          Built for HackUTD 2025 • PNC & NVIDIA Challenge
        </p>
      </div>
    </div>
  );
}

export default LoginPage;

