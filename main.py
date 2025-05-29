import json
import argparse
import os
import sys
import google.generativeai as genai
import jsonschema

# Add project root to Python path to allow importing sibling modules
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    from game_schema_validator import validate_game_schema, GAME_SCHEMA_DEFINITION
    from renderer import render_game_from_schema
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you are running this script from the 'genesis_ai_game_weaver' directory or have it in your PYTHONPATH.")
    sys.exit(1)

# Configure Gemini API
GEMINI_API_KEY = None
try:
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        print("Warning: GEMINI_API_KEY environment variable not set. Prompt generation will be skipped if requested.")
    else:
        genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f"Error configuring Gemini API: {e}")


def build_gemini_prompt(user_prompt_text, schema_definition_dict):
    """Builds the prompt for Gemini to generate the game schema."""
    schema_json_string = json.dumps(schema_definition_dict, indent=2)

    prompt = f"""You are an expert game design assistant. Your task is to generate a game schema in JSON format based on a user's natural language prompt.
The JSON output MUST strictly follow this structure and its type definitions:

{schema_json_string}

Key considerations for generation:
- Ensure all required fields from the schema definition are present.
- For colors, use an array of three integers (RGB, 0-255).
- For entity types, choose from the allowed enum values.
- Screen dimensions should be reasonable (e.g., width 800, height 600 for a desktop game).
- Entity positions and sizes should be within typical screen boundaries.
- For controllable entities (usually the player), set "is_controllable": true.
- Use "movement_pattern" and "speed" for entities that move automatically (e.g., "falling_down" for obstacles, "moving_left_right_patrol" for enemies).
- "player_horizontal_control" is a special movement_pattern for player entities controlled left/right by the user.
- "static" movement_pattern is for entities that don't move.
- "game_rules" can be a list of simple text strings describing objectives or win/loss conditions (e.g., "Avoid falling obstacles.", "Collect all targets.").

User prompt: "{user_prompt_text}"

Generated JSON game schema (provide only the JSON object, no extra text or markdown formatting like ```json):
"""
    return prompt

