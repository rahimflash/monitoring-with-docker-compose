from flask import Flask
from prometheus_client import make_wsgi_app, Counter, Gauge, Histogram
from werkzeug.middleware.dispatcher import DispatcherMiddleware
import random
import time

app = Flask(__name__)

# Create metrics
REQUEST_COUNTER = Counter('http_requests_total', 'Total HTTP Requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_latency_seconds', 'HTTP request latency', ['endpoint'])
TEMPERATURE_GAUGE = Gauge('temperature_celsius', 'Current temperature in Celsius')

# Add prometheus wsgi middleware to route /metrics requests
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

@app.route('/')
def home():
    start_time = time.time()
    REQUEST_COUNTER.labels(method='GET', endpoint='/', status='200').inc()
    
    # Simulate some processing time
    time.sleep(random.uniform(0.1, 0.5))
    
    # Update temperature gauge with random value
    TEMPERATURE_GAUGE.set(random.uniform(18.0, 25.0))
    
    REQUEST_LATENCY.labels(endpoint='/').observe(time.time() - start_time)
    return "Welcome to the Sample Monitoring App!"

@app.route('/slow')
def slow():
    start_time = time.time()
    REQUEST_COUNTER.labels(method='GET', endpoint='/slow', status='200').inc()
    
    # Simulate a slow endpoint
    time.sleep(random.uniform(0.5, 3.0))
    
    REQUEST_LATENCY.labels(endpoint='/slow').observe(time.time() - start_time)
    return "This is a slow endpoint for testing"

@app.route('/error')
def error():
    REQUEST_COUNTER.labels(method='GET', endpoint='/error', status='500').inc()
    return "Simulated Error", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)