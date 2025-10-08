from app.db.repositories.profile import ProfileRepository
from app.db.repositories.quiz import QuizRepository
from app.LLMs.client import LLMClient
from app.vectorDB.embeddings import EmbeddingGenerator
from app.vectorDB.vector_store import VectorStore
from uuid import UUID
from app.core import prompts
from typing import List
from app.core.config import settings
import json
import ast
from typing import List, Union
import re

class QuizService:
    def __init__(
        self,
        profile_repo: ProfileRepository,
        quiz_repo: QuizRepository,
        llm_client: LLMClient,
        vector_store: VectorStore,
        embedding_generator: EmbeddingGenerator
    ):
        self.profile_repo = profile_repo
        self.quiz_repo = quiz_repo
        self.llm_client = llm_client
        self.vector_store = vector_store
        self.embedding_generator = embedding_generator

    def generate_quiz_for_user(self, user_id: UUID, profile_data: dict):
        profile_data['user_id'] = str(user_id)
        profile = self.profile_repo.create_or_update(profile_data)

        prompt = prompts.build_quiz_prompt(profile=profile)

        raw_response = self.llm_client.chat(prompt=prompt,expect_json=True, default_keys={"questions": []})
        print("raw response: ",raw_response)
        questions = self._parse_llm_response(raw_response)
        # if isinstance(raw_response, str):
        #     try:
        #         raw_response = json.loads(raw_response)
        #     except json.JSONDecodeError as e:
        #         try:
        #             raw_response = ast.literal_eval(raw_response)
        #         except Exception as e:
        #             raise ValueError(f"Failed to parse LLM response as JSON or Python dict: {e}")

        # if isinstance(raw_response, dict):
        #     questions = raw_response.get("questions", [])
        # elif isinstance(raw_response, list):
        #     questions = raw_response
        # else:
        #     raise ValueError("Invalid LLM response format: expected dict or list.")
    
        if not isinstance(questions, list):
            raise ValueError("Questions must be a list.")
        

        tags = list({tag for q in questions for tag in q.get("tags", [])})
        quiz_type = "personalized"  

        quiz_data = {
            "user_id": user_id,
            "profile_snapshot": profile_data,
            "total_questions": len(questions),
            "quiz_type": quiz_type,
            "tags": tags,
            "quiz_metadata": {
                "source": "llm_generated",
                "model": settings.MODEL
            }
        }
        quiz = self.quiz_repo.create_quiz(quiz_data)

        formatted_questions = []
        for q in questions:
            options_raw = q.get("options", None)
            if options_raw and isinstance(options_raw, list):
                options = []
                for opt in options_raw:
                    if isinstance(opt, dict) and "text" in opt:
                        options.append(opt["text"])
                    else:
                        options.append(str(opt))
            else:
                options = None
            formatted_questions.append({
                "question_text": q["question_text"],
                "question_type": q.get("question_type", "open_ended"),
                "options": q.get("options", None),
                "correct_answer": q.get("correct_answer", None),
             #   "quiz_id": str(quiz.id)
            })

        self.quiz_repo.add_questions(quiz_id=str(quiz.id), questions=formatted_questions)

        return {
            "quiz_id": str(quiz.id),
            "total_questions": len(questions),
            "questions": formatted_questions
        }
    


    def process_quiz_response(self, user_id: UUID, quiz_id: UUID, responses: List[dict]):
        """
        responses: list of dicts with:
        {
            "question_id": UUID,
            "answer_text": str,
            "is_correct": bool | None,
            "score": float | None
        }
        """

        answers = self.quiz_repo.save_answers(user_id, quiz_id, responses)

        question_ids = [resp["question_id"] for resp in responses]
        question_objs = self.quiz_repo.get_questions_by_ids(question_ids)
        question_type_map = {str(q.id): q.question_type for q in question_objs}

        open_ended = [
            ans for ans in answers
            if question_type_map.get(str(ans.question_id)) == "open_ended"
        ]

        if not open_ended:
            return {"status": "saved", "embedded": 0}

        answer_texts = [ans.answer_text for ans in open_ended]
        embeddings = self.embedding_generator.embed(answer_texts)
        print("embeddings: ",embeddings)

        vector_docs = []
        for idx, ans in enumerate(open_ended):
            vector_docs.append({
                "id": str(ans.id),
                "embedding": embeddings[idx],
                "metadata": {
                    "user_id": str(ans.user_id),
                    "quiz_id": str(ans.quiz_id),
                    "question_id": str(ans.question_id),
                    "answer_text": ans.answer_text,
                    "created_at": str(ans.created_at)
                }
            })
            print(f"\nDocument {idx+1}:")
            print("ID:", ans.id)
            print("Embedding:",embeddings)
            print("Metadata:", ans.answer_text)

        self.vector_store.add_documents(vector_docs)

        return {"status": "saved", "embedded": len(open_ended)}
    

    def _parse_llm_response(self, raw_response: Union[str, dict, list]) -> list:
        """
        Robustly parse the LLM response and return a list of question dictionaries.
        Handles:
        - Raw JSON strings
        - Python literals
        - Nested strings inside 'questions', 'data', or 'response'
        - Fallbacks to `ast.literal_eval` when needed
        """

        def _clean_json_string(s: str) -> str:
            """Clean common JSON issues."""
            s = re.sub(r'//.*', '', s)  # Remove comments
            s = s.replace('...', '')  # Remove ellipses
            s = re.sub(r',\s*([\]}])', r'\1', s)  # Remove trailing commas
            return s.strip()

        def _try_parse_string(s: str):
            """Try parsing string as JSON or Python literal."""
            try:
                return json.loads(_clean_json_string(s))
            except Exception:
                try:
                    return ast.literal_eval(s)
                except Exception:
                    return None

        # Step 1: If string, parse
        if isinstance(raw_response, str):
            parsed = _try_parse_string(raw_response)
            if parsed is not None:
                raw_response = parsed

        # Step 2: If dict, look for embedded questions
        if isinstance(raw_response, dict):
            for key in ["questions", "data", "response", "items"]:
                if key in raw_response:
                    inner = raw_response[key]
                    if isinstance(inner, str):
                        inner = _try_parse_string(inner)
                    if isinstance(inner, list):
                        return inner
                    elif isinstance(inner, dict) and "questions" in inner:
                        return inner["questions"]
            # Edge case: if dict is actually a single question
            if "question_text" in raw_response:
                return [raw_response]

        # Step 3: Already a list
        if isinstance(raw_response, list):
            return raw_response

        # Final fallback failed
        raise ValueError(
            f"Unable to parse LLM response into list of questions. Type: {type(raw_response)} | Content: {str(raw_response)[:500]}"
        )


   