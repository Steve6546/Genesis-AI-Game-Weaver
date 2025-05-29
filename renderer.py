import pygame
import os
import random # For potential use in randomizing obstacle reset

# Default schema, mainly for internal testing if renderer is run directly.
# The main execution path via main.py will pass a schema.
DEFAULT_GAME_SCHEMA_FOR_RENDERER_TEST = { # Renamed to avoid conflict if imported elsewhere
    "game_title": "Default Renderer Test",
    "screen_dimensions": {
        "width": 800,
        "height": 600
    },
    "background_color": [30, 30, 30],
    "entities": [
        {
            "id": "default_player",
            "type": "player",
            "color": [0, 128, 255],
            "position": {"x": 50, "y": 500},
            "size": {"width": 50, "height": 50},
            "is_controllable": True,
            "movement_pattern": "player_horizontal_control",
            "speed": 7
        },
        {
            "id": "default_obstacle_1",
            "type": "obstacle",
            "color": [255, 0, 0],
            "position": {"x": 300, "y": 0},
            "size": {"width": 50, "height": 50},
            "movement_pattern": "falling_down",
            "speed": 4
        },
        {
            "id": "default_obstacle_2",
            "type": "obstacle",
            "color": [255, 100, 0],
            "position": {"x": 500, "y": -100}, # Start off-screen
            "size": {"width": 60, "height": 40},
            "movement_pattern": "falling_down",
            "speed": 3
        }
    ],
    "game_rules": ["Test the renderer!"]
}

