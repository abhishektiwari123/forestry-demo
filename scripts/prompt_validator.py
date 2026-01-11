#!/usr/bin/env python3
"""
Comprehensive Prompt Validation Module for Pokemon AI Video Generator.

Validates prompts against best practices for:
1. Image generation (Nano Banana Pro)
2. Video generation (Kling 2.6)
3. Scene descriptions
4. Motion prompts

Based on SOPs and best practices from the project.
"""

import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PromptValidationResult:
    """Result of prompt validation."""
    prompt_type: str  # "image", "video", "scene"
    passed: bool
    score: float  # 0.0 - 1.0
    issues: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    suggestions: list = field(default_factory=list)
    improved_prompt: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "prompt_type": self.prompt_type,
            "passed": self.passed,
            "score": self.score,
            "issues": self.issues,
            "warnings": self.warnings,
            "suggestions": self.suggestions,
            "improved_prompt": self.improved_prompt
        }


# =============================================================================
# BEST PRACTICES DEFINITIONS
# =============================================================================

IMAGE_PROMPT_BEST_PRACTICES = {
    # Required elements for Pokemon battle scenes
    "required_patterns": [
        (r"\b(charizard|dragonite|pikachu|mewtwo|haunter|gengar|pokemon)\b", "Pokemon name"),
        (r"\b(attack|battle|fight|pose|standing|flying|charging|launching)\b", "Action/pose"),
    ],

    # Photorealistic documentary style keywords (REQUIRED)
    "photorealistic_keywords": [
        "photorealistic", "wildlife photography", "BBC Earth",
        "National Geographic", "documentary style", "nature documentary",
        "shot on RED camera", "shot on ARRI", "cinematic",
        "natural lighting", "realistic", "lifelike"
    ],

    # Forbidden style keywords (2D/3D renders not allowed)
    "forbidden_styles": [
        (r"\b(anime|cartoon|manga|chibi)\b", "Anime/cartoon style (use photorealistic)"),
        (r"\b(2d|3d render|cgi|digital art)\b", "2D/3D render (use photorealistic)"),
        (r"\b(illustration|drawing|sketch|painted)\b", "Illustration style (use photorealistic)"),
        (r"\b(stylized|abstract|minimalist)\b", "Stylized (use photorealistic)"),
        (r"\b(pixel art|vector|flat)\b", "Non-photorealistic style")
    ],

    # Recommended quality keywords
    "quality_keywords": [
        "high quality", "detailed", "photorealistic", "cinematic",
        "dynamic", "dramatic", "professional", "vivid colors",
        "high detail", "sharp focus", "8K", "4K", "ultra realistic"
    ],

    # Forbidden elements that should NOT appear
    "forbidden_patterns": [
        (r"\b(shield|barrier|protective aura)\b", "Defensive barriers (forbidden)"),
        (r"\b(trainer|human|person|people)\b", "Humans/trainers (forbidden)"),
        (r"\b(text|label|watermark|logo)\b", "Text/watermarks (forbidden)"),
        (r"\b(multiple scene|split screen|grid|panel)\b", "Multi-panel layouts (forbidden)"),
        (r"\b(blur|blurry|low quality|distort)\b", "Quality issues (forbidden)"),
        (r"\b(extra limb|missing limb|deform)\b", "Anatomy issues (forbidden)")
    ],

    # Recommended environment/lighting elements
    "environment_keywords": [
        "background", "environment", "volcano", "forest", "sky",
        "arena", "field", "mountain", "cave", "ocean"
    ],

    "lighting_keywords": [
        "lighting", "dramatic", "cinematic", "glow", "bright",
        "dark", "sunset", "sunrise", "moonlight", "fire light"
    ]
}


