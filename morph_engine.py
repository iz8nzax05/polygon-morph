"""
Morphing Engine - The Core Algorithm
Vertices flow through sine wave resistance fields
WITH ADAPTIVE VERTEX GENERATION - vertices add/remove based on shape complexity!
"""

import pygame
import math


class MorphEngine:
    """Handles polygon morphing through wave resistance fields"""
    
    def __init__(self, start_polygon, end_polygon, wave_field):
        self.start_polygon = start_polygon
        self.end_polygon = end_polygon
        self.wave_field = wave_field
        
        # Current morphing state
        self.current_polygon = start_polygon.copy()
        self.progress = 0.0  # 0.0 to 1.0
        
        # Per-vertex progress (each vertex moves at different speed!)
        self.vertex_progress = [0.0] * start_polygon.get_vertex_count()
        
        # Adaptive vertex generation
        self.adaptive_mode = True
        self.vertex_life = [1.0] * start_polygon.get_vertex_count()  # 0.0 to 1.0 (fading in/out)
        self.last_adapt_time = 0.0
        self.adapt_interval = 0.1  # Check every 0.1 seconds
        
        # Visual toggles
        self.show_trails = False  # Toggle for vertex trails
        self.wave_enabled = True  # Toggle for wave influence
        
        # Match vertex counts (interpolate if different)
        self._match_vertex_counts()
    
    def _match_vertex_counts(self):
        """Ensure start and end have same number of vertices - SIMPLE approach"""
        start_count = self.start_polygon.get_vertex_count()
        end_count = self.end_polygon.get_vertex_count()
        
        if start_count == end_count:
            return
        
        # SIMPLE: Just use the smaller count
        # The adaptive system will add vertices during morphing if needed!
        min_count = min(start_count, end_count)
        self.start_polygon.vertices = self.start_polygon.vertices[:min_count]
        self.end_polygon.vertices = self.end_polygon.vertices[:min_count]
        self.current_polygon.vertices = self.current_polygon.vertices[:min_count]
        self.vertex_progress = self.vertex_progress[:min_count]
    
    def step(self, delta_time):
        """
        Execute one morphing step
        delta_time: time multiplier (speed control)
        Returns True when morphing is complete
        """
        # Adaptive vertex generation
        if self.adaptive_mode:
            self.last_adapt_time += delta_time
            if self.last_adapt_time >= self.adapt_interval:
                self._adapt_vertices()
                self._kill_deviant_vertices()  # NEW: Kill vertices that stray from straight path!
                self.last_adapt_time = 0.0
        
        all_complete = True
        
        for i in range(len(self.vertex_progress)):
            if self.vertex_progress[i] >= 1.0:
                continue
            
            all_complete = False
            
            # Get current vertex position
            current_x, current_y = self.current_polygon.get_vertex(i)
            
            # Get target position
            target_x, target_y = self.end_polygon.get_vertex(i)
            
            # Move towards target
            dx = target_x - current_x
            dy = target_y - current_y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 0.5:
                # Normalize direction
                dx /= distance
                dy /= distance
                
                if self.wave_enabled:
                    # WAVE MODE: Use sine wave resistance and forces
                    resistance = self.wave_field.get_resistance(current_x, current_y)
                    speed = 0.1 + (1.0 - resistance) * 0.9
                    
                    # Get WAVE FORCE - the push from the flowing waves!
                    wave_fx, wave_fy = self.wave_field.get_wave_force(current_x, current_y)
                    
                    # Apply speed and delta_time
                    move_amount = speed * delta_time * 50
                    
                    # Add wave force to movement (vertices surf the waves!)
                    wave_influence = 0.3  # How much waves push vertices around
                    new_x = current_x + dx * move_amount + wave_fx * delta_time * wave_influence
                    new_y = current_y + dy * move_amount + wave_fy * delta_time * wave_influence
                else:
                    # LINEAR MODE: Straight line interpolation, no waves!
                    speed = 1.0  # Constant speed
                    move_amount = speed * delta_time * 50
                    new_x = current_x + dx * move_amount
                    new_y = current_y + dy * move_amount
                
                self.current_polygon.set_vertex(i, new_x, new_y)
                
                # Update progress (0.0 to 1.0)
                total_distance = math.sqrt(
                    (target_x - self.start_polygon.get_vertex(i)[0])**2 +
                    (target_y - self.start_polygon.get_vertex(i)[1])**2
                )
                if total_distance > 0:
                    traveled = math.sqrt(
                        (new_x - self.start_polygon.get_vertex(i)[0])**2 +
                        (new_y - self.start_polygon.get_vertex(i)[1])**2
                    )
                    self.vertex_progress[i] = min(1.0, traveled / total_distance)
            else:
                # Snap to target
                self.current_polygon.set_vertex(i, target_x, target_y)
                self.vertex_progress[i] = 1.0
        
        # Calculate overall progress
        self.progress = sum(self.vertex_progress) / len(self.vertex_progress) if self.vertex_progress else 0.0
        
        return all_complete
    
    def _adapt_vertices(self):
        """
        Adaptively add or remove vertices based on shape complexity
        This is the INNOVATION - vertices optimize themselves!
        """
        if len(self.current_polygon.vertices) < 3:
            return
        
        # Calculate curvature at each vertex
        curvatures = self._calculate_curvatures()
        
        # STEP 1: Remove vertices where curvature is very low (straight lines)
        if len(self.current_polygon.vertices) > 4:
            self._remove_low_curvature_vertices(curvatures)
        
        # STEP 2: Add vertices where curvature is very high (sharp curves)
        if len(self.current_polygon.vertices) < 64:
            self._add_high_curvature_vertices(curvatures)
    
    def _calculate_curvatures(self):
        """Calculate curvature at each vertex"""
        curvatures = []
        n = len(self.current_polygon.vertices)
        
        for i in range(n):
            prev_idx = (i - 1) % n
            next_idx = (i + 1) % n
            
            prev = self.current_polygon.vertices[prev_idx]
            curr = self.current_polygon.vertices[i]
            next = self.current_polygon.vertices[next_idx]
            
            # Calculate angle change (simple curvature measure)
            v1 = (curr[0] - prev[0], curr[1] - prev[1])
            v2 = (next[0] - curr[0], next[1] - curr[1])
            
            # Normalize
            len1 = math.sqrt(v1[0]**2 + v1[1]**2) + 0.001
            len2 = math.sqrt(v2[0]**2 + v2[1]**2) + 0.001
            v1 = (v1[0]/len1, v1[1]/len1)
            v2 = (v2[0]/len2, v2[1]/len2)
            
            # Dot product gives angle
            dot = v1[0]*v2[0] + v1[1]*v2[1]
            dot = max(-1.0, min(1.0, dot))
            angle = math.acos(dot)
            
            curvatures.append(angle)
        
        return curvatures
    
    def _remove_low_curvature_vertices(self, curvatures, threshold=0.15):
        """Remove vertices where curvature is very low (nearly straight)"""
        to_remove = []
        
        for i, curvature in enumerate(curvatures):
            if curvature < threshold and self.progress > 0.3:  # Only remove after 30% progress
                # Check if vertex is far from target (don't remove if still moving)
                if i < len(self.vertex_progress) and self.vertex_progress[i] > 0.8:  # Almost at target
                    to_remove.append(i)
        
        # Remove 1/3 at a time
        num_to_remove = max(1, len(to_remove) // 3)
        
        # Remove vertices (in reverse to maintain indices)
        for i in reversed(to_remove[:num_to_remove]):
            if len(self.current_polygon.vertices) > 4:  # Keep at least 4 vertices
                # Remove from all tracking arrays
                if i < len(self.current_polygon.vertices):
                    del self.current_polygon.vertices[i]
                if i < len(self.vertex_progress):
                    del self.vertex_progress[i]
                if i < len(self.vertex_life):
                    del self.vertex_life[i]
                # Also remove from start/end to keep them in sync
                if i < len(self.start_polygon.vertices):
                    del self.start_polygon.vertices[i]
                if i < len(self.end_polygon.vertices):
                    del self.end_polygon.vertices[i]
    
    def _kill_deviant_vertices(self):
        """
        KILL vertices that stray too far from the straight line path!
        If a vertex isn't moving in a straight line from start to end, DELETE IT!
        """
        if len(self.current_polygon.vertices) <= 4:
            return  # Keep at least 4 vertices
        
        to_kill = []
        
        for i in range(len(self.current_polygon.vertices)):
            if i >= len(self.start_polygon.vertices) or i >= len(self.end_polygon.vertices):
                continue
            
            # Get the three positions
            start_pos = self.start_polygon.vertices[i]
            current_pos = self.current_polygon.vertices[i]
            end_pos = self.end_polygon.vertices[i]
            
            # Calculate the straight line from start to end
            line_dx = end_pos[0] - start_pos[0]
            line_dy = end_pos[1] - start_pos[1]
            line_length = math.sqrt(line_dx**2 + line_dy**2)
            
            if line_length < 0.1:
                continue  # Skip if start and end are the same
            
            # Normalize the line direction
            line_dx /= line_length
            line_dy /= line_length
            
            # Vector from start to current
            to_current_dx = current_pos[0] - start_pos[0]
            to_current_dy = current_pos[1] - start_pos[1]
            
            # Project current position onto the line
            projection = to_current_dx * line_dx + to_current_dy * line_dy
            
            # Find the closest point on the line
            closest_x = start_pos[0] + projection * line_dx
            closest_y = start_pos[1] + projection * line_dy
            
            # Calculate perpendicular distance (deviation)
            deviation = math.sqrt(
                (current_pos[0] - closest_x)**2 + 
                (current_pos[1] - closest_y)**2
            )
            
            # KILL if deviation is too high (more than 15 pixels off the straight path)
            if deviation > 15.0 and self.progress > 0.2:  # Only after 20% progress
                to_kill.append(i)
        
        # EXECUTE THE KILLS (in reverse to maintain indices)
        for i in reversed(to_kill):
            if len(self.current_polygon.vertices) > 4:
                # Remove from all tracking arrays
                if i < len(self.current_polygon.vertices):
                    del self.current_polygon.vertices[i]
                if i < len(self.vertex_progress):
                    del self.vertex_progress[i]
                if i < len(self.vertex_life):
                    del self.vertex_life[i]
                if i < len(self.start_polygon.vertices):
                    del self.start_polygon.vertices[i]
                if i < len(self.end_polygon.vertices):
                    del self.end_polygon.vertices[i]
    
    def _add_high_curvature_vertices(self, curvatures, threshold=1.0):
        """Add vertices where curvature is very high (sharp curves)"""
        to_add = []
        
        for i, curvature in enumerate(curvatures):
            if curvature > threshold and self.progress < 0.7:  # Only add before 70% progress
                # Check segment length - only add if segment is long enough
                if i < len(self.current_polygon.vertices):
                    curr = self.current_polygon.vertices[i]
                    next_idx = (i + 1) % len(self.current_polygon.vertices)
                    next = self.current_polygon.vertices[next_idx]
                    
                    dist = math.sqrt((next[0]-curr[0])**2 + (next[1]-curr[1])**2)
                    if dist > 20:  # Minimum segment length
                        to_add.append(i)
        
        # Add vertices (in reverse to maintain indices)
        for i in reversed(to_add[:max(2, len(to_add)//2)]):  # Add max half at a time
            if len(self.current_polygon.vertices) >= 64:
                break
            
            if i >= len(self.current_polygon.vertices):
                continue
            
            # Insert new vertex between i and i+1
            curr = self.current_polygon.vertices[i]
            next_idx = (i + 1) % len(self.current_polygon.vertices)
            next = self.current_polygon.vertices[next_idx]
            
            # Midpoint
            mid_x = (curr[0] + next[0]) / 2
            mid_y = (curr[1] + next[1]) / 2
            
            # Insert into current polygon
            self.current_polygon.vertices.insert(i + 1, (mid_x, mid_y))
            
            # Insert into start polygon
            if i < len(self.start_polygon.vertices):
                start_curr = self.start_polygon.vertices[i]
                start_next_idx = min(i + 1, len(self.start_polygon.vertices) - 1)
                start_next = self.start_polygon.vertices[start_next_idx]
                start_mid = ((start_curr[0] + start_next[0]) / 2, (start_curr[1] + start_next[1]) / 2)
                self.start_polygon.vertices.insert(i + 1, start_mid)
            
            # Insert into end polygon
            if i < len(self.end_polygon.vertices):
                end_curr = self.end_polygon.vertices[i]
                end_next_idx = min(i + 1, len(self.end_polygon.vertices) - 1)
                end_next = self.end_polygon.vertices[end_next_idx]
                end_mid = ((end_curr[0] + end_next[0]) / 2, (end_curr[1] + end_next[1]) / 2)
                self.end_polygon.vertices.insert(i + 1, end_mid)
            
            # Insert progress (average of neighbors)
            avg_progress = (self.vertex_progress[i] + self.vertex_progress[min(i + 1, len(self.vertex_progress) - 1)]) / 2
            self.vertex_progress.insert(i + 1, avg_progress)
            
            # Insert life (start faded, fade in)
            self.vertex_life.insert(i + 1, 0.3)
    
    def draw(self, screen):
        """Draw the current morphing state"""
        # Update vertex life (fade in new vertices)
        for i in range(len(self.vertex_life)):
            if self.vertex_life[i] < 1.0:
                self.vertex_life[i] = min(1.0, self.vertex_life[i] + 0.05)
        
        # Draw the morphing polygon with alpha based on vertex life
        self.current_polygon.draw(screen, (0, 255, 150), 3)
        
        # Draw vertex trails (if enabled)
        if self.show_trails:
            for i in range(self.current_polygon.get_vertex_count()):
                if i < len(self.start_polygon.vertices):
                    start_x, start_y = self.start_polygon.get_vertex(i)
                    current_x, current_y = self.current_polygon.get_vertex(i)
                    
                    # Draw faint line from start to current
                    color = (100, 100, 100)
                    pygame.draw.line(screen, color, (start_x, start_y), (current_x, current_y), 1)
        
        # Highlight vertices with different progress
        for i in range(self.current_polygon.get_vertex_count()):
            x, y = self.current_polygon.get_vertex(i)
            progress = self.vertex_progress[i]
            life = self.vertex_life[i] if i < len(self.vertex_life) else 1.0
            
            # Color based on progress and life (fading)
            if progress < 1.0:
                # Moving - bright color, modulated by life
                color = (0, int(255 * life), int(150 * life))
                radius = int(5 * life)
            else:
                # Done - dim color
                color = (0, int(100 * life), int(50 * life))
                radius = int(3 * life)
            
            pygame.draw.circle(screen, color, (int(x), int(y)), radius)
