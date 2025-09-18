#!/usr/bin/env python3
"""
Startup script for Technical Drawing Analyzer Streamlit App
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if required packages are installed"""
    required_packages = [
        'streamlit',
        'requests', 
        'ezdxf',
        'pandas',
        'plotly',
        'pillow',
        'openpyxl'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("📦 Installing missing packages...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
        print("✅ Packages installed successfully!")
    else:
        print("✅ All required packages are installed")

def setup_environment():
    """Setup environment variables"""
    env_file = Path('.env')
    
    if not env_file.exists():
        print("📝 Creating .env file...")
        with open('.env', 'w') as f:
            f.write("# OpenAI API Key for AI-powered analysis\n")
            f.write("# Get your key from: https://platform.openai.com/api-keys\n")
            f.write("OPENAI_API_KEY=your_openai_api_key_here\n")
        print("📝 Created .env file. Please add your OpenAI API key.")
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        if os.getenv('OPENAI_API_KEY') and os.getenv('OPENAI_API_KEY') != 'your_openai_api_key_here':
            print("✅ OpenAI API key loaded")
        else:
            print("⚠️  OpenAI API key not configured. AI analysis will be disabled.")
            print("   Edit .env file and add your OpenAI API key to enable AI features.")
    except ImportError:
        print("⚠️  python-dotenv not installed. Environment variables may not load properly.")

def run_streamlit():
    """Run the Streamlit application"""
    app_file = Path('app.py')
    
    if not app_file.exists():
        print("❌ app.py not found in current directory")
        print("   Make sure you're in the correct directory with the Streamlit app")
        return False
    
    print("🚀 Starting Technical Drawing Analyzer...")
    print("   App will open in your browser at: http://localhost:8501")
    print("   Press Ctrl+C to stop the server")
    
    try:
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 'app.py',
            '--server.port=8501',
            '--server.address=localhost',
            '--browser.gatherUsageStats=false'
        ])
    except KeyboardInterrupt:
        print("\n👋 Shutting down server...")
        return True
    except Exception as e:
        print(f"❌ Error running Streamlit: {e}")
        return False

def main():
    """Main startup function"""
    print("=" * 60)
    print("📐 Technical Drawing Analyzer - Startup Script")
    print("=" * 60)
    
    # Check and install requirements
    check_requirements()
    
    # Setup environment
    setup_environment()
    
    # Run the application
    run_streamlit()

if __name__ == "__main__":
    main()