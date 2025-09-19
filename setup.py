"""
Setup Script for Cold Email Automation App
Creates virtual environment, installs dependencies, and validates setup
"""

import os
import sys
import subprocess
import platform

def run_command(command, description):
    """Run a command and return success status"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def create_virtual_environment():
    """Create virtual environment"""
    print("🔒 Setting up virtual environment...")
    
    # Check if virtual environment already exists
    if os.path.exists('venv'):
        print("⚠️  Virtual environment 'venv' already exists")
        response = input("Do you want to recreate it? (y/N): ").lower()
        if response == 'y':
            print("🗑️  Removing existing virtual environment...")
            if platform.system() == "Windows":
                run_command("rmdir /s /q venv", "Remove existing venv")
            else:
                run_command("rm -rf venv", "Remove existing venv")
        else:
            print("✅ Using existing virtual environment")
            return True
    
    # Create new virtual environment
    if run_command("python -m venv venv", "Create virtual environment"):
        print("✅ Virtual environment created successfully")
        return True
    else:
        print("❌ Failed to create virtual environment")
        return False

def get_activation_command():
    """Get the correct activation command for the current OS"""
    if platform.system() == "Windows":
        return "venv\\Scripts\\activate"
    else:
        return "source venv/bin/activate"

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    # Determine pip command based on OS
    if platform.system() == "Windows":
        pip_cmd = "venv\\Scripts\\pip"
    else:
        pip_cmd = "venv/bin/pip"
    
    # Upgrade pip first
    if not run_command(f"{pip_cmd} install --upgrade pip", "Upgrade pip"):
        return False
    
    # Install requirements
    if run_command(f"{pip_cmd} install -r requirements.txt", "Install requirements"):
        print("✅ Dependencies installed successfully")
        return True
    else:
        print("❌ Failed to install dependencies")
        return False

def create_env_file():
    """Create .env file from template"""
    print("🔧 Setting up environment file...")
    
    if os.path.exists('.env'):
        print("⚠️  .env file already exists")
        response = input("Do you want to overwrite it? (y/N): ").lower()
        if response != 'y':
            print("✅ Using existing .env file")
            return True
    
    if os.path.exists('env.example'):
        if run_command("copy env.example .env" if platform.system() == "Windows" else "cp env.example .env", "Create .env file"):
            print("✅ .env file created from template")
            print("⚠️  Please edit .env file with your actual API keys")
            return True
        else:
            print("❌ Failed to create .env file")
            return False
    else:
        print("❌ env.example template not found")
        return False

def run_tests():
    """Run setup tests"""
    print("🧪 Running setup tests...")
    
    # Determine python command based on OS
    if platform.system() == "Windows":
        python_cmd = "venv\\Scripts\\python"
    else:
        python_cmd = "venv/bin/python"
    
    if run_command(f"{python_cmd} test_setup.py", "Run setup tests"):
        print("✅ Setup tests completed")
        return True
    else:
        print("❌ Setup tests failed")
        return False

def main():
    """Main setup function"""
    print("🚀 Cold Email Automation App - Setup")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required. Current version:", sys.version)
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    # Setup steps
    steps = [
        ("Create Virtual Environment", create_virtual_environment),
        ("Install Dependencies", install_dependencies),
        ("Create Environment File", create_env_file),
        ("Run Setup Tests", run_tests)
    ]
    
    for step_name, step_function in steps:
        print(f"\n📋 {step_name}")
        if not step_function():
            print(f"❌ Setup failed at: {step_name}")
            return False
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\nNext steps:")
    print(f"1. Activate virtual environment:")
    print(f"   {get_activation_command()}")
    print("2. Edit .env file with your API keys")
    print("3. Run: streamlit run app.py")
    print("4. Open browser to http://localhost:8501")
    
    return True

if __name__ == "__main__":
    main()
