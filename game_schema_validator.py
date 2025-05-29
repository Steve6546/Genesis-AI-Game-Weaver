import jsonschema

GAME_SCHEMA_DEFINITION = {
    "type": "object",
    "properties": {
        "game_title": {"type": "string", "minLength": 1},
        "screen_dimensions": {
            "type": "object",
            "properties": {
                "width": {"type": "integer", "minimum": 100},
                "height": {"type": "integer", "minimum": 100}
            },
            "required": ["width", "height"]
        },
        "background_color": {
            "type": "array",
            "items": {"type": "integer", "minimum": 0, "maximum": 255},
            "minItems": 3,
            "maxItems": 3
        },
        "entities": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "minLength": 1},
                    "type": {
                        "type": "string",
                        "enum": ["player", "enemy", "target", "platform", "collectible", "obstacle"]
                    },
                    "color": {
                        "type": "array",
                        "items": {"type": "integer", "minimum": 0, "maximum": 255},
                        "minItems": 3,
                        "maxItems": 3
                    },
                    "position": {
                        "type": "object",
                        "properties": {
                            "x": {"type": "integer"},
                            "y": {"type": "integer"}
                        },
                        "required": ["x", "y"]
                    },
                    "size": { "oneOf": [
                            {
                                "type": "object",
                                "properties": {
                                    "width": {"type": "integer", "minimum": 1},
                                    "height": {"type": "integer", "minimum": 1}
                                },
                                "required": ["width", "height"],
                                "description": "For rectangles or shapes defined by width and height."
                            },
                            {
                                "type": "object",
                                "properties": {
                                    "radius": {"type": "integer", "minimum": 1}
                                },
                                "required": ["radius"],
                                "description": "For circles or shapes defined by a radius."
                            }
                        ]
                    },
                    "is_controllable": {"type": "boolean", "default": False},
                    "movement_pattern": {
                        "type": "string",
                        "enum": ["static", "falling_down", "moving_left_right_patrol", "player_horizontal_control", "player_omni_directional_control", "projectile_movement"],
                        "default": "static"
                    },
                    "speed": {"type": "integer", "minimum": 0, "default": 0},
                    "health_points": {
                        "type": "integer",
                        "minimum": 0,
                        "description": "Health points for the entity. If 0, entity might be considered destroyed."
                    },
                    "can_shoot": {
                        "type": "boolean",
                        "default": False,
                        "description": "Determines if the entity can shoot projectiles."
                    },
                    "projectile_archetype": {
                        "type": "object",
                        "description": "Describes the projectiles fired by this entity, if can_shoot is true.",
                        "properties": {
                            "id_prefix": {"type": "string", "default": "proj_"},
                            "name_prefix": {"type": "string", "default": "Projectile "},
                            "type": {"type": "string", "default": "projectile"},
                            "shape": {
                                "type": "string",
                                "enum": ["rectangle", "circle"],
                                "default": "rectangle"
                            },
                            "size": { "oneOf": [
                                {
                                    "type": "object",
                                    "properties": {
                                        "width": {"type": "integer", "minimum": 1},
                                        "height": {"type": "integer", "minimum": 1}
                                    },
                                    "required": ["width", "height"]
                                },
                                {
                                    "type": "object",
                                    "properties": {
                                        "radius": {"type": "integer", "minimum": 1}
                                    },
                                    "required": ["radius"]
                                }
                            ]},
                            "color": {
                                "type": "array",
                                "items": {"type": "integer", "minimum": 0, "maximum": 255},
                                "minItems": 3,
                                "maxItems": 3,
                                "default": [255, 255, 0]
                            },
                            "speed": {"type": "integer", "minimum": 1, "default": 10},
                            "movement_pattern": {
                                "type": "string",
                                "enum": ["projectile_movement"], 
                                "default": "projectile_movement"
                            },
                            "damage": {"type": "integer", "minimum": 0, "default": 1},
                            "lifespan_ms": {
                                "type": "integer",
                                "minimum": 0,
                                "description": "Optional. Duration in milliseconds before projectile disappears. 0 or undefined means infinite."
                            }
                        },
                        "required": ["shape", "size", "color", "speed", "movement_pattern", "damage"]
                    }
                    # Future properties like "image_asset" can be added here
                },
                "required": ["id", "type", "color", "position", "size"]
            }
        },
        "game_rules": { # New top-level property
            "type": "array",
            "items": {"type": "string"},
            "description": "List of simple game rules or objectives."
        }
    },
    "required": ["game_title", "screen_dimensions", "entities"] # game_rules is optional for now
}

