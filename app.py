from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    # Create upload directory if it doesn't exist
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    
    # Create data directory if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')
    
    app.run(debug=True, host='0.0.0.0', port=5000)
