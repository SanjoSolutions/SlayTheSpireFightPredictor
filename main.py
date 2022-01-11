import os
import json
from functools import partial
from collections import Counter
import time
import gc
import re
import datetime
from itertools import groupby
import gzip
from multiprocessing import Process, Pool
from math import floor, ceil
from pathlib import Path
from tensorflow.io import TFRecordWriter
from tensorflow.train import Example, Features, Feature, BytesList, Int64List
from random import random

import pprint

BASE_GAME_RELICS = {
    "Burning Blood",
    "Cracked Core",
    "PureWater",
    "Ring of the Snake",
    "Akabeko",
    "Anchor",
    "Ancient Tea Set",
    "Art of War",
    "Bag of Marbles",
    "Bag of Preparation",
    "Blood Vial",
    "Bronze Scales",
    "Centennial Puzzle",
    "CeramicFish",
    "Damaru",
    "DataDisk",
    "Dream Catcher",
    "Happy Flower",
    "Juzu Bracelet",
    "Lantern",
    "MawBank",
    "MealTicket",
    "Nunchaku",
    "Oddly Smooth Stone",
    "Omamori",
    "Orichalcum",
    "Pen Nib",
    "Potion Belt",
    "PreservedInsect",
    "Red Skull",
    "Regal Pillow",
    "Smiling Mask",
    "Snake Skull",
    "Strawberry",
    "Boot",
    "Tiny Chest",
    "Toy Ornithopter",
    "Vajra",
    "War Paint",
    "Whetstone",
    "Blue Candle",
    "Bottled Flame",
    "Bottled Lightning",
    "Bottled Tornado",
    "Darkstone Periapt",
    "Yang",
    "Eternal Feather",
    "Frozen Egg 2",
    "Cables",
    "Gremlin Horn",
    "HornCleat",
    "InkBottle",
    "Kunai",
    "Letter Opener",
    "Matryoshka",
    "Meat on the Bone",
    "Mercury Hourglass",
    "Molten Egg 2",
    "Mummified Hand",
    "Ninja Scroll",
    "Ornamental Fan",
    "Pantograph",
    "Paper Crane",
    "Paper Frog",
    "Pear",
    "Question Card",
    "Self Forming Clay",
    "Shuriken",
    "Singing Bowl",
    "StrikeDummy",
    "Sundial",
    "Symbiotic Virus",
    "TeardropLocket",
    "The Courier",
    "Toxic Egg 2",
    "White Beast Statue",
    "Bird Faced Urn",
    "Calipers",
    "CaptainsWheel",
    "Champion Belt",
    "Charon's Ashes",
    "CloakClasp",
    "Dead Branch",
    "Du-Vu Doll",
    "Emotion Chip",
    "FossilizedHelix",
    "Gambling Chip",
    "Ginger",
    "Girya",
    "GoldenEye",
    "Ice Cream",
    "Incense Burner",
    "Lizard Tail",
    "Magic Flower",
    "Mango",
    "Old Coin",
    "Peace Pipe",
    "Pocketwatch",
    "Prayer Wheel",
    "Shovel",
    "StoneCalendar",
    "The Specimen",
    "Thread and Needle",
    "Tingsha",
    "Torii",
    "Tough Bandages",
    "TungstenRod",
    "Turnip",
    "Unceasing Top",
    "WingedGreaves",
    "Astrolabe",
    "Black Blood",
    "Black Star",
    "Busted Crown",
    "Calling Bell",
    "Coffee Dripper",
    "Cursed Key",
    "Ectoplasm",
    "Empty Cage",
    "FrozenCore",
    "Fusion Hammer",
    "HolyWater",
    "HoveringKite",
    "Inserter",
    "Mark of Pain",
    "Nuclear Battery",
    "Pandora's Box",
    "Philosopher's Stone",
    "Ring of the Serpent",
    "Runic Cube",
    "Runic Dome",
    "Runic Pyramid",
    "SacredBark",
    "SlaversCollar",
    "Snecko Eye",
    "Sozu",
    "Tiny House",
    "Velvet Choker",
    "VioletLotus",
    "WristBlade",
    "Bloody Idol",
    "CultistMask",
    "Enchiridion",
    "FaceOfCleric",
    "Golden Idol",
    "GremlinMask",
    "Mark of the Bloom",
    "MutagenicStrength",
    "Nloth's Gift",
    "NlothsMask",
    "Necronomicon",
    "NeowsBlessing",
    "Nilry's Codex",
    "Odd Mushroom",
    "Red Mask",
    "Spirit Poop",
    "SsserpentHead",
    "WarpedTongs",
    "Brimstone",
    "Cauldron",
    "Chemical X",
    "ClockworkSouvenir",
    "DollysMirror",
    "Frozen Eye",
    "HandDrill",
    "Lee's Waffle",
    "Medical Kit",
    "Melange",
    "Membership Card",
    "OrangePellets",
    "Orrery",
    "PrismaticShard",
    "Runic Capacitor",
    "Sling",
    "Strange Spoon",
    "TheAbacus",
    "Toolbox",
    "TwistedFunnel",
    "Black Blood",
    "Brimstone",
    "Burning Blood",
    "Champion Belt",
    "Charon's Ashes",
    "Magic Flower",
    "Mark of Pain",
    "Paper Frog",
    "Red Skull",
    "Runic Cube",
    "Self Forming Clay",
    "HoveringKite",
    "Ninja Scroll",
    "Paper Crane",
    "Ring of the Serpent",
    "Ring of the Snake",
    "Snake Skull",
    "The Specimen",
    "Tingsha",
    "Tough Bandages",
    "TwistedFunnel",
    "WristBlade",
    "Cracked Core",
    "DataDisk",
    "Emotion Chip",
    "FrozenCore",
    "Cables",
    "Inserter",
    "Nuclear Battery",
    "Runic Capacitor",
    "Symbiotic Virus",
    "CloakClasp",
    "Damaru",
    "GoldenEye",
    "HolyWater",
    "Melange",
    "PureWater",
    "VioletLotus",
    "TeardropLocket",
    "Yang"
}
BASE_GAME_POTIONS = {
    "BloodPotion",
    "ElixirPotion",
    "HeartOfIron",
    "Poison Potion",
    "CunningPotion",
    "GhostInAJar",
    "FocusPotion",
    "PotionOfCapacity",
    "EssenceOfDarkness",
    "BottledMiracle",
    "StancePotion",
    "Ambrosia",
    "Block Potion",
    "Dexterity Potion",
    "Energy Potion",
    "Explosive Potion",
    "Fire Potion",
    "Strength Potion",
    "Swift Potion",
    "Weak Potion",
    "FearPotion",
    "AttackPotion",
    "SkillPotion",
    "PowerPotion",
    "ColorlessPotion",
    "SteroidPotion",
    "SpeedPotion",
    "BlessingOfTheForge",
    "Regen Potion",
    "Ancient Potion",
    "LiquidBronze",
    "GamblersBrew",
    "EssenceOfSteel",
    "DuplicationPotion",
    "DistilledChaos",
    "LiquidMemories",
    "CultistPotion",
    "Fruit Juice",
    "SneckoOil",
    "FairyPotion",
    "SmokeBomb",
    "EntropicBrew"
}

