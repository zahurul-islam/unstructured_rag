"""
Simple test Flask server to confirm template rendering is working.
"""

from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

@app.route('/')
def index():
    """Render the main page."""
    return "Flask is working! This is the test server."

@app.route('/test')
def test():
    """Try to render a minimal template."""
    try:
        return render_template('test.html')
    except Exception as e:
        return f"Error rendering template: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=True)
