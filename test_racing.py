import unittest
import pygame
from ultimate_racing_pro import UltimateRacingGame, GameMode, Colors

class TestUltimateRacing(unittest.TestCase):
    def setUp(self):
        """Initialize before each test"""
        pygame.init()
        self.game = UltimateRacingGame(windowed=True)
    
    def tearDown(self):
        """Cleanup after each test"""
        pygame.quit()
    
    def test_game_initialization(self):
        """Test basic game initialization"""
        self.assertEqual(self.game.mode, GameMode.MENU)
        self.assertEqual(self.game.weather.value, "clear")
        self.assertEqual(len(self.game.car_catalog), 6)
        self.assertEqual(self.game.player_money, 10000)
    
    def test_game_update_cycle(self):
        """Test one game update cycle"""
        self.game.dt = 1/60  # Simulate 60 FPS
        self.game.update()
        self.assertIsNotNone(self.game.screen)
        self.assertTrue(pygame.get_init())
    
    def test_car_movement(self):
        """Test basic car movement physics"""
        initial_x = self.game.player.x
        initial_y = self.game.player.y
        
        # Simulate forward movement
        keys = {pygame.K_UP: True}
        self.game.player.update_physics(1/60, keys)
        
        # Car should have moved
        self.assertNotEqual(self.game.player.y, initial_y)

if __name__ == '__main__':
    unittest.main()