BASE_GAME_ATTACKS = {
    "Immolate",
    "Grand Finale",
    "Go for the Eyes",
    "Core Surge",
    "Glass Knife",
    "Consecrate",
    "BowlingBash",
    "Underhanded Strike",
    "Anger",
    "WheelKick",
    "Cleave",
    "Ball Lightning",
    "Sunder",
    "FlyingSleeves",
    "Streamline",
    "Dagger Spray",
    "Reaper",
    "Shiv",
    "Bane",
    "JustLucky",
    "Unload",
    "FlurryOfBlows",
    "Compile Driver",
    "TalkToTheHand",
    "Dagger Throw",
    "WindmillStrike",
    "Iron Wave",
    "Reckless Charge",
    "All For One",
    "Dramatic Entrance",
    "Hemokinesis",
    "Blizzard",
    "Choke",
    "Poisoned Stab",
    "Body Slam",
    "Barrage",
    "Blood for Blood",
    "Meteor Strike",
    "Clash",
    "CarveReality",
    "Wallop",
    "Thunderclap",
    "Rebound",
    "Endless Agony",
    "SashWhip",
    "Melter",
    "Pummel",
    "Riddle With Holes",
    "Pommel Strike",
    "Skewer",
    "Quick Slash",
    "Twin Strike",
    "Bash",
    "RitualDagger",
    "Gash",
    "Clothesline",
    "Rampage",
    "Sever Soul",
    "Eruption",
    "Whirlwind",
    "Bite",
    "LessonLearned",
    "CutThroughFate",
    "ReachHeaven",
    "Finisher",
    "Die Die Die",
    "Ragnarok",
    "FearNoEvil",
    "SandsOfTime",
    "Smite",
    "Fiend Fire",
    "Sweeping Beam",
    "FTL",
    "Rip and Tear",
    "Heel Hook",
    "Headbutt",
    "Expunger",
    "Wild Strike",
    "HandOfGreed",
    "Eviscerate",
    "Flash of Steel",
    "Heavy Blade",
    "Searing Blow",
    "Lockon",
    "Dash",
    "Conclude",
    "ThroughViolence",
    "Backstab",
    "FollowUp",
    "Scrape",
    "Feed",
    "Beam Cell",
    "Bludgeon",
    "Slice",
    "Brilliance",
    "Cold Snap",
    "CrushJoints",
    "Flechettes",
    "Tantrum",
    "Perfected Strike",
    "Strike_B",
    "Thunder Strike",
    "Carnage",
    "Masterful Stab",
    "Dropkick",
    "Swift Strike",
    "Strike_G",
    "Hyperbeam",
    "Sword Boomerang",
    "Weave",
    "SignatureMove",
    "Uppercut",
    "Mind Blast",
    "Neutralize",
    "Doom and Gloom",
    "Sucker Punch",
    "Strike_R",
    "Strike_P",
    "EmptyFist",
    "All Out Attack",
    "Flying Knee",
    "Predator"
}
BASE_GAME_SKILLS = {
    "Crippling Poison",
    "DeusExMachina",
    "Spot Weakness",
    "Genetic Algorithm",
    "Zap",
    "Steam Power",
    "Fission",
    "Beta",
    "Dark Shackles",
    "Cloak And Dagger",
    "Storm of Steel",
    "Warcry",
    "Glacier",
    "J.A.X.",
    "Offering",
    "Vengeance",
    "Exhume",
    "Consume",
    "Power Through",
    "Dual Wield",
    "Deadly Poison",
    "Leg Sweep",
    "PanicButton",
    "Flex",
    "Redo",
    "Bullet Time",
    "Fusion",
    "Catalyst",
    "Sanctity",
    "Halt",
    "Tactician",
    "Infernal Blade",
    "Blade Dance",
    "Deflect",
    "Protect",
    "Trip",
    "Indignation",
    "Amplify",
    "ThirdEye",
    "Night Terror",
    "Reboot",
    "ForeignInfluence",
    "FameAndFortune",
    "Aggregate",
    "Expertise",
    "Chaos",
    "Intimidate",
    "Impatience",
    "The Bomb",
    "Blur",
    "True Grit",
    "Insight",
    "Setup",
    "Crescendo",
    "SpiritShield",
    "Impervious",
    "ClearTheMind",
    "EmptyBody",
    "Shrug It Off",
    "Stack",
    "Miracle",
    "Flame Barrier",
    "Seek",
    "WreathOfFlame",
    "Collect",
    "Burning Pact",
    "Rainbow",
    "InnerPeace",
    "Burst",
    "Acrobatics",
    "Blind",
    "Doppelganger",
    "Omniscience",
    "Chill",
    "Adrenaline",
    "BootSequence",
    "Wish",
    "DeceiveReality",
    "Shockwave",
    "Coolheaded",
    "Alpha",
    "Vault",
    "Bandage Up",
    "Scrawl",
    "Secret Technique",
    "Calculated Gamble",
    "Tempest",
    "Deep Breath",
    "Escape Plan",
    "Seeing Red",
    "Violence",
    "Disarm",
    "Turbo",
    "Undo",
    "Terror",
    "Force Field",
    "Armaments",
    "Havoc",
    "Secret Weapon",
    "Apotheosis",
    "Darkness",
    "Blasphemy",
    "Double Energy",
    "Rage",
    "Reinforced Body",
    "Defend_P",
    "Limit Break",
    "Entrench",
    "Phantasmal Killer",
    "WaveOfTheHand",
    "Malaise",
    "Conserve Battery",
    "Defend_R",
    "Reflex",
    "Sentinel",
    "Survivor",
    "Defend_G",
    "Meditate",
    "Defend_B",
    "Battle Trance",
    "Forethought",
    "Dualcast",
    "Auto Shields",
    "Perseverance",
    "Swivel",
    "Reprogram",
    "Hologram",
    "Corpse Explosion",
    "Second Wind",
    "Enlightenment",
    "Purity",
    "Panacea",
    "Worship",
    "Transmutation",
    "Ghostly",
    "Chrysalis",
    "Vigilance",
    "Venomology",
    "Discovery",
    "Leap",
    "Bouncing Flask",
    "PathToVictory",
    "Finesse",
    "Recycle",
    "Backflip",
    "Outmaneuver",
    "Bloodletting",
    "Concentrate",
    "Skim",
    "White Noise",
    "Master of Strategy",
    "Evaluate",
    "Prepared",
    "Good Instincts",
    "EmptyMind",
    "Jack Of All Trades",
    "Ghostly Armor",
    "Safety",
    "Metamorphosis",
    "Prostrate",
    "PiercingWail",
    "Multi-Cast",
    "Double Tap",
    "ConjureBlade",
    "Judgement",
    "Steam",
    "Distraction",
    "Dodge and Roll",
    "Thinking Ahead",
    "Pray",
    "Madness"
}
BASE_GAME_POWERS = {
    "Storm",
    "A Thousand Cuts",
    "Hello World",
    "Creative AI",
    "Inflame",
    "Sadistic Nature",
    "Wireheading",
    "After Image",
    "BattleHymn",
    "Brutality",
    "Tools of the Trade",
    "LiveForever",
    "Echo Form",
    "Juggernaut",
    "Caltrops",
    "DevaForm",
    "LikeWater",
    "Establishment",
    "Fasting2",
    "Wraith Form v2",
    "Berserk",
    "Metallicize",
    "Self Repair",
    "Adaptation",
    "Loop",
    "Envenom",
    "MentalFortress",
    "BecomeAlmighty",
    "Static Discharge",
    "Heatsinks",
    "Combust",
    "Dark Embrace",
    "Well Laid Plans",
    "Buffer",
    "Electrodynamics",
    "Panache",
    "Barricade",
    "Feel No Pain",
    "Corruption",
    "Machine Learning",
    "Noxious Fumes",
    "Infinite Blades",
    "Mayhem",
    "Study",
    "Biased Cognition",
    "Devotion",
    "Rupture",
    "Magnetism",
    "Capacitor",
    "Nirvana",
    "MasterReality",
    "Omega",
    "Accuracy",
    "Defragment",
    "Demon Form",
    "Fire Breathing",
    "Evolve",
    "Footwork"
}
BASE_GAME_CURSES = {
    "Regret",
    "Writhe",
    "AscendersBane",
    "Decay",
    "Necronomicurse",
    "Pain",
    "Parasite",
    "Doubt",
    "Injury",
    "Clumsy",
    "CurseOfTheBell",
    "Normality",
    "Pride",
    "Shame"
}

