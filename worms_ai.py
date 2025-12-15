"""
Worms Rumble - Advanced AI System
Intelligent bot opponents with difficulty levels

Features:
- Multiple difficulty levels (Easy, Normal, Hard, Expert)
- Strategic target selection
- Trajectory calculation
- Weapon selection strategy
- Terrain analysis
- Risk assessment
- Adaptive learning
"""

import math
import random
from enum import Enum
from typing import Optional, List, Tuple

class AIStrategy(Enum):
    """AI behavior strategies"""
    AGGRESSIVE = "aggressive"  # High damage, risky
    DEFENSIVE = "defensive"    # Self-preservation
    TACTICAL = "tactical"      # Objective-focused
    SUPPORT = "support"        # Team-focused

class AIDifficulty(Enum):
    """AI difficulty levels with skill ratings"""
    EASY = 0.3
    NORMAL = 0.6
    HARD = 0.9
    EXPERT = 1.0

class TargetAssessment:
    """Assessment of potential targets"""
    def __init__(self, worm, distance, health_ratio, visibility, threat_level):
        self.worm = worm
        self.distance = distance
        self.health_ratio = health_ratio  # 0-1 (lower = weaker)
        self.visibility = visibility  # 0-1 (1 = fully visible)
        self.threat_level = threat_level  # 0-1 (higher = more dangerous)
        self.priority_score = self._calculate_priority()
    
    def _calculate_priority(self):
        """Calculate target priority (higher = better target)"""
        # Prioritize weak enemies that are visible
        weak_multiplier = (1 - self.health_ratio) * 0.5
        visible_multiplier = self.visibility * 0.3
        distance_multiplier = max(0, 1 - (self.distance / 1000)) * 0.2
        
        priority = weak_multiplier + visible_multiplier + distance_multiplier
        
        return priority

