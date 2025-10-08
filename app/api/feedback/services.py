from uuid import UUID
from typing import Optional
from app.db.repositories.feedback import FeedbackRepository
from app.db.repositories.quiz import QuizRepository
from app.LLMs.client import LLMClient
from app.vectorDB.embeddings import EmbeddingGenerator
from app.vectorDB.vector_store import VectorStore
from app.core import prompts
from app.db.repositories.profile import ProfileRepository
import re
import json


class FeedbackService:
    def __init__(
        self,
        feedback_repo: FeedbackRepository,
        quiz_repo: QuizRepository,
        profile_repo : ProfileRepository,
        vector_store: VectorStore,
        embedding_generator: EmbeddingGenerator,
        llm_client: LLMClient,
    ):
        self.feedback_repo = feedback_repo
        self.quiz_repo = quiz_repo
        self.profile_repo = profile_repo
        self.vector_store = vector_store
        self.embedding_generator = embedding_generator
        self.llm_client = llm_client

    def generate_feedback(
        self,
        user_id: UUID,
        quiz_id: Optional[UUID] = None,
        topic: Optional[str] = None
    ):
        """
        Generate personalized feedback for a user, based on their quiz or topic context.
        If no quiz/topic is provided, defaults to last quiz.
        """

        quiz = None
        if quiz_id:
            quiz = self.quiz_repo.get_quiz_by_id(quiz_id)
        else:
            quiz = self.quiz_repo.get_last_quiz_for_user(user_id)

        if not quiz:
            raise ValueError("No quiz found for this user.")

        search_text = ""
        if topic and quiz:
            search_text = f"{topic} {quiz.quiz_type}"
        elif topic:
            search_text = topic
        elif quiz:
            search_text = " ".join(quiz.tags or [])

        embedding = self.embedding_generator.embed([search_text])[0]
        print("embeddings: ", embedding)

        similar_docs = self.vector_store.similarity_search(embedding, top_k=5)
        print("similar_docs: ", similar_docs)

        retrieved_texts = []
        if similar_docs and "documents" in similar_docs:
            retrieved_texts = similar_docs["documents"][0]
        else:
            retrieved_texts = ["No similar answers found in vector DB."]

        feedback_prompt = prompts.build_feedback_prompt(
            user_profile=quiz.profile_snapshot,
            quiz_tags=quiz.tags,
            topic=topic,
            context=retrieved_texts
        )

        response = self.llm_client.chat(prompt=feedback_prompt,  expect_json=True, default_keys={"feedback_text": "", "follow_up_suggestion": ""})

        parsed = extract_feedback(response)
       # profile = self.profile_repo.get_by_user_id(user_id=user_id)
        feedback_data = {
            "profile_id": user_id,
            "quiz_id": quiz.id,
            "feedback_text": parsed.get("feedback_text", ""),
            "follow_up_suggestion": parsed.get("follow_up_suggestion", ""),
        }

        saved_feedback = self.feedback_repo.create_feedback(feedback_data)

        return {
            "feedback_id": str(saved_feedback.id),
            "quiz_id": str(quiz.id),
            "topic": topic or "overall",
            "feedback_text": parsed.get("feedback_text", ""),
            "follow_up_suggestion": parsed.get("follow_up_suggestion", ""),
        }
    

def extract_feedback(raw_response: str) -> dict:
    """
    Extracts 'feedback_text' and 'follow_up_suggestion' from:
    - JSON
    - Markdown-style JSON
    - Loose JSON inside text
    - Text with labeled lines (like 'Feedback Text:', 'Follow-up Suggestion:')
    """
    default = {
        "feedback_text": "No feedback provided.",
        "follow_up_suggestion": None
    }

    if not raw_response or not isinstance(raw_response, str):
        return default

    # --- Step 1: Try parsing full JSON
    try:
        data = json.loads(raw_response)
        return {
            "feedback_text": data.get("feedback_text", default["feedback_text"]).strip(),
            "follow_up_suggestion": data.get("follow_up_suggestion", default["follow_up_suggestion"])
        }
    except Exception:
        pass

    # --- Step 2: Look for ```json blocks
    json_blocks = re.findall(r"```json\n(.*?)```", raw_response, re.DOTALL | re.IGNORECASE)
    for block in json_blocks:
        try:
            data = json.loads(block)
            return {
                "feedback_text": data.get("feedback_text", default["feedback_text"]).strip(),
                "follow_up_suggestion": data.get("follow_up_suggestion", default["follow_up_suggestion"])
            }
        except Exception:
            continue

    # --- Step 3: Extract loose JSON-like objects
    loose_jsons = re.findall(r"({.*?})", raw_response, re.DOTALL)
    for snippet in loose_jsons:
        try:
            data = json.loads(snippet)
            if isinstance(data, dict) and ("feedback_text" in data or "follow_up_suggestion" in data):
                return {
                    "feedback_text": data.get("feedback_text", default["feedback_text"]).strip(),
                    "follow_up_suggestion": data.get("follow_up_suggestion", default["follow_up_suggestion"])
                }
        except Exception:
            continue

    # --- Step 4: Try extracting from labeled text
    feedback_match = re.search(r'(?i)feedback\s*text\s*:\s*"?(.*?)"?(?:\n|$)', raw_response, re.DOTALL)
    followup_match = re.search(r'(?i)follow[\s-]*up\s*(suggestion|succession)\s*:\s*(.*)', raw_response, re.DOTALL)

    feedback_text = feedback_match.group(1).strip() if feedback_match else default["feedback_text"]
    follow_up_suggestion = followup_match.group(2).strip() if followup_match else default["follow_up_suggestion"]

    return {
        "feedback_text": feedback_text,
        "follow_up_suggestion": follow_up_suggestion
    }

