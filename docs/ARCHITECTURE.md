# هيكلية مشروع Genesis AI Game Weaver

## 1. نظرة عامة (Overview)

يعتمد مشروع Genesis AI Game Weaver على بنية معيارية (modular) تهدف إلى فصل الاهتمامات المختلفة (separation of concerns) لتسهيل التطوير والصيانة. المكونات الرئيسية هي:

1.  **واجهة المستخدم (User Interface - حاليًا CLI):** لاستقبال أوامر المستخدم وتحديد مصدر مخطط اللعبة.
2.  **نواة المعالجة (Core Logic - `main.py`):** تنسيق عملية تحميل المخطط، التحقق منه، تصحيحه (بالمحاكاة)، وتمريره للعرض.
3.  **مدقق مخطط اللعبة (Schema Validator - `game_schema_validator.py`):** تعريف هيكل مخطط اللعبة والتحقق من صحته.
4.  **محاكي الذكاء الاصطناعي (AI Simulator - دوال داخل `main.py`):** محاكاة قدرة نماذج اللغة الكبيرة على توليد وتصحيح المخططات.
5.  **محرك عرض الألعاب (Game Renderer - `renderer.py`):** تحويل مخطط اللعبة إلى تجربة بصرية وتفاعلية باستخدام Pygame.

## 2. هيكل الملفات والمجلدات (File & Directory Structure)

```
/genesis_ai_game_weaver
|-- main.py                     # نقطة الدخول الرئيسية، إدارة سير العمل، محاكاة AI
|-- renderer.py                 # محرك عرض الألعاب باستخدام Pygame
|-- game_schema_validator.py    # تعريف JSON Schema للعبة والتحقق من صحته
|-- faulty_game_schema.json     # مثال على مخطط لعبة خاطئ للاختبار
|-- generated_game.json         # مثال على مخطط لعبة تم "توليده" (بالمحاكاة)
|-- corrected_faulty_game_schema.json # ناتج تصحيح المخطط الخاطئ (بالمحاكاة)
|-- rendered_game.png           # إطار واحد يتم حفظه إذا لم يتم التشغيل بـ --run_live
|-- README.md                   # الملف التعريفي الرئيسي للمشروع
|-- docs/                       # مجلد التوثيق
|   |-- PROJECT_VISION.md       # الرؤية الكاملة وخريطة الطريق
|   |-- ARCHITECTURE.md         # هذا الملف (هيكلية المشروع)
|   |-- HOW_TO_RUN.md           # دليل التشغيل والتجربة
|   |-- GAME_SCHEMA_FORMAT.md   # شرح تنسيق مخطط اللعبة
|   |-- AI_SIMULATION.md        # شرح محاكاة الذكاء الاصطناعي
|   |-- EXAMPLES.md             # أمثلة على مخططات ألعاب
|   |-- (contributing.md)       # (مستقبلي: للمساهمين)
```

## 3. شرح الملفات والمكونات الرئيسية

### `main.py`

