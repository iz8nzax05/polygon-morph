"""
Polygon representation with vertices
"""

import pygame


class Polygon:
    """Represents a polygon as a list of vertices"""
    
    def __init__(self, vertices):
        """
        vertices: list of (x, y) tuples
        """
        self.vertices = list(vertices)
    
    def get_vertex_count(self):
        """Get number of vertices"""
        return len(self.vertices)
    
    def get_vertex(self, index):
        """Get vertex at index"""
        return self.vertices[index]
    
    def set_vertex(self, index, x, y):
        """Set vertex position"""
        self.vertices[index] = (x, y)
    
    def draw(self, screen, color=(255, 255, 255), width=2):
        """Draw the polygon"""
        if len(self.vertices) < 2:
            return
        
        # Draw lines between vertices
        for i in range(len(self.vertices)):
            start = self.vertices[i]
            end = self.vertices[(i + 1) % len(self.vertices)]
            pygame.draw.line(screen, color, start, end, width)
        
        # Draw vertices as small circles
        for vertex in self.vertices:
            pygame.draw.circle(screen, color, (int(vertex[0]), int(vertex[1])), 3)
    
    def copy(self):
        """Create a copy of this polygon"""
        return Polygon(self.vertices.copy())

