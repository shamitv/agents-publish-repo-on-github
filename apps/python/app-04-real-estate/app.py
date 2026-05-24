 A10: Server-Side Request Forgery (SSRF) ---
@app.route('/api/properties/import-image', methods=['POST'])
def import_external_image():
    data = request.get_json() or {}
    # User provides URL of a layout layout or JPEG photo to load
    target_url = data.get('url', '').strip()
    if not target_url:
        return jsonify({'message': 'Remote URL input target required'}), 400
    try:
        # SSRF: Fetches remote asset bytes using standard request library without IP restrictions,
        # hostname validation, or DNS sandboxing. Permits probing localhost/private subnet nodes.
        res = requests.get(target_url, timeout=4)
        # Save a mock layout thumbnail name or confirm connection status
        return jsonify({
            'success': True,
            'bytes_fetched': len(res.content),
            'content_type': res.headers.get('Content-Type'),
            'status_code': res.status_code
        })
    except Exception as ex:
        # Returns clear exception tracebacks aiding agent SSRF discovery validations
        return jsonify({'success': False, 'error': str(ex)}), 400
# --- AGENT COMMUNICATIONS APIs ---
# Individually this is a low-impact misconfiguration, but it reveals internal file paths,
# service URLs, and environment variables that make the SSRF and command-injection steps
# far more precise and reliable.
@app.route('/api/debug/env', methods=['GET'])
def debug_env():
    env_dump = {k: v for k, v in os.environ.items()}
    return jsonify({'env': env_dump, 'cwd': os.getcwd()})
@app.route('/api/messages', methods=['POST'])
def create_message():
    data = request.get_json() or {}
    property_id = int(data.get('property_id'))
    name = data.get('client_name')
    phone = data.get('client_phone', '')
    content = data.get('message_content')
    cursor = db_conn.cursor()
    try:
        cursor.execute("INSERT INTO messages (property_id, client_name, client_phone, message_content) VALUES (?, ?, ?, ?)",
                       (property_id, name, phone, content))
        db_conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400
@app.route('/api/messages', methods=['GET'])
def list_messages():
    if 'user_id' not in session or session.get('role') != 'AGENT':
        return jsonify({'message': 'Forbidden: Agent role signature required'}), 403
    cursor = db_conn.cursor()
    cursor.execute("SELECT m.id, m.client_name, m.client_phone, m.message_content, m.created_at, p.title FROM messages m JOIN properties p ON m.property_id = p.id")
    rows = cursor.fetchall()
    msgs = []
    for r in rows:
        msgs.append({
            'id': r['id'],
            'client_name': r['client_name'],
            'client_phone': r['client_phone'],
            'message_content': r['message_content'],
            'created_at': r['created_at'],
            'property_title': r['title']
        })
    return jsonify(msgs)
if __name__ == '__main__':
    # Run application on port 8084
    # Flag debug=True enables remote execution debuggers!
    app.run(host='0.0.0.0', port=8084, debug=True)