VIDEO_PROMPT_BEST_PRACTICES = {
    # Priority hierarchy for motion prompts (from SOP 4.5)
    # 1. Core Action (HIGHEST)
    # 2. Specific Details
    # 3. Logical Sequence
    # 4. Environmental Context
    # 5. Camera Movement (LOWEST)

    # Motion keywords that should appear
    "motion_keywords": [
        "slowly", "gently", "gradually", "subtle", "breathing",
        "drifting", "floating", "rising", "falling", "swaying",
        "flickering", "pulsing", "glowing"
    ],

    # Temporal markers (recommended)
    "temporal_markers": [
        "begins to", "starts to", "slowly", "gradually",
        "continues", "then", "while", "as"
    ],

    # Forbidden in motion prompts (too complex)
    "forbidden_motion": [
        (r"\bcamera\s+(pan|zoom|track|dolly)\b", "Camera movement at start (should be last)"),
        (r"\b(run|sprint|jump|leap|dash|quick|fast|rapid)\b", "Fast motion (not suitable for breathing photograph)"),
        (r"\b(explosion|explode|crash|smash)\b", "Complex effects (too complex for 5s)"),
        (r"\b(fight|battle|attack)\b.*\b(fight|battle|attack)\b", "Multiple complex actions")
    ],

    # Creature motion types (breathing photograph style)
    "allowed_creature_motion": [
        "breathing", "chest rise", "chest fall", "blinking",
        "head turn", "tail sway", "wing flutter", "eyes glow",
        "eyes tracking"
    ],

    # Environmental motion types
    "allowed_env_motion": [
        "mist drift", "fog", "dust particles", "leaves rustle",
        "water ripple", "light rays", "shadows", "sparkle",
        "glow pulse", "smoke"
    ]
}


SCENE_DESCRIPTION_BEST_PRACTICES = {
    # Elements that make a good scene description
    "required_elements": [
        "subject",      # What/who is in the scene
        "action",       # What's happening
        "environment",  # Where it's happening
    ],

    # Composition keywords
    "composition_keywords": [
        "foreground", "background", "center", "left", "right",
        "close-up", "medium shot", "wide shot", "establishing"
    ],

    # Emotional/atmosphere keywords
    "atmosphere_keywords": [
        "intense", "calm", "fierce", "dramatic", "epic",
        "mysterious", "powerful", "serene", "tense"
    ]
}