BASE_GAME_CARDS_AND_UPGRADES = {
    "Immolate",
    "Grand Finale",
    "Regret",
    "Crippling Poison",
    "Storm",
    "DeusExMachina",
    "A Thousand Cuts",
    "Spot Weakness",
    "Genetic Algorithm",
    "Go for the Eyes",
    "Zap",
    "Steam Power",
    "Wound",
    "Core Surge",
    "Fission",
    "Writhe",
    "Beta",
    "Hello World",
    "Creative AI",
    "Dark Shackles",
    "Glass Knife",
    "Consecrate",
    "Cloak And Dagger",
    "BowlingBash",
    "Underhanded Strike",
    "Anger",
    "Storm of Steel",
    "WheelKick",
    "Cleave",
    "Ball Lightning",
    "Warcry",
    "Sunder",
    "Glacier",
    "Inflame",
    "Sadistic Nature",
    "J.A.X.",
    "Offering",
    "Vengeance",
    "FlyingSleeves",
    "Exhume",
    "Streamline",
    "Wireheading",
    "Consume",
    "Power Through",
    "Dual Wield",
    "Deadly Poison",
    "Leg Sweep",
    "PanicButton",
    "Flex",
    "Redo",
    "AscendersBane",
    "Dagger Spray",
    "Bullet Time",
    "Fusion",
    "Catalyst",
    "Sanctity",
    "Halt",
    "Reaper",
    "Shiv",
    "Bane",
    "Tactician",
    "JustLucky",
    "Infernal Blade",
    "After Image",
    "Unload",
    "FlurryOfBlows",
    "Blade Dance",
    "Deflect",
    "Compile Driver",
    "TalkToTheHand",
    "BattleHymn",
    "Protect",
    "Trip",
    "Indignation",
    "Dagger Throw",
    "Amplify",
    "ThirdEye",
    "Brutality",
    "Night Terror",
    "WindmillStrike",
    "Iron Wave",
    "Reboot",
    "Reckless Charge",
    "All For One",
    "ForeignInfluence",
    "Decay",
    "FameAndFortune",
    "Tools of the Trade",
    "Aggregate",
    "Expertise",
    "Dramatic Entrance",
    "Hemokinesis",
    "Blizzard",
    "Chaos",
    "LiveForever",
    "Intimidate",
    "Echo Form",
    "Necronomicurse",
    "Juggernaut",
    "Choke",
    "Caltrops",
    "Impatience",
    "DevaForm",
    "Poisoned Stab",
    "The Bomb",
    "Blur",
    "LikeWater",
    "Body Slam",
    "True Grit",
    "Insight",
    "Setup",
    "Barrage",
    "Crescendo",
    "SpiritShield",
    "Blood for Blood",
    "Impervious",
    "ClearTheMind",
    "EmptyBody",
    "Shrug It Off",
    "Meteor Strike",
    "Establishment",
    "Fasting2",
    "Clash",
    "Stack",
    "Miracle",
    "CarveReality",
    "Wallop",
    "Thunderclap",
    "Rebound",
    "Flame Barrier",
    "Seek",
    "Endless Agony",
    "WreathOfFlame",
    "Collect",
    "SashWhip",
    "Wraith Form v2",
    "Melter",
    "Berserk",
    "Pummel",
    "Burning Pact",
    "Riddle With Holes",
    "Metallicize",
    "Self Repair",
    "Pommel Strike",
    "Pain",
    "Rainbow",
    "InnerPeace",
    "Burst",
    "Acrobatics",
    "Adaptation",
    "Loop",
    "Blind",
    "Doppelganger",
    "Skewer",
    "Omniscience",
    "Envenom",
    "Chill",
    "Adrenaline",
    "Quick Slash",
    "Twin Strike",
    "BootSequence",
    "Parasite",
    "Bash",
    "RitualDagger",
    "Gash",
    "Wish",
    "Clothesline",
    "DeceiveReality",
    "MentalFortress",
    "Shockwave",
    "BecomeAlmighty",
    "Rampage",
    "Coolheaded",
    "Static Discharge",
    "Alpha",
    "Heatsinks",
    "Vault",
    "Bandage Up",
    "Scrawl",
    "Sever Soul",
    "Eruption",
    "Whirlwind",
    "Bite",
    "LessonLearned",
    "Secret Technique",
    "Calculated Gamble",
    "Tempest",
    "Combust",
    "Deep Breath",
    "Doubt",
    "Escape Plan",
    "CutThroughFate",
    "ReachHeaven",
    "Finisher",
    "Dark Embrace",
    "Die Die Die",
    "Well Laid Plans",
    "Ragnarok",
    "Buffer",
    "Electrodynamics",
    "FearNoEvil",
    "Seeing Red",
    "SandsOfTime",
    "Smite",
    "Violence",
    "Disarm",
    "Turbo",
    "Panache",
    "Undo",
    "Fiend Fire",
    "Terror",
    "Force Field",
    "Dazed",
    "Barricade",
    "Armaments",
    "Havoc",
    "Secret Weapon",
    "Apotheosis",
    "Sweeping Beam",
    "Feel No Pain",
    "FTL",
    "Rip and Tear",
    "Darkness",
    "Corruption",
    "Heel Hook",
    "Blasphemy",
    "Injury",
    "Double Energy",
    "Rage",
    "Headbutt",
    "Machine Learning",
    "Reinforced Body",
    "Defend_P",
    "Limit Break",
    "Entrench",
    "Noxious Fumes",
    "Infinite Blades",
    "Phantasmal Killer",
    "WaveOfTheHand",
    "Malaise",
    "Conserve Battery",
    "Defend_R",
    "Mayhem",
    "Reflex",
    "Study",
    "Expunger",
    "Sentinel",
    "Survivor",
    "Wild Strike",
    "Defend_G",
    "HandOfGreed",
    "Meditate",
    "Eviscerate",
    "Flash of Steel",
    "Defend_B",
    "Battle Trance",
    "Forethought",
    "Dualcast",
    "Auto Shields",
    "Perseverance",
    "Swivel",
    "Heavy Blade",
    "Slimed",
    "Clumsy",
    "Biased Cognition",
    "Searing Blow",
    "Devotion",
    "Reprogram",
    "Hologram",
    "Corpse Explosion",
    "Second Wind",
    "Enlightenment",
    "Purity",
    "Panacea",
    "Lockon",
    "Dash",
    "Worship",
    "Conclude",
    "ThroughViolence",
    "Transmutation",
    "Ghostly",
    "Backstab",
    "Chrysalis",
    "FollowUp",
    "Void",
    "Scrape",
    "Feed",
    "Vigilance",
    "Rupture",
    "Venomology",
    "Discovery",
    "Beam Cell",
    "Leap",
    "CurseOfTheBell",
    "Bouncing Flask",
    "PathToVictory",
    "Bludgeon",
    "Finesse",
    "Slice",
    "Recycle",
    "Backflip",
    "Outmaneuver",
    "Bloodletting",
    "Brilliance",
    "Magnetism",
    "Concentrate",
    "Skim",
    "White Noise",
    "Capacitor",
    "Cold Snap",
    "CrushJoints",
    "Master of Strategy",
    "Flechettes",
    "Tantrum",
    "Perfected Strike",
    "Strike_B",
    "Thunder Strike",
    "Carnage",
    "Masterful Stab",
    "Nirvana",
    "Evaluate",
    "Prepared",
    "Good Instincts",
    "Dropkick",
    "Swift Strike",
    "Normality",
    "Strike_G",
    "MasterReality",
    "Omega",
    "Hyperbeam",
    "Accuracy",
    "Sword Boomerang",
    "EmptyMind",
    "Pride",
    "Defragment",
    "Jack Of All Trades",
    "Demon Form",
    "Fire Breathing",
    "Ghostly Armor",
    "Weave",
    "Safety",
    "Metamorphosis",
    "Prostrate",
    "SignatureMove",
    "Uppercut",
    "PiercingWail",
    "Mind Blast",
    "Neutralize",
    "Multi-Cast",
    "Shame",
    "Doom and Gloom",
    "Evolve",
    "Double Tap",
    "Sucker Punch",
    "Burn",
    "ConjureBlade",
    "Strike_R",
    "Judgement",
    "Footwork",
    "Strike_P",
    "Steam",
    "Distraction",
    "Dodge and Roll",
    "Thinking Ahead",
    "EmptyFist",
    "All Out Attack",
    "Flying Knee",
    "Predator",
    "Pray",
    "Madness",

    # upgrades
    "Immolate+1",
    "Grand Finale+1",
    "Regret+1",
    "Crippling Poison+1",
    "Storm+1",
    "DeusExMachina+1",
    "A Thousand Cuts+1",
    "Spot Weakness+1",
    "Genetic Algorithm+1",
    "Go for the Eyes+1",
    "Zap+1",
    "Steam Power+1",
    "Wound+1",
    "Core Surge+1",
    "Fission+1",
    "Writhe+1",
    "Beta+1",
    "Hello World+1",
    "Creative AI+1",
    "Dark Shackles+1",
    "Glass Knife+1",
    "Consecrate+1",
    "Cloak And Dagger+1",
    "BowlingBash+1",
    "Underhanded Strike+1",
    "Anger+1",
    "Storm of Steel+1",
    "WheelKick+1",
    "Cleave+1",
    "Ball Lightning+1",
    "Warcry+1",
    "Sunder+1",
    "Glacier+1",
    "Inflame+1",
    "Sadistic Nature+1",
    "J.A.X.+1",
    "Offering+1",
    "Vengeance+1",
    "FlyingSleeves+1",
    "Exhume+1",
    "Streamline+1",
    "Wireheading+1",
    "Consume+1",
    "Power Through+1",
    "Dual Wield+1",
    "Deadly Poison+1",
    "Leg Sweep+1",
    "PanicButton+1",
    "Flex+1",
    "Redo+1",
    "AscendersBane+1",
    "Dagger Spray+1",
    "Bullet Time+1",
    "Fusion+1",
    "Catalyst+1",
    "Sanctity+1",
    "Halt+1",
    "Reaper+1",
    "Shiv+1",
    "Bane+1",
    "Tactician+1",
    "JustLucky+1",
    "Infernal Blade+1",
    "After Image+1",
    "Unload+1",
    "FlurryOfBlows+1",
    "Blade Dance+1",
    "Deflect+1",
    "Compile Driver+1",
    "TalkToTheHand+1",
    "BattleHymn+1",
    "Protect+1",
    "Trip+1",
    "Indignation+1",
    "Dagger Throw+1",
    "Amplify+1",
    "ThirdEye+1",
    "Brutality+1",
    "Night Terror+1",
    "WindmillStrike+1",
    "Iron Wave+1",
    "Reboot+1",
    "Reckless Charge+1",
    "All For One+1",
    "ForeignInfluence+1",
    "Decay+1",
    "FameAndFortune+1",
    "Tools of the Trade+1",
    "Aggregate+1",
    "Expertise+1",
    "Dramatic Entrance+1",
    "Hemokinesis+1",
    "Blizzard+1",
    "Chaos+1",
    "LiveForever+1",
    "Intimidate+1",
    "Echo Form+1",
    "Necronomicurse+1",
    "Juggernaut+1",
    "Choke+1",
    "Caltrops+1",
    "Impatience+1",
    "DevaForm+1",
    "Poisoned Stab+1",
    "The Bomb+1",
    "Blur+1",
    "LikeWater+1",
    "Body Slam+1",
    "True Grit+1",
    "Insight+1",
    "Setup+1",
    "Barrage+1",
    "Crescendo+1",
    "SpiritShield+1",
    "Blood for Blood+1",
    "Impervious+1",
    "ClearTheMind+1",
    "EmptyBody+1",
    "Shrug It Off+1",
    "Meteor Strike+1",
    "Establishment+1",
    "Fasting2+1",
    "Clash+1",
    "Stack+1",
    "Miracle+1",
    "CarveReality+1",
    "Wallop+1",
    "Thunderclap+1",
    "Rebound+1",
    "Flame Barrier+1",
    "Seek+1",
    "Endless Agony+1",
    "WreathOfFlame+1",
    "Collect+1",
    "SashWhip+1",
    "Wraith Form v2+1",
    "Melter+1",
    "Berserk+1",
    "Pummel+1",
    "Burning Pact+1",
    "Riddle With Holes+1",
    "Metallicize+1",
    "Self Repair+1",
    "Pommel Strike+1",
    "Pain+1",
    "Rainbow+1",
    "InnerPeace+1",
    "Burst+1",
    "Acrobatics+1",
    "Adaptation+1",
    "Loop+1",
    "Blind+1",
    "Doppelganger+1",
    "Skewer+1",
    "Omniscience+1",
    "Envenom+1",
    "Chill+1",
    "Adrenaline+1",
    "Quick Slash+1",
    "Twin Strike+1",
    "BootSequence+1",
    "Parasite+1",
    "Bash+1",
    "RitualDagger+1",
    "Gash+1",
    "Wish+1",
    "Clothesline+1",
    "DeceiveReality+1",
    "MentalFortress+1",
    "Shockwave+1",
    "BecomeAlmighty+1",
    "Rampage+1",
    "Coolheaded+1",
    "Static Discharge+1",
    "Alpha+1",
    "Heatsinks+1",
    "Vault+1",
    "Bandage Up+1",
    "Scrawl+1",
    "Sever Soul+1",
    "Eruption+1",
    "Whirlwind+1",
    "Bite+1",
    "LessonLearned+1",
    "Secret Technique+1",
    "Calculated Gamble+1",
    "Tempest+1",
    "Combust+1",
    "Deep Breath+1",
    "Doubt+1",
    "Escape Plan+1",
    "CutThroughFate+1",
    "ReachHeaven+1",
    "Finisher+1",
    "Dark Embrace+1",
    "Die Die Die+1",
    "Well Laid Plans+1",
    "Ragnarok+1",
    "Buffer+1",
    "Electrodynamics+1",
    "FearNoEvil+1",
    "Seeing Red+1",
    "SandsOfTime+1",
    "Smite+1",
    "Violence+1",
    "Disarm+1",
    "Turbo+1",
    "Panache+1",
    "Undo+1",
    "Fiend Fire+1",
    "Terror+1",
    "Force Field+1",
    "Dazed+1",
    "Barricade+1",
    "Armaments+1",
    "Havoc+1",
    "Secret Weapon+1",
    "Apotheosis+1",
    "Sweeping Beam+1",
    "Feel No Pain+1",
    "FTL+1",
    "Rip and Tear+1",
    "Darkness+1",
    "Corruption+1",
    "Heel Hook+1",
    "Blasphemy+1",
    "Injury+1",
    "Double Energy+1",
    "Rage+1",
    "Headbutt+1",
    "Machine Learning+1",
    "Reinforced Body+1",
    "Defend_P+1",
    "Limit Break+1",
    "Entrench+1",
    "Noxious Fumes+1",
    "Infinite Blades+1",
    "Phantasmal Killer+1",
    "WaveOfTheHand+1",
    "Malaise+1",
    "Conserve Battery+1",
    "Defend_R+1",
    "Mayhem+1",
    "Reflex+1",
    "Study+1",
    "Expunger+1",
    "Sentinel+1",
    "Survivor+1",
    "Wild Strike+1",
    "Defend_G+1",
    "HandOfGreed+1",
    "Meditate+1",
    "Eviscerate+1",
    "Flash of Steel+1",
    "Defend_B+1",
    "Battle Trance+1",
    "Forethought+1",
    "Dualcast+1",
    "Auto Shields+1",
    "Perseverance+1",
    "Swivel+1",
    "Heavy Blade+1",
    "Slimed+1",
    "Clumsy+1",
    "Biased Cognition+1",
    "Searing Blow+1",
    "Searing Blow+2",
    "Searing Blow+3",
    "Searing Blow+4",
    "Searing Blow+5",
    "Searing Blow+6",
    "Searing Blow+7",
    "Searing Blow+8",
    "Searing Blow+9",
    "Searing Blow+10",
    "Searing Blow+11",
    "Searing Blow+12",
    "Searing Blow+13",
    "Searing Blow+14",
    "Searing Blow+15",
    "Devotion+1",
    "Reprogram+1",
    "Hologram+1",
    "Corpse Explosion+1",
    "Second Wind+1",
    "Enlightenment+1",
    "Purity+1",
    "Panacea+1",
    "Lockon+1",
    "Dash+1",
    "Worship+1",
    "Conclude+1",
    "ThroughViolence+1",
    "Transmutation+1",
    "Ghostly+1",
    "Backstab+1",
    "Chrysalis+1",
    "FollowUp+1",
    "Void+1",
    "Scrape+1",
    "Feed+1",
    "Vigilance+1",
    "Rupture+1",
    "Venomology+1",
    "Discovery+1",
    "Beam Cell+1",
    "Leap+1",
    "CurseOfTheBell+1",
    "Bouncing Flask+1",
    "PathToVictory+1",
    "Bludgeon+1",
    "Finesse+1",
    "Slice+1",
    "Recycle+1",
    "Backflip+1",
    "Outmaneuver+1",
    "Bloodletting+1",
    "Brilliance+1",
    "Magnetism+1",
    "Concentrate+1",
    "Skim+1",
    "White Noise+1",
    "Capacitor+1",
    "Cold Snap+1",
    "CrushJoints+1",
    "Master of Strategy+1",
    "Flechettes+1",
    "Tantrum+1",
    "Perfected Strike+1",
    "Strike_B+1",
    "Thunder Strike+1",
    "Carnage+1",
    "Masterful Stab+1",
    "Nirvana+1",
    "Evaluate+1",
    "Prepared+1",
    "Good Instincts+1",
    "Dropkick+1",
    "Swift Strike+1",
    "Normality+1",
    "Strike_G+1",
    "MasterReality+1",
    "Omega+1",
    "Hyperbeam+1",
    "Accuracy+1",
    "Sword Boomerang+1",
    "EmptyMind+1",
    "Pride+1",
    "Defragment+1",
    "Jack Of All Trades+1",
    "Demon Form+1",
    "Fire Breathing+1",
    "Ghostly Armor+1",
    "Weave+1",
    "Safety+1",
    "Metamorphosis+1",
    "Prostrate+1",
    "SignatureMove+1",
    "Uppercut+1",
    "PiercingWail+1",
    "Mind Blast+1",
    "Neutralize+1",
    "Multi-Cast+1",
    "Shame+1",
    "Doom and Gloom+1",
    "Evolve+1",
    "Double Tap+1",
    "Sucker Punch+1",
    "Burn+1",
    "ConjureBlade+1",
    "Strike_R+1",
    "Judgement+1",
    "Footwork+1",
    "Strike_P+1",
    "Steam+1",
    "Distraction+1",
    "Dodge and Roll+1",
    "Thinking Ahead+1",
    "EmptyFist+1",
    "All Out Attack+1",
    "Flying Knee+1",
    "Predator+1",
    "Pray+1",
    "Madness+1"
}

