"""
Flask API server for decoy status
Provides public endpoints for other applications to check decoy status
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import os
from shared_state import decoy_status_manager

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
API_PORT = int(os.getenv('API_PORT', '5000'))
API_HOST = os.getenv('API_HOST', '0.0.0.0')

@app.route('/status', methods=['GET'])
def get_decoy_status():
    """Get current decoy status"""
    try:
        status_data = decoy_status_manager.get_status()
        
        # Add API metadata
        response = {
            'success': True,
            'data': status_data,
            'api_version': '1.0',
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        status_data = decoy_status_manager.get_status()
        
        # Determine health based on bot status and data freshness
        bot_online = status_data.get('bot_online', False)
        last_check = status_data.get('last_check')
        
        health_status = 'healthy' if bot_online else 'degraded'
        
        response = {
            'status': health_status,
            'bot_online': bot_online,
            'last_check': last_check,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/info', methods=['GET'])
def get_info():
    """Get API information and available endpoints"""
    return jsonify({
        'name': 'Decoy Status API',
        'version': '1.0',
        'description': 'Public API for checking decoy status from Discord bot',
        'endpoints': {
            '/status': 'GET - Get current decoy status',
            '/health': 'GET - Health check',
            '/info': 'GET - API information'
        },
        'timestamp': datetime.now().isoformat()
    }), 200

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'available_endpoints': ['/status', '/health', '/info'],
        'timestamp': datetime.now().isoformat()
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'timestamp': datetime.now().isoformat()
    }), 500

def run_api_server():
    """Run the API server"""
    print(f"🚀 Starting API server on {API_HOST}:{API_PORT}")
    app.run(host=API_HOST, port=API_PORT, debug=False, threaded=True)

if __name__ == "__main__":
    run_api_server()
