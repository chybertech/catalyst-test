#!/usr/bin/env python3
"""
Event Router for Helix ⇄ Catalyst System
Routes GitHub events to appropriate Redis streams for worker processing
"""

import os
import json
import hmac
import hashlib
from flask import Flask, request, jsonify
from redis_conn import redis_client
from datetime import datetime

app = Flask(__name__)

# Configuration
WEBHOOK_SECRET = os.environ.get('GITHUB_WEBHOOK_SECRET', 'default-secret')
STREAM_NAME = "helix_stream"

def verify_signature(payload_body, signature_header):
    """Verify GitHub webhook signature"""
    if not signature_header:
        return False
    
    sha_name, signature = signature_header.split('=')
    if sha_name != 'sha256':
        return False
    
    mac = hmac.new(
        WEBHOOK_SECRET.encode(),
        msg=payload_body,
        digestmod=hashlib.sha256
    )
    
    return hmac.compare_digest(mac.hexdigest(), signature)

@app.route('/webhook', methods=['POST'])
def github_webhook():
    """Handle GitHub webhook events"""
    try:
        # Verify signature
        signature = request.headers.get('X-Hub-Signature-256')
        if not verify_signature(request.data, signature):
            return jsonify({'error': 'Invalid signature'}), 401
        
        # Parse event data
        event_type = request.headers.get('X-GitHub-Event')
        payload = request.json
        
        # Route events to appropriate handlers
        if event_type == 'pull_request':
            return handle_pull_request(payload)
        elif event_type == 'push':
            return handle_push(payload)
        elif event_type == 'issues':
            return handle_issues(payload)
        else:
            return jsonify({'message': f'Event {event_type} not handled'}), 200
            
    except Exception as e:
        app.logger.error(f"Webhook error: {e}")
        return jsonify({'error': 'Internal error'}), 500

def handle_pull_request(payload):
    """Handle pull request events"""
    action = payload['action']
    pr = payload['pull_request']
    repo = payload['repository']['full_name']
    
    # Route PR events to tasks
    if action in ['opened', 'synchronize']:
        task_data = {
            'task_id': f"pr_{pr['number']}_{int(datetime.now().timestamp())}",
            # Worker expects tasks of type 'open_pr'
            'type': 'open_pr',
            'action': action,
            'repo': repo,
            'pr_number': str(pr['number']),
            'branch': pr['head']['ref'],
            'timestamp': datetime.now().isoformat()
        }
        
        # Send to Redis stream
        r = redis_client()
        msg_id = r.xadd(STREAM_NAME, task_data)
        
        app.logger.info(f"PR {action} event routed: {msg_id}")
        return jsonify({'message': 'PR event processed', 'task_id': task_data['task_id']})
    
    return jsonify({'message': f'PR action {action} ignored'}), 200

def handle_push(payload):
    """Handle push events"""
    ref = payload['ref']
    repo = payload['repository']['full_name']
    
    # Only handle main branch pushes
    if ref == 'refs/heads/main':
        task_data = {
            'task_id': f"push_{int(datetime.now().timestamp())}",
            'type': 'deploy_check',
            'repo': repo,
            'ref': ref,
            'commits': len(payload['commits']),
            'timestamp': datetime.now().isoformat()
        }
        
        # Send to Redis stream
        r = redis_client()
        msg_id = r.xadd(STREAM_NAME, task_data)
        
        app.logger.info(f"Push event routed: {msg_id}")
        return jsonify({'message': 'Push event processed', 'task_id': task_data['task_id']})
    
    return jsonify({'message': 'Non-main branch push ignored'}), 200

def handle_issues(payload):
    """Handle issue events"""
    action = payload['action']
    issue = payload['issue']
    repo = payload['repository']['full_name']
    
    if action == 'opened':
        task_data = {
            'task_id': f"issue_{issue['number']}_{int(datetime.now().timestamp())}",
            'type': 'issue_triage',
            'action': action,
            'repo': repo,
            'issue_number': str(issue['number']),
            'title': issue['title'],
            'timestamp': datetime.now().isoformat()
        }
        
        # Send to Redis stream
        r = redis_client()
        msg_id = r.xadd(STREAM_NAME, task_data)
        
        app.logger.info(f"Issue {action} event routed: {msg_id}")
        return jsonify({'message': 'Issue event processed', 'task_id': task_data['task_id']})
    
    return jsonify({'message': f'Issue action {action} ignored'}), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        r = redis_client()
        r.ping()
        return jsonify({'status': 'healthy', 'redis': 'connected'})
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'redis': str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    """Status endpoint showing stream info"""
    try:
        r = redis_client()
        stream_info = r.xinfo_stream(STREAM_NAME)
        return jsonify({
            'stream': STREAM_NAME,
            'length': stream_info['length'],
            'groups': stream_info['groups']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Development server
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'
    
    print(f"🌐  Event Router starting on port {port}")
    print(f"📡  Webhook endpoint: /webhook")
    print(f"❤️  Health check: /health")
    
    app.run(host='0.0.0.0', port=port, debug=debug)