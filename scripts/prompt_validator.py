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
        "name": "Charizard",
        "body_color": "orange body with cream/pale yellow underbelly",
        "height": "5'7\" (1.7 meters)",
        "weight": "199.5 lbs (90.5 kg)",
        "body_type": "bipedal dragon, muscular reptilian build",
        "features": [
            "two large blue-green inner membrane wings with orange outer edge",
            "flame constantly burning at tail tip (blue when angry, orange normal)",
            "long powerful neck with defined scales",
            "powerful jaws with visible fangs",
            "sharp white claws on three-fingered hands",
            "sharp claws on three-toed feet",
            "two backward-pointing horns on head",
            "small pointed nose horn",
            "cream-colored wing membranes",
            "thick powerful tail ending in flame",
            "visible muscle definition on arms and legs",
            "scaly textured skin with subtle orange gradient"
        ],
        "type": "fire/flying",
        "attacks": {
            "flamethrower": "continuous stream of intense orange-red fire from mouth, flames spiraling outward, heat distortion visible",
            "fire_blast": "star-shaped massive fire explosion, five-pointed flame projectile",
            "dragon_breath": "blue-purple dragon energy breath with sparkles",
            "wing_attack": "powerful wing strike with blue-glowing wing edges",
            "fire_spin": "spiraling tornado of flames surrounding target",
            "heat_wave": "wave of intense heat distortion rippling through air"
        },
        "attack_visuals": {
            "flamethrower": "VISIBLE orange-red flame stream shooting from open mouth, fire trail in air, heat shimmer effect",
            "charging": "throat glowing orange, flames licking from mouth corners, tail flame intensifying"
        },
        "expressions": {
            "fierce": "narrowed reptilian eyes with visible slit pupils, bared fangs, aggressive forward-leaning stance, wings partially spread",
            "attacking": "mouth wide open with flames visible inside, body leaning forward, wings back, tail raised with intensified flame",
            "damaged": "wincing expression, one eye closed, visible scorch marks on scales, smoke rising from body, staggered stance",
            "victorious": "head raised high in triumphant roar, wings fully spread wide, tail flame burning bright blue",
            "charging_attack": "throat bulging with fire energy, orange glow visible in chest, intense focused eyes"
        },
        "damage_appearance": {
            "burn_marks": "blackened scorch marks on orange scales, smoke wisping from wounds",
            "impact_wounds": "cracked scales, visible bruising under scales as darker patches",
            "exhaustion": "lowered wings, dimmer tail flame, heavy breathing visible"
        },
        "size": "approximately 5'7\" (1.7m) tall standing, 15ft wingspan when fully extended",
        "habitat": "volcanic mountains, hot climates, mountain peaks",
        "scale_texture": "overlapping hexagonal scales with slight iridescent sheen in firelight",
        "documentary_description": "Photorealistic Charizard - large bipedal fire dragon standing 5'7\" tall with orange scaly skin, cream underbelly, two powerful blue-membrane wings with 15ft wingspan, muscular reptilian build, long neck, two backward horns on head, sharp white claws on hands and feet, iconic flame burning at thick tail tip, fierce reptilian eyes with slit pupils"
    },
    "dragonite": {
        "name": "Dragonite",
        "body_color": "orange-yellow/amber body with cream/pale belly and inner wings",
        "height": "7'3\" (2.2 meters)",
        "weight": "463 lbs (210 kg)",
        "body_type": "bipedal dragon, rotund powerful build, deceptively strong",
        "features": [
            "two small teal-green wings (disproportionately small for body size)",
            "two long thin antennae on top of head",
            "round friendly face with small kind eyes",
            "thick powerful tail tapering to rounded tip",
            "small rounded horn on forehead",
            "chubby rounded body hiding immense strength",
            "gentle expression by default but fierce when angered",
            "three-clawed hands and feet",
            "cream-colored belly and inner wing membrane",
            "smooth skin texture compared to scaled Pokemon",
            "thick sturdy legs supporting heavy body"
        ],
        "type": "dragon/flying",
        "attacks": {
            "dragon_pulse": "orange-purple swirling energy beam from mouth, spiral pattern visible",
            "hyper_beam": "devastating golden-white concentrated energy beam, extremely bright",
            "thunder_punch": "fist surrounded by crackling yellow electricity, lightning arcs",
            "dragon_claw": "claws glowing purple-blue with dragon energy, visible aura",
            "outrage": "red-aura rampage state, eyes glowing red, fierce uncontrolled attacking",
            "dragon_rush": "full body charge surrounded by blue dragon-shaped energy aura"
        },
        "attack_visuals": {
            "dragon_pulse": "VISIBLE orange-purple spiral beam shooting from open mouth, energy crackling along beam",
            "hyper_beam": "VISIBLE massive golden-white beam, so bright it illuminates entire scene, recoil visible",
            "charging": "antennae glowing bright, mouth open with visible energy sphere forming, body tensing"
        },
        "expressions": {
            "fierce": "narrowed eyes (unusual for normally gentle face), jaw clenched tight, aggressive forward stance, wings spread",
            "charging": "mouth open with visible energy sphere forming inside, antennae glowing brightly, determined expression",
            "damaged": "visible burn marks on orange skin, pained expression but showing determination, one eye squinting",
            "attacking": "forward lean with full commitment, wings spread for balance, energy releasing from mouth",
            "determined": "furrowed brow, set jaw, unwavering gaze, battle-ready stance despite injuries"
        },
        "damage_appearance": {
            "burn_marks": "blackened patches on orange skin, blistering visible, smoke rising",
            "impact_wounds": "darker bruised areas, visible swelling",
            "accumulated_damage": "multiple burn marks, exhausted posture, heavy breathing, but still fighting"
        },
        "size": "approximately 7'3\" (2.2m) tall, powerful body mass, small wings ~6ft span",
        "habitat": "oceans, remote islands, mountainous regions, open skies",
        "skin_texture": "smooth leathery skin with slight sheen, not scaled",
        "documentary_description": "Photorealistic Dragonite - large bipedal dragon standing 7'3\" tall with orange-amber smooth skin, cream underbelly, surprisingly small teal wings for its massive body, two thin antennae on head, round friendly face with small eyes, small forehead horn, thick powerful tail, rotund yet immensely powerful build, three-clawed hands and feet"
    },
    "pikachu": {
        "name": "Pikachu",
        "body_color": "bright yellow with brown stripes on back",
        "height": "1'4\" (0.4 meters)",
        "weight": "13.2 lbs (6 kg)",
        "body_type": "small quadruped mouse, compact and agile",
        "features": [
            "lightning bolt shaped tail (flat, yellow with brown base)",
            "red circular cheek pouches (store electricity, glow when charging)",
            "long pointy ears with black tips",
            "small compact furry body",
            "large expressive brown eyes",
            "short stubby arms and legs",
            "two brown stripes across back",
            "small black nose",
            "pink inner ears"
        ],
        "type": "electric",
        "attacks": {
            "thunderbolt": "powerful yellow lightning bolt from body, branching electricity",
            "thunder": "massive storm of lightning from sky",
            "quick_attack": "fast dash leaving blur trail",
            "iron_tail": "tail glowing silver-white metallic, striking",
            "electro_ball": "sphere of electricity forming at tail"
        },
        "attack_visuals": {
            "thunderbolt": "VISIBLE yellow lightning arcing from red cheek pouches, electricity branching",
            "charging": "cheek pouches glowing bright red, electricity crackling around body, fur standing on end"
        },
        "expressions": {
            "determined": "narrowed eyes, cheeks sparking with electricity",
            "attacking": "cheeks glowing bright red, electricity arcing across body",
            "happy": "wide smile, ears up and forward",
            "battle_ready": "crouched low stance, tail raised and crackling"
        },
        "size": "approximately 1'4\" (0.4m) tall, small mouse-like",
        "habitat": "forests, power plants, urban areas",
        "fur_texture": "short soft yellow fur with slight static effect",
        "documentary_description": "Photorealistic Pikachu - small electric mouse standing 1'4\" tall with bright yellow fur, red circular cheek pouches that store electricity, distinctive lightning bolt shaped tail, long pointy ears with black tips, large expressive brown eyes, two brown stripes on back"
    },
    "mewtwo": {
        "name": "Mewtwo",
        "body_color": "pale purple/lavender body with darker purple tail",
        "height": "6'7\" (2.0 meters)",
        "weight": "269 lbs (122 kg)",
        "body_type": "humanoid psychic being, elegant yet powerful",
        "features": [
            "long thick purple tail with bulbous end",
            "three round fingers on each large hand",
            "two short curved horns extending from back of head",
            "psychic aura visible around body (purple energy)",
            "no wings, floats using psychic power",
            "humanoid bipedal stance",
            "intense piercing purple eyes",
            "tube-like structure connecting from back of head to spine",
            "muscular feline-like legs",
            "purple sections on thighs",
            "pale lavender main body"
        ],
        "type": "psychic",
        "attacks": {
            "psychic": "purple telekinetic waves emanating outward, visible distortion",
            "shadow_ball": "dark purple-black sphere of ghost energy, swirling darkness",
            "aura_sphere": "blue fighting-type energy sphere, bright glow",
            "psystrike": "powerful pink-purple psychic wave blast"
        },
        "attack_visuals": {
            "psychic": "VISIBLE purple energy waves radiating from body, objects floating nearby",
            "charging": "eyes glowing bright purple, psychic aura intensifying, energy gathering at hands"
        },
        "expressions": {
            "intense": "glowing purple eyes, psychic aura flaring around body",
            "attacking": "arm extended with palm forward, energy gathering at hand",
            "focused": "calm expression but immense power visible, hovering above ground",
            "powerful": "full psychic aura display, intimidating presence, eyes blazing"
        },
        "size": "approximately 6'7\" (2.0m) tall, usually floating",
        "habitat": "caves, laboratories, isolated locations",
        "skin_texture": "smooth almost organic-metallic surface, pale lavender",
        "documentary_description": "Photorealistic Mewtwo - powerful psychic Pokemon standing 6'7\" tall with pale purple humanoid body, long thick purple tail, three-fingered hands, two curved horns on back of head, intense glowing purple eyes, visible psychic aura emanating, tube structure on back of neck, muscular feline-like legs"
    },
    "haunter": {
        "name": "Haunter",
        "body_color": "dark purple gaseous/ethereal body",
        "height": "5'3\" (1.6 meters)",
        "weight": "0.2 lbs (0.1 kg) - nearly weightless ghost",
        "body_type": "floating ghost, no solid lower body",
        "features": [
            "two floating disembodied hands with claws",
            "no visible legs (floats, lower body fades to gas)",
            "large pointed pink tongue often visible",
            "glowing white eyes with no pupils",
            "spiky gaseous purple form",
            "mischievous wide grin",
            "triangular spikes around head",
            "semi-transparent ghostly body"
        ],
        "type": "ghost/poison",
        "attacks": {
            "shadow_ball": "dark purple ghost energy sphere forming between hands",
            "lick": "long tongue extending to paralyze target",
            "hypnosis": "swirling hypnotic waves emanating from eyes",
            "dream_eater": "dark aura absorbing energy from sleeping target"
        },
        "attack_visuals": {
            "shadow_ball": "VISIBLE dark purple sphere forming between floating hands, ghostly energy swirling",
            "charging": "hands raised, dark energy gathering between them, eyes glowing brighter"
        },
        "expressions": {
            "menacing": "wide toothy grin, glowing eyes, hovering close threateningly",
            "attacking": "hands thrust forward, tongue out, eyes intensely glowing",
            "lurking": "partially transparent, half-emerging from shadows"
        },
        "size": "approximately 5'3\" (1.6m) when fully manifested, gaseous form",
        "habitat": "abandoned buildings, dark caves, haunted locations",
        "body_texture": "semi-transparent gaseous form, constantly shifting",
        "documentary_description": "Photorealistic Haunter - ethereal ghost Pokemon hovering at 5'3\" with dark purple gaseous body, two floating disembodied clawed hands, glowing white pupil-less eyes, large pointed pink tongue, wide menacing grin, spiky head silhouette, semi-transparent and constantly shifting form"
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

    def get_pokemon_full_description(self, pokemon_name: str) -> str:
        """
        Get a complete physical description of a Pokemon for image generation.

        Args:
            pokemon_name: Name of the Pokemon

        Returns:
            Comprehensive description string
        """
        name_lower = pokemon_name.lower()
        info = self.pokemon_info.get(name_lower, {})

        if not info:
            return f"Photorealistic {pokemon_name}"

        parts = [
            f"Photorealistic {info.get('name', pokemon_name)}",
            f"({info.get('height', 'unknown height')}, {info.get('weight', 'unknown weight')})",
            f"- Body: {info.get('body_color', 'unknown color')}, {info.get('body_type', 'unknown build')}",
        ]

        # Add key features
        features = info.get('features', [])[:6]  # Top 6 features
        if features:
            parts.append(f"- Features: {', '.join(features)}")

        # Add texture if available
        texture = info.get('scale_texture') or info.get('skin_texture') or info.get('fur_texture') or info.get('body_texture')
        if texture:
            parts.append(f"- Texture: {texture}")

        return " ".join(parts)

    def generate_optimized_storyboard_prompt(
        self,
        pokemon_names: list,
        environment: str = "volcanic",
        use_cinematic: bool = True
    ) -> dict:
        """
        Generate an OPTIMIZED storyboard prompt using the PROVEN USER FORMAT.

        Key principles (from Nano Banana Pro best practices):
        - Use CINEMATIC action sequence format with timestamps
        - Very detailed Pokemon descriptions with specific colors
        - Explicit facial expressions and reactions
        - 16:9 widescreen aspect ratio for cinematic look

        Args:
            pokemon_names: [attacker, defender] Pokemon names
            environment: Environment setting
            use_cinematic: If True, use cinematic 16:9 format (recommended)

        Returns:
            Dict with prompt, negative_prompt, and recommended parameters
        """
        p1_name = pokemon_names[0]
        p2_name = pokemon_names[1]

        # Use CINEMATIC format (proven to produce better results)
        if use_cinematic:
            return self._generate_cinematic_prompt(pokemon_names, environment)

        # Fallback to panel-based format
        return self._generate_panel_prompt(pokemon_names, environment)

    def _generate_cinematic_prompt(
        self,
        pokemon_names: list,
        environment: str = "volcanic"
    ) -> dict:
        """
        Generate CINEMATIC action sequence prompt (user's proven format).
        Uses 10-second action sequence with timestamps.
        """
        p1_name = pokemon_names[0]
        p2_name = pokemon_names[1]

        # Pokemon-specific details matching user's proven format
        pokemon_details = {
            "charizard": {
                "height": "5'7\"",
                "desc": "lean orange dragon with realistic detailed reptilian scales, teal wings, cream belly, flaming tail",
                "attack": "orange-red Flamethrower stream",
                "attack_effect": "massive flames",
                "damage_type": "BLACKENED BURNT SCORCH MARKS and charred patterns",
                "wing_desc": "teal wings"
            },
            "dragonite": {
                "height": "7'3\"",
                "desc": "bulky ORANGE-TAN body with realistic scales, teal wings, two antennae, cream belly stripes, NO tail flame",
                "attack": "orange-purple Dragon Pulse beam",
                "attack_effect": "massive energy beam",
                "damage_type": "BLACKENED IMPACT DAMAGE and energy burns",
                "wing_desc": "teal wings"
            },
            "pikachu": {
                "height": "1'4\"",
                "desc": "small yellow electric mouse with red cheek pouches, lightning bolt tail, pointy ears with black tips",
                "attack": "bright yellow Thunderbolt lightning",
                "attack_effect": "massive electrical discharge",
                "damage_type": "ELECTRICAL BURN MARKS and singed fur",
                "wing_desc": ""
            },
            "mewtwo": {
                "height": "6'7\"",
                "desc": "pale purple humanoid with long thick tail, three-fingered hands, piercing purple eyes, psychic aura",
                "attack": "purple Psychic energy waves",
                "attack_effect": "massive telekinetic force",
                "damage_type": "PSYCHIC DAMAGE with visible distortion marks",
                "wing_desc": ""
            },
            "haunter": {
                "height": "5'3\"",
                "desc": "dark purple ghost with floating disembodied hands, glowing white eyes, menacing grin, semi-transparent body",
                "attack": "dark purple Shadow Ball",
                "attack_effect": "massive ghost energy sphere",
                "damage_type": "GHOSTLY BURNS and ethereal damage marks",
                "wing_desc": ""
            }
        }

        p1 = pokemon_details.get(p1_name.lower(), pokemon_details["charizard"])
        p2 = pokemon_details.get(p2_name.lower(), pokemon_details["dragonite"])

        # Environment descriptions
        env_map = {
            "volcanic": "volcanic valley background with lava pools and smoke",
            "forest": "ancient forest background with towering trees and dappled sunlight",
            "ocean": "coastal cliffs background with crashing waves and stormy sky",
            "cave": "underground cavern background with glowing crystals",
            "mountain": "mountain peak background above clouds"
        }
        env_desc = env_map.get(environment, env_map["volcanic"])

        # Build prompt using USER'S EXACT PROVEN FORMAT
        prompt = f"""PHOTOREALISTIC hyperrealistic CGI render: COMPLETE 10-SECOND ACTION SEQUENCE with BOTH Pokemon: OPENING (0-4s): Smaller {p1_name} ({p1['height']}, {p1['desc']}) on LEFT side launching massive sustained {p1['attack']} from open jaws with fierce determined expression, flames traveling across frame toward significantly larger {p2_name} ({p2['height']}, 30% bigger, {p2['desc']}) on RIGHT side, {p2_name} with PAINED FACIAL EXPRESSION (eyes squinting in pain, mouth open wide showing teeth in grimace, eyebrows furrowed in distress, face contorted) being PUSHED BACKWARD by force of {p1['attack_effect']}, body leaning back and recoiling from heat and impact, attempting to brace with arms raised defensively but failing against overwhelming fire stream, flame stream clearly connecting both Pokemon with visible bright orange-red impact glow where flames strike {p2_name}'s torso, intense heat distortion and fire sparks bursting from impact point, physical knockback evident. TRANSITION (4-6s): Flames dissipating, close-up on {p2_name}'s torso and cream belly revealing {p2['damage_type']}, smoke wisping from burnt scales showing realistic heat damage texture, {p2_name}'s facial expression transitioning from PAIN to FIERCE ANGER (eyes narrowing with determination and rage, teeth bared in aggressive snarl, eyebrows furrowed in fury showing intense resolve for revenge). FINALE (6-10s): {p2_name} recovering from knockback and CHARGING FORWARD aggressively toward {p1_name} with {p2['wing_desc'] or 'arms'} spread wide pulling back for powerful counter-attack, body accelerating rapidly with building momentum, {p1_name} visible in frame bracing for incoming revenge attack, dramatic battle tension rising, side-angle wide shot capturing complete revenge charge sequence, realistic physics with dynamic motion, camera starts side-angle capturing both Pokemon, zooms into impact showing damage and pain, then pulls back wide as {p2_name} charges forward for revenge, realistic detailed reptilian scales with texture depth, leathery wing texture, natural lighting with physically accurate shadows, organic weathering appearance, dramatic cinematic composition, 8K quality, {env_desc}, battle-worn with scratches and scars visible, weathered appearance"""

        negative_prompt = "anime, cartoon, manga, chibi, 2d, 3d render, cgi, digital art, illustration, drawing, sketch, painted, stylized, pixel art, vector, flat colors, shields, defensive barriers, protective auras, trainers, humans, people, pokeballs in hand, text, labels, watermarks, logos, multiple scenes, split screen, grid layout, panel layout, low quality, blurry, distorted, deformed, bad anatomy, extra limbs, missing limbs, wrong proportions, ugly, duplicate, nsfw, gore, blood, violence"

        # CINEMATIC format uses 16:9 widescreen and JPG
        return {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "resolution": "2K",
            "aspect_ratio": "16:9",  # Widescreen cinematic
            "output_format": "jpg",
            "model": "nano-banana-pro"
        }

    def _generate_panel_prompt(
        self,
        pokemon_names: list,
        environment: str = "volcanic"
    ) -> dict:
        """
        Generate 4-panel storyboard prompt (alternative format).
        Uses square 1:1 aspect ratio for grid layout.
        """
        p1_name = pokemon_names[0]
        p2_name = pokemon_names[1]

        p1_info = self.pokemon_info.get(p1_name.lower(), {})
        p2_info = self.pokemon_info.get(p2_name.lower(), {})

        # Simple feature summaries
        p1_simple_features = self._get_simple_features(p1_name.lower())
        p2_simple_features = self._get_simple_features(p2_name.lower())

        # Get attack names
        p1_attacks = p1_info.get('attacks', {})
        p2_attacks = p2_info.get('attacks', {})
        p1_attack_name = list(p1_attacks.keys())[0] if p1_attacks else "fire_attack"
        p2_attack_name = list(p2_attacks.keys())[0] if p2_attacks else "energy_attack"

        # Simple attack descriptions
        p1_attack_simple = self._get_simple_attack_desc(p1_name.lower(), p1_attack_name)
        p2_attack_simple = self._get_simple_attack_desc(p2_name.lower(), p2_attack_name)

        # Simple key features for consistency
        p1_key_features = self._get_key_features(p1_name.lower())
        p2_key_features = self._get_key_features(p2_name.lower())

        # Environment description
        env_map = {
            "volcanic": "volcanic mountain battlefield with molten lava rivers, smoke and ash in the air, dramatic orange-red lighting",
            "forest": "ancient forest clearing with towering trees, dappled golden sunlight filtering through canopy",
            "ocean": "coastal cliffs over turbulent ocean, crashing waves, stormy sky with lightning",
            "cave": "vast underground cavern with glowing crystals, bioluminescent glow, mysterious atmosphere",
            "mountain": "mountain peak above clouds, rocky alpine terrain, golden hour lighting"
        }
        env_desc = env_map.get(environment, env_map["volcanic"])

        prompt = f"""Photorealistic 4-panel Pokemon battle storyboard
wildlife photography style, BBC Earth documentary quality
shot on RED camera, natural cinematic lighting, 8K detail

Pokemon: Photorealistic {p1_name}, {p1_simple_features}. Photorealistic {p2_name}, {p2_simple_features}

Environment: {env_desc}

Panels:
Panel 1: {p1_name} launching {p1_attack_name} - VISIBLE {p1_attack_simple}, aggressive stance, attack beam/effect clearly visible between them
Panel 2: {p2_name} being hit by the attack, VISIBLE impact explosion on body, pain expression, burn marks/damage appearing, {p1_name} visible in attack follow-through pose
Panel 3: {p2_name} charging {p2_attack_name} - VISIBLE {p2_attack_simple} forming at mouth/hands, energy gathering with visible glow, fierce determination, preparing to counterattack
Panel 4: {p2_name} releasing {p2_attack_name} - VISIBLE {p2_attack_simple} beam/effect hitting {p1_name}, impact explosion on {p1_name}, both showing battle damage

Key features to maintain: {p1_key_features}, {p2_key_features}

Style: Photorealistic, lifelike, detailed textures, natural lighting, documentary feel
Composition: Dynamic action poses, clear character separation, consistent character design across panels"""

        negative_prompt = "anime, cartoon, manga, chibi, 2d, 3d render, cgi, digital art, illustration, drawing, sketch, painted, stylized, pixel art, vector, flat colors, shields, defensive barriers, protective auras, trainers, humans, people, pokeballs in hand, text, labels, watermarks, logos, multiple scenes, split screen, grid layout, panel layout, low quality, blurry, distorted, deformed, bad anatomy, extra limbs, missing limbs, wrong proportions, ugly, duplicate, nsfw, gore, blood, violence"

        # Panel format uses 1:1 square for grid layout
        return {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "resolution": "2K",
            "aspect_ratio": "1:1",  # Square for 4-panel grid
            "output_format": "png",
            "model": "nano-banana-pro"
        }

    def _get_simple_features(self, pokemon_name: str) -> str:
        """Get SIMPLE feature description (proven to work better than detailed)."""
        simple_descriptions = {
            "charizard": "orange fire-dragon with powerful blue wings, flame burning at tail tip, muscular reptilian build, sharp claws and horns",
            "dragonite": "large orange dragon-type with small wings, friendly rounded face, antennae on head, powerful thick body",
            "pikachu": "small yellow electric mouse with red cheek pouches, lightning bolt tail, pointy ears with black tips",
            "mewtwo": "pale purple psychic humanoid, long thick tail, piercing purple eyes, floating with psychic aura",
            "haunter": "dark purple ghost with floating hands, glowing white eyes, menacing grin, semi-transparent body"
        }
        return simple_descriptions.get(pokemon_name, "powerful dragon creature")

    def _get_simple_attack_desc(self, pokemon_name: str, attack_name: str) -> str:
        """Get SIMPLE attack description."""
        attack_descriptions = {
            "charizard": {
                "flamethrower": "stream of intense fire from mouth, orange-red flames traveling forward",
                "fire_blast": "massive star-shaped fire explosion from mouth",
                "dragon_breath": "blue-purple dragon energy breath"
            },
            "dragonite": {
                "dragon_pulse": "orange-purple swirling energy beam from mouth",
                "hyper_beam": "golden-white concentrated energy beam from mouth",
                "thunder_punch": "fist crackling with yellow electricity"
            },
            "pikachu": {
                "thunderbolt": "powerful yellow lightning bolt from body",
                "thunder": "massive storm of lightning from sky"
            },
            "mewtwo": {
                "psychic": "purple telekinetic waves emanating from body",
                "shadow_ball": "dark purple-black sphere of ghost energy"
            },
            "haunter": {
                "shadow_ball": "dark purple ghost energy sphere between hands",
                "lick": "long tongue extending forward"
            }
        }
        pokemon_attacks = attack_descriptions.get(pokemon_name, {})
        return pokemon_attacks.get(attack_name, "energy attack from mouth")

    def _get_key_features(self, pokemon_name: str) -> str:
        """Get KEY features to maintain consistency across panels."""
        key_features = {
            "charizard": "two large blue inner wings with orange membrane, flame constantly burning at tail tip, long neck with powerful jaws",
            "dragonite": "two small wings (disproportionately small for body), two antennae on head, round friendly face with small eyes",
            "pikachu": "red circular cheek pouches, lightning bolt shaped tail, long pointy ears with black tips",
            "mewtwo": "long thick purple tail, three-fingered hands, two curved horns on back of head",
            "haunter": "floating disembodied clawed hands, glowing white eyes, spiky head silhouette"
        }
        return key_features.get(pokemon_name, "distinctive features")

    def generate_single_panel_prompt(
        self,
        pokemon_names: list,
        panel_number: int,
        environment: str = "volcanic"
    ) -> tuple[str, str]:
        """
        Generate a SHORT, FOCUSED prompt for a SINGLE panel image.

        This approach generates 4 separate high-quality images that can be
        combined into a storyboard grid afterward. Much better quality than
        trying to generate all 4 panels in one image.

        Args:
            pokemon_names: [attacker, defender] Pokemon names
            panel_number: 1-4 indicating which panel
            environment: Environment setting

        Returns:
            Tuple of (prompt, negative_prompt)
        """
        p1_name = pokemon_names[0]  # Attacker in panel 1-2
        p2_name = pokemon_names[1]  # Defender, counterattacks in panel 3-4

        p1_info = self.pokemon_info.get(p1_name.lower(), {})
        p2_info = self.pokemon_info.get(p2_name.lower(), {})

        # Environment descriptions (short)
        env_map = {
            "volcanic": "volcanic battlefield, lava pools, smoke",
            "forest": "ancient forest clearing, dappled sunlight",
            "ocean": "coastal cliffs, crashing waves, stormy sky",
            "cave": "underground cavern, glowing crystals",
            "mountain": "mountain peak above clouds, snow"
        }
        env_desc = env_map.get(environment, env_map["volcanic"])

        # Get key visual info
        p1_color = p1_info.get('body_color', 'orange body')
        p2_color = p2_info.get('body_color', 'orange-yellow body')
        p1_height = p1_info.get('height', "5'7\"").split()[0]
        p2_height = p2_info.get('height', "7'3\"").split()[0]

        # Get primary attack visuals
        p1_attacks = p1_info.get('attacks', {})
        p2_attacks = p2_info.get('attacks', {})
        p1_attack = list(p1_attacks.values())[0] if p1_attacks else "fire breath"
        p2_attack = list(p2_attacks.values())[0] if p2_attacks else "energy beam"

        # Build panel-specific SHORT prompts (under 500 chars)
        if panel_number == 1:
            # Panel 1: Initial Attack
            prompt = f"""PHOTOREALISTIC wildlife photography: {p1_name} ({p1_height}, {p1_color}) on LEFT side launching {p1_attack} toward {p2_name} ({p2_height}, {p2_color}) on RIGHT side. Both Pokemon facing each other in battle stance. VISIBLE attack beam connecting them. {env_desc}. Dramatic lighting, 8K detail, BBC Earth documentary style, cinematic composition."""

        elif panel_number == 2:
            # Panel 2: Impact Hit
            prompt = f"""PHOTOREALISTIC wildlife photography: {p2_name} ({p2_color}) on RIGHT being HIT by attack from {p1_name} on LEFT. VISIBLE IMPACT EXPLOSION on {p2_name}'s body, pained expression, recoiling backward. {p1_name} ({p1_color}) follow-through attack pose. Both facing each other. {env_desc}. 8K detail, dramatic lighting, BBC Earth documentary style."""

        elif panel_number == 3:
            # Panel 3: Counter-Attack Charging
            prompt = f"""PHOTOREALISTIC wildlife photography: {p2_name} ({p2_color}) on RIGHT with VISIBLE BURN MARKS/DAMAGE from previous attack, mouth open with VISIBLE ENERGY CHARGING, fierce determined expression. {p1_name} ({p1_color}) on LEFT in defensive stance. Both facing each other. {env_desc}. 8K detail, energy glow effect, BBC Earth documentary style."""

        else:  # Panel 4
            # Panel 4: Counter-Attack Release
            prompt = f"""PHOTOREALISTIC wildlife photography: {p2_name} ({p2_color}) on RIGHT releasing massive {p2_attack} toward {p1_name} on LEFT. {p2_name} still shows burn damage from earlier. {p1_name} ({p1_color}) being HIT, recoiling from impact. VISIBLE attack beam between them. {env_desc}. 8K detail, dramatic lighting, BBC Earth documentary style."""

        negative_prompt = "anime, cartoon, 3d render, cgi, illustration, drawing, sketch, stylized, text, watermark, low quality, blurry, deformed, bad anatomy"

        return prompt, negative_prompt

    def get_all_panel_prompts(
        self,
        pokemon_names: list,
        environment: str = "volcanic"
    ) -> list[tuple[str, str]]:
        """
        Get all 4 panel prompts for generating individual storyboard images.

        Args:
            pokemon_names: [attacker, defender] Pokemon names
            environment: Environment setting

        Returns:
            List of 4 (prompt, negative_prompt) tuples
        """
        return [
            self.generate_single_panel_prompt(pokemon_names, i, environment)
            for i in range(1, 5)
        ]

    def generate_cinematic_storyboard_prompt(
        self,
        pokemon_names: list,
        scene_type: str = "battle",
        environment: str = "volcanic"
    ) -> tuple[str, str]:
        """
        Generate a CINEMATIC ACTION SEQUENCE prompt (proven format).
        Uses timestamps and continuous action flow instead of panel descriptions.

        This format has been tested and produces better results than panel-by-panel.

        Args:
            pokemon_names: List of Pokemon in the scene
            scene_type: Type of scene
            environment: Environment setting

        Returns:
            Tuple of (prompt, negative_prompt)
        """
        p1_name = pokemon_names[0]
        p2_name = pokemon_names[1]
        p1_info = self.pokemon_info.get(p1_name.lower(), {})
        p2_info = self.pokemon_info.get(p2_name.lower(), {})

        # Get heights for size comparison
        p1_height = p1_info.get('height', "5'7\"").split()[0]
        p2_height = p2_info.get('height', "7'3\"").split()[0]

        # Get attack info
        p1_attacks = list(p1_info.get("attacks", {}).items())
        p2_attacks = list(p2_info.get("attacks", {}).items())
        p1_attack_name = p1_attacks[0][0].replace("_", " ").title() if p1_attacks else "attack"
        p1_attack_visual = p1_attacks[0][1] if p1_attacks else "energy beam"
        p2_attack_name = p2_attacks[0][0].replace("_", " ").title() if p2_attacks else "attack"

        # Get physical descriptions
        p1_body = p1_info.get('body_color', 'orange body')
        p1_features = p1_info.get('features', [])[:4]
        p2_body = p2_info.get('body_color', 'orange body')
        p2_features = p2_info.get('features', [])[:4]

        # Get expressions
        p1_expr_attack = p1_info.get('expressions', {}).get('attacking', 'fierce expression')
        p2_expr_damaged = p2_info.get('expressions', {}).get('damaged', 'pained expression')
        p2_expr_charging = p2_info.get('expressions', {}).get('charging', 'determined expression')

        # Get damage appearance
        damage_type = "fire" if "fire" in p1_info.get("type", "") else "impact"
        damage_desc = p1_info.get('damage_appearance', {}).get('burn_marks', 'blackened burn marks')

        # Environment descriptions
        env_map = {
            "volcanic": "volcanic valley background with lava pools and smoke",
            "forest": "ancient forest background with towering trees",
            "ocean": "coastal cliffs background with crashing waves",
            "cave": "underground cavern background with glowing crystals",
            "urban": "abandoned city background at sunset",
            "mountain": "mountain peak background above clouds"
        }
        env_desc = env_map.get(environment, env_map["volcanic"])

        # Build cinematic prompt using proven format
        prompt = f"""PHOTOREALISTIC hyperrealistic CGI render: COMPLETE 10-SECOND ACTION SEQUENCE with BOTH Pokemon: OPENING (0-4s): Smaller {p1_name} ({p1_height}, {p1_body}, {', '.join(p1_features[:3])}) on LEFT side launching massive sustained {p1_attack_visual} from open jaws with {p1_expr_attack}, attack traveling across frame toward significantly larger {p2_name} ({p2_height}, 30% bigger, {p2_body}, {', '.join(p2_features[:3])}) on RIGHT side, {p2_name} with PAINED FACIAL EXPRESSION (eyes squinting in pain, mouth open wide showing teeth in grimace, eyebrows furrowed in distress, face contorted) being PUSHED BACKWARD by force of massive attack, body leaning back and recoiling from impact, attempting to brace with arms raised defensively but failing against overwhelming attack stream, attack clearly connecting both Pokemon with visible bright impact glow where attack strikes {p2_name}'s torso, intense energy and sparks bursting from impact point, physical knockback evident. TRANSITION (4-6s): Attack dissipating, close-up on {p2_name}'s torso revealing {damage_desc.upper()} from attack impact, smoke wisping from damaged areas showing realistic damage texture, {p2_name}'s facial expression transitioning from PAIN to FIERCE ANGER (eyes narrowing with determination and rage, teeth bared in aggressive snarl, eyebrows furrowed in fury showing intense resolve for revenge). FINALE (6-10s): {p2_name} recovering from knockback and CHARGING FORWARD aggressively toward {p1_name} with wings spread wide pulling back for powerful counter-attack, body accelerating rapidly with building momentum, {p1_name} visible in frame bracing for incoming revenge attack, dramatic battle tension rising, side-angle wide shot capturing complete revenge charge sequence, realistic physics with dynamic motion, camera starts side-angle capturing both Pokemon, zooms into impact showing damage and pain, then pulls back wide as {p2_name} charges forward for revenge, realistic detailed scales/skin with texture depth, natural lighting with physically accurate shadows, organic weathering appearance, dramatic cinematic composition, 8K quality, {env_desc}, battle-worn with scratches and scars visible, weathered appearance"""

        negative_prompt = self.generate_negative_prompt(pokemon_names)
        return prompt, negative_prompt

    def generate_holistic_storyboard_prompt(
        self,
        pokemon_names: list,
        scene_type: str = "battle",
        environment: str = "volcanic",
        panel_count: int = 4
    ) -> tuple[str, str]:
        """
        Generate a COMPREHENSIVE storyboard prompt with FULL Pokemon details.
        NOTE: For better results, consider using generate_cinematic_storyboard_prompt() instead.

        Args:
            pokemon_names: List of Pokemon in the scene
            scene_type: Type of scene (battle, encounter, documentary)
            environment: Environment setting
            panel_count: Number of panels

        Returns:
            Tuple of (prompt, negative_prompt)
        """
        # Get FULL detailed Pokemon info
        p1_name = pokemon_names[0]
        p2_name = pokemon_names[1]
        p1_info = self.pokemon_info.get(p1_name.lower(), {})
        p2_info = self.pokemon_info.get(p2_name.lower(), {})

        # Build comprehensive environment description
        env_descriptions = {
            "volcanic": "volcanic battlefield - black volcanic rock terrain, pools of glowing molten lava, smoke and ash rising, dramatic orange-red ambient glow from lava, heat distortion in air, dark stormy sky with fire reflections",
            "forest": "ancient forest clearing - massive ancient trees surrounding clearing, dappled golden sunlight filtering through canopy, soft forest floor with moss and ferns, mystical atmospheric haze, natural green tones",
            "ocean": "coastal cliffside - dramatic rocky cliffs over turbulent ocean, crashing waves below, stormy dark sky with lightning, sea spray in air, blue-grey color palette with white foam",
            "cave": "underground cavern - vast cavern with glowing crystals, bioluminescent fungi, stalactites hanging from ceiling, mysterious purple-blue ambient glow, rock formations",
            "urban": "abandoned city - crumbling skyscrapers at sunset, overgrown with vines, dramatic orange sunset light, debris and rubble, post-apocalyptic atmosphere",
            "mountain": "mountain peak - above the clouds, rocky alpine terrain, snow patches, majestic vista, clear blue sky, golden hour lighting, epic scale"
        }
        env_desc = env_descriptions.get(environment, env_descriptions["volcanic"])

        # Get attack details
        p1_attacks = p1_info.get("attacks", {})
        p2_attacks = p2_info.get("attacks", {})
        p1_attack_visuals = p1_info.get("attack_visuals", {})
        p2_attack_visuals = p2_info.get("attack_visuals", {})

        # Select primary attacks
        p1_attack_name = list(p1_attacks.keys())[0] if p1_attacks else "attack"
        p2_attack_name = list(p2_attacks.keys())[0] if p2_attacks else "attack"
        p1_attack_desc = p1_attacks.get(p1_attack_name, "energy beam")
        p2_attack_desc = p2_attacks.get(p2_attack_name, "energy beam")
        p1_attack_visual = p1_attack_visuals.get(p1_attack_name.replace("_", ""), p1_attack_visuals.get("flamethrower", "visible attack effect"))
        p2_attack_visual = p2_attack_visuals.get(p2_attack_name.replace("_", ""), p2_attack_visuals.get("dragon_pulse", "visible attack effect"))

        # Get expressions for each scene
        p1_expressions = p1_info.get("expressions", {})
        p2_expressions = p2_info.get("expressions", {})

        # Get damage appearance details
        p1_damage_type = "fire" if "fire" in p1_info.get("type", "") else "impact"
        p1_damage_appearance = p1_info.get("damage_appearance", {})
        p2_damage_appearance = p2_info.get("damage_appearance", {})
        damage_desc = p1_damage_appearance.get("burn_marks", "blackened burn marks") if p1_damage_type == "fire" else p1_damage_appearance.get("impact_wounds", "impact damage")
        accumulated_damage = p2_damage_appearance.get("accumulated_damage", f"multiple {damage_desc}, exhausted but determined")

        # Build COMPREHENSIVE panel descriptions - each panel is a detailed standalone image
        panel_descs = []

        # === PANEL 1: Initial Attack ===
        panel1 = f"""
PANEL 1 (TOP-LEFT) - {p1_name} ATTACKS:

COMPOSITION:
- {p1_name} positioned on LEFT side of frame, body angled RIGHT, facing {p2_name}
- {p2_name} positioned on RIGHT side of frame, body angled LEFT, facing {p1_name}
- Both Pokemon clearly visible and FACING EACH OTHER
- Attack effect visible in CENTER between them

{p1_name.upper()} (LEFT SIDE):
- Full body visible: {p1_info.get('documentary_description', f'Photorealistic {p1_name}')}
- Height: {p1_info.get('height', 'large')}, Body: {p1_info.get('body_color', 'colored body')}
- Key features: {', '.join(p1_info.get('features', ['powerful build'])[:4])}
- Expression: {p1_expressions.get('attacking', 'fierce attacking expression')}
- Pose: Leaning forward aggressively, mouth WIDE OPEN releasing attack
- ATTACK EFFECT: {p1_attack_visual}

{p2_name.upper()} (RIGHT SIDE):
- Full body visible: {p2_info.get('documentary_description', f'Photorealistic {p2_name}')}
- Height: {p2_info.get('height', 'large')}, Body: {p2_info.get('body_color', 'colored body')}
- Key features: {', '.join(p2_info.get('features', ['powerful build'])[:4])}
- Expression: {p2_expressions.get('fierce', 'battle-ready fierce expression')}
- Pose: Defensive stance, bracing for impact, facing the incoming attack

ENVIRONMENT: {env_desc}
LIGHTING: Dramatic side lighting, attack effect illuminating both Pokemon
"""
        panel_descs.append(panel1)

        # === PANEL 2: Impact ===
        panel2 = f"""
PANEL 2 (TOP-RIGHT) - {p2_name} HIT BY ATTACK:

COMPOSITION:
- {p1_name} positioned on LEFT side of frame, facing RIGHT toward {p2_name}
- {p2_name} positioned on RIGHT side of frame, facing LEFT toward {p1_name}
- VISIBLE IMPACT EXPLOSION on {p2_name}'s body
- Both Pokemon still facing each other

{p1_name.upper()} (LEFT SIDE):
- Full body visible: {p1_info.get('body_color', 'colored body')}, {p1_info.get('body_type', 'powerful build')}
- Features: {', '.join(p1_info.get('features', [])[:3])}
- Expression: Follow-through pose after attack, intense satisfaction
- Pose: Attack follow-through, body still extended from release

{p2_name.upper()} (RIGHT SIDE) - BEING HIT:
- Full body visible but showing IMPACT REACTION
- Body: {p2_info.get('body_color', 'colored body')} NOW WITH VISIBLE DAMAGE STARTING
- Expression: {p2_expressions.get('damaged', 'pained expression, wincing')}
- VISIBLE: Impact explosion on body, {damage_desc} beginning to appear
- Pose: Body recoiling backward from hit, head thrown back in pain
- NEW DAMAGE VISIBLE: {damage_desc} appearing on {p2_name}'s body

ATTACK EFFECT: Impact explosion visible, {p1_attack_desc} hitting {p2_name}
ENVIRONMENT: {env_desc}, dust/debris from impact
"""
        panel_descs.append(panel2)

        # === PANEL 3: Counter-Attack Charging ===
        panel3 = f"""
PANEL 3 (BOTTOM-LEFT) - {p2_name} CHARGES COUNTER-ATTACK:

COMPOSITION:
- {p1_name} positioned on LEFT side of frame, facing RIGHT
- {p2_name} positioned on RIGHT side of frame, facing LEFT
- {p2_name} NOW VISIBLY DAMAGED but charging attack
- Energy gathering effect at {p2_name}'s mouth

{p1_name.upper()} (LEFT SIDE):
- Full body visible: {p1_info.get('body_color', 'colored body')}
- Features: {', '.join(p1_info.get('features', [])[:3])}
- Expression: Alert, watching {p2_name} charge up
- Pose: Battle stance, wings/limbs ready

{p2_name.upper()} (RIGHT SIDE) - DAMAGED BUT FIGHTING:
- Full body visible with ACCUMULATED DAMAGE FROM PANEL 2
- Body: {p2_info.get('body_color', 'colored body')} WITH VISIBLE {damage_desc.upper()}
- *** DAMAGE CONTINUITY: {damage_desc} clearly visible from previous attack ***
- Expression: {p2_expressions.get('charging', 'determined, charging attack')} - fierce despite injuries
- Pose: Stance widened, mouth opening with energy forming
- CHARGING EFFECT: {p2_attack_visuals.get('charging', 'visible energy gathering at mouth')}
- {p2_attack_desc} forming, energy sphere/beam building

ENVIRONMENT: {env_desc}
LIGHTING: Glow from {p2_name}'s charging attack illuminating scene
"""
        panel_descs.append(panel3)

        # === PANEL 4: Counter-Attack Release ===
        panel4 = f"""
PANEL 4 (BOTTOM-RIGHT) - {p2_name} RELEASES COUNTER-ATTACK:

COMPOSITION:
- {p1_name} positioned on LEFT side of frame, facing RIGHT - NOW BEING HIT
- {p2_name} positioned on RIGHT side of frame, facing LEFT - ATTACKING
- VISIBLE ATTACK BEAM from {p2_name} hitting {p1_name}
- Both Pokemon STILL FACING EACH OTHER

{p1_name.upper()} (LEFT SIDE) - NOW BEING HIT:
- Full body visible, reacting to incoming attack
- Body: {p1_info.get('body_color', 'colored body')}
- Expression: {p1_expressions.get('damaged', 'reacting to impact, pained')}
- Pose: Body bracing or recoiling from {p2_name}'s attack
- Impact visible on {p1_name}'s body

{p2_name.upper()} (RIGHT SIDE) - ATTACKING WITH DAMAGE:
- Full body visible: {p2_info.get('body_color', 'colored body')}
- *** DAMAGE CONTINUITY: STILL SHOWING {damage_desc.upper()} from earlier ***
- {accumulated_damage}
- Expression: {p2_expressions.get('attacking', 'fierce determination, releasing attack')}
- Pose: Full extension, mouth wide open releasing attack
- ATTACK EFFECT: {p2_attack_visual}

ATTACK VISIBLE: {p2_attack_desc} - beam/energy traveling from {p2_name} to {p1_name}
ENVIRONMENT: {env_desc}
LIGHTING: Attack beam illuminating entire scene
"""
        panel_descs.append(panel4)

        # Build the COMPREHENSIVE holistic prompt
        prompt_parts = [
            "=== PHOTOREALISTIC 4-PANEL POKEMON BATTLE STORYBOARD ===",
            "2x2 grid layout, each panel is a detailed photorealistic scene",
            "",
            "### ABSOLUTE STYLE REQUIREMENTS ###",
            "- PHOTOREALISTIC wildlife documentary photography style",
            "- BBC Earth / National Geographic quality",
            "- Shot on RED Komodo 6K camera, natural cinematic lighting",
            "- Real creature textures: scales, skin, feathers must look REAL",
            "- 8K detail, shallow depth of field, atmospheric perspective",
            "- ABSOLUTELY NOT: anime, cartoon, 3D render, CGI, illustration, stylized",
            "",
            "### CRITICAL POSITIONING RULES (EVERY PANEL) ###",
            f"- {p1_name} ALWAYS on LEFT side of frame, body facing RIGHT toward {p2_name}",
            f"- {p2_name} ALWAYS on RIGHT side of frame, body facing LEFT toward {p1_name}",
            "- BOTH Pokemon visible and FACING EACH OTHER in EVERY panel",
            "- Consistent size relationship maintained (based on actual heights)",
            "",
            "### DAMAGE CONTINUITY REQUIREMENT ###",
            f"- Panel 1-2: {p2_name} gets hit, {damage_desc} begins appearing",
            f"- Panel 3-4: {p2_name} MUST STILL SHOW {damage_desc} from earlier hit",
            "- Damage accumulates and persists across panels",
            "",
            f"### {p1_name.upper()} COMPLETE DESCRIPTION ###",
            p1_info.get('documentary_description', f'Photorealistic {p1_name}'),
            f"Height: {p1_info.get('height', 'unknown')}, Weight: {p1_info.get('weight', 'unknown')}",
            f"Body: {p1_info.get('body_color', 'unknown')}, {p1_info.get('body_type', 'powerful build')}",
            f"Features: {', '.join(p1_info.get('features', [])[:6])}",
            f"Texture: {p1_info.get('scale_texture', p1_info.get('skin_texture', 'detailed texture'))}",
            "",
            f"### {p2_name.upper()} COMPLETE DESCRIPTION ###",
            p2_info.get('documentary_description', f'Photorealistic {p2_name}'),
            f"Height: {p2_info.get('height', 'unknown')}, Weight: {p2_info.get('weight', 'unknown')}",
            f"Body: {p2_info.get('body_color', 'unknown')}, {p2_info.get('body_type', 'powerful build')}",
            f"Features: {', '.join(p2_info.get('features', [])[:6])}",
            f"Texture: {p2_info.get('skin_texture', p2_info.get('scale_texture', 'detailed texture'))}",
            "",
            "### ENVIRONMENT ###",
            env_desc,
            "",
            "### DETAILED PANEL DESCRIPTIONS ###",
            *panel_descs,
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