# Detailed Pokemon information for holistic prompts
POKEMON_DETAILED_INFO = {
    "charizard": {
        "body_color": "orange body with cream belly",
        "features": [
            "two large blue inner wings with orange membrane",
            "flame constantly burning at tail tip",
            "long neck with powerful jaws",
            "sharp claws on hands and feet",
            "two horns on head",
            "dragon-like appearance",
            "muscular build"
        ],
        "type": "fire/flying",
        "attacks": {
            "flamethrower": "stream of intense fire from mouth, orange-red flames",
            "fire_blast": "star-shaped massive fire explosion",
            "dragon_breath": "blue-purple dragon energy breath",
            "wing_attack": "powerful wing strike with blue-glowing wings",
            "fire_spin": "spiraling tornado of flames",
            "heat_wave": "wave of intense heat distortion"
        },
        "expressions": {
            "fierce": "narrowed eyes, bared teeth, aggressive stance",
            "attacking": "mouth wide open, flames visible, leaning forward",
            "damaged": "wincing, one eye closed, smoke rising from body",
            "victorious": "head raised high, triumphant roar, wings spread"
        },
        "size": "approximately 5'7\" (1.7m) tall, large wingspan",
        "habitat": "volcanic mountains, hot climates",
        "documentary_description": "Photorealistic Charizard, orange fire-dragon with powerful blue wings, flame burning at tail tip, muscular reptilian build, sharp claws and horns"
    },
    "dragonite": {
        "body_color": "orange-yellow body with cream belly",
        "features": [
            "two small wings (disproportionately small for body)",
            "two antennae on head",
            "round friendly face with small eyes",
            "thick tail",
            "small horn on forehead",
            "chubby rounded body",
            "gentle expression by default"
        ],
        "type": "dragon/flying",
        "attacks": {
            "dragon_pulse": "orange-purple swirling energy beam from mouth",
            "hyper_beam": "devastating golden-white energy beam",
            "thunder_punch": "fist crackling with electricity",
            "dragon_claw": "glowing purple-blue slashing claws",
            "outrage": "red-aura rampage state, fierce attacking",
            "dragon_rush": "full body charge with dragon energy aura"
        },
        "expressions": {
            "fierce": "narrowed eyes (unusual), jaw clenched, aggressive stance",
            "charging": "mouth open with energy gathering, antennae glowing",
            "damaged": "visible burn marks, pained expression, determination",
            "attacking": "forward lean, wings spread, energy releasing"
        },
        "size": "approximately 7'3\" (2.2m) tall, large powerful body",
        "habitat": "oceans, islands, mountainous regions",
        "documentary_description": "Photorealistic Dragonite, large orange dragon-type with small wings, friendly rounded face, antennae on head, powerful thick body"
    },
    "pikachu": {
        "body_color": "bright yellow with brown stripes on back",
        "features": [
            "lightning bolt shaped tail (flat, yellow with brown base)",
            "red circular cheek pouches (store electricity)",
            "long pointy ears with black tips",
            "small compact body",
            "large brown eyes",
            "short arms and legs"
        ],
        "type": "electric",
        "attacks": {
            "thunderbolt": "powerful yellow lightning bolt from body",
            "thunder": "massive storm of lightning from sky",
            "quick_attack": "fast dash leaving blur trail",
            "iron_tail": "tail glowing silver-white, striking",
            "electro_ball": "sphere of electricity at tail"
        },
        "expressions": {
            "determined": "narrowed eyes, cheeks sparking",
            "attacking": "cheeks glowing red, electricity arcing",
            "happy": "wide smile, ears up",
            "battle_ready": "crouched stance, tail raised"
        },
        "size": "approximately 1'4\" (0.4m) tall, small mouse-like",
        "habitat": "forests, power plants, urban areas",
        "documentary_description": "Photorealistic Pikachu, small yellow electric mouse with red cheek pouches, lightning bolt tail, pointy black-tipped ears"
    },
    "mewtwo": {
        "body_color": "pale purple body with darker purple tail",
        "features": [
            "long thick purple tail",
            "three round fingers on each hand",
            "two short horns on head",
            "psychic aura visible around body",
            "no wings",
            "humanoid stance",
            "intense piercing eyes",
            "tube-like connection on back of head"
        ],
        "type": "psychic",
        "attacks": {
            "psychic": "purple telekinetic waves, objects floating",
            "shadow_ball": "dark purple-black sphere of ghost energy",
            "aura_sphere": "blue fighting-type energy sphere",
            "psystrike": "powerful pink-purple psychic blast"
        },
        "expressions": {
            "intense": "glowing eyes, psychic aura flaring",
            "attacking": "hand raised, energy gathering",
            "focused": "calm but power visible, hovering",
            "powerful": "full aura display, intimidating presence"
        },
        "size": "approximately 6'7\" (2.0m) tall, floating usually",
        "habitat": "caves, laboratories, isolated locations",
        "documentary_description": "Photorealistic Mewtwo, powerful psychic Pokemon with pale purple body, long tail, intense eyes, psychic aura emanating"
    },
    "haunter": {
        "body_color": "dark purple gaseous body",
        "features": [
            "floating disembodied hands",
            "no visible legs (floats)",
            "large pointed tongue",
            "glowing eyes",
            "spiky gaseous form",
            "mischievous expression"
        ],
        "type": "ghost/poison",
        "attacks": {
            "shadow_ball": "dark purple ghost energy sphere",
            "lick": "long tongue attack, paralyzing",
            "hypnosis": "swirling hypnotic waves from eyes",
            "dream_eater": "dark aura absorbing energy"
        },
        "expressions": {
            "menacing": "wide grin, glowing eyes, hovering close",
            "attacking": "hands forward, tongue out",
            "lurking": "partially transparent, emerging from shadows"
        },
        "size": "approximately 5'3\" (1.6m) tall, gaseous form",
        "habitat": "abandoned buildings, caves, darkness",
        "documentary_description": "Photorealistic Haunter, purple ghost-type with floating hands, gaseous body, glowing eyes, menacing grin"
    }
}

# Backwards compatible alias
POKEMON_ANATOMY = {k: {"body_color": v["body_color"], "features": v["features"],
                       "type": v["type"], "attacks": list(v["attacks"].keys())}
                  for k, v in POKEMON_DETAILED_INFO.items()}


