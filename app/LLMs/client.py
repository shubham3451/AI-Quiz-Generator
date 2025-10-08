import requests
import json
from typing import Any
from app.core.config import settings
import ast

class LLMClient:
    def __init__(self, base_url=settings.LLM_BASE_URL, model=settings.MODEL):
        self.base_url = base_url
        self.model = model
    def chat(
        self, 
        prompt: str, 
        expect_json: bool = False, 
        default_keys: dict = None
    ) -> Any:
        """
        Generic LLM call.

        Parameters:
        - prompt: str -> the text prompt to send
        - expect_json: bool -> whether to parse LLM response as JSON
        - default_keys: dict -> fallback keys/values if JSON is incomplete

        Returns:
        - JSON object if expect_json=True
        - Raw text if expect_json=False
        """
        print("prompt: ",prompt)
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "temperature": 0.7
        }

        response = requests.post(self.base_url, json=payload)
        if response.status_code != 200:
            raise Exception(f"LLM request failed: {response.text}")
        print("response text: ",response.text)
        # raw_response = response.json().get("response", "").strip()
        # print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

        # if expect_json:
        #     try:
        #         parsed = json.loads(raw_response)  # Try normal JSON parse
        #     except json.JSONDecodeError:
        #         try:
        #             parsed = ast.literal_eval(raw_response)  # Try Python literal parse
        #         except Exception:
        #             if default_keys:
        #                 return default_keys
        #             return {"raw_text": raw_response}
    
        #     # Handle list response wrapped in default keys
        #     if isinstance(parsed, list) and default_keys:
        #         # e.g. {"questions": [ ... ]}
        #         key = list(default_keys.keys())[0]
        #         return {key: parsed}
    
        #     if default_keys:
        #         for k, v in default_keys.items():
        #             if k not in parsed:
        #                 parsed[k] = v
    
        #     return parsed
        # print("raw response: ", raw_response)
        # return raw_response
        raw_response = response.json().get("response", "").strip()
        print("response text: ", raw_response)
        print()

        return raw_response

        # if not expect_json:
        #     return raw_response
    
        # try:
        #     parsed = json.loads(raw_response)
        # except json.JSONDecodeError:
        #     try:
        #         parsed = ast.literal_eval(raw_response)
        #     except Exception:
        #         return default_keys or {"raw_text": raw_response}
    
        # # If the response is a list with dicts, just take the first dict (for consistency)
        # if isinstance(parsed, list) and parsed and isinstance(parsed[0], dict):
        #     parsed = parsed[0]
    
        # # Ensure all default keys exist in parsed, fill with defaults
        # if default_keys:
        #     for key, default_val in default_keys.items():
        #         if key not in parsed or parsed[key] is None:
        #             parsed[key] = default_val
        #         else:
        #             # For nested lists/dicts convert to JSON string if needed
        #             val = parsed[key]
        #             if isinstance(val, (list, dict)):
        #                 parsed[key] = json.dumps(val, indent=2)
        #             elif isinstance(val, str):
        #                 parsed[key] = val.strip()
        #             else:
        #                 parsed[key] = str(val)
    
        # return parsed
    
    
        