# crewai_news_agent.py

"""
News Agent using CrewAI with Groq API
Optimized to work reliably with Groq
"""

import requests
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Make CrewAI optional so we can run Groq-only
try:
    from crewai import Agent, Crew, Task, LLM  # type: ignore
    from crewai.tools import BaseTool  # type: ignore
    CREWAI_AVAILABLE = True
except Exception:
    CREWAI_AVAILABLE = False
    # Minimal BaseTool fallback so NewsTool can be defined without crewai
    class BaseTool:
        def __init__(self, *args, **kwargs):
            pass

# Respect an environment override to force Groq-only mode
GROQ_ONLY = os.getenv("GROQ_ONLY", "true").lower() in ("1", "true", "yes")
if GROQ_ONLY:
    CREWAI_AVAILABLE = False

# ----------------------------
# News Tool
# ----------------------------
class NewsTool(BaseTool):
    name: str = "NewsTool"
    description: str = "Get current news and information about any topic"
    
    def _run(self, query: str) -> str:
        """Get news using web search"""
        try:
            # Use a simple search approach
            tavily_key = os.getenv("TAVILY_API_KEY")
            url = f"https://api.tavily.com/search?q={query}&apiKey={tavily_key}"
            
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            results = r.json()
            
            # Extract useful information
            if results and "results" in results and results["results"]:
                top_result = results["results"][0]
                return (
                    f"Title: {top_result.get('title', 'No title')}\n"
                    f"Summary: {top_result.get('content', 'No content')[:300]}\n"
                    f"Source: {top_result.get('url', 'No source')}\n"
                    f"Published: {top_result.get('published_date', 'Unknown')}\n"
                )
            else:
                return "No current news found on this topic."
                
        except Exception as e:
            return f"Error getting news: {str(e)}"

# ----------------------------
# LLM Configuration (use OpenAI to avoid google-genai extras)
# ----------------------------
# Use OpenAI provider only when crewai is available and OPENAI_API_KEY is present
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_llm = None
if CREWAI_AVAILABLE and openai_api_key:
    try:
        openai_llm = LLM(
            model="gpt-4o",
            api_key=openai_api_key,
            provider="openai"
        )
    except Exception as e:
        print(f"❌ Failed to initialize OpenAI LLM: {e}")
        openai_llm = None
else:
    if not CREWAI_AVAILABLE:
        print("⚠️ CrewAI not available; LLM disabled.")
    else:
        print("⚠️ OPENAI_API_KEY not set; LLM disabled. Set it in your .env or environment to enable LLM features.")
    openai_llm = None

# ----------------------------
# News Agents (create only if crewai is available and not forcing Groq-only)
# ----------------------------
news_researcher = None
news_analyst = None
news_crew = None
research_task = None
analysis_task = None

if CREWAI_AVAILABLE and not GROQ_ONLY:
    # Create agents with clear roles and minimal complexity
    news_researcher = Agent(
        name="NewsResearcher",
        role="News Research Specialist",
        goal="Find current news and relevant information",
        backstory="You are an expert researcher who quickly finds accurate and current news information.",
        llm=openai_llm if openai_llm is not None else None,
        tools=[NewsTool()],
        verbose=False,
        allow_delegation=False
    )

    news_analyst = Agent(
        name="NewsAnalyst",
        role="News Analyst",
        goal="Analyze news and provide insights",
        backstory="You are a skilled analyst who can identify key trends and provide meaningful insights from news.",
        llm=openai_llm if openai_llm is not None else None,
        verbose=False,
        allow_delegation=False
    )

    # Create tasks and crew
    research_task = Task(
        description="Search for and gather news about: {topic}",
        expected_output="Current news articles and information about the topic",
        agent=news_researcher,
        async_execution=False
    )

    analysis_task = Task(
        description="Analyze the gathered news and provide insights about: {topic}",
        expected_output="Comprehensive analysis with trends and implications",
        agent=news_analyst,
        async_execution=False
    )

    news_crew = Crew(
        agents=[news_researcher, news_analyst],
        tasks=[research_task, analysis_task],
        verbose=True,
        process="sequential"
    )

