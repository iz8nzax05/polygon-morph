"""
Polygon Morphing with Sine Wave Resistance Fields
Watch vertices flow through resistance terrain!
"""

import pygame
import sys
import math
from wave_field import WaveField
from polygon import Polygon
from morph_engine import MorphEngine

# Constants
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
FPS = 60
BACKGROUND_COLOR = (20, 20, 30)

class PolygonMorpher:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Polygon Morphing - Sine Wave Resistance Fields")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Core components
        self.wave_field = WaveField(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.morph_engine = None
        
        # State
        self.is_morphing = False
        self.show_field = True
        self.wave_enabled = True  # Actually enable/disable wave influence
        self.morph_speed = 1.0
        
        # Draw mode
        self.draw_mode = False
        self.drawing_points = []
        self.custom_shape = None
        
        # Preset shapes (polygons only - no circles!)
        # Center at (600, 400) with radius 250 to fill the screen!
        cx, cy, radius = 600, 400, 250
        self.presets = {
            'square': self.create_square(cx, cy, radius * 1.2),
            'triangle': self.create_triangle(cx, cy, radius * 1.3),
            'star': self.create_star(cx, cy, radius),
            'hexagon': self.create_hexagon(cx, cy, radius),
            'pentagon': self.create_pentagon(cx, cy, radius),
            'octagon': self.create_octagon(cx, cy, radius),
            'star8': self.create_star(cx, cy, radius, points=8),
            'star12': self.create_star(cx, cy, radius, points=12),
            'dodecagon': self.create_dodecagon(cx, cy, radius),
        }
        
        self.current_start = 'square'
        self.current_end = 'triangle'
        
    def create_circle(self, cx, cy, radius, segments=32):
        """Create circle as polygon"""
        vertices = []
        for i in range(segments):
            angle = (i / segments) * 2 * math.pi
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            vertices.append((x, y))
        return Polygon(vertices)
    
    def create_square(self, cx, cy, size):
        """Create square with same vertex count as circle for smooth morphing"""
        # Create square with many vertices (same as circle)
        vertices = []
        segments = 32  # Match circle vertex count
        half = size / 2
        
        # Create vertices around square perimeter
        perimeter = size * 4
        for i in range(segments):
            t = i / segments
            distance = t * perimeter
            
            if distance < size:  # Top edge
                x = cx - half + distance
                y = cy - half
            elif distance < size * 2:  # Right edge
                x = cx + half
                y = cy - half + (distance - size)
            elif distance < size * 3:  # Bottom edge
                x = cx + half - (distance - size * 2)
                y = cy + half
            else:  # Left edge
                x = cx - half
                y = cy + half - (distance - size * 3)
            
            vertices.append((x, y))
        
        return Polygon(vertices)
    
    def create_triangle(self, cx, cy, size):
        """Create triangle with many vertices for smooth morphing"""
        vertices = []
        segments = 32  # Match circle vertex count
        h = size * 0.866  # height
        
        # Three corners
        corners = [
            (cx, cy - h * 0.66),           # Top
            (cx + size/2, cy + h * 0.33),  # Bottom right
            (cx - size/2, cy + h * 0.33),  # Bottom left
        ]
        
        # Distribute vertices along the three edges
        verts_per_edge = segments // 3
        
        for edge in range(3):
            start = corners[edge]
            end = corners[(edge + 1) % 3]
            
            for i in range(verts_per_edge):
                t = i / verts_per_edge
                x = start[0] + (end[0] - start[0]) * t
                y = start[1] + (end[1] - start[1]) * t
                vertices.append((x, y))
        
        return Polygon(vertices)
    
    def create_star(self, cx, cy, radius, points=5):
        """Create star shape with distributed vertices"""
        vertices = []
        segments = 32  # Match circle vertex count
        inner_radius = radius * 0.4
        
        # Calculate star points
        star_points = []
        for i in range(points * 2):
            angle = (i / (points * 2)) * 2 * math.pi - math.pi / 2
            r = radius if i % 2 == 0 else inner_radius
            x = cx + r * math.cos(angle)
            y = cy + r * math.sin(angle)
            star_points.append((x, y))
        
        # Distribute vertices along star edges
        verts_per_edge = segments // (points * 2)
        
        for edge in range(points * 2):
            start = star_points[edge]
            end = star_points[(edge + 1) % (points * 2)]
            
            for i in range(verts_per_edge):
                t = i / verts_per_edge
                x = start[0] + (end[0] - start[0]) * t
                y = start[1] + (end[1] - start[1]) * t
                vertices.append((x, y))
        
        return Polygon(vertices)
    
    def create_hexagon(self, cx, cy, radius):
        """Create hexagon with distributed vertices"""
        vertices = []
        segments = 32  # Match circle vertex count
        
        # Calculate hexagon corners
        hex_points = []
        for i in range(6):
            angle = (i / 6) * 2 * math.pi
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            hex_points.append((x, y))
        
        # Distribute vertices along hexagon edges
        verts_per_edge = segments // 6
        
        for edge in range(6):
            start = hex_points[edge]
            end = hex_points[(edge + 1) % 6]
            
            for i in range(verts_per_edge):
                t = i / verts_per_edge
                x = start[0] + (end[0] - start[0]) * t
                y = start[1] + (end[1] - start[1]) * t
                vertices.append((x, y))
        
        return Polygon(vertices)
    
    def create_pentagon(self, cx, cy, radius):
        """Create pentagon with distributed vertices"""
        vertices = []
        segments = 32  # Match other shapes
        
        # Calculate pentagon corners
        pent_points = []
        for i in range(5):
            angle = (i / 5) * 2 * math.pi - math.pi / 2  # Start at top
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            pent_points.append((x, y))
        
        # Distribute vertices along pentagon edges
        verts_per_edge = segments // 5
        
        for edge in range(5):
            start = pent_points[edge]
            end = pent_points[(edge + 1) % 5]
            
            for i in range(verts_per_edge):
                t = i / verts_per_edge
                x = start[0] + (end[0] - start[0]) * t
                y = start[1] + (end[1] - start[1]) * t
                vertices.append((x, y))
        
        return Polygon(vertices)
    
    def create_octagon(self, cx, cy, radius):
        """Create octagon (8 sides) with distributed vertices"""
        vertices = []
        segments = 32
        
        # Calculate octagon corners
        oct_points = []
        for i in range(8):
            angle = (i / 8) * 2 * math.pi
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            oct_points.append((x, y))
        
        # Distribute vertices along octagon edges
        verts_per_edge = segments // 8
        
        for edge in range(8):
            start = oct_points[edge]
            end = oct_points[(edge + 1) % 8]
            
            for i in range(verts_per_edge):
                t = i / verts_per_edge
                x = start[0] + (end[0] - start[0]) * t
                y = start[1] + (end[1] - start[1]) * t
                vertices.append((x, y))
        
        return Polygon(vertices)
    
    def create_dodecagon(self, cx, cy, radius):
        """Create dodecagon (12 sides) - STRESS TEST!"""
        vertices = []
        segments = 48  # More vertices for complexity!
        
        # Calculate dodecagon corners
        dodec_points = []
        for i in range(12):
            angle = (i / 12) * 2 * math.pi
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            dodec_points.append((x, y))
        
        # Distribute vertices along dodecagon edges
        verts_per_edge = segments // 12
        
        for edge in range(12):
            start = dodec_points[edge]
            end = dodec_points[(edge + 1) % 12]
            
            for i in range(verts_per_edge):
                t = i / verts_per_edge
                x = start[0] + (end[0] - start[0]) * t
                y = start[1] + (end[1] - start[1]) * t
                vertices.append((x, y))
        
        return Polygon(vertices)
    
    def handle_events(self):
        """Handle user input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.draw_mode and event.button == 1:  # Left click in draw mode
                    # Add point to custom shape
                    self.drawing_points.append(event.pos)
                    print(f"Point {len(self.drawing_points)}: {event.pos}")
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.start_morph()
                elif event.key == pygame.K_BACKSPACE:
                    self.reset()
                elif event.key == pygame.K_g:
                    self.show_field = not self.show_field
                    print(f"Field visualization: {'ON' if self.show_field else 'OFF'}")
                elif event.key == pygame.K_h:
                    self.wave_enabled = not self.wave_enabled
                    if self.morph_engine:
                        self.morph_engine.wave_enabled = self.wave_enabled
                    print(f"Wave influence: {'ON' if self.wave_enabled else 'OFF (LINEAR MORPH)'}")
                elif event.key == pygame.K_t:
                    if self.morph_engine:
                        self.morph_engine.show_trails = not self.morph_engine.show_trails
                        print(f"Trails: {'ON' if self.morph_engine.show_trails else 'OFF'}")
                elif event.key == pygame.K_1:
                    self.current_start = 'square'
                elif event.key == pygame.K_2:
                    self.current_start = 'triangle'
                elif event.key == pygame.K_3:
                    self.current_start = 'star'
                elif event.key == pygame.K_4:
                    self.current_start = 'hexagon'
                elif event.key == pygame.K_5:
                    self.current_start = 'pentagon'
                elif event.key == pygame.K_q:
                    self.current_start = 'octagon'
                elif event.key == pygame.K_w:
                    self.current_start = 'star8'
                elif event.key == pygame.K_e:
                    self.current_start = 'star12'
                elif event.key == pygame.K_r:
                    self.current_start = 'dodecagon'
                elif event.key == pygame.K_6:
                    self.current_end = 'square'
                elif event.key == pygame.K_7:
                    self.current_end = 'triangle'
                elif event.key == pygame.K_8:
                    self.current_end = 'star'
                elif event.key == pygame.K_9:
                    self.current_end = 'hexagon'
                elif event.key == pygame.K_0:
                    self.current_end = 'pentagon'
                elif event.key == pygame.K_a:
                    self.current_end = 'octagon'
                elif event.key == pygame.K_s:
                    self.current_end = 'star8'
                elif event.key == pygame.K_d:
                    self.current_end = 'star12'
                elif event.key == pygame.K_f:
                    self.current_end = 'dodecagon'
                elif event.key == pygame.K_c:
                    self.current_start = 'custom'
                elif event.key == pygame.K_v:
                    self.current_end = 'custom'
                elif event.key == pygame.K_x:
                    # Toggle draw mode
                    self.draw_mode = not self.draw_mode
                    if self.draw_mode:
                        self.drawing_points = []
                        print("DRAW MODE: Click to add points. Press ENTER to finish, ESC to cancel")
                    else:
                        print("Draw mode OFF")
                elif event.key == pygame.K_RETURN:
                    # Finish drawing
                    if self.draw_mode and len(self.drawing_points) >= 3:
                        self.custom_shape = Polygon(self.drawing_points)
                        self.presets['custom'] = self.custom_shape
                        print(f"Custom shape created with {len(self.drawing_points)} vertices!")
                        self.draw_mode = False
                        self.drawing_points = []
                    elif self.draw_mode:
                        print("Need at least 3 points to make a shape!")
                elif event.key == pygame.K_UP:
                    self.wave_field.frequency += 0.5
                    print(f"Frequency: {self.wave_field.frequency}")
                elif event.key == pygame.K_DOWN:
                    self.wave_field.frequency = max(0.5, self.wave_field.frequency - 0.5)
                    print(f"Frequency: {self.wave_field.frequency}")
                elif event.key == pygame.K_RIGHT:
                    self.wave_field.amplitude += 0.1
                    print(f"Amplitude: {self.wave_field.amplitude}")
                elif event.key == pygame.K_LEFT:
                    self.wave_field.amplitude = max(0.1, self.wave_field.amplitude - 0.1)
                    print(f"Amplitude: {self.wave_field.amplitude}")
                    
            elif event.type == pygame.MOUSEWHEEL:
                self.morph_speed *= 1.2 if event.y > 0 else 0.8
                self.morph_speed = max(0.1, min(10.0, self.morph_speed))
                print(f"Speed: {self.morph_speed:.1f}x")
    
    def start_morph(self):
        """Start morphing animation"""
        # Get FRESH copies of the shapes (not references!)
        start_shape = self.presets[self.current_start].copy()
        end_shape = self.presets[self.current_end].copy()
        
        self.morph_engine = MorphEngine(start_shape, end_shape, self.wave_field)
        self.morph_engine.wave_enabled = self.wave_enabled
        self.is_morphing = True
        print(f"Morphing {self.current_start} -> {self.current_end} | Waves: {'ON' if self.wave_enabled else 'OFF'}")
    
    def reset(self):
        """Reset to start - regenerate fresh shapes"""
        self.is_morphing = False
        self.morph_engine = None
        
        # Regenerate all preset shapes to reset them to original state
        self.presets = {
            'circle': self.create_circle(300, 400, 100),
            'square': self.create_square(300, 400, 100),
            'triangle': self.create_triangle(300, 400, 120),
            'star': self.create_star(300, 400, 100),
            'hexagon': self.create_hexagon(300, 400, 100),
        }
        print("Reset - shapes regenerated")
    
    def update(self):
        """Update state"""
        # Always update wave field (animate the waves!)
        self.wave_field.update(1.0 / 60.0)
        
        if self.is_morphing and self.morph_engine:
            finished = self.morph_engine.step(self.morph_speed / 60.0)
            if finished:
                print("Morph complete!")
                self.is_morphing = False
    
    def draw(self):
        """Render everything"""
        self.screen.fill(BACKGROUND_COLOR)
        
        # Draw wave field visualization
        if self.show_field:
            self.wave_field.draw(self.screen)
        
        # Draw morphing polygon
        if self.morph_engine:
            self.morph_engine.draw(self.screen)
        elif self.draw_mode:
            # Draw mode - show points being drawn
            if len(self.drawing_points) > 0:
                # Draw lines between points
                for i in range(len(self.drawing_points)):
                    start = self.drawing_points[i]
                    end = self.drawing_points[(i + 1) % len(self.drawing_points)]
                    pygame.draw.line(self.screen, (0, 255, 255), start, end, 2)
                
                # Draw points
                for point in self.drawing_points:
                    pygame.draw.circle(self.screen, (255, 255, 0), point, 5)
                
                # Draw preview line to mouse
                mouse_pos = pygame.mouse.get_pos()
                if len(self.drawing_points) > 0:
                    pygame.draw.line(self.screen, (100, 255, 100), self.drawing_points[-1], mouse_pos, 1)
            
            # Draw instructions
            font = pygame.font.Font(None, 36)
            text = font.render("DRAW MODE: Click to add points | ENTER to finish | ESC to cancel", True, (255, 255, 0))
            self.screen.blit(text, (50, 50))
        else:
            # Draw start and end shapes
            if self.current_start in self.presets and self.current_end in self.presets:
                start_shape = self.presets[self.current_start]
                end_shape = self.presets[self.current_end]
                start_shape.draw(self.screen, (100, 200, 255), 2)
                end_shape.draw(self.screen, (255, 100, 200), 2)
        
        # Draw UI
        self.draw_ui()
        
        pygame.display.flip()
    
    def draw_ui(self):
        """Draw user interface"""
        font = pygame.font.Font(None, 22)
        y = 10
        
        wave_status = "ON" if self.wave_enabled else "OFF"
        instructions = [
            f"START: {self.current_start.upper()} | END: {self.current_end.upper()}",
            "1-5/QWER: Start Shape | 6-0/ASDF: End Shape | C/V: Custom",
            "SPACE: Morph | BACKSPACE: Reset | X: Draw Mode",
            f"G: Field Visual | H: Wave Influence [{wave_status}] | T: Trails | Arrows: Adjust",
            f"Wave: Freq={self.wave_field.frequency:.1f} Amp={self.wave_field.amplitude:.1f} | Speed: {self.morph_speed:.1f}x",
        ]
        
        if self.is_morphing and self.morph_engine:
            progress = self.morph_engine.progress * 100
            verts = len(self.morph_engine.current_polygon.vertices)
            instructions.append(f"Progress: {progress:.1f}% | Vertices: {verts}")
        
        for text in instructions:
            surface = font.render(text, True, (255, 255, 255))
            self.screen.blit(surface, (10, y))
            y += 23
    
    def run(self):
        """Main loop"""
        print("=== POLYGON MORPHING - SINE WAVE RESISTANCE FIELDS ===")
        print("START: 1=Square 2=Triangle 3=Star5 4=Hexagon 5=Pentagon | Q=Octagon W=Star8 E=Star12 R=Dodecagon | C=Custom")
        print("END:   6=Square 7=Triangle 8=Star5 9=Hexagon 0=Pentagon | A=Octagon S=Star8 D=Star12 F=Dodecagon | V=Custom")
        print("SPACE=Morph | BACKSPACE=Reset | G=Field | T=Trails | X=Draw Mode | Arrows=Waves | Scroll=Speed")
        
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    morpher = PolygonMorpher()
    morpher.run()

