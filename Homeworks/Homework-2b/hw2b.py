from openai import AsyncOpenAI
import asyncio

from chroma_demo import ingest_folder, query_whole_documents

client = AsyncOpenAI()

async def get_answers(question: str):
    relevant_talks = query_whole_documents(
        chroma_dir="./chroma_db",
        collection="conference_talks",
        query=question,
        n_results=3,
    )
    
    context = "\n---\n".join(relevant_talks)
    
    system_prompt = f"""
    You are a helpful assistant that answers spiriual questions based on talks from the past general conference from the church of Jesus Christ of Latter-day Saints. Use the following relevant talks to answer the question. If you don't know the answer, say you don't know. Always use all relevant talks to answer the question.
    
    In your answer, cite the talks you used by including the title and speaker of the talk in parentheses after the relevant information. For example, if you used a talk called "The Power of Faith" by John Doe, you would include "(The Power of Faith by John Doe)" in your answer after any information that came from that talk.
    
    Relevant talks:
    {context}
    """
    
    response = await client.responses.create(
        model="gpt-5-nano",
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
        reasoning={"effort": "low"},
    )
    
    return response.output_text

async def main():
    
    ingest_folder(
        persist_dir="./chroma_db",
        chroma_collection_name="conference_talks",
        folder= "./conference_talks",
    )
    
    user_question = input("Ask a spiritual question: ")
    answer = await get_answers(user_question)
    print(f"Answer: {answer}")
    
    
if __name__ == ("__main__"):
    asyncio.run(main())