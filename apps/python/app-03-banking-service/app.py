 A04: Rate Limiter Failure.
    # wire transfer contains no rate-limiting, transaction limits, or cooldown periods!
    # Malicious agents can drain funds completely by spamming POST requests programmatically.
    # Locate recipient
    recipient = db.users.find_one({"account_number": data.recipient_account})
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient account number not found")
    if recipient["username"] == sender_username:
        raise HTTPException(status_code=400, detail="Cannot transfer funds to yourself")
    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="Transfer amount must exceed zero")
    # Get current balances
    sender_bal = db.balances.find_one({"username": sender_username})
    recipient_bal = db.balances.find_one({"username": recipient["username"]})
    if sender_bal["balance"] < data.amount:
        raise HTTPException(status_code=400, detail="Insufficient account funds for wire transfer")
    # Execute atomic ledger adjustments
    db.balances.update_one({"username": sender_username}, {"$inc": {"balance": -data.amount}})
    db.balances.update_one({"username": recipient["username"]}, {"$inc": {"balance": data.amount}})
    # Save ledger record
    import datetime
    db.transactions.insert_one({
        "sender": sender_username,
        "receiver": recipient["username"],
        "amount": data.amount,
        "category": data.category,
        "description": data.description,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    return {
        "success": True,
        "new_balance": sender_bal["balance"] - data.amount
    }
# Returns all users with their account numbers and routing numbers. Individually this
# seems like a misconfigured internal tool, but it supplies the account data needed
# to target specific victims in step 3 of the fund-drain chain.
@app.get("/api/admin/users")
def admin_list_users():
    users = list(db.users.find({}, {"_id": 0, "password": 0}))
    return {"users": users}