def generate_schema_from_prompt(gemini_full_prompt: str) -> dict | None:
    """
    Simulates a call to Gemini API to generate a game schema.
    In a real scenario, this would use the Gemini API.
    For simulation, it returns a predefined schema based on keywords in the prompt.
    """
    print("\n[SIMULATION] Gemini is processing the request to generate a schema...")
    # print(f"[SIMULATION] Full prompt received by simulation:\n{gemini_full_prompt[:500]}...") # For debugging

    # Simplified keyword matching for simulation
    if "obstacle dodger" in gemini_full_prompt.lower() or \
       ("blue square player" in gemini_full_prompt.lower() and "red circle obstacles" in gemini_full_prompt.lower()):
        print("[SIMULATION] Detected 'obstacle dodger' type prompt. Returning simulated obstacle dodger schema.")
        return {
            "game_title": "Simulated Obstacle Dodger",
            "screen_dimensions": {"width": 800, "height": 600},
            "background_color": [20, 20, 20],
            "entities": [
                {
                    "name": "player", "id": "player_1", "type": "player", "color": [0, 150, 255], "shape": "rectangle", 
                    "size": {"width": 40, "height": 40}, "position": {"x": 380, "y": 500}, "speed": 7,
                    "movement_pattern": "player_horizontal_control", "is_controllable": True
                },
                {
                    "name": "obstacle1", "id": "obstacle_1", "type": "obstacle", "color": [255, 50, 50], "shape": "circle",
                    "size": {"radius": 20}, "position": {"x": 100, "y": 0}, "speed": 3, # size is radius for circle
                    "movement_pattern": "falling_down", "is_controllable": False
                },
                {
                    "name": "obstacle2", "id": "obstacle_2", "type": "obstacle", "color": [255, 50, 50], "shape": "circle",
                    "size": {"radius": 25}, "position": {"x": 400, "y": -50}, "speed": 4,
                    "movement_pattern": "falling_down", "is_controllable": False
                }
            ],
            "game_rules": ["Avoid the falling red circles.", "Use arrow keys to move left and right."]
        }
    elif "faulty player" in gemini_full_prompt.lower() or ("is_controllable" in gemini_full_prompt.lower() and "missing" in gemini_full_prompt.lower()): # for testing correction
        print("[SIMULATION] Detected 'faulty player' type prompt. Returning a schema known to be faulty.")
        return {
            "game_title": "Faulty Game for Correction Test",
            "screen_dimensions": {"width": 800, "height": 600},
            "background_color": [0, 0, 50],
            "entities": [
                {
                    "name": "faulty_player", "id": "faulty_player_1", "type": "player", "color": [0, 0, 255], "shape": "rectangle",
                    "size": {"width": 50, "height": 50}, "position": [375, 500], "speed": 5, # INTENTIONALLY FAULTY position
                    "movement_pattern": "player_horizontal_control" 
                    # Missing "is_controllable": True
                }
            ],
            "game_rules": ["This schema is intentionally faulty."]
        }
    elif "simple game" in gemini_full_prompt.lower() or "red circle that falls" in gemini_full_prompt.lower():
        print("[SIMULATION] Detected 'simple game' or 'red circle' prompt. Returning a very simple schema.")
        return {
            "game_title": "Simulated Simple Game",
            "screen_dimensions": {"width": 600, "height": 400},
            "background_color": [100, 100, 100],
            "entities": [
                {
                    "name": "falling_object", "id": "object_1", "type": "obstacle", "color": [255, 0, 0], "shape": "circle",
                    "size": {"radius": 30}, "position": {"x": 300, "y": 0}, "speed": 2,
                    "movement_pattern": "falling_down", "is_controllable": False
                }
            ],
            "game_rules": ["Watch the red circle fall."]
        }
    else:
        print("[SIMULATION] Prompt not recognized for specific simulation. Returning a default basic schema.")
        return {
            "game_title": "Default Simulated Game",
            "screen_dimensions": {"width": 300, "height": 200},
            "background_color": [50, 50, 50],
            "entities": [
                {"name": "p1", "id": "p1_1", "type": "player", "color": [0,255,0], "shape": "rectangle", "size": {"width": 20, "height": 20}, "position": {"x": 10, "y": 10}, "is_controllable": True, "movement_pattern": "static", "speed": 0}
            ],
            "game_rules": ["A default game."]
        }

def build_gemini_correction_prompt(original_user_query: str, faulty_schema_json: str, error_message: str, game_schema_definition_json: str) -> str:
    """Builds a prompt for Gemini to correct a faulty game schema based on an error."""
    return f"""The user originally asked for: '{original_user_query}'.
Based on that, a game schema was generated:
{faulty_schema_json}

However, this schema failed validation with the error: '{error_message}'.

The expected schema structure is defined by this JSON Schema:
{game_schema_definition_json}

Please provide a corrected version of the game schema in JSON format that fixes the validation error and still adheres to the user's original request. Only output the corrected JSON schema.
"""

