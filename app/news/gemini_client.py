import google.generativeai as genai
from django.conf import settings
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class GeminiClient:
    """Enhanced Gemini API client for news processing"""
    
    def __init__(self):
        """Initialize the Gemini client with API key from settings"""
        if not settings.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY not found in settings")
            self.client = None
            return
            
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.client = True
            logger.info("Gemini client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            self.client = None

    def _generate_content(self, prompt: str) -> str:
        """Generate content using Gemini API"""
        if not self.client:
            return "AI service unavailable. Please check configuration."
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            return "Sorry, I couldn't generate a response at this time."

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
        Analyze these current news headlines and provide insights:

        {headlines_text}

        Please provide:
        1. Top 3 trending topics or themes
        2. Key insights about current news patterns
        3. Notable developments worth attention
        4. Brief analysis of the overall news landscape

        Format your response clearly with headings and bullet points.
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
gemini_client = GeminiClient()