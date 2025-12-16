"""
AI Client for Ultimate Racing Pro
Integrates Claude API for intelligent game features
"""

import os
from typing import Optional, Dict, List
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ClaudeAIClient:
    """Client for interacting with Claude AI API"""
    
    def __init__(self):
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key or api_key == 'your_api_key_here':
            print("Warning: ANTHROPIC_API_KEY not set. AI features will be disabled.")
            print("Get your API key from: https://console.anthropic.com/")
            self.client = None
        else:
            self.client = Anthropic(api_key=api_key)
        
        self.model = os.getenv('CLAUDE_MODEL', 'claude-3-5-sonnet-20241022')
        self.max_tokens = 1024
    
    def is_available(self) -> bool:
        """Check if AI client is properly configured"""
        return self.client is not None
    
    def generate_ai_opponent_strategy(self, race_context: Dict) -> Dict:
        """
        Generate intelligent racing strategy for AI opponents
        
        Args:
            race_context: Dictionary containing race state (position, speed, track conditions, etc.)
        
        Returns:
            Strategy dictionary with decisions (use_nitro, target_speed, overtake_side, etc.)
        """
        if not self.is_available():
            return self._fallback_strategy()
        
        prompt = f"""You are an expert racing AI controller. Given the following race context, provide optimal racing decisions.

Race Context:
- Current Position: {race_context.get('position', 'unknown')}
- Current Speed: {race_context.get('speed', 0)} km/h
- Distance to Leader: {race_context.get('distance_to_leader', 0)}m
- Nitro Available: {race_context.get('nitro_percent', 0)}%
- Track Condition: {race_context.get('track_condition', 'normal')}
- Weather: {race_context.get('weather', 'clear')}
- Upcoming Curve Sharpness: {race_context.get('curve_ahead', 0)}

Provide racing decisions as JSON:
{{
    "use_nitro": true/false,
    "target_speed_percent": 0-100,
    "braking_intensity": 0-100,
    "overtake_side": "left"/"right"/"none",
    "aggression_level": 0-100,
    "reasoning": "brief explanation"
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Parse response (you may need to add JSON extraction logic)
            strategy_text = response.content[0].text
            # Simple parsing - in production, use proper JSON extraction
            return self._parse_strategy_response(strategy_text)
            
        except Exception as e:
            print(f"AI Strategy generation error: {e}")
            return self._fallback_strategy()
    
    def generate_dynamic_track_commentary(self, event: str, context: Dict) -> str:
        """
        Generate dynamic racing commentary for events
        
        Args:
            event: Type of event (overtake, crash, drift, powerup, etc.)
            context: Event context details
        
        Returns:
            Commentary string
        """
        if not self.is_available():
            return self._fallback_commentary(event)
        
        prompt = f"""You are a professional racing commentator. Create exciting, brief commentary for this event:

Event: {event}
Context: {context}

Provide a single exciting commentary line (max 15 words) that captures the moment."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=100,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            print(f"Commentary generation error: {e}")
            return self._fallback_commentary(event)
    
    def generate_procedural_track_design(self, difficulty: float, length: int) -> List[Dict]:
        """
        Generate procedural track design using AI
        
        Args:
            difficulty: Track difficulty (0.0-1.0)
            length: Desired track length
        
        Returns:
            List of track segment dictionaries
        """
        if not self.is_available():
            return []
        
        prompt = f"""Design an exciting racing track with these parameters:
- Difficulty: {difficulty}/1.0
- Length: {length} meters

Generate 10 diverse track segments with varying curves, elevations, and features.
Provide as JSON array with format:
[
    {{"type": "straight/curve/chicane/hairpin", "length": meters, "curve_intensity": 0-100, "elevation_change": meters, "powerup_placement": true/false}},
    ...
]"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Parse and return track segments
            return self._parse_track_design(response.content[0].text)
            
        except Exception as e:
            print(f"Track design generation error: {e}")
            return []
    
    def adjust_difficulty(self, player_performance: Dict) -> Dict:
        """
        Dynamically adjust game difficulty based on player performance
        
        Args:
            player_performance: Dictionary with player stats (win_rate, avg_position, etc.)
        
        Returns:
            Difficulty adjustment recommendations
        """
        if not self.is_available():
            return {"ai_difficulty": 0.7, "powerup_frequency": 0.5}
        
        prompt = f"""Analyze player performance and suggest difficulty adjustments:

