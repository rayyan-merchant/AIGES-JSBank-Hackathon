import os
import json
import sqlite3

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "aegis.db"))
SCHEMA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "schema.sql"))

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    with open(SCHEMA_PATH, "r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

def new_run(income, debt, emi, rounds):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO simulation_runs (income, debt, emi, rounds) VALUES (?, ?, ?, ?)",
        (income, debt, emi, rounds),
    )
    run_id = cur.lastrowid
    conn.commit()
    conn.close()
    return run_id

def log_metric(run_id, name, value):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO metrics_log (run_id, metric_name, metric_value) VALUES (?, ?, ?)",
        (run_id, name, float(value)),
    )
    conn.commit()
    conn.close()

def log_contract(run_id, contract, compliance_score, profit_expectation, survival_probability):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO contracts (run_id, contract_json, compliance_score, profit_expectation, survival_probability) VALUES (?, ?, ?, ?, ?)",
        (run_id, json.dumps(contract), float(compliance_score), float(profit_expectation), float(survival_probability)),
    )
    conn.commit()
    conn.close()
