from openai import OpenAI
from app.core.config import settings


class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    def generate_search_query(self, user_input: str) -> str:
        """
        Convert free-text user input into an optimized Google/LinkedIn search query.

        Args:
            user_input: Natural language description of the search, e.g.,
                       "Find Ruby on Rails developers in Hyderabad"

        Returns:
            Optimized search query string for Google Custom Search targeting LinkedIn profiles.
        """
        system_prompt = """You are an expert at creating optimized search queries for finding professionals on LinkedIn via Google search.

Your task is to convert natural language descriptions into precise Google search queries that:
1. Target LinkedIn profiles using site:linkedin.com/in
2. Use Boolean operators (AND, OR) effectively
3. Include relevant job titles, skills, and variations
4. Include location variations (e.g., Bengaluru/Bangalore, Hyderabad/Hyd)
5. Optionally include phrases like "open to work" or "seeking opportunities" when relevant

Guidelines:
- Always start with site:linkedin.com/in
- Group related terms with parentheses
- Use OR for synonyms and variations
- Use quotes for exact phrases
- Include common title variations for the role
- Include location name variations

Output ONLY the search query string, nothing else. No explanations, no markdown formatting."""

        user_prompt = f"""Convert this into a LinkedIn search query:

"{user_input}"

Generate an optimized search query for finding these professionals on LinkedIn via Google."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=500,
        )

        generated_query = response.choices[0].message.content.strip()
        
        # Clean up the query - remove any markdown code blocks if present
        if generated_query.startswith("```"):
            lines = generated_query.split("\n")
            generated_query = "\n".join(
                line for line in lines if not line.startswith("```")
            ).strip()

        return generated_query

    def refine_search_query(self, original_query: str, refinement_instructions: str) -> str:
        """
        Refine an existing search query based on user feedback.

        Args:
            original_query: The current search query
            refinement_instructions: User's instructions for how to modify the query

        Returns:
            Refined search query string.
        """
        system_prompt = """You are an expert at refining Google search queries for finding professionals on LinkedIn.

You will be given an existing search query and instructions on how to modify it. Apply the modifications while maintaining proper search query syntax.

Output ONLY the refined search query string, nothing else."""

        user_prompt = f"""Original query:
{original_query}

Refinement instructions:
{refinement_instructions}

Generate the refined search query."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=500,
        )

        refined_query = response.choices[0].message.content.strip()

        if refined_query.startswith("```"):
            lines = refined_query.split("\n")
            refined_query = "\n".join(
                line for line in lines if not line.startswith("```")
            ).strip()

        return refined_query


# Singleton instance for easy import
openai_service = OpenAIService()
