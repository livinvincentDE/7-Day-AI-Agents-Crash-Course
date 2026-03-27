import asyncio
import json
import random
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel
from pydantic_ai import Agent

from data import load_data

# ========================= Schema =========================
class QuestionsList(BaseModel):
    questions: list[str]


# ========================= Prompt =========================
question_generation_prompt = """
You are helping create realistic test questions for a course FAQ assistant.

Based on the provided FAQ content, generate **one natural question** that a student might actually ask.

Make questions sound real and varied:
- Some short and casual ("How do I join late?")
- Some more detailed ("Can I still get a certificate if I join after week 3?")
- Mix of technical and general course questions

Generate exactly ONE question per FAQ record provided.
Return only the list of questions.
"""

# Global variable
question_generator = None


def setup_question_generator(model):
    """Initialize the question generator. Call this from main.py"""
    global question_generator
    question_generator = Agent(
        model=model,
        instructions=question_generation_prompt,
        output_type=QuestionsList
    )
    print("✅ Question generator agent is ready")
    return question_generator


async def generate_test_questions(num_questions: int = 10):
    """Generate realistic test questions from your FAQ data"""
    if question_generator is None:
        print("❌ Question generator not initialized. Call setup_question_generator(model) first!")
        return []

    print(f"🔄 Generating {num_questions} test questions from FAQ data...")

    documents = load_data()

    # Sample documents
    if len(documents) > num_questions:
        sample_docs = random.sample(documents, num_questions)
    else:
        sample_docs = documents

    # Prepare input
    doc_texts = [f"Q: {doc.get('question', '')}\nA: {doc.get('content', '')}" 
                 for doc in sample_docs]

    prompt_input = "\n\n---\n\n".join(doc_texts)

    try:
        result = await question_generator.run(prompt_input)
        questions = result.output.questions

        print(f"\n✅ Successfully generated {len(questions)} questions:\n")
        for i, q in enumerate(questions, 1):
            print(f"{i:2d}. {q}")

        # Save to file
        output_file = Path("generated_questions.json")
        output_data = {
            "generated_at": datetime.now().isoformat(),
            "count": len(questions),
            "questions": questions
        }
        output_file.write_text(json.dumps(output_data, indent=2), encoding="utf-8")

        print(f"\n💾 Questions saved to: generated_questions.json")
        return questions

    except Exception as e:
        print(f"❌ Error during question generation: {e}")
        return []


async def run_generated_questions(agent, questions, num_to_test=5):
    """Run generated questions through your main agent and log them"""
    from evaluation import log_interaction_to_file

    print(f"\n🚀 Testing {min(num_to_test, len(questions))} generated questions...\n")

    for i, q in enumerate(questions[:num_to_test], 1):
        print(f"Q{i}: {q}")
        try:
            from main import build_context   # Import inside function to avoid circular import

            context = build_context(q)
            full_prompt = f"""Context:
{context}

Question: {q}
"""

            result = await agent.run(full_prompt)
            answer = result.output
            print(f"Agent: {answer[:250]}{'...' if len(answer) > 250 else ''}\n")

            # Log as ai-generated
            log_path = log_interaction_to_file(agent, result.all_messages(), source="ai-generated")
            if log_path:
                print(f"   📝 Logged as ai-generated → {log_path.name}")

        except Exception as e:
            print(f"   Error testing question: {e}")
        print("-" * 80)