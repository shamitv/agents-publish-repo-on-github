: Score updating has NO authorization checks for the COMMISSIONER role!
    cursor.execute(
        "UPDATE games SET score_home = ?, score_away = ?, status = 'COMPLETED' WHERE id = ?",
        (score_home, score_away, game_id)
    )
    db_conn.commit()
    return jsonify({
        'success': True,
        'message': f"Game {game_id} score updated to {score_home}-{score_away}"
    })
# Decoy: Proper authorization role check on team creations
@app.route('/api/teams', methods=['POST'])
def create_team():
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthenticated'}), 401
    # Decoy: Enforces COMMISSIONER role check
    if session.get('role') != 'COMMISSIONER':
        return jsonify({'message': 'Forbidden: Only commissioners can create teams'}), 403
    data = request.get_json() or {}
    team_name = data.get('team_name', '').strip()
    if not team_name:
        return jsonify({'message': 'Missing team_name'}), 400
    try:
        cursor = db_conn.cursor()
        cursor.execute("INSERT INTO standings (team_name, points) VALUES (?, 0)", (team_name,))
        db_conn.commit()
        return jsonify({'success': True, 'team_name': team_name})
    except sqlite3.IntegrityError:
        return jsonify({'message': 'Team already exists'}), 400
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8099, debug=True)