Player Performance:
- Win Rate: {player_performance.get('win_rate', 0)}%
- Average Position: {player_performance.get('avg_position', 4)}/8
- Average Lap Time: {player_performance.get('avg_lap_time', 60)}s
- Crashes per Race: {player_performance.get('crashes', 0)}
- Nitro Usage: {player_performance.get('nitro_usage', 50)}%

Provide difficulty adjustments as JSON:
{{
    "ai_difficulty": 0.0-1.0,
    "powerup_frequency": 0.0-1.0,
    "nitro_regeneration_rate": 0.0-1.0,
    "traffic_density": 0.0-1.0,
    "explanation": "brief reasoning"
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return self._parse_difficulty_adjustment(response.content[0].text)
            
        except Exception as e:
            print(f"Difficulty adjustment error: {e}")
            return {"ai_difficulty": 0.7, "powerup_frequency": 0.5}
    
    # Fallback methods for when AI is unavailable
    
    def _fallback_strategy(self) -> Dict:
        """Simple rule-based strategy when AI unavailable"""
        import random
        return {
            "use_nitro": random.random() > 0.7,
            "target_speed_percent": random.randint(70, 100),
            "braking_intensity": random.randint(0, 30),
            "overtake_side": random.choice(["left", "right", "none"]),
            "aggression_level": random.randint(50, 80),
            "reasoning": "Fallback strategy"
        }
    
    def _fallback_commentary(self, event: str) -> str:
        """Simple commentary when AI unavailable"""
        commentaries = {
            "overtake": "Incredible overtake!",
            "crash": "Oh no! That's going to hurt!",
            "drift": "Perfect drift around that corner!",
            "powerup": "Power-up collected!",
            "nitro": "Nitro boost activated!",
        }
        return commentaries.get(event, "Amazing racing action!")
    
    def _parse_strategy_response(self, text: str) -> Dict:
        """Parse AI response into strategy dict"""
        # Simple JSON extraction - improve for production
        import json
        import re
        
        # Try to find JSON in response
        json_match = re.search(r'\{[^}]+\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except:
                pass
        
        return self._fallback_strategy()
    
    def _parse_track_design(self, text: str) -> List[Dict]:
        """Parse track design response"""
        import json
        import re
        
        # Try to find JSON array in response
        json_match = re.search(r'\[[^\]]+\]', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except:
                pass
        
        return []
    
    def _parse_difficulty_adjustment(self, text: str) -> Dict:
        """Parse difficulty adjustment response"""
        import json
        import re
        
        json_match = re.search(r'\{[^}]+\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except:
                pass
        
        return {"ai_difficulty": 0.7, "powerup_frequency": 0.5}


# Example usage
if __name__ == "__main__":
    client = ClaudeAIClient()
    
    if client.is_available():
        print("✓ Claude AI Client initialized successfully!")
        print(f"Using model: {client.model}")
        
        # Test strategy generation
        race_context = {
            'position': 3,
            'speed': 180,
            'distance_to_leader': 150,
            'nitro_percent': 75,
            'track_condition': 'wet',
            'weather': 'rain',
            'curve_ahead': 45
        }
        
        strategy = client.generate_ai_opponent_strategy(race_context)
        print("\nGenerated Strategy:")
        print(strategy)
    else:
        print("✗ Claude AI Client not configured.")
        print("Set ANTHROPIC_API_KEY in .env file to enable AI features.")