# ----------------------------
# Groq fallback helper
# ----------------------------
def _groq_fallback(topic: str):
    """Run direct Groq fallback analysis. Returns string or None.

    Improved error handling: on exception print HTTP status and response body when
    available so a 404 can be diagnosed, and return a helpful message.
    """
    print("🔄 Using direct Groq analysis (fallback)")
    fallback_prompt = f"""
Please provide a comprehensive news analysis about "{topic}".
Include:
1. Recent developments and key events
2. Important context and background
3. Expert analysis and insights
4. Potential implications or impact
5. Related trends and future outlook
"""
    try:
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": fallback_prompt}],
            max_tokens=800,
            temperature=0.7
        )

        return response.choices[0].message.content

    except Exception as fallback_error:
        # Print traceback for debugging
        import traceback
        print("❌ Fallback failed:", str(fallback_error))
        traceback.print_exc()

        # If the SDK attached an HTTP response, try to show status and body
        resp = getattr(fallback_error, "response", None)
        try:
            if resp is not None:
                # httpx.Response or requests.Response
                status = getattr(resp, "status_code", None) or getattr(resp, "status", None)
                body = None
                try:
                    body = resp.text
                except Exception:
                    try:
                        body = resp.content.decode()
                    except Exception:
                        body = repr(resp)
                print(f"HTTP response status: {status}")
                print("HTTP response body:")
                print(body)
        except Exception:
            pass

        print("Please verify your GROQ_API_KEY, the model name, and network access. If the model name is incorrect the API may return 404.")
        return None

# ----------------------------
# Main Function
# ----------------------------
def get_news_analysis(topic):
    """Get news analysis using CrewAI"""
    print(f"📰 CrewAI News Analysis")
    print("=" * 40)
    print(f"Topic: {topic}")
    print("=" * 40)

    # If LLM not configured, use Groq fallback directly
    if openai_llm is None:
        print("⚠️ LLM not configured — skipping CrewAI execution.")
        result = _groq_fallback(topic)
        if result:
            print("\n📊 GROQ FALLBACK ANALYSIS:")
            print("=" * 40)
            print(result)
        return result

    try:
        # Run the crew with proper error handling
        result = news_crew.kickoff(inputs={"topic": topic})

        print("\n📊 CREWAI ANALYSIS:")
        print("=" * 40)
        print(result)

        return result

    except Exception as e:
        print(f"❌ CrewAI Error: {str(e)}")
        # Use Groq fallback if Crew fails
        return _groq_fallback(topic)

# ----------------------------
# Interactive Mode
# ----------------------------
def main():
    """Main interactive function"""
    print("🤖 CREWAI NEWS AGENT")
    print("=" * 30)
    print("Powered by Groq + CrewAI")
    print("=" * 30)
    print("👥 Researcher + Analyst Team")
    print("⚡ Optimized for reliability")
    print("=" * 30)
    
    # Sample topics
    sample_topics = [
        "artificial intelligence news",
        "climate change updates", 
        "technology trends",
        "global economy"
    ]
    
    print("\n📋 Sample topics:")
    for i, topic in enumerate(sample_topics, 1):
        print(f"{i}. {topic}")
    
    while True:
        user_input = input("\nEnter news topic (or 'quit' to exit, or number for sample): ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("👋 Thanks for using the CrewAI News Agent!")
            break
        
        # Handle sample topic selection
        try:
            topic_num = int(user_input)
            if 1 <= topic_num <= len(sample_topics):
                topic = sample_topics[topic_num - 1]
            else:
                print(f"Please enter a number 1-{len(sample_topics)} or type a topic")
                continue
        except ValueError:
            topic = user_input
        
        if topic:
            result = get_news_analysis(topic)
            if result:
                print("\n✅ CrewAI analysis complete!")
            print("\n" + "=" * 60 + "\n")

if __name__ == "__main__":
    main()