class PromptValidator:
    """Validates prompts against best practices."""

    def __init__(self):
        self.image_practices = IMAGE_PROMPT_BEST_PRACTICES
        self.video_practices = VIDEO_PROMPT_BEST_PRACTICES
        self.scene_practices = SCENE_DESCRIPTION_BEST_PRACTICES
        self.pokemon_info = POKEMON_DETAILED_INFO

    def generate_holistic_storyboard_prompt(
        self,
        pokemon_names: list,
        scene_type: str = "battle",
        environment: str = "volcanic",
        panel_count: int = 4
    ) -> tuple[str, str]:
        """
        Generate a holistic storyboard prompt with detailed Pokemon information.

        Args:
            pokemon_names: List of Pokemon in the scene
            scene_type: Type of scene (battle, encounter, documentary)
            environment: Environment setting
            panel_count: Number of panels

        Returns:
            Tuple of (prompt, negative_prompt)
        """
        # Get detailed Pokemon info
        pokemon_descriptions = []
        pokemon_features = []
        pokemon_attacks = []

        for name in pokemon_names:
            name_lower = name.lower()
            if name_lower in self.pokemon_info:
                info = self.pokemon_info[name_lower]
                pokemon_descriptions.append(info["documentary_description"])
                pokemon_features.extend(info["features"][:3])

                # Get relevant attacks for battle scenes
                if scene_type == "battle":
                    attacks = list(info["attacks"].items())[:2]
                    for attack_name, attack_desc in attacks:
                        pokemon_attacks.append(f"{name} {attack_name}: {attack_desc}")

        # Build environment description
        env_descriptions = {
            "volcanic": "volcanic mountain battlefield with molten lava rivers, smoke and ash in the air, dramatic orange-red lighting",
            "forest": "dense ancient forest clearing, dappled sunlight through canopy, natural peaceful atmosphere",
            "ocean": "coastal cliffside overlooking turbulent ocean, sea spray, dramatic stormy sky",
            "cave": "deep underground cavern with crystal formations, bioluminescent glow, mysterious atmosphere",
            "urban": "abandoned city streets at dusk, overgrown buildings, atmospheric lighting",
            "mountain": "high mountain peak above clouds, thin air visible, majestic alpine landscape"
        }
        env_desc = env_descriptions.get(environment, env_descriptions["volcanic"])

        # Build panel descriptions for battle storyboard with EXPLICIT attack effects
        panel_descs = []
        if scene_type == "battle" and len(pokemon_names) >= 2:
            # Get attack info for explicit effect descriptions
            p1_info = self.pokemon_info.get(pokemon_names[0].lower(), {})
            p2_info = self.pokemon_info.get(pokemon_names[1].lower(), {})

            p1_attacks = list(p1_info.get("attacks", {}).items())
            p2_attacks = list(p2_info.get("attacks", {}).items())

            p1_attack = p1_attacks[0] if p1_attacks else ("attack", "energy beam")
            p2_attack = p2_attacks[0] if p2_attacks else ("attack", "energy beam")

            panel_descs = [
                f"Panel 1: {pokemon_names[0]} launching {p1_attack[0]} - VISIBLE {p1_attack[1]} traveling toward {pokemon_names[1]}, aggressive stance, attack beam/effect clearly visible between them",
                f"Panel 2: {pokemon_names[1]} being hit by the attack, VISIBLE impact explosion on body, pain expression, burn marks/damage appearing, {pokemon_names[0]} visible in attack follow-through pose",
                f"Panel 3: {pokemon_names[1]} charging {p2_attack[0]} - VISIBLE {p2_attack[1]} forming at mouth/hands, energy gathering with visible glow, fierce determination, preparing to counterattack",
                f"Panel 4: {pokemon_names[1]} releasing {p2_attack[0]} - VISIBLE {p2_attack[1]} beam/effect hitting {pokemon_names[0]}, impact explosion on {pokemon_names[0]}, both showing battle damage"
            ]

        # Build the holistic prompt
        prompt_parts = [
            f"Photorealistic {panel_count}-panel Pokemon battle storyboard",
            f"wildlife photography style, BBC Earth documentary quality",
            f"shot on RED camera, natural cinematic lighting, 8K detail",
            "",
            f"Pokemon: {', '.join(pokemon_descriptions)}",
            "",
            f"Environment: {env_desc}",
            "",
            "Panels:",
            *panel_descs,
            "",
            f"Key features to maintain: {', '.join(pokemon_features[:6])}",
            "",
            "Style: Photorealistic, lifelike, detailed textures, natural lighting, documentary feel",
            "Composition: Dynamic action poses, clear character separation, consistent character design across panels"
        ]

        prompt = "\n".join(prompt_parts)

        # Generate comprehensive negative prompt
        negative_prompt = self.generate_negative_prompt(pokemon_names)

        return prompt, negative_prompt

    def generate_holistic_video_prompt(
        self,
        pokemon_name: str,
        action: str,
        scene_context: str = ""
    ) -> str:
        """
        Generate a holistic video/motion prompt with detailed Pokemon information.

        Args:
            pokemon_name: Pokemon in the scene
            action: What action is happening
            scene_context: Additional context

        Returns:
            Motion prompt for video generation
        """
        name_lower = pokemon_name.lower()
        info = self.pokemon_info.get(name_lower, {})

        # Get relevant motion details
        expressions = info.get("expressions", {})
        features = info.get("features", [])

        # Build motion prompt following priority hierarchy:
        # 1. Core Action (HIGHEST)
        # 2. Specific Details
        # 3. Logical Sequence
        # 4. Environmental Context
        # 5. Camera Movement (LOWEST)

        motion_parts = []

        # 1. Core action
        motion_parts.append(f"{pokemon_name} {action}")

        # 2. Specific details based on action with VISIBLE effects
        if "attack" in action.lower() or "launch" in action.lower() or "releasing" in action.lower():
            expr = expressions.get("attacking", "intense focus, body tensing")
            motion_parts.append(expr)
            motion_parts.append("subtle body movement forward")
            # Add explicit effect visibility
            if "beam" in action.lower() or "stream" in action.lower():
                motion_parts.append("energy beam visible and intensifying")
                motion_parts.append("attack effect growing brighter")
        elif "damage" in action.lower() or "hit" in action.lower() or "reacting" in action.lower():
            expr = expressions.get("damaged", "pained expression, recoiling slightly")
            motion_parts.append(expr)
            motion_parts.append("body reacting to impact")
            motion_parts.append("visible flinching motion")
        elif "recover" in action.lower() or "charge" in action.lower() or "charging" in action.lower():
            expr = expressions.get("fierce", "determination visible, energy building")
            motion_parts.append(expr)
            motion_parts.append("stance stabilizing, power gathering")
            # Add explicit charging effect
            motion_parts.append("visible energy glow building at mouth/hands")
            motion_parts.append("charging effect intensifying")

        # 3. Logical sequence with temporal markers
        motion_parts.append("motion begins slowly and builds")

        # 4. Environmental context
        motion_parts.append("atmospheric effects: smoke drifting, heat distortion visible")

        # 5. Feature-specific subtle motion
        if "wings" in str(features).lower():
            motion_parts.append("wings slowly adjusting position")
        if "tail" in str(features).lower():
            motion_parts.append("tail tip flickering with energy")
        if "aura" in str(features).lower() or "glow" in str(features).lower():
            motion_parts.append("subtle glow pulsing")

        # Add scene context if provided
        if scene_context:
            motion_parts.append(scene_context)

        return ", ".join(motion_parts)

    def validate_image_prompt(self, prompt: str, pokemon_names: list = None) -> PromptValidationResult:
        """
        Validate an image generation prompt.

        Args:
            prompt: The prompt to validate
            pokemon_names: List of Pokemon that should appear

        Returns:
            PromptValidationResult with score and suggestions
        """
        result = PromptValidationResult(prompt_type="image", passed=True, score=1.0)
        prompt_lower = prompt.lower()

        # Check required patterns
        for pattern, description in self.image_practices["required_patterns"]:
            if not re.search(pattern, prompt_lower, re.IGNORECASE):
                result.issues.append(f"Missing required: {description}")
                result.score -= 0.15

        # Check for PHOTOREALISTIC style (REQUIRED for documentary)
        photorealistic_count = sum(1 for kw in self.image_practices["photorealistic_keywords"]
                                   if kw.lower() in prompt_lower)
        if photorealistic_count < 1:
            result.issues.append("Missing photorealistic/documentary style keywords")
            result.suggestions.append(
                "Add: 'photorealistic', 'wildlife photography', 'BBC Earth documentary style'"
            )
            result.score -= 0.2

        # Check for FORBIDDEN styles (2D/3D renders not allowed)
        for pattern, description in self.image_practices["forbidden_styles"]:
            if re.search(pattern, prompt_lower, re.IGNORECASE):
                result.issues.append(f"Forbidden style: {description}")
                result.score -= 0.25

        # Check for specific Pokemon names if provided
        if pokemon_names:
            for pokemon in pokemon_names:
                if pokemon.lower() not in prompt_lower:
                    result.warnings.append(f"Pokemon '{pokemon}' not explicitly mentioned")
                    result.score -= 0.05

        # Check forbidden patterns
        for pattern, description in self.image_practices["forbidden_patterns"]:
            if re.search(pattern, prompt_lower, re.IGNORECASE):
                result.issues.append(f"Contains forbidden: {description}")
                result.score -= 0.2

        # Check quality keywords
        quality_count = sum(1 for kw in self.image_practices["quality_keywords"]
                          if kw.lower() in prompt_lower)
        if quality_count < 2:
            result.suggestions.append(
                f"Add quality keywords: {', '.join(self.image_practices['quality_keywords'][:4])}"
            )
            result.score -= 0.05

        # Check environment keywords
        env_count = sum(1 for kw in self.image_practices["environment_keywords"]
                       if kw.lower() in prompt_lower)
        if env_count < 1:
            result.suggestions.append("Add environment/background description")
            result.score -= 0.05

        # Check lighting keywords
        light_count = sum(1 for kw in self.image_practices["lighting_keywords"]
                         if kw.lower() in prompt_lower)
        if light_count < 1:
            result.suggestions.append("Add lighting description")
            result.score -= 0.05

        # Normalize score
        result.score = max(0, min(1, result.score))
        result.passed = result.score >= 0.6 and len(result.issues) == 0

        # Generate improved prompt if needed
        if not result.passed:
            result.improved_prompt = self._improve_image_prompt(prompt, result, pokemon_names)

        return result

    def validate_video_prompt(self, prompt: str, scene_type: str = "battle") -> PromptValidationResult:
        """
        Validate a video/motion generation prompt.

        Args:
            prompt: The motion prompt to validate
            scene_type: Type of scene ("battle", "calm", "environmental")

        Returns:
            PromptValidationResult with score and suggestions
        """
        result = PromptValidationResult(prompt_type="video", passed=True, score=1.0)
        prompt_lower = prompt.lower()

        # Check for forbidden motion patterns
        for pattern, description in self.video_practices["forbidden_motion"]:
            if re.search(pattern, prompt_lower, re.IGNORECASE):
                result.issues.append(f"Problematic motion: {description}")
                result.score -= 0.2

        # Check if camera movement leads the prompt (BAD!)
        camera_pattern = r"^(camera|pan|zoom|track|dolly)"
        if re.match(camera_pattern, prompt_lower.strip()):
            result.issues.append("Camera movement leads prompt (should be last)")
            result.score -= 0.25

        # Check for motion keywords
        motion_count = sum(1 for kw in self.video_practices["motion_keywords"]
                          if kw.lower() in prompt_lower)
        if motion_count < 1:
            result.warnings.append("Add subtle motion keywords (slowly, gently, gradually)")
            result.score -= 0.1

        # Check for temporal markers
        temporal_count = sum(1 for marker in self.video_practices["temporal_markers"]
                            if marker.lower() in prompt_lower)
        if temporal_count < 1:
            result.suggestions.append("Add temporal markers (begins to, gradually, etc.)")
            result.score -= 0.05

        # Check prompt length (should be descriptive but not too long)
        word_count = len(prompt.split())
        if word_count < 10:
            result.warnings.append(f"Prompt too short ({word_count} words), add more detail")
            result.score -= 0.1
        elif word_count > 100:
            result.warnings.append(f"Prompt too long ({word_count} words), simplify")
            result.score -= 0.1

        # Check for allowed motion types
        creature_motion_found = any(motion in prompt_lower
                                    for motion in self.video_practices["allowed_creature_motion"])
        env_motion_found = any(motion in prompt_lower
                              for motion in self.video_practices["allowed_env_motion"])

        if not creature_motion_found and not env_motion_found:
            result.suggestions.append(
                "Specify motion type: " +
                ", ".join(self.video_practices["allowed_creature_motion"][:3]) +
                " or " +
                ", ".join(self.video_practices["allowed_env_motion"][:3])
            )

        # Normalize score
        result.score = max(0, min(1, result.score))
        result.passed = result.score >= 0.6 and len(result.issues) == 0

        # Generate improved prompt if needed
        if not result.passed:
            result.improved_prompt = self._improve_video_prompt(prompt, result)

        return result

    def validate_scene_description(self, description: str) -> PromptValidationResult:
        """
        Validate a scene description for completeness.

        Args:
            description: The scene description

        Returns:
            PromptValidationResult
        """
        result = PromptValidationResult(prompt_type="scene", passed=True, score=1.0)
        desc_lower = description.lower()

        # Check for required elements
        has_subject = any(pokemon in desc_lower for pokemon in POKEMON_ANATOMY.keys())
        has_action = re.search(r"\b(attack|battle|fight|move|fly|charge|dodge|react)\b", desc_lower)
        has_environment = any(kw in desc_lower for kw in
                             ["background", "environment", "volcano", "sky", "arena", "field"])

        if not has_subject:
            result.issues.append("Missing subject (Pokemon)")
            result.score -= 0.2
        if not has_action:
            result.warnings.append("Missing action description")
            result.score -= 0.1
        if not has_environment:
            result.suggestions.append("Add environment context")
            result.score -= 0.05

        # Check for composition keywords
        composition_count = sum(1 for kw in self.scene_practices["composition_keywords"]
                               if kw in desc_lower)
        if composition_count < 1:
            result.suggestions.append("Add composition details (close-up, wide shot, etc.)")

        # Normalize
        result.score = max(0, min(1, result.score))
        result.passed = result.score >= 0.6

        return result

    def validate_storyboard_prompt(self, prompt: str, panel_count: int = 4,
                                   pokemon_names: list = None) -> PromptValidationResult:
        """
        Validate a storyboard generation prompt.

        Args:
            prompt: The storyboard prompt
            panel_count: Expected number of panels
            pokemon_names: Pokemon that should appear

        Returns:
            PromptValidationResult
        """
        result = PromptValidationResult(prompt_type="storyboard", passed=True, score=1.0)
        prompt_lower = prompt.lower()

        # Check for panel indicators
        panel_pattern = r"panel\s*\d|scene\s*\d|\d[.:]\s"
        panel_matches = re.findall(panel_pattern, prompt_lower)

        if len(panel_matches) < panel_count:
            result.warnings.append(
                f"Expected {panel_count} panel descriptions, found {len(panel_matches)}"
            )
            result.score -= 0.1

        # Check for sequence/story flow
        sequence_words = ["then", "next", "after", "finally", "first", "second"]
        if not any(word in prompt_lower for word in sequence_words):
            result.suggestions.append("Add sequence words for story flow (then, next, finally)")

        # Run base image validation
        image_result = self.validate_image_prompt(prompt, pokemon_names)

        # Combine results
        result.issues.extend(image_result.issues)
        result.warnings.extend(image_result.warnings)
        result.suggestions.extend(image_result.suggestions)
        result.score = (result.score + image_result.score) / 2

        result.passed = result.score >= 0.6 and len(result.issues) == 0

        return result

    def _improve_image_prompt(self, prompt: str, result: PromptValidationResult,
                              pokemon_names: list = None) -> str:
        """Generate an improved image prompt based on validation results."""
        improved = prompt
        additions = []
        prefix_additions = []

        # Add photorealistic prefix if missing (CRITICAL for documentary style)
        if not any(kw in prompt.lower() for kw in ["photorealistic", "realistic", "photography"]):
            prefix_additions.append("Photorealistic")

        # Add missing elements
        for issue in result.issues:
            if "Action/pose" in issue:
                additions.append("dynamic pose, intense moment")
            if "environment" in issue.lower():
                additions.append("natural environment with atmospheric effects")
            if "photorealistic" in issue.lower():
                additions.append("wildlife photography style, BBC Earth documentary quality")
                additions.append("shot on RED camera, natural lighting, 8K detail")

        # Add quality keywords if missing
        if not any(kw in prompt.lower() for kw in ["quality", "detailed", "sharp"]):
            additions.append("high detail, sharp focus, professional quality")

        # Add lighting if missing
        if not any(kw in prompt.lower() for kw in ["lighting", "light", "glow"]):
            additions.append("natural cinematic lighting")

        # Build improved prompt
        if prefix_additions:
            improved = f"{' '.join(prefix_additions)} {prompt}"

        if additions:
            improved = f"{improved}, {', '.join(additions)}"

        return improved

    def _improve_video_prompt(self, prompt: str, result: PromptValidationResult) -> str:
        """Generate an improved video/motion prompt based on validation results."""
        improved = prompt

        # Remove camera movement from start if present
        camera_pattern = r"^(camera\s+\w+|pan\s+\w+|zoom\s+\w+)"
        camera_match = re.match(camera_pattern, prompt, re.IGNORECASE)
        if camera_match:
            camera_instruction = camera_match.group()
            improved = prompt[len(camera_instruction):].strip(", ")
            improved = f"{improved}, {camera_instruction.lower()}"

        # Add motion keywords if missing
        motion_words = ["slowly", "gently", "gradually"]
        if not any(word in prompt.lower() for word in motion_words):
            improved = f"{improved}, motion is subtle and gradual"

        return improved

    def generate_negative_prompt(self, pokemon_names: list = None) -> str:
        """
        Generate a comprehensive negative prompt based on best practices.

        Args:
            pokemon_names: Pokemon in the scene (to avoid wrong features)

        Returns:
            Negative prompt string
        """
        forbidden = [
            # CRITICAL: No 2D/3D renders (documentary style only)
            "anime", "cartoon", "manga", "chibi", "2d", "3d render",
            "cgi", "digital art", "illustration", "drawing", "sketch",
            "painted", "stylized", "pixel art", "vector", "flat colors",

            # From best practices
            "shields", "defensive barriers", "protective auras",
            "trainers", "humans", "people", "pokeballs in hand",
            "text", "labels", "watermarks", "logos",
            "multiple scenes", "split screen", "grid layout", "panel layout",

            # Quality issues
            "low quality", "blurry", "distorted", "deformed",
            "bad anatomy", "extra limbs", "missing limbs",
            "wrong proportions", "ugly", "duplicate",

            # Unwanted elements
            "nsfw", "gore", "blood", "violence"
        ]

        return ", ".join(forbidden)


