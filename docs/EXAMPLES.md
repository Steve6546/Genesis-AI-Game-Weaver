# أمثلة على مخططات الألعاب (Game Schema Examples)

هذا الملف يحتوي على أمثلة كاملة لمخططات ألعاب بصيغة JSON يمكن استخدامها مع مشروع Genesis AI Game Weaver. يمكنك استخدام هذه الأمثلة كنقطة انطلاق لفهم كيفية بناء مخططات الألعاب الخاصة بك أو لاختبار النظام.

## مثال 1: لعبة إطلاق نار من منظور علوي (Top-Down Shooter)

هذا المثال يمثل مخطط لعبة Top-Down Shooter الذي يتم استخدامه حاليًا في محاكاة تصحيح الأخطاء (`generate_corrected_schema_from_prompt` في `main.py`).

```json
{
    "game_title": "Top-Down Shooter - Corrected (Simulated)",
    "screen_dimensions": {"width": 800, "height": 600},
    "background_color": [20, 20, 20],
    "entities": [
        {
            "name": "shooter_player",
            "id": "player_1", 
            "type": "player",
            "color": [0, 200, 0],
            "shape": "rectangle",
            "size": {"width": 40, "height": 40}, 
            "position": {"x": 380, "y": 500}, 
            "is_controllable": true,
            "movement_pattern": "player_omni_directional_control",
            "speed": 4,
            "health_points": 10,
            "can_shoot": true,
            "projectile_archetype": {
                "id_prefix": "p_bullet_",
                "name_prefix": "Player Bullet ",
                "type": "projectile",
                "shape": "circle",
                "size": {"radius": 5},
                "color": [0, 255, 255],
                "speed": 12,
                "movement_pattern": "projectile_movement",
                "damage": 1,
                "cooldown_ms": 200,
                "lifespan_ms": 3000
            }
        },
        {
            "name": "basic_enemy_1",
            "id": "enemy_1",
            "type": "enemy",
            "color": [200, 0, 0],
            "shape": "rectangle",
            "size": {"width": 50, "height": 50},
            "position": {"x": 100, "y": 100},
            "movement_pattern": "static",
            "speed": 0,
            "health_points": 3,
            "is_controllable": false
        },
        {
            "name": "basic_enemy_2",
            "id": "enemy_2",
            "type": "enemy",
            "color": [200, 0, 0],
            "shape": "rectangle",
            "size": {"width": 50, "height": 50},
            "position": {"x": 650, "y": 150},
            "movement_pattern": "static",
            "speed": 0,
            "health_points": 3,
            "is_controllable": false
        },
        {
            "name": "patrolling_enemy_1",
            "id": "enemy_3_patrol",
            "type": "enemy",
            "color": [200, 100, 0], /* Orange */
            "shape": "rectangle",
            "size": {"width": 60, "height": 30},
            "position": {"x": 50, "y": 250},
            "movement_pattern": "moving_left_right_patrol",
            "speed": 2,
            "health_points": 5,
            "is_controllable": false
        }
    ],
    "game_rules": [
        "Top-Down Shooter!",
        "Use Arrow Keys to Move. Space to Shoot.",
        "Destroy the red and orange enemies."
    ]
}
```

**شرح الميزات في هذا المثال:**

*   **لاعب (`shooter_player`):**
    *   يتحرك في جميع الاتجاهات (`player_omni_directional_control`).
    *   يمكنه إطلاق النار (`can_shoot: true`).
    *   لديه 10 نقاط صحة.
    *   يطلق مقذوفات دائرية سماوية (`projectile_archetype`) سريعة، ذات ضرر، ولها مدة بقاء وفترة تهدئة.
*   **أعداء ثابتون (`basic_enemy_1`, `basic_enemy_2`):**
    *   لونهم أحمر ولا يتحركون.
    *   لديهم 3 نقاط صحة.
*   **عدو دورية (`patrolling_enemy_1`):**
    *   لونه برتقالي.
    *   يتحرك أفقيًا يمينًا ويسارًا (`moving_left_right_patrol`).
    *   لديه 5 نقاط صحة.
*   **قواعد اللعبة:** توضح كيفية اللعب والهدف.

## مثال 2: لعبة بسيطة (لاعب وعقبة ساقطة)

هذا مثال على مخطط لعبة أبسط، مشابه لما قد يتم إنشاؤه بواسطة `generated_game.json` أو عند طلب لعبة بسيطة من محاكي `generate_schema_from_prompt`.

```json
{
    "game_title": "Simple Dodger Game",
    "screen_dimensions": {"width": 600, "height": 400},
    "background_color": [50, 50, 50],
    "entities": [
        {
            "name": "dodger_player",
            "id": "player_main",
            "type": "player",
            "color": [0, 128, 255],
            "shape": "rectangle",
            "size": {"width": 50, "height": 50},
            "position": {"x": 275, "y": 340},
            "is_controllable": true,
            "movement_pattern": "player_horizontal_control",
            "speed": 7
        },
        {
            "name": "falling_ball",
            "id": "obstacle_1",
            "type": "obstacle",
            "color": [255, 0, 0],
            "shape": "circle",
            "size": {"radius": 20},
            "position": {"x": 300, "y": 0},
            "movement_pattern": "falling_down",
            "speed": 4,
            "is_controllable": false
        }
    ],
    "game_rules": [
        "Move the player left and right.",
        "Avoid the falling red ball!"
    ]
}
```

**شرح الميزات في هذا المثال:**

*   **لاعب (`dodger_player`):**
    *   يتحرك أفقيًا فقط (`player_horizontal_control`).
*   **عقبة (`falling_ball`):**
    *   دائرة حمراء تسقط من الأعلى (`falling_down`).
    *   عندما تصل إلى أسفل الشاشة، تعود للظهور في الأعلى (قد يكون في موقع أفقي مختلف).

يمكنك نسخ هذه الأمثلة وحفظها في ملفات `.json` خاصة بك (مثل `my_top_down_shooter.json`) ثم تشغيلها باستخدام الأمر:

```bash
python main.py --json_file my_top_down_shooter.json --run_live
```

(تأكد من أنك في مجلد `/workspace/genesis_ai_game_weaver/` عند تشغيل الأمر، أو قم بتعديل المسار إلى ملف JSON).
