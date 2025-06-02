import importlib.util
import sys
import logging
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('remotereach.log') if os.access('.', os.W_OK) else logging.NullHandler()
    ]
)
logger = logging.getLogger(__name__)

# Check if eventlet is available and import it first for proper monkey patching
eventlet_available = importlib.util.find_spec("eventlet") is not None
if eventlet_available:
    import eventlet
    eventlet.monkey_patch()

from flask import Flask, render_template
from flask_socketio import SocketIO
import pyautogui
import time
import platform
import socket

# Function to get the local IP address
def get_local_ip():
    try:
        # Create a socket connection to an external server
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Doesn't need to be reachable
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"  # Fallback to localhost

# Configure pyautogui
pyautogui.FAILSAFE = True  # Move mouse to upper left to abort

# Initialize Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'remotereach-dev-key-change-in-production')

# Platform-specific socket.io setup to avoid eventlet.hubs.epolls errors
if getattr(sys, 'frozen', False):
    # Running as a bundled exe - use threading mode which is more reliable
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
else:
    # In development, use eventlet if available (already monkey patched at top of file if available)
    if eventlet_available:
        socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')
    else:
        socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Routes
@app.route('/')
def index():
    return render_template('index.html')
# Socket.IO event handlers
@socketio.on('connect')
def handle_connect():
    logger.info('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    logger.info('Client disconnected')

# Mouse movement - original directional handler
@socketio.on('mouse_move')
def handle_mouse_move(direction):
    current_x, current_y = pyautogui.position()
    move_amount = 20  # pixels to move
    
    if direction == 'up':
        pyautogui.moveTo(current_x, current_y - move_amount)
    elif direction == 'down':
        pyautogui.moveTo(current_x, current_y + move_amount)
    elif direction == 'left':
        pyautogui.moveTo(current_x - move_amount, current_y)
    elif direction == 'right':
        pyautogui.moveTo(current_x + move_amount, current_y)

# New relative mouse movement for trackpad with enhanced features
@socketio.on('mouse_move_relative')
def handle_mouse_move_relative(data):
    current_x, current_y = pyautogui.position()
    
    # Get movement values and settings
    delta_x = data['x']
    delta_y = data['y']
    sensitivity = data.get('sensitivity', 5) / 5  # Normalize to 1.0 for sensitivity=5
    acceleration = data.get('acceleration', 5) / 5  # Normalize to 1.0 for acceleration=5
    smoothing = data.get('smoothing', 5) / 5  # Normalize to 1.0 for smoothing=5
    deadzone = data.get('deadzone', 0)  # Deadzone threshold
    
    # Apply deadzone if movement is too small
    if abs(delta_x) < deadzone:
        delta_x = 0
    if abs(delta_y) < deadzone:
        delta_y = 0
        
    # Apply sensitivity
    delta_x *= sensitivity
    delta_y *= sensitivity
    
    # Apply acceleration for larger movements
    if acceleration > 0:
        magnitude = (delta_x**2 + delta_y**2)**0.5  # Calculate movement magnitude
        if magnitude > 5:  # Only accelerate beyond a minimum threshold
            accel_factor = 1 + (magnitude / 10) * acceleration  # Progressive acceleration
            delta_x *= accel_factor
            delta_y *= accel_factor
    
    # Round to integers for pixel movement
    move_x = round(delta_x)
    move_y = round(delta_y)
      # Calculate new position with boundary checks
    new_x = current_x + move_x
    new_y = current_y + move_y
    
    # Get screen size to enforce boundaries
    screen_width, screen_height = pyautogui.size()
    
    # Set margin to prevent getting stuck at screen edges
    margin = 5
    
    # Apply screen boundaries with margins
    new_x = max(margin, min(screen_width - margin, new_x))
    new_y = max(margin, min(screen_height - margin, new_y))
    
    # Move the mouse cursor
    if new_x <= margin or new_x >= screen_width - margin or new_y <= margin or new_y >= screen_height - margin:
        # Slow down movement near edges for better control
        pyautogui.moveRel(new_x - current_x, new_y - current_y, duration=0.01)
    else:
        # Normal movement when not near edges
        pyautogui.moveTo(new_x, new_y)

# Mouse click
@socketio.on('mouse_click')
def handle_mouse_click(click_type):
    if click_type == 'left':
        pyautogui.click()
    elif click_type == 'right':
        pyautogui.rightClick()
    elif click_type == 'double':
        pyautogui.doubleClick()

# Keyboard input
@socketio.on('key_press')
def handle_key_press(key_data):
    key = key_data['key']
    
    # If it's a combination (contains '+')
    if '+' in key:
        keys = key.split('+')
        # Press all keys in the combination
        for k in keys[:-1]:
            pyautogui.keyDown(k.lower())
        
        # Press and release the last key
        pyautogui.press(keys[-1].lower())
        
        # Release modifier keys
        for k in reversed(keys[:-1]):
            pyautogui.keyUp(k.lower())
    else:
        # Regular single key press
        pyautogui.press(key)

@socketio.on('text_input')
def handle_text_input(text):
    pyautogui.write(text)

# Mouse scroll
@socketio.on('scroll')
def handle_scroll(data):
    direction = data.get('direction', 'down')
    amount = data.get('amount', 50)
    
    # Convert amount to scroll clicks (pyautogui scroll amount)
    scroll_clicks = max(1, int(amount / 50))  # Minimum 1 click, scale based on amount
    
    if direction == 'up':
        pyautogui.scroll(scroll_clicks)  # Positive values scroll up    elif direction == 'down':
        pyautogui.scroll(-scroll_clicks)  # Negative values scroll down

# Function to find an available port
def find_available_port(start_port, max_attempts=10):
    for port_attempt in range(start_port, start_port + max_attempts):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(('0.0.0.0', port_attempt))
            sock.close()
            return port_attempt
        except OSError:
            logger.warning(f"Port {port_attempt} is in use, trying next...")
            continue
    return None

# Main execution
if __name__ == '__main__':
    local_ip = get_local_ip()
    
    # Start with port 8080 and try to find an available one
    start_port = 8080
    port = find_available_port(start_port)
    if port is None:
        logger.error(f"Could not find an available port after trying {start_port} through {start_port + 9}")
        sys.exit(1)
    
    logger.info(f"RemoteReach server running at http://localhost:{port}")
    logger.info(f"Connect from your phone by using: http://{local_ip}:{port}")
    
    try:
        socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True)
    except OSError as e:
        logger.error(f"Error starting server: {e}")
        sys.exit(1)