def generate_corrected_schema_from_prompt(prompt: str) -> dict | None:
    """Simulates a call to Gemini to get a corrected game schema. Returns a Python dict or None."""
    print("\n[SIMULATION] Gemini is attempting to correct the schema...")
    # For simulation, always return the standard corrected schema if this function is called.
    # This implies our simulated "Gemini" can always fix the schema for now.
    print("[SIMULATION] Returning a standard simulated corrected schema.")
    return {
        "game_title": "Top-Down Shooter - Corrected (Simulated)",
        "screen_dimensions": {"width": 800, "height": 600},
        "background_color": [20, 20, 20], # Darker background
        "entities": [
            {
                "name": "shooter_player",
                "id": "player_1", 
                "type": "player",
                "color": [0, 200, 0], # Green
                "shape": "rectangle",
                "size": {"width": 40, "height": 40}, 
                "position": {"x": 380, "y": 500}, 
                "is_controllable": True,
                "movement_pattern": "player_omni_directional_control",
                "speed": 4,
                "health_points": 10,
                "can_shoot": True,
                "projectile_archetype": {
                    "id_prefix": "p_bullet_",
                    "name_prefix": "Player Bullet ",
                    "type": "projectile",
                    "shape": "circle",
                    "size": {"radius": 5},
                    "color": [0, 255, 255], # Cyan bullets
                    "speed": 12,
                    "movement_pattern": "projectile_movement", # Assumes upwards for now
                    "damage": 1,
                    "cooldown_ms": 200 # Faster shooting
                }
            },
            {
                "name": "basic_enemy_1",
                "id": "enemy_1",
                "type": "enemy",
                "color": [200, 0, 0], # Red
                "shape": "rectangle",
                "size": {"width": 50, "height": 50},
                "position": {"x": 100, "y": 100},
                "movement_pattern": "static", # Simple static enemy
                "speed": 0,
                "health_points": 3,
                "is_controllable": False
            },
            {
                "name": "basic_enemy_2",
                "id": "enemy_2",
                "type": "enemy",
                "color": [200, 0, 0], # Red
                "shape": "rectangle",
                "size": {"width": 50, "height": 50},
                "position": {"x": 650, "y": 150},
                "movement_pattern": "static",
                "speed": 0,
                "health_points": 3,
                "is_controllable": False
            }
        ],
        "game_rules": [
            "Top-Down Shooter!",
            "Use Arrow Keys to Move. Space to Shoot.",
            "Destroy the red enemies."
        ]
    }



def load_game_from_json_file(file_path):
    """Loads game data from a JSON file."""
    try:
        with open(file_path, 'r') as f:
            game_data = json.load(f)
        print(f"Successfully loaded game data from {file_path}")
        return game_data
    except FileNotFoundError:
        print(f"Error: Game schema file not found at {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file {file_path}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while loading {file_path}: {e}")
        return None


def get_game_idea_from_user() -> str:
    """Prompts the user for their game idea and returns the input."""
    while True:
        idea = input("Please describe the game you'd like to create (e.g., 'a blue square player at bottom, red circle obstacles falling from top'): ")
        if idea.strip():
            return idea.strip()
        print("Input cannot be empty. Please describe your game idea.")