BASE_GAME_ENEMIES = {
    'Blue Slaver',
    'Cultist',
    'Jaw Worm',
    '2 Louse',
    'Small Slimes',
    
    'Gremlin Gang',
    'Large Slime',
    'Looter',
    'Lots of Slimes',
    'Exordium Thugs',
    'Exordium Wildlife',
    'Red Slaver',
    '3 Louse',
    '2 Fungi Beasts',
    
    'Gremlin Nob',
    'Lagavulin',
    '3 Sentries',
    
    'Lagavulin Event',
    'The Mushroom Lair',
    
    'The Guardian',
    'Hexaghost',
    'Slime Boss',
    
    'Chosen',
    'Shell Parasite',
    'Spheric Guardian',
    '3 Byrds',
    '2 Thieves',
    
    'Chosen and Byrds',
    'Sentry and Sphere',
    'Snake Plant',
    'Snecko',
    'Centurion and Healer',
    'Cultist and Chosen',
    '3 Cultists',
    'Shelled Parasite and Fungi',
    
    'Gremlin Leader',
    'Slavers',
    'Book of Stabbing',
    
    'Masked Bandits',
    'Colosseum Nobs',
    'Colosseum Slavers',
    
    'Automaton',
    'Champ',
    'Collector',
    
    'Orb Walker',
    '3 Darklings',
    '3 Shapes',
    
    'Transient',
    '4 Shapes',
    'Maw',
    'Jaw Worm Horde',
    'Sphere and 2 Shapes',
    'Spire Growth',
    'Writhing Mass',
    
    'Giant Head',
    'Nemesis',
    'Reptomancer',
    
    'Mysterious Sphere',
    'Mind Bloom Boss Battle',
    '2 Orb Walkers',
    
    'Awakened One',
    'Donu and Deca',
    'Time Eater',
    
    'Shield and Spear',
    
    'The Heart'
}


