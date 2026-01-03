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

# Force agent mode - disable Groq-only
GROQ_ONLY = False
CREWAI_AVAILABLE = True

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
# Simple Agent using Groq directly
# ----------------------------
class FitnessAgent:
    def __init__(self):
        self.name = "Ash"
        self.role = "Personal Fitness Coach"
        
    def process_query(self, topic):
        """Process fitness query using agent-like behavior"""
        # Check if topic is fitness related
        fitness_keywords = ['gym', 'fitness', 'workout', 'exercise', 'muscle', 'strength', 'training', 
                           'bodybuilding', 'cardio', 'weight', 'protein', 'nutrition', 'diet', 
                           'supplements', 'health', 'athletic', 'sport', 'physical', 'body']
        
        topic_lower = topic.lower()
        is_fitness_related = any(keyword in topic_lower for keyword in fitness_keywords)
        
        if not is_fitness_related:
            return "Hey there! I'm Ash, your fitness agent! 💪 I specialize in workouts, nutrition, muscle building, and fitness goals. What fitness challenge can I help you with?"
        
        # Use Groq for response generation (silent processing)
        return self._generate_response(topic)
    
    def _generate_response(self, topic):
        """Generate response using Groq API"""
        agent_prompt = f"""
You are Ash, a personal fitness coach agent. You have these characteristics:
- Role: Personal Fitness Coach
- Goal: Provide helpful, concise fitness advice
- Personality: Friendly, enthusiastic, encouraging
- Response style: 2-3 sentences max, practical and motivating

User query: "{topic}"

As agent Ash, provide a brief, helpful response:
"""
        
        try:
            from groq import Groq
            client = Groq(api_key=os.getenv("GROQ_API_KEY"))

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": agent_prompt}],
                max_tokens=200,
                temperature=0.8
            )
            
            result = response.choices[0].message.content
            return result

        except Exception as e:
            print(f"❌ Agent error: {str(e)}")
            return "Hey! I'm having some technical issues right now, but I'm still here to help with your fitness goals! What would you like to work on? 💪"

# Create fitness agent instance
fitness_agent = FitnessAgent()

# ----------------------------
# Groq fallback helper
# ----------------------------
def _groq_fallback(topic: str):
    """Run direct Groq fallback analysis focused on gym and fitness topics only."""
    print("🔄 Using direct Groq fitness analysis (fallback)")
    
    # Check if topic is fitness/gym related
    fitness_keywords = ['gym', 'fitness', 'workout', 'exercise', 'muscle', 'strength', 'training', 
                       'bodybuilding', 'cardio', 'weight', 'protein', 'nutrition', 'diet', 
                       'supplements', 'health', 'athletic', 'sport', 'physical', 'body']
    
    topic_lower = topic.lower()
    is_fitness_related = any(keyword in topic_lower for keyword in fitness_keywords)
    
    if not is_fitness_related:
        return "Hey there! I'm your fitness buddy here to help you crush your goals! 💪 I love talking about workouts, nutrition, muscle building, and everything gym-related. What fitness challenge can I help you tackle today?"
    
    fallback_prompt = f"""
You are a friendly, enthusiastic fitness coach named Ash. Give SHORT but helpful responses (2-3 sentences max). Be conversational and encouraging.

User asked: "{topic}"

Provide a brief, practical response covering the most important points. Keep it concise but informative.
"""
    try:
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": fallback_prompt}],
            max_tokens=200,
            temperature=0.8
        )

        return response.choices[0].message.content

    except Exception as fallback_error:
        import traceback
        print("❌ Fallback failed:", str(fallback_error))
        traceback.print_exc()
        return "Oops! I'm having some technical hiccups right now. But hey, while I get back on track, why don't you tell me about your fitness goals? I'd love to help you plan your next workout! 🏋️‍♂️"

# ----------------------------
# Main Function
# ----------------------------
def get_news_analysis(topic):
    """Get fitness analysis using custom fitness agent"""
    print(f"💪 ASHFIT AI Agent Analysis")
    print("=" * 40)
    print(f"Topic: {topic}")
    print("=" * 40)

    # Use custom fitness agent
    try:
        result = fitness_agent.process_query(topic)
        print("\n💪 AGENT RESPONSE:")
        print("=" * 40)
        print(result)
        return result
    except Exception as e:
        print(f"❌ Agent Error: {str(e)}")
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