def main():
    CORRECTION_PROMPT_SUFFIX = "Please provide a corrected version of the game schema in JSON format that fixes the validation error. Only output the corrected JSON schema."
    parser = argparse.ArgumentParser(description="Genesis AI Game Weaver - POC Main Runner")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--json_file", help="Path to the game schema JSON file.")
    group.add_argument("--prompt", help="Natural language prompt to generate the game schema.")
    # parser.add_argument("--run_live", action="store_true", help="Run the game in a live loop instead of saving a single frame.") # Removed duplicate

    parser.add_argument(
        "--output_image",
        default="rendered_game.png",
        help="Path to save the rendered game frame."
    )
    parser.add_argument(
        "--output_json",
        default="generated_game.json",
        help="Path to save the JSON schema generated from a prompt."
    )
    parser.add_argument(
        "--run_live",
        action="store_true",
        help="Run the game with a live Pygame window instead of just saving a frame."
    )

    args = parser.parse_args()

    game_data = None
    schema_source_type = None  # To track 'file', 'prompt_arg', or 'user_input'
    original_user_prompt_text = None # Store the original text from user/arg for potential re-prompting

    # Construct absolute path for output_json (used if schema is generated)
    if not os.path.isabs(args.output_json):
        output_json_abs_path = os.path.join(project_root, args.output_json)
    else:
        output_json_abs_path = args.output_json

    if args.json_file:
        # Construct absolute path for json_file if it's relative
        if not os.path.isabs(args.json_file):
            json_file_abs_path = os.path.join(project_root, args.json_file)
        else:
            json_file_abs_path = args.json_file
        
        print(f"Attempting to load schema from: {json_file_abs_path}")
        game_data = load_game_from_json_file(json_file_abs_path)
        schema_source_type = "file"
        if game_data is None:
            print(f"Error: Could not load game from JSON file: {json_file_abs_path}. Exiting.")
            return 1

    elif args.prompt:
        original_user_prompt_text = args.prompt
        print(f"Using prompt from argument: \"{original_user_prompt_text}\"")
        
        gemini_full_prompt = build_gemini_prompt(original_user_prompt_text, GAME_SCHEMA_DEFINITION)
        # print(f"\n--- Gemini Prompt (from arg) ---\n{gemini_full_prompt}\n--- End of Gemini Prompt ---\n")
        
        game_data = generate_schema_from_prompt(gemini_full_prompt) # Simulates Gemini call
        schema_source_type = "prompt_arg"
        if game_data is None:
            print("Error: Gemini simulation failed to generate schema from prompt argument. Exiting.")
            return 1
        else:
            try:
                with open(output_json_abs_path, 'w') as f:
                    json.dump(game_data, f, indent=4)
                print(f"Generated schema (from arg prompt) saved to {output_json_abs_path}")
            except Exception as e:
                print(f"Error saving generated schema to {output_json_abs_path}: {e}")
    
    else: # Neither --json_file nor --prompt argument was given
        print("No JSON file or --prompt argument provided. Let's create a game from your idea!")
        original_user_prompt_text = get_game_idea_from_user()
        print(f"Processing your idea: \"{original_user_prompt_text}\"")

        gemini_full_prompt = build_gemini_prompt(original_user_prompt_text, GAME_SCHEMA_DEFINITION)
        # print(f"\n--- Gemini Prompt (from user input) ---\n{gemini_full_prompt}\n--- End of Gemini Prompt ---\n")

        game_data = generate_schema_from_prompt(gemini_full_prompt) # Simulates Gemini call
        schema_source_type = "user_input"
        if game_data is None:
            print("Error: Gemini simulation failed to generate schema from user input. Exiting.")
            return 1
        else:
            try:
                with open(output_json_abs_path, 'w') as f:
                    json.dump(game_data, f, indent=4)
                print(f"Generated schema (from user input) saved to {output_json_abs_path}")
            except Exception as e:
                print(f"Error saving generated schema to {output_json_abs_path}: {e}")

    if game_data is None: # Should be caught by specific error messages above, but as a safeguard
        print("Critical Error: No game data available after attempting all input methods. Exiting.")
        return 1



    MAX_CORRECTION_ATTEMPTS = 1 # In a real scenario, might be 2 or 3
    attempts = 0
    is_valid_schema = False
    original_prompt_for_correction = original_user_prompt_text # This was set earlier based on schema_source_type

    current_game_data = game_data # Use a temporary variable for potential modifications

    while attempts <= MAX_CORRECTION_ATTEMPTS and not is_valid_schema:
        try:
            print(f"Attempting to validate game schema (Attempt {attempts + 1})...")
            validate_game_schema(current_game_data) # Validate current_game_data
            is_valid_schema = True
            print("Schema is valid after validation.")
            game_data = current_game_data # Persist validated data
        except jsonschema.exceptions.ValidationError as e:
            print(f"Schema validation failed (Attempt {attempts + 1} of {MAX_CORRECTION_ATTEMPTS + 1}): {e.message}")
            attempts += 1
            if attempts <= MAX_CORRECTION_ATTEMPTS:
                print("Attempting to correct schema with Gemini (Simulated)...")
                correction_prompt_for_gemini = None
                if schema_source_type == "file":
                    file_path_for_message = json_file_abs_path if 'json_file_abs_path' in locals() else args.json_file
                    correction_prompt_for_gemini = (
                        f"The game schema from file '{file_path_for_message}' has a validation error: '{e.message}'. "
                        f"Original schema: {json.dumps(current_game_data)}. "
                        f"{CORRECTION_PROMPT_SUFFIX}"
                    )
                elif original_prompt_for_correction: # prompt_arg or user_input
                    game_schema_def_json_str = json.dumps(GAME_SCHEMA_DEFINITION, indent=2)
                    correction_prompt_for_gemini = (
                        f"The user's game idea was: \"{original_prompt_for_correction}\". "
                        f"The generated schema failed validation with error: \"{e.message}\". "
                        f"Original (faulty) schema: {json.dumps(current_game_data)}. "
                        f"The game schema must conform to this JSON Schema definition: {game_schema_def_json_str}. "
                        f"{CORRECTION_PROMPT_SUFFIX}"
                    )

                if correction_prompt_for_gemini:
                    print(f"[SIMULATION] Using correction prompt for Gemini: '{correction_prompt_for_gemini[:150]}...'" )
                    corrected_data = generate_corrected_schema_from_prompt(correction_prompt_for_gemini)
                    print(f"[DEBUG] In main, corrected_data is None: {corrected_data is None}")
                    if corrected_data:
                        current_game_data = corrected_data # Update current_game_data for next validation attempt
                        # Save the corrected schema
                        if schema_source_type == "file":
                            corrected_filename = "corrected_" + (args.json_file.split('/')[-1])
                        else: # prompt_arg or user_input
                            corrected_filename = "corrected_" + (output_json_abs_path.split('/')[-1])
                        
                        # Ensure project_root is defined (should be at the start of main)
                        corrected_schema_path = os.path.join(project_root, corrected_filename)
                        try:
                            with open(corrected_schema_path, 'w') as f_corrected:
                                json.dump(current_game_data, f_corrected, indent=4)
                            print(f"Corrected schema saved to {corrected_schema_path}")
                        except Exception as save_err:
                            print(f"Error saving corrected schema to {corrected_schema_path}: {save_err}")
                        continue # Retry validation with corrected data
                    else:
                        print("Gemini (Simulated) failed to provide a corrected schema. Cannot proceed with this attempt.")
                        # No more attempts if Gemini fails to provide correction
                        break # Exit the while loop
                else:
                    print("Could not generate a correction prompt. Cannot proceed with this attempt.")
                    break # Exit the while loop
            # If correction failed or not attempted, and still not valid, loop will exit or error out
            else: # Max attempts for correction loop reached
                print(f"Max correction attempts ({MAX_CORRECTION_ATTEMPTS +1 }) reached. Schema is still invalid after the last attempt.")
                is_valid_schema = False # Ensure it's marked as invalid
                break # Exit the while loop
        except Exception as e:
            print(f"An unexpected error occurred during schema validation: {e}")
            return

    if not is_valid_schema:
        print("Could not obtain a valid game schema after attempts. Exiting.")
        return

    # Construct absolute path for output_image
    if not os.path.isabs(args.output_image):
        output_image_abs_path = os.path.join(project_root, args.output_image)
    else:
        output_image_abs_path = args.output_image
        
    print(f"Rendering game. Output image: {output_image_abs_path}, Run live: {args.run_live}")
    try:
        if not args.run_live and os.environ.get('SDL_VIDEODRIVER') is None:
            os.environ['SDL_VIDEODRIVER'] = 'dummy'
            print("Set SDL_VIDEODRIVER to dummy for headless rendering.")

        render_game_from_schema(
            game_data,
            output_image_path=output_image_abs_path,
            run_loop=args.run_live
        )
        if not args.run_live:
            print(f"Game frame should be saved to {output_image_abs_path}")
        else:
            print("Game loop finished.")
    except Exception as e:
        print(f"An error occurred during game rendering: {e}")

if __name__ == "__main__":
    main()
