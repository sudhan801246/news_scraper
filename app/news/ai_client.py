from groq import Groq
from django.conf import settings
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class GroqAIClient:
    """Groq AI client for news processing - Fast, free, and efficient"""
    
    def __init__(self):
        """Initialize the Groq client with API key from settings"""
        if not settings.GROQ_API_KEY:
            logger.warning("GROQ_API_KEY not found in settings")
            self.client = None
            return
            
        try:
            self.client = Groq(
                api_key=settings.GROQ_API_KEY,
            )
            self.model_name = "llama-3.1-8b-instant"  # Fast and free model
            logger.info("Groq AI client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {e}")
            self.client = None

    def _generate_content(self, prompt: str) -> str:
        """Generate content using Groq API"""
        if not self.client:
            return "AI service unavailable. Please check configuration."
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=self.model_name,
                temperature=0.7,
                max_tokens=1024,
                top_p=1,
                stream=False,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            if "429" in str(e) or "rate limit" in str(e).lower():
                return "AI service rate limit reached. Please wait a few minutes and try again."
            elif "401" in str(e) or "api key" in str(e).lower():
                return "AI service authentication failed. Please contact admin to check the API key configuration."
            else:
                return "Sorry, I couldn't generate a response at this time. Please try again later."

    def summarize_article(self, title: str, content: str) -> str:
        """Generate a concise summary of a news article"""
        prompt = f"""
        Summarize the following news article in 3-4 sentences, focusing on the key points:

        Title: {title}
        Content: {content}

        Provide a clear, concise summary:
        """
        
        return self._generate_content(prompt)

    def generate_insights(self, headlines: List[Dict[str, str]]) -> Dict[str, Any]:
        """Generate insights from a collection of news headlines"""
        if not headlines:
            return {
                "success": False,
                "error": "No headlines provided for analysis."
            }
        
        # Format headlines for analysis
        headlines_text = "\n".join([
            f"• {headline.get('title', 'No title')} (Source: {headline.get('source', 'Unknown')})"
            for headline in headlines
        ])
        
        prompt = f"""
        Analyze these news headlines and provide insights in this EXACT format:

        {headlines_text}

        IMPORTANT: Follow this exact structure:

        SECTION: Trending Topics
        1. [Topic Name]: [2-3 sentence explanation]
        2. [Topic Name]: [2-3 sentence explanation]  
        3. [Topic Name]: [2-3 sentence explanation]

        SECTION: News Patterns
        1. [Pattern Name]: [Explanation of what this indicates]
        2. [Pattern Name]: [Explanation of what this indicates]
        3. [Pattern Name]: [Explanation of what this indicates]

        SECTION: Notable Developments  
        1. [Development]: [Why it's significant]
        2. [Development]: [Why it's significant]

        SECTION: Overall Analysis
        [Write 2-3 paragraphs analyzing the overall news landscape]

        Do NOT use markdown, asterisks, or special formatting. Use the exact "SECTION:" and numbered format shown above.
        """
        
        try:
            insights = self._generate_content(prompt)
            return {
                "success": True,
                "insights": insights
            }
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return {
                "success": False,
                "error": "Unable to generate insights at this time."
            }

    def personalize_recommendations(self, user_interests: List[str], headlines: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Generate personalized news recommendations based on user interests"""
        if not headlines:
            return []
        
        if not user_interests:
            # Return top 5 articles if no interests specified
            return headlines[:5]
        
        interests_text = ", ".join(user_interests)
        headlines_text = "\n".join([
            f"{i+1}. {headline.get('title', 'No title')} (Source: {headline.get('source', 'Unknown')})"
            for i, headline in enumerate(headlines)
        ])
        
        prompt = f"""
        Given a user interested in: {interests_text}
        
        Rank these news headlines from most to least relevant to their interests:
        
        {headlines_text}
        
        Return only the numbers (1, 2, 3, etc.) of the top 5 most relevant articles in order of relevance.
        Just provide the numbers separated by commas, like: 1, 5, 8, 3, 12
        """
        
        try:
            response = self._generate_content(prompt)
            
            # Parse the response to get article indices
            recommended_indices = []
            for item in response.split(','):
                try:
                    index = int(item.strip()) - 1  # Convert to 0-based index
                    if 0 <= index < len(headlines):
                        recommended_indices.append(index)
                except ValueError:
                    continue
            
            # Return recommended headlines in order
            recommended_headlines = []
            for index in recommended_indices:
                if index < len(headlines):
                    recommended_headlines.append(headlines[index])
            
            # Fill remaining slots if needed
            while len(recommended_headlines) < 5 and len(recommended_headlines) < len(headlines):
                for headline in headlines:
                    if headline not in recommended_headlines:
                        recommended_headlines.append(headline)
                        if len(recommended_headlines) >= 5:
                            break
            
            return recommended_headlines[:5]
            
        except Exception as e:
            logger.error(f"Error generating personalized recommendations: {e}")
            # Return first 5 headlines as fallback
            return headlines[:5]

    def analyze_sentiment(self, headlines: List[Dict[str, str]]) -> Dict[str, Any]:
        """Analyze sentiment of news headlines"""
        if not headlines:
            return {"sentiment": "neutral", "analysis": "No headlines to analyze"}
        
        headlines_text = "\n".join([
            f"• {headline.get('title', 'No title')}"
            for headline in headlines[:10]  # Limit to 10 for analysis
        ])
        
        prompt = f"""
        Analyze the overall sentiment of these news headlines:
        
        {headlines_text}
        
        Provide:
        1. Overall sentiment (positive, negative, neutral, mixed)
        2. Brief explanation of the sentiment analysis
        3. Key themes that influence the sentiment
        
        Keep the response concise and informative.
        """
        
        try:
            analysis = self._generate_content(prompt)
            return {
                "success": True,
                "analysis": analysis
            }
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {
                "success": False,
                "error": "Unable to analyze sentiment at this time."
            }


# Global instance for easy access
groq_client = GroqAIClient()