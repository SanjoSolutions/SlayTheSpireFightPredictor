import numpy as np
import tensorflow as tf
import pdb

train_data_input_path = r'E:\i_train.tfrecord'
test_data_input_path = r'E:\i_test.tfrecord'

train_dataset = tf.data.TFRecordDataset(filenames=[train_data_input_path])
test_dataset = tf.data.TFRecordDataset(filenames=[test_data_input_path])

from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import LabelEncoder
import re

# TODO: Inputs for Searing Blow+n (with n > 1)
# Categories for one hot encoder. Categories are in alphabetical order and is the order used by OneHotEncoder
ALL_CARDS = [
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
    "Madness"
]

character_letters = ('B', 'G', 'R', 'P')


def replace_card_with_generalized_card(name):
    for character_letter in character_letters:
        ALL_CARDS.remove(name + '_' + character_letter)
    ALL_CARDS.append(name)

replace_card_with_generalized_card('Strike')
replace_card_with_generalized_card('Defend')

ALL_RELICS = [
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
]
ALL_ENCOUNTERS = [
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
]
ALL_CHARACTERS = [
    'DEFECT',
    'IRONCLAD',
    'THE_SILENT',
    'WATCHER'
]

card_to_index = dict()
for index, card in enumerate(ALL_CARDS):
    card_to_index[card] = index


def encode_list(list_to_encode, category):
    np_array = np.array(list_to_encode)
    encoder = OneHotEncoder(categories=[category], sparse=False)
    n_by_1 = np_array.reshape(len(np_array), 1)
    onehot_encoded = encoder.fit_transform(n_by_1)
    summed = np.sum(onehot_encoded, axis=0)
    return summed


def encode_single(value, category):
    np_array = np.array([[value]])
    encoder = OneHotEncoder(categories=[category], sparse=False)
    onehot_encoded = encoder.fit_transform(np_array)
    collapsed = np.sum(onehot_encoded, axis=0)
    # inverse = encoder.inverse_transform(collapsed[np.newaxis, ...])
    # print(np.array_equal(np_array, inverse))
    return collapsed


def generalize_strikes_and_defends(cards):
    """
    Modifies any character specific Strikes and Defends (eg. Strike_R) into
    general Strikes and Defends(Strike)
    """
    for i, s in enumerate(cards):
        if s.startswith('Strike_') or s.startswith('Defend_'):
            cards[i] = re.sub('_.', '', s)


MAX_AMOUNT_PER_CARD_TYPE = 10
MAX_UPGRADES_PER_CARD = 1


def encode_cards(cards):
    cards = np.array(cards)
    generalize_strikes_and_defends(cards)
    encoding = np.zeros(((len(ALL_CARDS) + MAX_UPGRADES_PER_CARD) * MAX_AMOUNT_PER_CARD_TYPE,))
    for card in cards:
        base_card_name, number_of_upgrades = parse_card(card)
        index = card_to_index[base_card_name]
        for offset in range(0, (MAX_AMOUNT_PER_CARD_TYPE + MAX_UPGRADES_PER_CARD), 1 + MAX_UPGRADES_PER_CARD):
            if encoding[index + offset] == 0:
                encoding[index + offset] = 1
                if number_of_upgrades >= 1:
                    encoding[index + offset + 1] = 1
                break
    return encoding


CARD_NAME_REGULAR_EXPRESSION = re.compile("^(.+?)(?:\+(\d+))?$")


def parse_card(card):
    match = CARD_NAME_REGULAR_EXPRESSION.match(card)
    if match is None:
        print('match is None', card)
    base_card_name = match.group(1)
    number_of_upgrades = match.group(2)
    if number_of_upgrades:
        number_of_upgrades = int(number_of_upgrades)
    else:
        number_of_upgrades = 0
    return base_card_name, number_of_upgrades


def encode_relics(relics):
    """
    Encodes a list of relics into a modified one-hot vector of length ALL_RELICS.
    If the relic is present in relics, it will be represented as 1 in the returned
    vector
    """
    relics = np.array(relics)
    return encode_list(relics, ALL_RELICS)


def encode_encounter(encounter):
    """
    Encode an encounter into a one-hot vector of length ALL_ENCOUNTERS
    """
    return encode_single(encounter, ALL_ENCOUNTERS)


def encode_character(character):
    """
    Encode the chosen character into a one-hot vector of length ALL_CHARACTERS
    """
    return encode_single(character, ALL_CHARACTERS)


def encode_sample_with_loop(sample):
    """
    Encode a single sample into a 1D vector
    """
    cards = encode_cards(sample['cards'])
    relics = encode_relics(sample['relics'])
    encounter = encode_encounter(sample['enemies'])
    num_and_bool_data = np.array(
        [sample['max_hp'], sample['entering_hp'], sample['ascension'], int(sample['potion_used'] == 'true')])
    return np.concatenate((cards, relics, encounter, num_and_bool_data))


# Less than 10 samples of 50 000 affected by limits
NUM_CARDS_FOR_EMB = 45
NUM_RELICS_FOR_EMB = 25
card_encoder = LabelEncoder()
card_encoder.fit(ALL_CARDS)
relic_encoder = LabelEncoder()
relic_encoder.fit(ALL_RELICS)
encounter_encoder = LabelEncoder()
encounter_encoder.fit(ALL_ENCOUNTERS)


