from typing import List, Optional



def build_quiz_prompt(profile) -> str:
    hobbies = ", ".join(profile.hobbies or [])
    return f"""
You are an expert tutor. Your task is to generate 6 personalized quiz questions** based on the following student profile.

🧑 User Profile:
- Name: {profile.name}
- Age: {profile.age}
- Gender: {profile.gender}
- Education Level: {profile.education}
- Location: {profile.city}
- Interests: {hobbies}

📘 Instructions:
- Include a 2 of each question types**: multiple choice (MCQ), open-ended, and true/false.
- Questions should reflect the user's interests and educational background.
- Use neutral, inclusive language.

📤 Output Format:
Respond in **pure JSON**, structured as a list of question objects:

```json
[
  {{
    "question_text": "What is the main function of a CPU in a computer?",
    "question_type": "mcq",                // mcq | open_ended | true_false
    "options": ["Storage", "Processing", "Display", "Cooling"],  // Required for MCQ
    "correct_answer": "Processing",        // Optional (can be null for open-ended)
    "tags": ["technology", "computers"]
  }},
  ...
]

"""



def build_feedback_prompt(
    user_profile: dict,
    quiz_tags: List[str],
    context: List[str],
    topic: Optional[str] = None
) -> str:
    profile_str = ", ".join(f"{k}: {v}" for k, v in user_profile.items() if v)
    tags_str = ", ".join(quiz_tags or [])
    topic_str = f"Topic: {topic}" if topic else "General performance"
    context_str = "\n".join(f"- {c}" for c in context[:10]) if context else "No contextual answers provided."

    return f"""
You are an expert learning coach. Your task is to provide personalized feedback based on the user's profile and quiz activity.

🧑 User Profile: {profile_str}
🏷️ Quiz Tags: {tags_str}
📚 {topic_str}

📘 Contextual Information:
{context_str}

✍️ Instructions:
- Analyze the user's performance based on the context.
- Provide helpful feedback that highlights strengths, weaknesses, and learning style.
- Suggest **specific, actionable next steps** for improvement or further study.

📤 Output Format:
Respond in **pure JSON** using the exact structure below:

```json


{{
  "feedback_text": "<detailed written feedback here as plain text>",
  "follow_up_suggestion": "<follow-up suggestions or next steps as plain text>"
}}

Avoid using arrays or nested objects. Use clear, readable paragraphs for both fields.
"""

