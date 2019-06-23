import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), './src'))

from app import app

# Only needed for local development
# Zappa handles the "app" object directly
if __name__ == '__main__':
    app.run()
