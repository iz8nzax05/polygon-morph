"""
Sine Wave Resistance Field
Creates the "terrain" that guides polygon morphing
"""

import pygame
import math
import numpy as np


class WaveField:
    """Generates and visualizes sine wave resistance fields"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        # Wave parameters
        self.frequency = 3.0  # How many waves across the space
        self.amplitude = 0.5  # How strong the resistance variation is
        self.time = 0.0       # For animated waves (optional)
        
        # Pre-calculate field for performance
        self.field = None
        self.surface = None
        self.needs_update = True
        
    def get_resistance(self, x, y):
        """
        Get resistance value at position (x, y)
        Returns value between 0.0 (low resistance) and 1.0 (high resistance)
        ANIMATED - waves PULSE and FLOW across the screen!
        """
        # Normalize coordinates to 0-1 range
        nx = x / self.width
        ny = y / self.height
        
        # FLOWING WAVES - move diagonally across screen
        # Wave 1: Flows from top-left to bottom-right
        wave1 = math.sin((nx + ny) * self.frequency * math.pi + self.time * 2)
        
        # Wave 2: Flows from top-right to bottom-left
        wave2 = math.sin((nx - ny) * self.frequency * math.pi + self.time * 1.5)
        
        # Wave 3: Vertical pulse
        wave3 = math.sin(ny * self.frequency * 2 * math.pi + self.time * 3)
        
        # Combine all waves for complex flowing pattern
        combined = (wave1 + wave2 + wave3) / 3.0
        
        # Apply amplitude and normalize to 0-1 range
        resistance = 0.5 + combined * self.amplitude
        
        # Clamp to 0-1
        return max(0.0, min(1.0, resistance))
    
    def get_wave_force(self, x, y):
        """
        Get the DIRECTIONAL FORCE from the wave at position (x, y)
        Returns (force_x, force_y) - the push/pull from the wave motion
        """
        # Sample resistance at nearby points to get gradient (wave direction)
        sample_dist = 5.0
        
        r_center = self.get_resistance(x, y)
        r_right = self.get_resistance(x + sample_dist, y)
        r_left = self.get_resistance(x - sample_dist, y)
        r_down = self.get_resistance(x, y + sample_dist)
        r_up = self.get_resistance(x, y - sample_dist)
        
        # Calculate gradient (direction of steepest change)
        gradient_x = (r_right - r_left) / (2 * sample_dist)
        gradient_y = (r_down - r_up) / (2 * sample_dist)
        
        # Force pushes DOWN the gradient (from high to low resistance)
        force_x = -gradient_x * 20.0  # Scale factor
        force_y = -gradient_y * 20.0
        
        return (force_x, force_y)
    
    def update(self, dt):
        """Update the wave animation"""
        self.time += dt * 2.0  # Speed of wave animation
        self.needs_update = True  # Mark field for redraw
    
    def generate_field(self):
        """Pre-generate the entire resistance field for visualization"""
        # Create field array
        step = 4  # Sample every 4 pixels for performance
        field_w = self.width // step
        field_h = self.height // step
        
        self.field = np.zeros((field_h, field_w))
        
        for fy in range(field_h):
            for fx in range(field_w):
                x = fx * step
                y = fy * step
                self.field[fy, fx] = self.get_resistance(x, y)
        
        self.needs_update = False
    
    def draw(self, screen):
        """Draw the wave field as a PULSING, FLOWING heatmap"""
        # Draw field in real-time (no caching for smooth animation)
        step = 8  # Larger for performance
        
        for y in range(0, self.height, step):
            for x in range(0, self.width, step):
                # Get resistance at this position (with time animation)
                resistance = self.get_resistance(x, y)
                
                # PULSING COLOR - from BLUE (low) to RED (high)
                # Make it more dramatic and visible!
                if resistance < 0.5:
                    # BLUE ZONE (low resistance, fast movement)
                    t = resistance * 2  # 0 to 1
                    color = (
                        int(10 + t * 30),      # Very little red
                        int(20 + t * 80),      # Some green
                        int(150 + t * 105)     # Strong blue
                    )
                else:
                    # RED ZONE (high resistance, slow movement)
                    t = (resistance - 0.5) * 2  # 0 to 1
                    color = (
                        int(40 + t * 215),     # Strong red
                        int(100 - t * 80),     # Fade out green
                        int(255 - t * 235)     # Fade out blue
                    )
                
                pygame.draw.rect(screen, color, (x, y, step, step))