*   **الوظيفة:** هو الملف التنفيذي الرئيسي ونقطة انطلاق البرنامج. ينسق العمليات المختلفة.
*   **المكونات الرئيسية:**
    *   **`ArgumentParser`:** لمعالجة وسائط سطر الأوامر مثل `--json_file`, `--prompt`, `--run_live`.
    *   **`load_game_from_json_file(file_path)`:** تحميل مخطط اللعبة من ملف JSON.
    *   **`validate_game_schema(data_to_validate, schema_definition, attempt_number, max_attempts)`:** التحقق من صحة مخطط اللعبة مقابل `GAME_SCHEMA_DEFINITION`. إذا فشل التحقق، يحاول استدعاء نظام التصحيح.
    *   **`generate_schema_from_prompt(prompt: str)` (محاكاة):**
        *   تحاكي استدعاء نموذج لغة كبير (LLM) لتوليد مخطط لعبة جديد بناءً على وصف نصي من المستخدم.
        *   حاليًا، تحتوي على منطق مبسط يعتمد على كلمات مفتاحية في الـ `prompt` لإرجاع مخططات مُعدة مسبقًا.
    *   **`build_gemini_correction_prompt(...)` (محاكاة):**
        *   تُنشئ الـ "prompt" (النص التوجيهي) الذي سيتم (نظريًا) إرساله إلى Gemini لتصحيح مخطط خاطئ. يتضمن هذا الـ prompt وصف الخطأ، المخطط الخاطئ، وتعريف مخطط اللعبة الصحيح.
    *   **`generate_corrected_schema_from_prompt(prompt: str)` (محاكاة):**
        *   تحاكي استدعاء Gemini لتصحيح مخطط لعبة خاطئ.
        *   حاليًا، تُرجع دائمًا مخططًا مُعدًا مسبقًا يمثل النسخة المصححة (مثل مخطط لعبة Top-Down Shooter).
    *   **`main()`:** الدالة الرئيسية التي تدير سير العمل:
        1.  تحليل وسائط سطر الأوامر.
        2.  إذا تم توفير `--prompt` (مستقبلي)، تستدعي `generate_schema_from_prompt`.
        3.  إذا تم توفير `--json_file`، تستدعي `load_game_from_json_file`.
        4.  تستدعي `validate_game_schema` للتحقق من المخطط. إذا فشل التحقق وتم تفعيل التصحيح، تستدعي `generate_corrected_schema_from_prompt` ثم تعيد التحقق.
        5.  إذا كان المخطط صحيحًا، تستدعي `render_game_from_schema` من `renderer.py`.

### `renderer.py`

*   **الوظيفة:** مسؤول عن تحويل مخطط اللعبة (JSON) إلى لعبة مرئية وتفاعلية باستخدام مكتبة Pygame.
*   **المكونات الرئيسية:**
    *   **`DEFAULT_GAME_SCHEMA_FOR_RENDERER_TEST`:** مخطط لعبة افتراضي بسيط يُستخدم عند تشغيل `renderer.py` مباشرة للاختبار.
    *   **`render_game_from_schema(game_schema, output_image_path="frame.png", run_loop=False)`:** الدالة الأساسية التي تقوم بكل أعمال العرض.
        1.  **الإعداد الأولي:** تهيئة Pygame، إعداد الشاشة (الأبعاد، العنوان، لون الخلفية) بناءً على `game_schema`.
        2.  **تحميل الخطوط وعرض قواعد اللعبة:** تحميل خط لعرض النصوص، وعرض `game_rules` من المخطط.
        3.  **معالجة الكيانات (Entities):**
            *   تحويل كل كيان في `game_schema["entities"]` إلى كائن Pygame `Rect` وتخزين خصائصه (اللون، نمط الحركة، السرعة، إلخ) في قائمة `active_entities`.
            *   تحديد الكيان الذي يتحكم به اللاعب (`player_entity`).
        4.  **حلقة اللعبة الرئيسية (Game Loop - إذا `run_loop` كان `True`):**
            *   **معالجة الأحداث (Events):** الاستماع لأحداث مثل إغلاق النافذة أو ضغطات المفاتيح.
            *   **التحكم باللاعب:** تحديث موقع اللاعب بناءً على ضغطات المفاتيح (الأسهم، Space للإطلاق) ونمط الحركة المحدد له في المخطط (`player_horizontal_control`, `player_omni_directional_control`).
            *   **إطلاق المقذوفات:** إذا كان اللاعب يستطيع إطلاق النار (`can_shoot`) وتم الضغط على مفتاح الإطلاق، يتم إنشاء مقذوف جديد بناءً على `projectile_archetype` الخاص باللاعب، مع تطبيق نظام تهدئة (cooldown).
            *   **تحديث الكيانات الأخرى:** تحديث مواقع الكيانات الأخرى بناءً على أنماط حركتها (`falling_down`, `moving_left_right_patrol`, `projectile_movement`, `static`).
                *   إزالة المقذوفات إذا خرجت من الشاشة أو انتهت مدة بقائها.
            *   **اكتشاف الاصطدامات (Collision Detection):**
                *   بين اللاعب والكيانات الأخرى (أعداء، عقبات).
                *   بين المقذوفات والأعداء.
                *   تطبيق التأثيرات: طباعة رسائل، تقليل نقاط الصحة، إزالة الكيانات المدمرة من `active_entities`.
            *   **الرسم (Drawing):**
                *   مسح الشاشة بلون الخلفية.
                *   رسم كل الكيانات النشطة (`active_entities`) بأشكالها وألوانها ومواقعها المحدثة.
                *   رسم حدود حول الكيان الذي يتحكم به اللاعب.
                *   عرض قواعد اللعبة.
                *   عرض نقاط صحة اللاعب.
                *   تحديث الشاشة (`pygame.display.flip()`).
                *   التحكم في معدل الإطارات (`clock.tick(FPS)`).
        5.  **حفظ إطار واحد (إذا `run_loop` كان `False`):** رسم الحالة الأولية للعبة وحفظها كصورة.
        6.  **التنظيف:** `pygame.quit()`.