def validate_game_schema(game_data):
    """
    Validates the given game_data dictionary against the GAME_SCHEMA_DEFINITION.
    Returns True if valid, raises jsonschema.exceptions.ValidationError otherwise.
    """
    try:
        jsonschema.validate(instance=game_data, schema=GAME_SCHEMA_DEFINITION)
        print("Schema validation successful.")
        return True
    except jsonschema.exceptions.ValidationError as err:
        print(f"Schema validation error: {err.message}")
        # print(f"Error path: {list(err.path)}") # More detailed path
        # print(f"Validator: {err.validator} = {err.validator_value}") # Validator that failed
        raise # Re-raise the exception to be handled by the caller
    except Exception as e:
        print(f"An unexpected error occurred during schema validation: {e}")
        raise

if __name__ == '__main__':
    # Example of using the validator with the schema from renderer.py
    # (We'll move DEFAULT_GAME_SCHEMA to a JSON file later)
    DEFAULT_GAME_SCHEMA_FOR_TESTING = {
        "game_title": "My First Genesis Game",
        "screen_dimensions": {
            "width": 800,
            "height": 600
        },
        "background_color": [30, 30, 30], # Changed to list for schema
        "entities": [
            {
                "id": "player",
                "type": "player",
                "color": [0, 128, 255], # Changed to list
                "position": {"x": 50, "y": 50},
                "size": {"width": 50, "height": 50}
            },
            {
                "id": "target",
                "type": "target",
                "color": [255, 0, 0], # Changed to list
                "position": {"x": 600, "y": 400},
                "size": {"width": 70, "height": 70}
            },
            {
                "id": "platform_1",
                "type": "platform",
                "color": [0, 255, 0], # Changed to list
                "position": {"x": 100, "y": 500},
                "size": {"width": 200, "height": 20}
            }
        ]
    }

    print("Testing with a valid schema:")
    try:
        validate_game_schema(DEFAULT_GAME_SCHEMA_FOR_TESTING)
    except Exception as e:
        print(f"Validation failed for valid schema (unexpected): {e}")

    print("\nTesting with an invalid schema (missing game_title):")
    invalid_schema_missing_title = DEFAULT_GAME_SCHEMA_FOR_TESTING.copy()
    del invalid_schema_missing_title["game_title"]
    try:
        validate_game_schema(invalid_schema_missing_title)
    except jsonschema.exceptions.ValidationError:
        print("Validation correctly failed for missing title.")
    except Exception as e:
        print(f"Validation error was not a ValidationError (unexpected): {e}")


    print("\nTesting with an invalid schema (wrong entity type):")
    invalid_schema_wrong_type = DEFAULT_GAME_SCHEMA_FOR_TESTING.copy()
    # Create a deep copy of entities to modify one
    import copy
    invalid_schema_wrong_type["entities"] = copy.deepcopy(invalid_schema_wrong_type["entities"])
    invalid_schema_wrong_type["entities"][0]["type"] = "unknown_type" # This type is not in enum
    try:
        validate_game_schema(invalid_schema_wrong_type)
    except jsonschema.exceptions.ValidationError:
        print("Validation correctly failed for wrong entity type.")
    except Exception as e:
        print(f"Validation error was not a ValidationError (unexpected): {e}")

    print("\nTesting with an invalid schema (color as tuple instead of list):")
    invalid_schema_color_tuple = DEFAULT_GAME_SCHEMA_FOR_TESTING.copy()
    invalid_schema_color_tuple["entities"] = copy.deepcopy(invalid_schema_color_tuple["entities"])
    invalid_schema_color_tuple["entities"][0]["color"] = (0, 128, 255) # Tuple instead of list
    try:
        validate_game_schema(invalid_schema_color_tuple)
    except jsonschema.exceptions.ValidationError:
        print("Validation correctly failed for color as tuple.")
    except Exception as e:
        print(f"Validation error was not a ValidationError (unexpected): {e}")
