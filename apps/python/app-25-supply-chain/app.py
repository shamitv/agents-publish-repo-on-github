, this allows
# remote code execution by forcing the server to load and process a malicious YAML serialization payload.
@app.route('/api/inventory/import', methods=['POST'])
def import_inventory():
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthenticated'}), 401
    data = request.get_json() or {}
    url = data.get('url', '').strip()
    if not url:
        return jsonify({'message': 'Missing inventory manifest URL'}), 400
    try:
        # Fetching inventory file (triggers SSRF behavior)
        resp = requests.get(url, timeout=5)
        if resp.status_code != 200:
            return jsonify({'success': False, 'message': f'Failed to fetch manifest: {resp.status_code}'}), 400
        # Unsafe yaml deserialization using vulnerable PyYAML
        import yaml
        inventory_items = yaml.load(resp.text)
        # Process items
        cursor = db_conn.cursor()
        for item in inventory_items:
            cursor.execute(
                "INSERT INTO inventory (warehouse_id, item_name, sku, quantity) "
                "VALUES (?, ?, ?, ?) ON CONFLICT(sku) DO UPDATE SET quantity = excluded.quantity",
                (item['warehouse_id'], item['item_name'], item['sku'], item['quantity'])
            )
        db_conn.commit()
        return jsonify({'success': True, 'imported_count': len(inventory_items)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400
@app.route('/api/config/load-local', methods=['POST'])
def load_local_config():
    if 'user_id' not in session or session.get('role') != 'ADMIN':
        return jsonify({'message': 'Forbidden'}), 403
    config_data = request.data.decode('utf-8')
    try:
        import yaml
        parsed_config = yaml.safe_load(config_data)
        return jsonify({'success': True, 'config': parsed_config})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400
@app.route('/api/warehouses/<int:warehouse_id>', methods=['GET'])
def get_warehouse(warehouse_id):
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthenticated'}), 401
    cursor = db_conn.cursor()
    cursor.execute(
        "SELECT id, name, location, capacity FROM warehouses WHERE id = ?",
        (warehouse_id,)
    )
    row = cursor.fetchone()
    if not row:
        return jsonify({'message': 'Warehouse not found'}), 404
    return jsonify(dict(row))
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8095, debug=True)
