import asyncio
from data_generation import generate_test_questions, run_generated_questions
from main import agent, model
from data_generation import setup_question_generator

async def main():
    # ✅ Must initialize question generator first
    setup_question_generator(model)

    # Generate new questions
    questions = await generate_test_questions(num_questions=15)

    # Test them through the agent
    if questions:
        await run_generated_questions(agent, questions, num_to_test=8)

if __name__ == "__main__":
    asyncio.run(main())