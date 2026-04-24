from core.llm import call_llm
from core.sql_sanitizer import sanitize_sql
from supabase import create_client
import os

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

SCHEMA = """
Table: businesses2
Columns:
name, city, state, street, country, sales_volume
"""

def generate_sql(query):
    prompt = f"""
    You are a SQL expert.

    {SCHEMA}

    STRICT RULES:
    - Only ONE SELECT query
    - No semicolons
    - No explanation

    Query: {query}

    SQL:
    """
    return call_llm(prompt)


def execute_sql(sql):
    sql = sanitize_sql(sql)
    res = supabase.rpc("execute_sql24", {"query": sql}).execute()
    return res.data


# 🔥 NEW: interpretation layer
def interpret_results(query, sql, result):
    prompt = f"""
    You are a business analyst.

    User Query: {query}
    SQL Query: {sql}
    SQL Result: {result}

    Convert this into a clean natural language answer.

    Rules:
    - Be concise
    - Answer the question directly
    - Do NOT mention SQL
    """
    return call_llm(prompt)


def agent_run(query):
    try:
        sql = generate_sql(query)
        print(sql)
        result = execute_sql(sql)

        final_answer = interpret_results(query, sql, result)

        return {
            "sql": sql,
            "raw_result": result,
            "final_answer": final_answer
        }

    except Exception as e:
        return {
            "error": str(e)
        }