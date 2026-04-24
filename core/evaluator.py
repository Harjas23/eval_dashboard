# import json
# from core.llm import call_llm
# from deepeval.metrics import AnswerRelevancyMetric, HallucinationMetric
# from deepeval.models import DeepEvalBaseLLM


# # ---------------- SAFE JSON PARSER ----------------
# def safe_json_parse(text):
#     try:
#         return json.loads(text)
#     except:
#         return {
#             "score": 0,
#             "reason": f"Invalid JSON response: {text}"
#         }


# # ---------------- CUSTOM LLM WRAPPER ----------------
# class OpenRouterLLM(DeepEvalBaseLLM):
#     def __init__(self, model="nvidia/nemotron-3-super-120b-a12b:free"):
#         self.model = model

#     def load_model(self):
#         # No local loading required
#         return self

#     def get_model_name(self):
#         return self.model

#     def generate(self, prompt: str):
#         return call_llm(prompt, model=self.model)

#     async def a_generate(self, prompt: str):
#         return self.generate(prompt)


# # Initialize LLM
# llm = OpenRouterLLM()


# # ---------------- METRICS ----------------
# relevance_metric = AnswerRelevancyMetric(model=llm)
# hallucination_metric = HallucinationMetric(model=llm)


# # ---------------- CORRECTNESS ----------------
# def correctness(query, gt, output):
#     prompt = f"""
#     Compare ground truth and output.

#     Query: {query}
#     Ground Truth: {gt}
#     Output: {output}

#     Score between 0 and 1 based on correctness.

#     Return JSON:
#     {{
#       "score": float,
#       "reason": "short explanation"
#     }}
#     """

#     response = call_llm(prompt)
#     return safe_json_parse(response)


# # ---------------- PII DETECTION ----------------
# def pii_check(output):
#     prompt = f"""
#     Check if the following text contains PII
#     (emails, phone numbers, addresses, personal identifiers).

#     Text: {output}

#     Return JSON:
#     {{
#       "pii": 0 or 1,
#       "reason": "short explanation"
#     }}
#     """

#     response = call_llm(prompt)
#     parsed = safe_json_parse(response)

#     # Ensure structure
#     return {
#         "pii": parsed.get("pii", 0),
#         "reason": parsed.get("reason", "")
#     }


# # ---------------- MAIN EVALUATION ----------------
# # def evaluate(query, gt, output):
# #     try:
# #         rel = relevance_metric.measure(
# #             input=query,
# #             actual_output=output
# #         )
# #         relevance_score = rel.score
# #     except:
# #         relevance_score = 0

# #     try:
# #         hall = hallucination_metric.measure(
# #             input=query,
# #             actual_output=output
# #         )
# #         hallucination_score = hall.score
# #     except:
# #         hallucination_score = 0

# #     corr = correctness(query, gt, output)
# #     pii = pii_check(output)

# #     return {
# #         "correctness": corr.get("score", 0),
# #         "correctness_reason": corr.get("reason", ""),
# #         "relevance": relevance_score,
# #         "hallucination": hallucination_score,
# #         "pii": pii.get("pii", 0),
# #         "pii_reason": pii.get("reason", "")
# #     }
# from deepeval.test_case import LLMTestCase

# def evaluate(query, gt, output):
#     test_case = LLMTestCase(
#         input=query,
#         actual_output=output,
#         expected_output=gt
#     )

#     try:
#         rel = relevance_metric.measure(test_case)
#         relevance_score = rel.score
#     except:
#         relevance_score = 0

#     try:
#         hall = hallucination_metric.measure(test_case)
#         hallucination_score = hall.score
#     except:
#         hallucination_score = 0

#     corr = correctness(query, gt, output)
#     pii = pii_check(output)

#     return {
#         "correctness": corr.get("score", 0),
#         "correctness_reason": corr.get("reason", ""),
#         "relevance": relevance_score,
#         "hallucination": hallucination_score,
#         "pii": pii.get("pii", 0),
#         "pii_reason": pii.get("reason", "")
#     }

# from core.judge import call_judge


# def evaluate(query, gt, output):
#     """
#     Unified evaluation using LLM as judge.
#     Returns:
#     {
#         correctness: 0/1,
#         relevance: 0/1,
#         hallucination: 0/1,
#         pii: 0/1,
#         correctness_reason: str
#     }
#     """

#     prompt = f"""
# You are an expert evaluator of LLM responses.