input_path = r'E:\google_drive\2_0'
train_output_path = r'E:\i_train.tfrecord'
test_output_path = r'E:\i_test.tfrecord'
TEST_DATA_PERCENTAGE = 0.2


def process_runs():
    Path(train_output_path).unlink(missing_ok=True)
    Path(test_output_path).unlink(missing_ok=True)
    file_paths = gather_file_paths(input_path)
    total_number_of_files = float(len(file_paths))
    number_of_files_processed = 0
    last_reported_percentage_of_files_processed = 0
    total_number_of_examples = 0
    with TFRecordWriter(train_output_path) as train_file_writer:
        with TFRecordWriter(test_output_path) as test_file_writer:
            with Pool(8) as pool:
                for examples in pool.imap_unordered(process, file_paths, chunksize=1):
                    for example in examples:
                        if random() < TEST_DATA_PERCENTAGE:
                            test_file_writer.write(example)
                        else:
                            train_file_writer.write(example)
                        total_number_of_examples += 1

                    number_of_files_processed += 1
                    percentage_of_files_processed = number_of_files_processed / total_number_of_files
                    if percentage_of_files_processed - last_reported_percentage_of_files_processed >= 0.10:
                        print(str(floor(percentage_of_files_processed * 100)) + '% of files processed.')
                        last_reported_percentage_of_files_processed = percentage_of_files_processed

    print('Number of examples: ' + str(total_number_of_examples))


