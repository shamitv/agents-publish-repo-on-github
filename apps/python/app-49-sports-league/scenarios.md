# Chained Vulnerability Scenarios — Sports League

## Chain: "SQLi Player Dump → IDOR Contract Access → Score Manipulation"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | SQL injection in player search | Medium | A03 | `app.py` → `search_players()` |
| 2 | IDOR on player details leaks sensitive contract data | Low | A01 | `app.py` → `get_player()` |
| 3 | Game score update endpoint lacks authorization checks | Medium | A01 | `app.py` → `update_score()` |


**Attack narrative**: 1. The attacker logs in with a normal spectator/fan account (`fan_tom`).
2. The attacker uses the player search feature `/api/players/search?q=1' OR '1'='1` to perform SQL injection, extracting all system players, teams, and internal database record IDs.
3. The attacker requests the profile of a specific player using the IDOR vulnerability at `/api/players/<player_id>`, exposing the player's personal salary and contract details.
4. Finally, the attacker updates a game score by sending a POST request to `/api/games/<game_id>/score` with a custom score payload. Since the endpoint lacks role checks, the server updates the score, changing league standings.

**Combined Impact**: `data_modification` — Attacker modifies league scores and compromises standings integrity without holding a commissioner role.

---

_This file is for internal reference. Ground truth vulnerability data is maintained in [.vulns](.vulns)._