# IMPORTANT CONTEXT:
# - The model output may be a natural language interpretation of SQL query results.
# - The ground truth may be shorter or less detailed.
# - Do NOT penalize verbosity or formatting differences.
# - Focus on semantic correctness.


# EVALUATION RULES:

# 1. Correctness:
# - Does the output contain the correct answer based on the ground truth?
# - Minor wording differences are acceptable.
# - Score: Between 0 to 1.
# - If any additional information is returned check from business pov whether its helpful for user and then consider scoring

# 2. Relevance:
# - Does the output directly answer the user’s query?
# - Even if phrased differently, it should still be considered relevant.
# - Score: Between 0 to 1, 0 being non relevant, 1 being completely relevant

# 3. Hallucination:
# - Does the output include facts not supported by the data?
# - Score: Between 0 to 1, 0 being non hallucinated, 1 being completely hallucinated.

# 4. PII:
# - ONLY flag if output contains:
#   - email addresses
#   - phone numbers
# - DO NOT flag business addresses (street, city, etc.)
# - Score: 1 (PII present) or 0 (no PII)

# OUTPUT FORMAT:
# Return STRICT JSON only (no text outside JSON):

# {{
#   "correctness": 0 or 1,
#   "relevance": 0 or 1,
#   "hallucination": 0 or 1,
#   "pii": 0 or 1,
#   "reason": "short explanation"
# }}

# INPUTS:
# Query: {query}
# Ground Truth: {gt}
# Model Output: {output}
# """

#     try:
#         result = call_judge(prompt)

#         if not isinstance(result, dict):
#             raise ValueError("Invalid response format")

#         return {
#             "correctness": result.get("correctness", 0),
#             "relevance": result.get("relevance", 0),
#             "hallucination": result.get("hallucination", 0),
#             "pii": result.get("pii", 0),
#             "correctness_reason": result.get("reason", "No explanation provided")
#         }

#     except Exception as e:
#         return {
#             "correctness": 0,
#             "relevance": 0,
#             "hallucination": 0,
#             "pii": 0,
#             "correctness_reason": f"Evaluation failed: {str(e)}"
#         }
from core.judge import call_judge


def evaluate(query, gt, output):

    prompt = f"""
You are an expert evaluator of LLM responses.

IMPORTANT CONTEXT:
- The output may include reasoning steps (e.g., SQL logic, filtering, ordering).
- These reasoning steps are NOT hallucinations.
- The ground truth may be shorter than the output.
- Judge based on semantic correctness.

EVALUATION RULES:

1. Correctness:
- Does the output contain the correct answer?
- Ignore extra explanation.
- Score: 1 or 0

2. Relevance:
- Does the output answer the user's query?
- Extra helpful details are allowed.
- Do NOT penalize for verbosity.
- Score: 1 or 0

3. Hallucination:
- Only mark as hallucination if:
  - facts are incorrect OR
  - facts contradict ground truth
- Extra correct details or reasoning are NOT hallucinations.
- Score: 1 or 0

4. PII:
- Only flag:
  - email addresses
  - phone numbers
- DO NOT flag business addresses
- Score: 1 or 0

OUTPUT FORMAT (STRICT JSON):

{{
  "correctness": 0 or 1,
  "relevance": 0 or 1,
  "hallucination": 0 or 1,
  "pii": 0 or 1,
  "reasons": {{
    "correctness": "short explanation",
    "relevance": "short explanation",
    "hallucination": "short explanation",
    "pii": "short explanation"
  }}
}}

INPUT:
Query: {query}
Ground Truth: {gt}
Model Output: {output}
"""

    try:
        result = call_judge(prompt)

        if not isinstance(result, dict):
            raise ValueError("Invalid response")

        reasons = result.get("reasons", {})

        return {
            "correctness": result.get("correctness", 0),
            "relevance": result.get("relevance", 0),
            "hallucination": result.get("hallucination", 0),
            "pii": result.get("pii", 0),

            # store individual reasons
            "correctness_reason": reasons.get("correctness", ""),
            "relevance_reason": reasons.get("relevance", ""),
            "hallucination_reason": reasons.get("hallucination", ""),
            "pii_reason": reasons.get("pii", "")
        }

    except Exception as e:
        return {
            "correctness": 0,
            "relevance": 0,
            "hallucination": 0,
            "pii": 0,
            "correctness_reason": str(e),
            "relevance_reason": "",
            "hallucination_reason": "",
            "pii_reason": ""
        }