def gather_file_paths(folder_path):
    file_paths = []
    for root_path, _, file_names in os.walk(folder_path):
        for file_name in file_names:
            file_path = os.path.join(root_path, file_name)
            file_paths.append(file_path)
    return file_paths


act_3_bosses = {
    'Awakened One',
    'Donu and Deca',
    'Time Eater',
}


def process(file_path):
    examples = []
    if file_path.endswith(".run.json") or file_path.endswith(".run") or file_path.endswith(".json.gz"):
        try:
            entries = read_file(file_path)
            for entry in entries:
                if not is_bad_entry(entry):
                    try:
                        run_examples = process_run(entry)
                        run_examples = filter(lambda example: example['enemies'] in act_3_bosses, run_examples)
                        examples.extend(run_examples)
                    except Exception as e:
                        pass
        except Exception as e:
            pass

    return convert_to_tfrecord_examples(examples)


def convert_to_tfrecord_examples(examples):
    return list(map(convert_to_tfrecord_example, examples))


def convert_to_tfrecord_example(example):
    return Example(features=Features(feature={
        'cards': Feature(bytes_list=BytesList(value=to_byte_strings(example['cards']))),
        'relics': Feature(bytes_list=BytesList(value=to_byte_strings(example['relics']))),
        'max_hp': Feature(int64_list=Int64List(value=[example['max_hp']])),
        'entering_hp': Feature(int64_list=Int64List(value=[example['entering_hp']])),
        'character': Feature(bytes_list=BytesList(value=[to_byte_string(example['character'])])),
        'ascension': Feature(int64_list=Int64List(value=[example['ascension']])),
        'enemies': Feature(bytes_list=BytesList(value=[to_byte_string(example['enemies'])])),
        'potion_used': Feature(int64_list=Int64List(value=[example['potion_used']])),
        'floor': Feature(int64_list=Int64List(value=[example['floor']])),
        'damage_taken': Feature(int64_list=Int64List(value=[example['damage_taken']])),
    })).SerializeToString()


def to_byte_strings(strings):
    return list(map(to_byte_string, strings))


def to_byte_string(string):
    return string.encode('utf-8')


def read_file(file_path):
    with open_file(file_path) as file:
        data = json.load(file)
        if not isinstance(data, list):
            data = [data]
        data = list(map(lambda entry: entry['event'] if 'event' in entry else entry, data))
        return data


def open_file(file_path):
    filename, file_extension = os.path.splitext(file_path)
    if file_extension == '.gz':
        return gzip.open(file_path, 'r')
    else:
        return open(file_path, 'r', encoding='utf8')


def process_run(data):
    battle_stats_by_floor = {battle_stat['floor']: battle_stat for battle_stat in data['damage_taken']}
    events_by_floor = {event_stat['floor']: event_stat for event_stat in data['event_choices']}
    card_choices_by_floor = {key: list(group) for key, group in groupby(data['card_choices'], key=lambda card_choice: card_choice['floor'])}
    relics_by_floor = get_relics_by_floor(data)
    campfire_choices_by_floor = {campfire_choice['floor']: campfire_choice for campfire_choice in
                                 data['campfire_choices']}
    purchases_by_floor = get_stat_with_separate_floor_list(data, 'items_purchased', 'item_purchase_floors')
    purges_by_floor = get_stat_with_separate_floor_list(data, 'items_purged', 'items_purged_floors')
    potion_use_by_floor = list(set(data['potions_floor_usage']))

    current_deck = get_starting_deck(data['character_chosen'], data['ascension_level'])
    current_relics = get_starting_relics(data['character_chosen'])

    unknown_removes_by_floor = dict()
    unknown_upgrades_by_floor = dict()
    unknown_transforms_by_floor = dict()
    unknown_cards_by_floor = dict()
    unknowns = (unknown_removes_by_floor, unknown_upgrades_by_floor, unknown_transforms_by_floor, unknown_cards_by_floor)

    master_deck = sorted(data['master_deck'])

    processed_fights = list()
    for floor in range(0, data['floor_reached'] + 1):
        if floor in battle_stats_by_floor and floor != 1:
            fight_data = process_battle(data, battle_stats_by_floor[floor], potion_use_by_floor, current_deck, current_relics, floor)
            processed_fights.append(fight_data)

        if floor in relics_by_floor:
            process_relics(relics_by_floor[floor], current_relics, data['relics'], current_deck, master_deck, floor, unknowns)

        if floor in card_choices_by_floor:
            process_card_choice(card_choices_by_floor[floor], current_deck, current_relics)

        if floor in campfire_choices_by_floor:
            restart_needed, new_data = try_process_data(partial(process_campfire_choice, campfire_choices_by_floor[floor], current_deck), floor, current_deck, current_relics, data, unknowns)
            if restart_needed:
                return process_run(new_data)

        if floor in purchases_by_floor:
            try_process_data(partial(process_purchases, purchases_by_floor[floor], current_deck, master_deck, current_relics, data['relics'], floor, unknowns), floor, current_deck, current_relics, data, unknowns)

        if floor in purges_by_floor:
            try_process_data(partial(process_purges, purges_by_floor[floor], current_deck), floor, current_deck, current_relics, data, unknowns)

        if floor in events_by_floor:
            try_process_data(partial(process_events, events_by_floor[floor], current_deck, master_deck, current_relics, data['relics'], floor, unknowns), floor, current_deck, current_relics, data, unknowns)

        if floor == 0:
            process_neow(data['neow_bonus'], current_deck, current_relics, data['relics'], unknowns)

    current_deck.sort()
    current_relics.sort()
    master_relics = sorted(data['relics'])
    if current_deck != master_deck or current_relics != master_relics:
        success, new_data = resolve_missing_data(current_deck, current_relics, master_deck=data['master_deck'],
                                                 master_relics=data['relics'], unknowns=unknowns, master_data=data)
        if success:
            return process_run(new_data)
        else:
            last_fight = processed_fights[-1]
            last_fight['cards'] = list(data['master_deck'])
            last_fight['relics'] = list(data['relics'])
            processed_fights = [last_fight]
            return processed_fights
    else:
        return processed_fights


def try_process_data(func, floor, current_deck, current_relics, master_data, unknowns):
    try:
        func()
        return False, None
    except Exception as e:
        # success, new_data = resolve_missing_data(current_deck, current_relics, master_deck=master_data['master_deck'], master_relics=master_data['relics'], unknowns=unknowns, master_data=master_data)
        # if success:
        #     return success, new_data
        # else:
        floor_reached = master_data['floor_reached']
        master_deck = master_data['master_deck']
        # print(f'\nFunction {func.func.__name__} failed on floor {floor} of {floor_reached}')
        # print(f'Reason for exception: {e}')
        # print(f'Current Deck\t: {sorted(current_deck)}')
        # print(f'Master Deck\t\t: {sorted(master_deck)}\n')
        raise e