def render_game_from_schema(game_schema, output_image_path="frame.png", run_loop=False):
    pygame.init()

    try:
        title = game_schema.get("game_title", "Untitled Game")
        dimensions = game_schema.get("screen_dimensions", {"width": 800, "height": 600})
        width = dimensions.get("width", 800)
        height = dimensions.get("height", 600)
        bg_color_list = game_schema.get("background_color", [0, 0, 0])
        bg_color = tuple(bg_color_list) # Pygame needs tuples for colors

        screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)

        # Font for game_rules
        try:
            font = pygame.font.Font(None, 28) # Default font, size 28
        except Exception as e:
            print(f"Warning: Could not load default font. Game rules will not be displayed. Error: {e}")
            font = None
        
        game_rules_text_surfaces = []
        if font:
            rules = game_schema.get("game_rules", [])
            for i, rule_text in enumerate(rules):
                try:
                    text_surface = font.render(rule_text, True, (255, 255, 255)) # White text
                    game_rules_text_surfaces.append(text_surface)
                except Exception as e_render:
                    print(f"Warning: Could not render rule text: '{rule_text}'. Error: {e_render}")

        entities_from_schema = game_schema.get("entities", [])
        
        # Create a list of entity objects (dictionaries with a 'rect' for Pygame)
        # This list will be modified during the game loop
        active_entities = []
        for entity_data in entities_from_schema:
            # Make a copy to avoid modifying the original schema dict directly if it's reused
            entity_copy = entity_data.copy() 
            entity_copy["rect"] = pygame.Rect(
                entity_copy.get("position", {}).get("x", 0),
                entity_copy.get("position", {}).get("y", 0),
                entity_copy.get("size", {}).get("width", 10),
                entity_copy.get("size", {}).get("height", 10)
            )
            # Ensure color is a tuple
            entity_copy["color_tuple"] = tuple(entity_copy.get("color", [255, 255, 255]))
            
            # Get new properties with defaults from schema or general defaults
            entity_copy["is_controllable"] = entity_copy.get("is_controllable", False)
            entity_copy["movement_pattern"] = entity_copy.get("movement_pattern", "static")
            entity_copy["speed"] = entity_copy.get("speed", 0)
            if entity_copy["movement_pattern"] == "moving_left_right_patrol":
                entity_copy["patrol_direction"] = 1 # 1 for right, -1 for left
            active_entities.append(entity_copy)
        
        player_entity = None
        for entity in active_entities:
            if entity["is_controllable"] and entity["movement_pattern"] == "player_horizontal_control":
                if player_entity is None:
                    player_entity = entity
                else:
                    print("Warning: Multiple controllable entities for horizontal control. Using the first one.")
        
        if run_loop:
            running = True
            clock = pygame.time.Clock()
            FPS = 30 

            projectile_id_counter = 0 # Initialize counter for unique projectile IDs
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                
                # Player control
                if player_entity:
                    keys = pygame.key.get_pressed()
                    player_speed = player_entity.get("speed", 5) # Using a default of 5 if speed is 0 or not set
                    
                    current_pattern = player_entity.get("movement_pattern")
                    
                    if current_pattern == "player_horizontal_control":
                        if keys[pygame.K_LEFT]:
                            player_entity["rect"].x -= player_speed
                        if keys[pygame.K_RIGHT]:
                            player_entity["rect"].x += player_speed
                    elif current_pattern == "player_omni_directional_control":
                        if keys[pygame.K_LEFT]:
                            player_entity["rect"].x -= player_speed
                        if keys[pygame.K_RIGHT]:
                            player_entity["rect"].x += player_speed
                        if keys[pygame.K_UP]:
                            player_entity["rect"].y -= player_speed
                        if keys[pygame.K_DOWN]:
                            player_entity["rect"].y += player_speed
                    
                    # Keep player within screen bounds
                    current_pattern_bounds_check = player_entity.get("movement_pattern") # Re-get in case it changed, though unlikely here
                    if current_pattern_bounds_check == "player_horizontal_control" or current_pattern_bounds_check == "player_omni_directional_control":
                        if player_entity["rect"].left < 0:
                            player_entity["rect"].left = 0
                        if player_entity["rect"].right > width:
                            player_entity["rect"].right = width
                        if current_pattern_bounds_check == "player_omni_directional_control":
                            if player_entity["rect"].top < 0:
                                player_entity["rect"].top = 0
                            if player_entity["rect"].bottom > height:
                                player_entity["rect"].bottom = height
                        # Shooting (if player can shoot)
                        if player_entity.get("can_shoot") and keys[pygame.K_SPACE]:
                            now = pygame.time.get_ticks()
                            last_shot_time = player_entity.get("last_shot_time", 0)
                            # Cooldown from projectile_archetype or a default
                            shoot_cooldown = player_entity.get("projectile_archetype", {}).get("cooldown_ms", 250) 

                            if now - last_shot_time > shoot_cooldown:
                                player_entity["last_shot_time"] = now
                                archetype = player_entity.get("projectile_archetype")
                                if archetype:
                                    projectile_id_counter += 1 # Increment for next
                                    
                                    # Prepare projectile data from archetype
                                    new_projectile = {
                                        "id": f"{archetype.get('id_prefix', 'proj_')}{projectile_id_counter}",
                                        "name": f"{archetype.get('name_prefix', 'Projectile ')}{projectile_id_counter}",
                                        "type": archetype.get("type", "projectile"), # Should be 'projectile'
                                        "shape": archetype.get("shape", "rectangle"),
                                        "color_tuple": tuple(archetype.get("color", [255, 255, 0])),
                                        "size_data": archetype.get("size"), # Raw size data from schema
                                        "speed": archetype.get("speed", 10),
                                        "movement_pattern": archetype.get("movement_pattern", "projectile_movement"),
                                        "damage": archetype.get("damage", 1),
                                        "lifespan_ms": archetype.get("lifespan_ms"),
                                        "spawn_time_ms": now if archetype.get("lifespan_ms") else None,
                                        # Ensure projectiles are not controllable and have no patrol direction by default
                                        "is_controllable": False, 
                                        "patrol_direction": 0 
                                    }
                                    
                                    # Calculate initial position and rect for projectile
                                    proj_size_data = new_projectile["size_data"]
                                    if new_projectile["shape"] == "circle":
                                        proj_radius = proj_size_data.get("radius", 5)
                                        proj_width, proj_height = proj_radius * 2, proj_radius * 2
                                    else: # rectangle
                                        proj_width = proj_size_data.get("width", 10)
                                        proj_height = proj_size_data.get("height", 5)
                                    
                                    # Spawn projectile from center-top of player
                                    new_projectile["rect"] = pygame.Rect(
                                        player_entity["rect"].centerx - proj_width // 2,
                                        player_entity["rect"].top - proj_height, 
                                        proj_width,
                                        proj_height
                                    )
                                    active_entities.append(new_projectile)
                                    # print(f"Fired: {new_projectile['id']} at {new_projectile['rect']}") # Debug

                # Update other entities
                for entity in active_entities:
                    if entity.get("movement_pattern") == "falling_down":
                        entity["rect"].y += entity.get("speed", 0)
                        if entity["rect"].top > height: # If entity is past the bottom edge
                            entity["rect"].y = 0 - entity["rect"].height # Reset to top, above screen
                            # Randomize x position for falling objects upon reset
                            if entity["rect"].width < width : # ensure it's not wider than screen
                                entity["rect"].x = random.randint(0, width - entity["rect"].width)
                            else:
                                entity["rect"].x = 0
                    elif entity.get("movement_pattern") == "moving_left_right_patrol":
                        speed = entity.get("speed", 0)
                        direction = entity.get("patrol_direction", 1)
                        entity["rect"].x += speed * direction
                        
                        if entity["rect"].left < 0:
                            entity["rect"].left = 0
                            entity["patrol_direction"] = 1 # Change direction to right
                        elif entity["rect"].right > width:
                            entity["rect"].right = width
                            entity["patrol_direction"] = -1 # Change direction to left
                    elif entity.get("movement_pattern") == "projectile_movement":
                        entity["rect"].y -= entity.get("speed", 10) # Move upwards
                        
                        # Check lifespan
                        if entity.get("lifespan_ms") is not None and entity.get("spawn_time_ms") is not None:
                            now = pygame.time.get_ticks()
                            if now - entity["spawn_time_ms"] > entity["lifespan_ms"]:
                                if entity in active_entities: # Ensure it's still there
                                    active_entities.remove(entity)
                                    # print(f"Projectile {entity.get('id')} expired by lifespan.") # Debug
                                    continue # Skip further processing for this removed entity
                        
                        # Remove if off-screen (top)
                        if entity["rect"].bottom < 0:
                            if entity in active_entities: # Check if not already removed by lifespan
                                active_entities.remove(entity)
                                # print(f"Projectile {entity.get('id')} went off-screen (top).") # Debug
                                continue # Skip further processing

                # Collision detection
                entities_to_remove = []
                if player_entity:
                    # Iterate over a copy of active_entities if we modify it during iteration (e.g. removing projectiles/enemies)
                    for entity in list(active_entities): # Iterate over a copy

                        # 1. Player vs. Other Entities (excluding projectiles from player)
                        if entity is not player_entity and entity.get("type") != "projectile":
                            if player_entity["rect"].colliderect(entity["rect"]):
                                print(f"[COLLISION] Player '{player_entity.get('name', player_entity.get('id'))}' collided with '{entity.get('name', entity.get('id'))}' ({entity.get('type')})")
                                if entity.get("type") == "enemy":
                                    # Player takes damage or game over, for now just print
                                    player_health = player_entity.get("health_points")
                                    if player_health is not None:
                                        # player_entity["health_points"] -= 1 # Example damage, can be made configurable
                                        # print(f"Player health: {player_entity['health_points']}")
                                        # if player_entity["health_points"] <= 0:
                                        #     print("Game Over!")
                                        #     running = False # End game
                                        pass # Placeholder for player damage logic

                        # 2. Projectiles vs. Other Entities
                        if entity.get("type") == "projectile":
                            # Ensure projectile itself is still active before checking its collisions
                            if entity in entities_to_remove: # Already marked for removal by lifespan or off-screen
                                continue

                            for target_entity in list(active_entities):
                                # Projectile should not collide with player who fired it (or other projectiles for now)
                                # Also, target should not be the projectile itself, and target should not be already marked for removal
                                if target_entity is player_entity or target_entity.get("type") == "projectile" or target_entity is entity or target_entity in entities_to_remove:
                                    continue

                                if entity["rect"].colliderect(target_entity["rect"]):
                                    print(f"[COLLISION] Projectile '{entity.get('name', entity.get('id'))}' hit '{target_entity.get('name', target_entity.get('id'))}' ({target_entity.get('type')})")
                                    
                                    # Mark projectile for removal
                                    if entity not in entities_to_remove:
                                        entities_to_remove.append(entity)
                                    
                                    if target_entity.get("type") == "enemy":
                                        target_health = target_entity.get("health_points")
                                        if target_health is not None:
                                            target_entity["health_points"] = target_health - entity.get("damage", 1)
                                            # print(f"Enemy '{target_entity.get('name', target_entity.get('id'))}' health: {target_entity['health_points']}")
                                            if target_entity["health_points"] <= 0:
                                                if target_entity not in entities_to_remove:
                                                    entities_to_remove.append(target_entity)
                                                print(f"Enemy '{target_entity.get('name', target_entity.get('id'))}' destroyed.")
                                    break # Projectile hits one target and is done for this frame's check

                # Remove entities marked for removal
                if entities_to_remove:
                    active_entities = [e for e in active_entities if e not in entities_to_remove]
                    # Update player_entity reference if it was removed (e.g. game over)
                    if player_entity in entities_to_remove:
                        player_entity = None 

                # Drawing
                screen.fill(bg_color)
                for entity in active_entities:
                    shape = entity.get("shape", "rectangle") # Default to rectangle
                    color = entity["color_tuple"]
                    rect = entity["rect"]

                    if shape == "circle":
                        radius = entity.get("size", {}).get("radius", rect.width // 2) 
                        # Pygame's circle center is based on the rect's top-left for consistency if only rect is updated
                        # The rect itself defines the bounding box of the circle.
                        # So, center_x should be rect.centerx and center_y should be rect.centery
                        # And radius should be rect.width / 2 (or height / 2, assuming it's a circle)
                        # For simplicity and direct use of schema's radius:
                        center_x = rect.x + radius # Assuming rect.x, rect.y is top-left of bounding box
                        center_y = rect.y + radius # Assuming rect.x, rect.y is top-left of bounding box
                        pygame.draw.circle(screen, color, (center_x, center_y), radius)
                    else: # Default to rectangle
                        pygame.draw.rect(screen, color, rect)
                    if entity["is_controllable"]: 
                         pygame.draw.rect(screen, (255,255,255), entity["rect"], 2) # White border
                
                # Draw game_rules
                if font and game_rules_text_surfaces:
                    for i, text_surface in enumerate(game_rules_text_surfaces):
                        screen.blit(text_surface, (10, 10 + i * 25)) # Position rules at top-left
                    # Draw Player Health (if player exists and has health)
                    if player_entity and player_entity.get("health_points") is not None and font:
                        health_text = f"Player Health: {player_entity['health_points']}"
                        try:
                            health_surface = font.render(health_text, True, (255, 255, 255)) # White text
                            # Position health below game rules
                            rules_height = len(game_rules_text_surfaces) * 25 
                            screen.blit(health_surface, (10, 10 + rules_height + 5)) # 5px padding
                        except Exception as e_render_health:
                            print(f"Warning: Could not render health text. Error: {e_render_health}")

                pygame.display.flip()
                clock.tick(FPS)
            
            print("Exiting Pygame loop.")

        else: # Just save a single frame
            screen.fill(bg_color)
            # Draw entities based on their *initial* positions from the schema for a single frame
            for entity_data_original in entities_from_schema:
                pos_x = entity_data_original.get("position", {}).get("x", 0)
                pos_y = entity_data_original.get("position", {}).get("y", 0)
                shape = entity_data_original.get("shape", "rectangle")
                
                if shape == "circle":
                    radius = entity_data_original.get("size", {}).get("radius", 10)
                    initial_rect = pygame.Rect(pos_x, pos_y, radius * 2, radius * 2)
                else: # rectangle
                    width = entity_data_original.get("size", {}).get("width", 10)
                    height = entity_data_original.get("size", {}).get("height", 10)
                    initial_rect = pygame.Rect(pos_x, pos_y, width, height)
                color_tuple = tuple(entity_data_original.get("color", [255,255,255]))
                # shape is already defined from when initial_rect was created
                if shape == "circle": 
                    radius = entity_data_original.get("size", {}).get("radius", initial_rect.width // 2)
                    pygame.draw.circle(screen, color_tuple, initial_rect.center, radius)
                else: # Default to rectangle
                    pygame.draw.rect(screen, color_tuple, initial_rect)
                if entity_data_original.get("is_controllable", False):
                     pygame.draw.rect(screen, (255,255,255), initial_rect, 2) # White border

            # Draw game_rules for single frame
            if font and game_rules_text_surfaces:
                for i, text_surface in enumerate(game_rules_text_surfaces):
                    screen.blit(text_surface, (10, 10 + i * 25))

            try:
                pygame.image.save(screen, output_image_path)
                print(f"Game frame saved to {output_image_path}")
            except pygame.error as e:
                print(f"Error saving image: {e}. Ensure path is valid and Pygame has image support.")
                # Fallback for headless environments if direct save fails
                temp_surface = screen.copy()
                try:
                    pygame.image.save(temp_surface, output_image_path)
                    print(f"Game frame saved to {output_image_path} using temporary surface.")
                except pygame.error as e_temp:
                    print(f"Error saving image with temporary surface: {e_temp}")


    except Exception as e:
        print(f"An error occurred in render_game_from_schema: {e}")
        import traceback
        traceback.print_exc() # For more detailed error during development
    finally:
        pygame.quit()

if __name__ == '__main__':
    # This part is for direct testing of the renderer.
    print("Running renderer.py directly for testing...")
    
    # Ensure SDL_VIDEODRIVER is set for headless environments if testing run_loop
    # For run_loop=True, you might need a display.
    # For run_loop=False (saving frame), 'dummy' should work.
    # Simplified logic for SDL_VIDEODRIVER setting for direct test
    is_direct_run_loop_test = True # Set to True to test run_loop directly from here

    if os.environ.get('SDL_VIDEODRIVER') is None and not is_direct_run_loop_test:
         os.environ['SDL_VIDEODRIVER'] = 'dummy'
         print("Set SDL_VIDEODRIVER to dummy for headless frame saving test.")

    if is_direct_run_loop_test:
        print("\nTesting live loop directly (requires display or virtual display like Xvfb)...")
        print("If this hangs or errors in a headless environment without Xvfb, it's expected.")
        print("Press Ctrl+C in terminal or close Pygame window to exit loop.")
        render_game_from_schema(DEFAULT_GAME_SCHEMA_FOR_RENDERER_TEST, run_loop=True)
    else:
        # Test saving a single frame
        output_path_test = "/workspace/genesis_ai_game_weaver/renderer_direct_test_frame.png"
        render_game_from_schema(DEFAULT_GAME_SCHEMA_FOR_RENDERER_TEST, 
                                output_image_path=output_path_test, 
                                run_loop=False)
        print(f"Test frame saved by renderer.py direct execution: {output_path_test}")