### `game_schema_validator.py`

*   **الوظيفة:** يحتوي على التعريف الرسمي لهيكل مخطط اللعبة (JSON Schema) ويستخدم للتحقق من صحة أي مخطط لعبة يتم تحميله أو توليده.
*   **المكونات الرئيسية:**
    *   **`GAME_SCHEMA_DEFINITION` (قاموس Python):** هذا هو الـ JSON Schema الفعلي. يحدد الحقول المطلوبة والاختيارية لكل جزء من مخطط اللعبة (مثل `game_title`, `screen_dimensions`, `entities`, وخصائص كل كيان مثل `id`, `type`, `shape`, `color`, `position`, `size`, `movement_pattern`, `speed`, `health_points`, `can_shoot`, `projectile_archetype`, إلخ)، وأنواع البيانات المتوقعة لكل حقل.
    *   هذا الملف لا يحتوي على دوال تنفيذية مباشرة، بل يتم استيراد `GAME_SCHEMA_DEFINITION` منه في `main.py` لاستخدامه مع مكتبة `jsonschema`.

### ملفات JSON (`*.json`)

*   **`faulty_game_schema.json`:** مثال على مخطط لعبة يحتوي على خطأ متعمد (مثل نوع بيانات خاطئ لحقل `position`). يستخدم لاختبار قدرة النظام على اكتشاف الأخطاء ومحاكاة تصحيحها.
*   **`generated_game.json`:** مثال على مخطط لعبة يمكن اعتباره ناتجًا أوليًا من محاكاة `generate_schema_from_prompt`. (ملاحظة: حاليًا، قد يتم الكتابة فوق هذا الملف أو `corrected_faulty_game_schema.json` أثناء الاختبارات إذا كان اسم ملف الإخراج هو نفسه).
*   **`corrected_faulty_game_schema.json`:** الملف الذي يتم فيه حفظ المخطط المصحح (بالمحاكاة) بعد اكتشاف خطأ في `faulty_game_schema.json`.

## 4. تدفق البيانات والتحكم (Data & Control Flow)

1.  يبدأ المستخدم بتشغيل `main.py` مع وسائط (مثل مسار ملف JSON أو prompt نصي).
2.  `main.py` يحمل/يولد مخطط اللعبة الأولي.
3.  يتم تمرير المخطط إلى `validate_game_schema` (داخل `main.py`) للتحقق من صحته باستخدام `GAME_SCHEMA_DEFINITION` من `game_schema_validator.py`.
4.  إذا كان المخطط خاطئًا، تحاول `main.py` (بالمحاكاة) تصحيحه باستخدام `generate_corrected_schema_from_prompt` وتعيد التحقق.
5.  إذا أصبح المخطط صحيحًا، يتم تمريره إلى `render_game_from_schema` في `renderer.py`.
6.  `renderer.py` يقرأ المخطط، يهيئ Pygame، وينشئ الكيانات وحلقة اللعبة.
7.  أثناء حلقة اللعبة، يتفاعل المستخدم (إذا كانت اللعبة تفاعلية)، ويقوم `renderer.py` بتحديث حالة اللعبة ورسمها على الشاشة.

## 5. الاعتماديات الرئيسية (Key Dependencies)

*   **Python 3.x:** لغة البرمجة الأساسية.
*   **Pygame:** مكتبة لتطوير الألعاب ثنائية الأبعاد (الرسومات، الصوت، الإدخال).
*   **jsonschema:** مكتبة للتحقق من صحة بيانات JSON مقابل مخطط JSON Schema.
*   **(مستقبلي) google-generativeai:** مكتبة للتفاعل مع Gemini API.