def process_battle(master_data, battle_stat, potion_use_by_floor, current_deck, current_relics, floor):
    if battle_stat['enemies'] not in BASE_GAME_ENEMIES:
        raise RuntimeError('Modded enemy')

    fight_data = dict()
    fight_data['cards'] = list(current_deck)
    fight_data['relics'] = list(current_relics)
    fight_data['max_hp'] = master_data['max_hp_per_floor'][floor - 2]
    fight_data['entering_hp'] = master_data['current_hp_per_floor'][floor - 2]
    fight_data['character'] = master_data['character_chosen']
    fight_data['ascension'] = master_data['ascension_level']
    fight_data['enemies'] = battle_stat['enemies']
    fight_data['potion_used'] = floor in potion_use_by_floor
    fight_data['floor'] = floor
    if master_data['current_hp_per_floor'] == 0:
        hp_change = battle_stat['damage']
    else:
        hp_change = master_data['current_hp_per_floor'][floor - 2] - master_data['current_hp_per_floor'][floor - 1]
    fight_data['damage_taken'] = hp_change
    return fight_data


def process_card_choice(card_choice_data, current_deck, current_relics):
    for card_choice in card_choice_data:
        picked_card = card_choice['picked']
        if picked_card != 'SKIP' and picked_card != 'Singing Bowl':
            add_card_to_deck(current_deck, current_relics, picked_card)


def add_card_to_deck(current_deck, current_relics, card):
    if 'Molten Egg 2' in current_relics and card in BASE_GAME_ATTACKS and card[-2] != '+1':
        card += '+1'
    if 'Toxic Egg 2' in current_relics and card in BASE_GAME_SKILLS and card[-2] != '+1':
        card += '+1'
    if 'card Egg 2' in current_relics and card in BASE_GAME_POWERS and card[-2] != '+1':
        picked_card += '+1'
    current_deck.append(card)



def process_relics(relics, current_relics, master_relics, current_deck, master_deck, floor, unknowns):
    for r in relics:
        obtain_relic(r, current_deck, master_deck, current_relics, master_relics, floor, unknowns)


def process_campfire_choice(campfire_data, current_deck):
    choice = campfire_data['key']
    if choice == 'SMITH':
        upgrade_card(current_deck, campfire_data['data'])
    if choice == 'PURGE':
        current_deck.remove(campfire_data['data'])


def process_purchases(purchase_data, current_deck, master_deck, current_relics, master_relics, floor, unknowns):
    purchased_cards = [x for x in purchase_data if x not in BASE_GAME_RELICS and x not in BASE_GAME_POTIONS]
    purchased_relics = [x for x in purchase_data if x not in purchased_cards and x not in BASE_GAME_POTIONS]
    current_deck.extend(purchased_cards)
    for r in purchased_relics:
        obtain_relic(r, current_deck, master_deck, current_relics, master_relics, floor, unknowns)


def process_purges(purge_data, current_deck):
    for card in purge_data:
        current_deck.remove(card)


def process_events(event_data, current_deck, master_deck, current_relics, master_relics, floor, unknowns):
    if 'relics_obtained' in event_data:
        for r in event_data['relics_obtained']:
            obtain_relic(r, current_deck, master_deck, current_relics, master_relics, floor, unknowns)
    if 'relics_lost' in event_data:
        for relic in event_data['relics_lost']:
            current_relics.remove(relic)
    if 'cards_obtained' in event_data:
        for card in event_data['cards_obtained']:
            add_card_to_deck(current_deck, current_relics, card)
    if 'cards_removed' in event_data:
        for card in event_data['cards_removed']:
            current_deck.remove(card)
    if 'cards_upgraded' in event_data:
        for card in event_data['cards_upgraded']:
            upgrade_card(current_deck, card)
    if 'cards_transformed' in event_data:
        for card in event_data['cards_transformed']:
            current_deck.remove(card)
    if 'event_name' in event_data and event_data['event_name'] == 'Vampires':
        current_deck[:] = [x for x in current_deck if not x.startswith('Strike')]


def process_neow(neow_bonus, current_deck, current_relics, master_relics, unknowns):
    unknown_removes_by_floor, unknown_upgrades_by_floor, unknown_transforms_by_floor, unknown_cards_by_floor = unknowns
    if neow_bonus == 'ONE_RARE_RELIC' or neow_bonus == 'RANDOM_COMMON_RELIC':
        current_relics.append(master_relics[1])
    if neow_bonus == 'BOSS_RELIC':
        current_relics[0] = master_relics[0]
    if neow_bonus == 'THREE_ENEMY_KILL':
        current_relics.append('NeowsBlessing')
    if neow_bonus == 'UPGRADE_CARD':
        unknown_upgrades_by_floor[0] = [{'type': 'unknown'}]
    if neow_bonus == 'REMOVE_CARD':
        unknown_removes_by_floor[0] = 1
    if neow_bonus == 'REMOVE_TWO':
        unknown_removes_by_floor[0] = 2
    if neow_bonus == 'TRANSFORM_CARD':
        unknown_transforms_by_floor[0] = 1
    if neow_bonus == 'THREE_CARDS':
        unknown_cards_by_floor[0] = [{'type': 'unknown'}]
    if neow_bonus == 'THREE_RARE_CARDS' or neow_bonus == 'ONE_RANDOM_RARE_CARD':
        unknown_cards_by_floor[0] = [{'type': 'rare'}]


def upgrade_card(current_deck, card_to_upgrade):
    card_to_upgrade_index = current_deck.index(card_to_upgrade)
    # if 'earing' in card_to_upgrade:
        # print(f'Probably Searing Blow id: {card_to_upgrade}')
    current_deck[card_to_upgrade_index] += '+1'


def obtain_relic(relic_to_obtain, current_deck, master_deck, current_relics, master_relics, floor, unknowns):
    unknown_removes_by_floor, unknown_upgrades_by_floor, unknown_transforms_by_floor, unknown_cards_by_floor = unknowns
    if relic_to_obtain == 'Black Blood':
        current_relics[0] = 'Black Blood'
        return
    if relic_to_obtain == 'Ring of the Serpent':
        current_relics[0] = 'Ring of the Serpent'
        return
    if relic_to_obtain == 'FrozenCore':
        current_relics[0] = 'FrozenCore'
        return
    if relic_to_obtain == 'Calling Bell':
        current_relics.extend(master_relics[len(current_relics) + 1:len(current_relics) + 4])
        current_deck.append('CurseOfTheBell')
    if relic_to_obtain == 'Empty Cage':
        unknown_removes_by_floor[floor] = 2
    if relic_to_obtain == 'Whetstone':
        unknown_upgrades_by_floor[floor] = [{'type': 'attack'}, {'type': 'attack'}]
    if relic_to_obtain == 'War Paint':
        unknown_upgrades_by_floor[floor] = [{'type': 'skill'}, {'type': 'skill'}]
    if relic_to_obtain == 'HolyWater':
        current_relics.remove('PureWater')
    elif relic_to_obtain == 'Necronomicon' and 'Necronomicurse' in master_deck:
        current_deck.append('Necronomicurse')
    current_relics.append(relic_to_obtain)


def get_stats_by_floor_with_list(data, data_key):
    stats_by_floor = dict()
    if data_key in data:
        for stat in data[data_key]:
            floor = stat['floor']
            if floor not in stats_by_floor:
                stats_by_floor[floor] = list()
            stats_by_floor[floor].append(stat['key'])
    return stats_by_floor