def main():
    """Test the prompt validator."""
    validator = PromptValidator()

    # Test image prompt
    test_image_prompt = """
    Charizard launching powerful flamethrower attack at Dragonite,
    volcanic battlefield with lava in background
    """

    print("=" * 60)
    print("IMAGE PROMPT VALIDATION")
    print("=" * 60)

    result = validator.validate_image_prompt(test_image_prompt, ["Charizard", "Dragonite"])
    print(f"Prompt: {test_image_prompt[:50]}...")
    print(f"Passed: {result.passed}")
    print(f"Score: {result.score:.2f}")
    print(f"Issues: {result.issues}")
    print(f"Suggestions: {result.suggestions}")
    if result.improved_prompt:
        print(f"Improved: {result.improved_prompt[:100]}...")

    # Test video prompt
    test_video_prompt = """
    Camera pans across the battlefield as Charizard attacks
    """

    print("\n" + "=" * 60)
    print("VIDEO PROMPT VALIDATION")
    print("=" * 60)

    result = validator.validate_video_prompt(test_video_prompt)
    print(f"Prompt: {test_video_prompt}")
    print(f"Passed: {result.passed}")
    print(f"Score: {result.score:.2f}")
    print(f"Issues: {result.issues}")
    print(f"Suggestions: {result.suggestions}")
    if result.improved_prompt:
        print(f"Improved: {result.improved_prompt}")

    # Test good video prompt
    good_video_prompt = """
    Dragonite's chest rises and falls with heavy breathing after the attack,
    wings slowly spreading wide, eyes narrowing with determination,
    smoke and heat distortion gradually clearing in the volcanic environment
    """

    print("\n" + "=" * 60)
    print("GOOD VIDEO PROMPT VALIDATION")
    print("=" * 60)

    result = validator.validate_video_prompt(good_video_prompt)
    print(f"Passed: {result.passed}")
    print(f"Score: {result.score:.2f}")
    print(f"Issues: {result.issues}")


if __name__ == "__main__":
    main()