def encode_sample_embedding_with_loop(sample):
    """
    Encode a single sample into a 1D vector. Uses a label encoder for cards, relics, and encounters.
    To be used with the model with embedding layers
    """
    # Zap = 714 after the +1
    cards = np.array(sample['cards'])
    generalize_strikes_and_defends(cards)
    enc_cards = card_encoder.transform(cards)
    enc_cards += 1
    enc_cards = enc_cards.reshape(1, -1)
    enc_cards = tf.keras.preprocessing.sequence.pad_sequences(enc_cards, maxlen=NUM_CARDS_FOR_EMB, padding='post',
                                                              truncating='post')

    relics = np.array(sample['relics'])
    enc_relics = relic_encoder.transform(relics)
    enc_relics += 1
    enc_relics = enc_relics.reshape(1, -1)
    enc_relics = tf.keras.preprocessing.sequence.pad_sequences(enc_relics, maxlen=NUM_RELICS_FOR_EMB, padding='post',
                                                               truncating='post')

    encounter = np.array(sample['enemies'])
    enc_encounter = encounter_encoder.transform([encounter])
    enc_encounter = enc_encounter.reshape(1, -1)

    num_and_bool_data = np.array(
        [sample['max_hp'], sample['entering_hp'], sample['ascension'], int(sample['potion_used'] == 'true')], ndmin=2)

    return np.concatenate((enc_cards, enc_relics, enc_encounter, num_and_bool_data), axis=None)


# Set to True to test embedding experiments
USE_EMBEDDING = False


def preprocess(sample):
    return tf.py_function(preprocess2, [sample], [tf.float32, tf.float32])


def preprocess2(sample):
    example = tf.train.Example.FromString(sample.numpy())

    parsed_example = parse_example(example)
    parsed_example['cards'] = convert_list_of_bytes_to_strings(parsed_example['cards'])
    parsed_example['relics'] = convert_list_of_bytes_to_strings(parsed_example['relics'])
    parsed_example['max_hp'] = parsed_example['max_hp'][0] / 100.
    parsed_example['entering_hp'] = parsed_example['entering_hp'][0] / 100.
    parsed_example['character'] = convert_bytes_to_string(parsed_example['character'][0])
    parsed_example['ascension'] = parsed_example['ascension'][0] / 20.
    parsed_example['enemies'] = convert_bytes_to_string(parsed_example['enemies'][0])
    parsed_example['potion_used'] = parsed_example['potion_used'][0]
    parsed_example['floor'] = parsed_example['floor'][0] / 56.
    parsed_example['damage_taken'] = parsed_example['damage_taken'][0] / 100.

    if USE_EMBEDDING:
        x = encode_sample_embedding_with_loop(parsed_example)
    else:
        x = encode_sample_with_loop(parsed_example)
    y = parsed_example['damage_taken']

    return x, y


def parse_example(example):
    result = {}
    for key, feature in example.features.feature.items():
        result[key] = get_value(feature)
    return result


def get_value(feature):
    feature_kind = feature.WhichOneof('kind')
    value = getattr(feature, feature_kind).value
    return value


def convert_list_of_bytes_to_strings(list_of_bytes):
    return list(map(convert_bytes_to_string, list_of_bytes))


def convert_bytes_to_string(bytes):
    return bytes.decode('utf-8')


from tensorflow import keras
from keras.layers import Input, Dense, Dropout, Concatenate, Average, Embedding, Lambda
from keras.layers.merge import concatenate
from keras.models import Model, Sequential
from sklearn.preprocessing import MaxAbsScaler
from sklearn.model_selection import train_test_split
import datetime, os

batch_size = 256

train_dataset = train_dataset.map(preprocess, num_parallel_calls=tf.data.AUTOTUNE)
train_dataset = train_dataset.repeat()
train_dataset = train_dataset.shuffle(5000)
train_dataset = train_dataset.batch(batch_size)
train_dataset = train_dataset.prefetch(tf.data.AUTOTUNE)

test_dataset = test_dataset.map(preprocess, num_parallel_calls=tf.data.AUTOTUNE)
test_dataset = test_dataset.repeat()
test_dataset = test_dataset.batch(batch_size)
test_dataset = test_dataset.prefetch(tf.data.AUTOTUNE)

model = tf.keras.models.Sequential([
    tf.keras.layers.Dense(
        400,
        input_shape=((len(ALL_CARDS) + MAX_UPGRADES_PER_CARD) * MAX_AMOUNT_PER_CARD_TYPE + len(ALL_RELICS) + len(ALL_ENCOUNTERS) + 4,),
        activation='relu'
    ),
    tf.keras.layers.Dropout(.2),
    tf.keras.layers.Dense(40, activation='relu'),
    tf.keras.layers.Dropout(.1),
    tf.keras.layers.Dense(1)
])

model.summary()
model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=.001),
    loss='mean_absolute_error'
)

early_stopping_callback = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=3)

# Tensorboard
logdir = os.path.join("logs", "fit", datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
tensorboard_callback = tf.keras.callbacks.TensorBoard(logdir, histogram_freq=1)

history = model.fit(
    train_dataset,
    validation_data=test_dataset,
    validation_steps=100,
    batch_size=batch_size,
    epochs=100,
    steps_per_epoch=100,
    callbacks=[
        early_stopping_callback,
        tensorboard_callback
    ],
    max_queue_size=os.cpu_count(),
    workers=os.cpu_count(),
    use_multiprocessing=True
)

model.save("STSFightPredictor")
