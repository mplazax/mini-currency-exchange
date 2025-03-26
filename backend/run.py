"""
Entry point for running the application
"""
from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    # Get host and port from environment or use defaults
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', '5000'))
    
    app.run(host=host, port=port) 