def get_stat_with_separate_floor_list(data, obtain_key, floor_key):
    stats_by_floor = dict()
    if obtain_key in data and floor_key in data and len(data[obtain_key]) == len(data[floor_key]):
        obtains = data[obtain_key]
        floors = data[floor_key]
        for index, obt in enumerate(obtains):
            flr = floors[index]
            obt = obtains[index]
            if flr not in stats_by_floor:
                stats_by_floor[flr] = list()
            stats_by_floor[flr].append(obt)
    return stats_by_floor


def get_relics_by_floor(data):
    relics_by_floor = get_stats_by_floor_with_list(data, 'relics_obtained')
    boss_relics = data['boss_relics']
    if len(boss_relics) >= 1:
        first_boss_relic = get_picked_boss_relic(boss_relics, 0)
        if first_boss_relic is not None:
            relics_by_floor[17] = [first_boss_relic]
    if len(boss_relics) >= 2:
        second_boss_relic = get_picked_boss_relic(boss_relics, 1)
        if second_boss_relic is not None:
            relics_by_floor[34] = [second_boss_relic]
    return relics_by_floor


def get_picked_boss_relic(boss_relics, index):
    if len(boss_relics) > index:
        boss_relic = boss_relics[index]
        if 'picked' in boss_relic:
            picked_relic = boss_relic['picked']
            if picked_relic != 'SKIP':
                return picked_relic
    return None


def get_starting_relics(character):
    if character == 'IRONCLAD':
        return ['Burning Blood']
    elif character == 'THE_SILENT':
        return ['Ring of the Snake']
    elif character == 'DEFECT':
        return ['Cracked Core']
    elif character == 'WATCHER':
        return ['PureWater']
    else:
        print(f'Unsupported character {character}')


def get_starting_deck(character, ascension):
    basic_deck = ['Strike', 'Strike', 'Strike', 'Strike', 'Defend', 'Defend', 'Defend', 'Defend']
    if character == 'IRONCLAD':
        basic_deck.extend(['Strike', 'Bash'])
        character_spefic_basic_cards(basic_deck, '_R')
    elif character == 'THE_SILENT':
        basic_deck.extend(['Strike', 'Defend', 'Survivor', 'Neutralize'])
        character_spefic_basic_cards(basic_deck, '_G')
    elif character == 'DEFECT':
        basic_deck.extend(['Zap', 'Dualcast'])
        character_spefic_basic_cards(basic_deck, '_B')
    elif character == 'WATCHER':
        basic_deck.extend(['Eruption', 'Vigilance'])
        character_spefic_basic_cards(basic_deck, '_P')
    else:
        print(f'Unsupported character {character}')
    if ascension >= 10:
        basic_deck.append('AscendersBane')
    return basic_deck


def character_spefic_basic_cards(deck, suffix):
    for index, card in enumerate(deck):
        if card == 'Strike' or card == 'Defend':
            deck[index] = card + suffix


def resolve_missing_data(current_deck, current_relics, master_deck, master_relics, unknowns, master_data):
    unknown_removes_by_floor, unknown_upgrades_by_floor, unknown_transforms_by_floor, unknown_cards_by_floor = unknowns
    if current_deck != master_deck:
        if len(current_deck) > len(master_deck) and len(unknown_removes_by_floor) == 1 and len(unknown_upgrades_by_floor) == 0 and len(unknown_transforms_by_floor) == 0 and len(unknown_cards_by_floor) == 0:
            differences = list((Counter(current_deck) - Counter(master_deck)).elements())
            for floor, number_of_removes in unknown_removes_by_floor.items():
                if len(differences) == number_of_removes:
                    master_data['items_purged'].extend(differences)
                    for i in range(number_of_removes):
                        items_purched_floors = master_data['items_purged_floors']
                        items_purched_floors.append(floor)
                    return True, master_data
        elif len(current_deck) == len(master_deck) and len(unknown_upgrades_by_floor) == 1 and len(unknown_removes_by_floor) == 0 and len(unknown_transforms_by_floor) == 0 and len(unknown_cards_by_floor) == 0:
            diff1 = list((Counter(current_deck) - Counter(master_deck)).elements())
            diff2 = list((Counter(master_deck) - Counter(current_deck)).elements())
            if len(diff1) == len(diff2):
                upgraded_names_of_unupgraded_cards = [x + "+1" for x in diff1]
                if upgraded_names_of_unupgraded_cards == diff2:
                    for floor, upgrade_types in unknown_upgrades_by_floor.items():
                        if len(diff1) == len(upgrade_types):
                            for unupgraded_card in diff1:
                                master_data['campfire_choices'].append({"data": unupgraded_card, "floor": floor, "key": "SMITH"})
                            return True, master_data

    return False, None


BUILD_VERSION_REGEX = re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}$')


def valid_build_number(string):
    pattern = re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}$')
    if pattern.match(string):
        m = re.search('(.+)-(.+)-(.+)', string)
        year = int(m.group(1))
        month = int(m.group(2))
        day = int(m.group(3))

        date = datetime.date(year, month, day)
        if date >= datetime.date(2020, 1, 14):
            return True

    return False


def is_bad_entry(data):
    key = 'floor_reached'
    if key not in data or data[key] < 51 or data[key] > 56:
        return True

    key = 'character_chosen'
    # if data[key] not in ['IRONCLAD', 'THE_SILENT', 'DEFECT', 'WATCHER']:
    if data[key] != 'WATCHER':
        # print(f'Modded character: {data[key]}')
        return True

    key = 'build_version'
    if key not in data or valid_build_number(data[key]) is False:
        return True

    # Non standard runs
    key = 'is_trial'
    if key not in data or data[key] is True:
        return True

    key = 'is_daily'
    if key not in data or data[key] is True:
        return True

    key = 'daily_mods'
    if key in data:
        return True

    key = 'chose_seed'
    if key not in data or data[key] is True:
        return True

    # Endless mode
    key = 'is_endless'
    if key not in data or data[key] is True:
        return True

    # Corrupted files
    necessary_fields = ['damage_taken', 'event_choices', 'card_choices', 'relics_obtained', 'campfire_choices',
                        'items_purchased', 'item_purchase_floors', 'items_purged', 'items_purged_floors',
                        'character_chosen', 'boss_relics', 'floor_reached', 'master_deck', 'relics']
    for field in necessary_fields:
        if field not in data:
            # print(f'File missing field: {field}')
            return True

    key = 'master_deck'
    if key not in data or set(data[key]).issubset(BASE_GAME_CARDS_AND_UPGRADES) is False:
        return True

    key = 'relics'
    if key not in data or set(data[key]).issubset(BASE_GAME_RELICS) is False:
        return True



def write_file(data, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)


if __name__ == '__main__':
    process_runs()

"""
# Keys

gold_per_floor
floor_reached
playtime
items_purged
score
play_id
local_time
is_ascension_mode
campfire_choices
neow_cost
seed_source_timestamp
circlet_count
master_deck
relics
potions_floor_usage
damage_taken
seed_played
potions_obtained
is_trial
path_per_floor
character_chosen
items_purchased
campfire_rested
item_purchase_floors
current_hp_per_floor
gold
neow_bonus
is_prod
is_daily
chose_seed
campfire_upgraded
win_rate
timestamp
path_taken
build_version
purchased_purges
victory
max_hp_per_floor
card_choices
player_experience
relics_obtained
event_choices
is_beta
boss_relics
items_purged_floors
is_endless
potions_floor_spawned
killed_by
ascension_level
"""