class AIBot:
    """Advanced AI opponent"""
    
    def __init__(self, difficulty: AIDifficulty = AIDifficulty.NORMAL):
        self.difficulty = difficulty
        self.skill_level = difficulty.value
        self.strategy = AIStrategy.TACTICAL
        self.memory = {}  # Store environment data
        self.last_known_targets = {}
        self.turn_count = 0
        self.success_rate = 0.5
    
    def decide_action(self, worm, game_state) -> dict:
        """Decide what action to take"""
        self.turn_count += 1
        
        # Analyze situation
        targets = self._find_targets(worm, game_state)
        best_target = self._select_target(targets)
        
        if not best_target:
            return self._explore_move(worm, game_state)
        
        # Calculate shot
        action = self._calculate_optimal_shot(worm, best_target, game_state)
        
        # Modify based on difficulty
        if self.difficulty == AIDifficulty.EASY:
            action = self._add_easy_errors(action)
        elif self.difficulty == AIDifficulty.NORMAL:
            action = self._add_normal_errors(action)
        elif self.difficulty == AIDifficulty.HARD:
            action = self._add_hard_refinements(action)
        # EXPERT: no modifications
        
        return action
    
    def _find_targets(self, worm, game_state) -> List[TargetAssessment]:
        """Find all potential targets"""
        targets = []
        
        for team in game_state.teams:
            if team.team_id == worm.team_id:
                continue  # Skip own team
            
            for enemy in team.get_alive_worms():
                distance = math.sqrt((enemy.x - worm.x)**2 + (enemy.y - worm.y)**2)
                
                # Calculate visibility (terrain obstruction)
                visibility = self._check_visibility(worm, enemy, game_state.terrain)
                
                # Assess threat
                threat = self._assess_threat(worm, enemy)
                
                # Health ratio (0 = dead, 1 = full)
                health_ratio = 1 - (enemy.health / enemy.max_health)
                
                assessment = TargetAssessment(
                    worm=enemy,
                    distance=distance,
                    health_ratio=health_ratio,
                    visibility=visibility,
                    threat_level=threat
                )
                
                targets.append(assessment)
        
        return sorted(targets, key=lambda t: t.priority_score, reverse=True)
    
    def _select_target(self, targets: List[TargetAssessment]) -> Optional[TargetAssessment]:
        """Select best target based on difficulty"""
        if not targets:
            return None
        
        if self.difficulty == AIDifficulty.EASY:
            # Random target
            return random.choice(targets)
        elif self.difficulty == AIDifficulty.NORMAL:
            # Good target with some randomness
            if random.random() < 0.7:
                return targets[0]
            else:
                return random.choice(targets[:len(targets)//2])
        elif self.difficulty in [AIDifficulty.HARD, AIDifficulty.EXPERT]:
            # Best target
            return targets[0]
    
    def _check_visibility(self, worm, target, terrain) -> float:
        """Check line of sight to target"""
        # Simple line of sight check
        steps = 20
        for i in range(1, steps):
            t = i / steps
            check_x = worm.x + (target.x - worm.x) * t
            check_y = worm.y + (target.y - worm.y) * t
            
            if terrain.is_solid(check_x, check_y):
                return i / steps  # Partially visible
        
        return 1.0  # Fully visible
    
    def _assess_threat(self, worm, enemy) -> float:
        """Assess how dangerous an enemy is"""
        threat = 0.0
        
        # Higher health = more dangerous
        threat += (enemy.health / enemy.max_health) * 0.3
        
        # More ammo = more dangerous
        total_ammo = sum(enemy.ammo.values())
        threat += (total_ammo / 20) * 0.3
        
        # Closer proximity = more dangerous
        distance = math.sqrt((enemy.x - worm.x)**2 + (enemy.y - worm.y)**2)
        threat += max(0, 1 - (distance / 500)) * 0.4
        
        return min(1.0, threat)
    
    def _calculate_optimal_shot(self, worm, target_assessment, game_state) -> dict:
        """Calculate angle and power for optimal shot"""
        target = target_assessment.worm
        
        # Calculate angle to target
        dx = target.x - worm.x
        dy = target.y - worm.y
        
        # Add wind compensation
        wind_compensation = game_state.wind * 2
        dx += wind_compensation
        
        angle = math.degrees(math.atan2(-dy, dx))
        
        # Normalize angle
        if angle < 0:
            angle = 180 + angle
        
        angle = max(0, min(90, angle))
        
        # Estimate required power based on distance
        distance = math.sqrt(dx**2 + dy**2)
        power = min(100, int(distance / 5))
        
        # Add aiming error based on difficulty
        if self.difficulty == AIDifficulty.EASY:
            angle += random.uniform(-15, 15)
            power += random.uniform(-20, 20)
        elif self.difficulty == AIDifficulty.NORMAL:
            angle += random.uniform(-8, 8)
            power += random.uniform(-10, 10)
        elif self.difficulty == AIDifficulty.HARD:
            angle += random.uniform(-3, 3)
            power += random.uniform(-5, 5)
        # EXPERT: no error
        
        return {
            "action": "fire",
            "angle": angle,
            "power": power,
            "weapon": worm.current_weapon,
            "should_switch_weapon": self._should_switch_weapon(worm, target_assessment)
        }
    
    def _should_switch_weapon(self, worm, target_assessment) -> bool:
        """Determine if should switch weapon"""
        distance = target_assessment.distance
        
        # Switch based on distance
        if distance < 200:
            return worm.current_weapon.name != "Shotgun"
        elif distance < 500:
            return worm.current_weapon.name not in ["Rocket", "Grenade"]
        else:
            return worm.current_weapon.name == "Pistol"
    
    def _explore_move(self, worm, game_state) -> dict:
        """Move to explore if no targets"""
        direction = random.choice([-1, 1])
        
        return {
            "action": "move",
            "direction": direction,
            "distance": random.randint(20, 100)
        }
    
    def _add_easy_errors(self, action: dict) -> dict:
        """Add errors for easy difficulty"""
        if action.get("action") == "fire":
            action["angle"] = max(0, min(90, action["angle"] + random.uniform(-20, 20)))
            action["power"] = max(10, min(100, action["power"] + random.uniform(-30, 30)))
        
        return action
    
    def _add_normal_errors(self, action: dict) -> dict:
        """Add errors for normal difficulty"""
        if action.get("action") == "fire":
            action["angle"] = max(0, min(90, action["angle"] + random.uniform(-10, 10)))
            action["power"] = max(10, min(100, action["power"] + random.uniform(-15, 15)))
        
        return action
    
    def _add_hard_refinements(self, action: dict) -> dict:
        """Add refinements for hard difficulty"""
        if action.get("action") == "fire":
            # Lead target prediction
            action["angle"] = max(0, min(90, action["angle"] + random.uniform(-5, 5)))
            action["power"] = max(10, min(100, action["power"] + random.uniform(-8, 8)))
        
        return action
    
    def execute_action(self, worm, action: dict):
        """Execute action on the worm"""
        if action.get("should_switch_weapon"):
            # Switch weapon logic here
            pass
        
        if action.get("action") == "fire":
            worm.angle = action["angle"]
            worm.power = action["power"]
            return worm.fire()
        
        elif action.get("action") == "move":
            direction = action["direction"]
            distance = action["distance"]
            
            if direction > 0:
                worm.vx = 3
            else:
                worm.vx = -3
        
        return None

class TeamAI:
    """Manages AI for entire team"""
    
    def __init__(self, team_id: int, difficulty: AIDifficulty):
        self.team_id = team_id
        self.difficulty = difficulty
        self.bots = {}  # worm_id -> AIBot
        self.team_strategy = AIStrategy.TACTICAL
    
    def add_bot(self, worm_id: int):
        """Add AI bot for worm"""
        self.bots[worm_id] = AIBot(self.difficulty)
    
    def decide_team_strategy(self, game_state):
        """Decide overall team strategy based on game state"""
        team = game_state.teams[self.team_id]
        alive_worms = team.get_alive_worms()
        
        if len(alive_worms) == 1:
            self.team_strategy = AIStrategy.AGGRESSIVE
        else:
            self.team_strategy = AIStrategy.TACTICAL
    
    def get_action(self, worm, game_state) -> dict:
        """Get action for worm"""
        if worm.worm_id not in self.bots:
            self.add_bot(worm.worm_id)
        
        bot = self.bots[worm.worm_id]
        return bot.decide_action(worm, game_state)

# Example usage
"""
# Create AI for team
ai_team = TeamAI(team_id=1, difficulty=AIDifficulty.HARD)

# During game turn
if worm.is_ai:
    action = ai_team.get_action(worm, game_state)
    projectile = ai_team.bots[worm.worm_id].execute_action(worm, action)
    if projectile:
        game.projectiles.append(projectile)
"""
