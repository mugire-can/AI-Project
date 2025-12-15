# Claude AI Integration for Ultimate Racing Pro

## Setup Instructions

### 1. Get Your Claude API Key
1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Sign up or log in to your account
3. Navigate to API Keys section
4. Create a new API key

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Configure API Key
1. Copy `.env.example` to `.env`:
   ```powershell
   Copy-Item .env.example .env
   ```

2. Edit `.env` and add your API key:
   ```
   ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
   ```

### 4. Test AI Integration
```powershell
python ai_client.py
```

## Features

### 🤖 Intelligent AI Opponents
- Dynamic racing strategies based on race conditions
- Adaptive difficulty that responds to player performance
- Context-aware decision making (when to use nitro, overtaking, braking)

### 💬 Dynamic Commentary
- AI-generated racing commentary for exciting moments
- Contextual event descriptions
- Immersive racing experience

### 🏁 Procedural Track Generation
- AI-designed track layouts based on difficulty
- Varied segment types (straights, curves, chicanes, hairpins)
- Strategic powerup placement

### 📊 Adaptive Difficulty
- Analyzes player performance metrics
- Adjusts AI difficulty dynamically
- Balances challenge for optimal engagement

## Integration with Your Game

### Basic Example
```python
from ai_client import ClaudeAIClient

# Initialize AI client
ai_client = ClaudeAIClient()

# In your AI driver update loop
if ai_client.is_available():
    race_context = {
        'position': ai_car.position,
        'speed': ai_car.velocity,
        'nitro_percent': ai_car.nitro / ai_car.stats.nitro_capacity * 100,
        'weather': self.weather.value,
        # ... other context
    }
    
    strategy = ai_client.generate_ai_opponent_strategy(race_context)
    
    # Apply strategy to AI car
    if strategy['use_nitro'] and ai_car.nitro > 50:
        ai_car.nitro_active = True
```

### Advanced Integration Points

#### 1. Enhanced AI Driver (ultimate_racing_pro.py)
```python
class AIDriver:
    def __init__(self, car, difficulty=0.7, ai_client=None):
        self.ai_client = ai_client
        # ... existing code
    
    def update(self, track, player_y, dt):
        if self.ai_client and self.ai_client.is_available():
            # Use AI-powered strategy
            context = self._build_race_context(track, player_y)
            strategy = self.ai_client.generate_ai_opponent_strategy(context)
            self._apply_strategy(strategy)
        else:
            # Fallback to rule-based AI
            # ... existing code
```

#### 2. Dynamic Commentary System
```python
# When exciting events happen
if overtake_occurred:
    commentary = ai_client.generate_dynamic_track_commentary(
        event="overtake",
        context={"driver": driver_name, "position": new_position}
    )
    display_commentary(commentary)
```

#### 3. Adaptive Difficulty
```python
# At end of each race
player_stats = {
    'win_rate': calculate_win_rate(),
    'avg_position': get_avg_position(),
    'crashes': crash_count
}

adjustments = ai_client.adjust_difficulty(player_stats)
update_ai_difficulty(adjustments['ai_difficulty'])
```

## Model Selection

Available Claude models (set in `.env`):
- **claude-3-5-sonnet-20241022** (Default) - Best balance of intelligence and speed
- **claude-3-opus-20240229** - Highest intelligence, slower
- **claude-3-sonnet-20240229** - Good balance
- **claude-3-haiku-20240307** - Fastest, more economical

## API Usage & Costs

- Requests are made only when AI features are actively used
- Fallback to rule-based logic when API unavailable
- Consider implementing caching for repeated scenarios
- Monitor your usage at [Anthropic Console](https://console.anthropic.com/)

## Troubleshooting

### "API key not set" warning
- Ensure `.env` file exists in project root
- Verify `ANTHROPIC_API_KEY` is set correctly
- API key should start with `sk-ant-`

### Import errors
```powershell
pip install --upgrade anthropic python-dotenv
```

### AI features not working
- Check `ai_client.is_available()` returns `True`
- Verify internet connection
- Check API key validity at Anthropic Console

## Next Steps

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Configure API key**: Copy `.env.example` to `.env` and add your key
3. **Test integration**: Run `python ai_client.py`
4. **Integrate into game**: Import and use `ClaudeAIClient` in your game loop
5. **Customize**: Adjust prompts and features to match your game design

Happy racing with AI! 🏎️✨
