from flask import Flask, jsonify, request
from flask_cors import CORS
from typing import Dict, Any
import uuid

app = Flask(__name__)
CORS(app)

# Define the list of agent names
AGENT_NAMES = [
    "Market Analyst", "Social Analyst", "News Analyst", "Fundamentals Analyst",
    "Bull Researcher", "Bear Researcher", "Research Manager", "Trader",
    "Risky Analyst", "Neutral Analyst", "Safe Analyst", "Portfolio Manager"
]

# In-memory storage for trades only
mock_pending_trades_store: Dict[str, Dict[str, Any]] = {}

def initialize_mock_trades():
    """Initializes or re-initializes the mock trades store."""
    global mock_pending_trades_store
    proposals_init = [
        {
            "trade_id": str(uuid.uuid4()),
            "pair": "EUR/USD",
            "side": "buy",
            "type": "market",
            "entry_price": None,
            "sl": 1.0750,
            "tp": 1.0950,
            "calculated_position_size": 0.01,
            "meta_rationale": "DayTrader: Bullish EMA crossover on M15, RSI not overbought. MetaAgent: Aligned with bullish USD directive, low risk.",
            "sub_agent_confidence": 0.7,
            "risk_assessment": {
                "risk_score": 0.2,
                "assessment_summary": "Low market risk, good alignment with strategy.",
                "proceed_with_trade": True,
                "recommended_modifications": {"size_factor": 1.0}
            },
            "status": "pending_approval"
        },
        {
            "trade_id": str(uuid.uuid4()),
            "pair": "USD/JPY",
            "side": "buy",
            "type": "limit",
            "entry_price": 149.50,
            "sl": 149.00,
            "tp": 150.50,
            "calculated_position_size": 0.02,
            "meta_rationale": "SwingTrader: Price at H4 support, MACD turning bullish. MetaAgent: Aligned with bullish USD directive, moderate risk due to upcoming news.",
            "sub_agent_confidence": 0.65,
            "risk_assessment": {
                "risk_score": 0.4,
                "assessment_summary": "Moderate risk due to event. Consider half size.",
                "proceed_with_trade": True,
                "recommended_modifications": {"size_factor": 0.5}
            },
            "status": "pending_approval"
        },
        {
            "trade_id": str(uuid.uuid4()),
            "pair": "GBP/USD",
            "side": "sell",
            "type": "market",
            "entry_price": None,
            "sl": 1.2650,
            "tp": 1.2500,
            "calculated_position_size": 0.01,
            "meta_rationale": "DayTrader: Bearish EMA crossover. MetaAgent: Aligned with bearish GBP directive (hypothetical), low risk.",
            "sub_agent_confidence": 0.72,
            "risk_assessment": {
                "risk_score": 0.3,
                "assessment_summary": "Low risk, setup aligns with short-term bearish view for GBP.",
                "proceed_with_trade": True,
                "recommended_modifications": {}
            },
            "status": "pending_approval"
        }
    ]
    mock_pending_trades_store = {p["trade_id"]: p for p in proposals_init}
    print(f"Mock trades initialized. Count: {len(mock_pending_trades_store)}")

initialize_mock_trades()

@app.route('/api/agents', methods=['GET'])
def get_agents():
    """Returns the list of available agent names."""
    return jsonify(AGENT_NAMES)

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handles chat messages to agents or StroudAI."""
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "Missing message in request"}), 400

    message = data['message']
    agent_id = data.get('agent_id')

    if agent_id:
        if agent_id in AGENT_NAMES:
            response_text = f"Response from {agent_id}: You said '{message}'"
        else:
            return jsonify({"error": f"Agent {agent_id} not found"}), 404
    else:
        response_text = f"Response from StroudAI: You said '{message}'"

    return jsonify({"sender": "ai", "text": response_text})

@app.route('/api/pending_trades', methods=['GET'])
def pending_trades():
    global mock_pending_trades_store
    print(f"API: /api/pending_trades called, returning {len(mock_pending_trades_store)} trades that are pending approval.")
    pending_list = [trade for trade in mock_pending_trades_store.values() if trade['status'] == 'pending_approval']
    return jsonify(pending_list)

@app.route('/api/trades/<string:trade_id>/approve', methods=['POST'])
def approve_trade_by_id(trade_id):
    global mock_pending_trades_store
    if trade_id in mock_pending_trades_store:
        if mock_pending_trades_store[trade_id]['status'] == 'pending_approval':
            mock_pending_trades_store[trade_id]['status'] = 'approved'
            print(f"Mock API: Trade {trade_id} approved by user.")
            return jsonify({"status": "success", "message": f"Trade {trade_id} approved."}), 200
        else:
            print(f"Mock API: Trade {trade_id} was not pending approval (current status: {mock_pending_trades_store[trade_id]['status']}).")
            return jsonify({"status": "error", "message": f"Trade {trade_id} not in 'pending_approval' state.", "current_status": mock_pending_trades_store[trade_id]['status']}), 400
    else:
        print(f"Mock API: Trade {trade_id} not found for approval.")
        return jsonify({"status": "error", "message": f"Trade {trade_id} not found."}), 404

@app.route('/api/trades/<string:trade_id>/reject', methods=['POST'])
def reject_trade_by_id(trade_id):
    global mock_pending_trades_store
    if trade_id in mock_pending_trades_store:
        if mock_pending_trades_store[trade_id]['status'] == 'pending_approval':
            mock_pending_trades_store[trade_id]['status'] = 'rejected'
            print(f"Mock API: Trade {trade_id} rejected by user.")
            return jsonify({"status": "success", "message": f"Trade {trade_id} rejected."}), 200
        else:
            print(f"Mock API: Trade {trade_id} was not pending approval (current status: {mock_pending_trades_store[trade_id]['status']}).")
            return jsonify({"status": "error", "message": f"Trade {trade_id} not in 'pending_approval' state.", "current_status": mock_pending_trades_store[trade_id]['status']}), 400
    else:
        print(f"Mock API: Trade {trade_id} not found for rejection.")
        return jsonify({"status": "error", "message": f"Trade {trade_id} not found."}), 404

if __name__ == '__main__':
    print("Starting trade approval API server on http://127.0.0.1:5000 ...")
    app.run(debug=True, port=5000)
