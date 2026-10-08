"""Knowledge Graph Seeds — Balanced across all 20 domains."""

# ══════════════════════════════════════════════════════════════════════
#  DOMAIN-ORGANIZED SEEDS (~80-100 per domain)
# ══════════════════════════════════════════════════════════════════════

SEEDS_BY_DOMAIN = {

    # ─────────────────────────────────────────────────────────────────
    "ComputerScience": [
        # Programming Languages
        "Python", "JavaScript", "TypeScript", "Java", "Kotlin",
        "Cplusplus", "CSharp", "Rust", "Golang", "Swift",
        "Ruby", "Scala", "Haskell", "Erlang", "Elixir",
        "Perl", "Lua", "Dart", "Julia", "Fortran",
        "Cobol", "Assembly", "Prolog", "Lisp", "Clojure",
        # Algorithms
        "BubbleSort", "MergeSort", "QuickSort", "HeapSort",
        "BinarySearch", "DepthFirstSearch", "BreadthFirstSearch",
        "DijkstraAlgorithm", "BellmanFord", "FloydWarshall",
        "DynamicProgramming", "KnapsackProblem", "Backtracking",
        "KMPAlgorithm", "AStarSearch", "TopologicalSort",
        # Data Structures
        "LinkedList", "BinaryTree", "HashTable", "Stack", "Queue",
        "Heap", "Graph", "Trie", "SegmentTree", "BloomFilter",
        "RedBlackTree", "AVLTree", "BPlusTree", "SkipList",
        # Core CS
        "OperatingSystem", "Compiler", "Database", "Networking",
        "Cryptography", "Cybersecurity", "CloudComputing",
        "Blockchain", "QuantumComputing", "Microservice",
        "Docker", "Kubernetes", "RestApi", "GraphQL",
        # AI / ML
        "ArtificialIntelligence", "MachineLearning", "DeepLearning",
        "NeuralNetwork", "Transformer", "Backpropagation",
        "ReinforcementLearning", "NaturalLanguageProcessing",
        "ComputerVision", "GenerativeAdversarialNetwork",
        "LargeLanguageModel", "ConvolutionalNeuralNetwork",
        "RecurrentNeuralNetwork", "TransferLearning",
    ],

    # ─────────────────────────────────────────────────────────────────
    "Mathematics": [
        # Algebra
        "LinearAlgebra", "AbstractAlgebra", "Matrix", "Vector",
        "Eigenvalue", "Eigenvector", "Determinant", "GroupTheory",
        "RingTheory", "FieldTheory", "Polynomial", "Quaternion",
        # Calculus & Analysis
        "Calculus", "Derivative", "Integral", "DifferentialEquation",
        "PartialDerivative", "TaylorSeries", "FourierTransform",
        "LaplaceTransform", "RealAnalysis", "ComplexAnalysis",
        "FunctionalAnalysis", "MeasureTheory",
        # Geometry & Topology
        "EuclideanGeometry", "NonEuclideanGeometry", "Topology",
        "DifferentialGeometry", "AlgebraicTopology", "Manifold",
        "Trigonometry", "FractalGeometry",
        # Discrete Math
        "Combinatorics", "GraphTheory", "NumberTheory",
        "SetTheory", "Probability", "Statistics",
        "BayesianInference", "MarkovChain", "StochasticProcess",
        "GameTheory", "InformationTheory", "CategoryTheory",
        # Applied Math
        "NumericalAnalysis", "Optimization", "LinearProgramming",
        "ConvexOptimization", "MonteCarlo", "ChaosTheory",
        # Famous Mathematicians
        "Euler", "Gauss", "Riemann", "Ramanujan", "Hilbert",
        "Cantor", "Galois", "Fibonacci", "Turing", "Godel",
        "Pythagoras", "Archimedes", "Leibniz", "Fermat", "Noether",
    ],

    # ─────────────────────────────────────────────────────────────────
    "Physics": [
        # Classical Mechanics
        "ClassicalMechanics", "NewtonianMechanics", "Lagrangian",
        "Hamiltonian", "Momentum", "AngularMomentum", "Torque",
        "Friction", "Elasticity", "FluidMechanics", "Bernoulli",
        # Electromagnetism
        "Electromagnetism", "MaxwellEquations", "ElectricField",
        "MagneticField", "Capacitor", "Inductor", "Resistor",
        "Electromagnetic", "Faraday", "Coulomb",
        # Quantum Mechanics
        "QuantumMechanics", "WaveFunction", "Superposition",
        "Entanglement", "HeisenbergUncertainty", "SchrodingerEquation",
        "Qubit", "QuantumField", "DiracEquation",
        # Thermodynamics
        "Thermodynamics", "Entropy", "Enthalpy", "Carnot",
        "BoltzmannDistribution", "StatisticalMechanics",
        # Relativity
        "GeneralRelativity", "SpecialRelativity", "Spacetime",
        "Lorentz", "GravitationalWave", "BlackHole",
        # Particle Physics
        "StandardModel", "Quark", "Lepton", "Boson", "Fermion",
        "HiggsBoson", "Photon", "Gluon", "Neutrino", "Positron",
        "Antimatter", "Hadron", "Meson", "Baryon",
        # Optics & Waves
        "Optics", "Refraction", "Diffraction", "Interference",
        "Polarization", "WaveParticleDuality", "Laser",
        # Famous Physicists
        "AlbertEinstein", "IsaacNewton", "NielsBohr",
        "RichardFeynman", "MaxPlanck", "WernerHeisenberg",
        "NikolaTesla", "MarieCurie", "StephenHawking",
    ],

    # ─────────────────────────────────────────────────────────────────
    "Chemistry": [
        # General
        "PeriodicTable", "Atom", "Molecule", "Ion", "Isotope",
        "Electron", "Proton", "Neutron", "ChemicalBond",
        "CovalentBond", "IonicBond", "MetallicBond", "HydrogenBond",
        "VanDerWaals", "Electronegativity", "Valence",
        # Organic Chemistry
        "OrganicChemistry", "Alkane", "Alkene", "Alkyne",
        "Benzene", "Phenol", "Alcohol", "Aldehyde", "Ketone",
        "CarboxylicAcid", "Ester", "Amine", "Amide",
        "Polymer", "Polymerization", "Isomer", "Chirality",
        # Inorganic Chemistry
        "InorganicChemistry", "TransitionMetal", "Coordination",
        "Catalyst", "Alloy", "Crystal", "Semiconductor",
        # Physical Chemistry
        "PhysicalChemistry", "Thermochemistry", "Electrochemistry",
        "ChemicalKinetics", "ChemicalEquilibrium", "Stoichiometry",
        "Molarity", "Enthalpy", "GibbsFreeEnergy", "ActivationEnergy",
        # Analytical Chemistry
        "Spectroscopy", "Chromatography", "MassSpectrometry",
        "Titration", "Distillation", "Crystallization",
        # Biochemistry
        "AminoAcid", "Protein", "Enzyme", "Glucose",
        "Lipid", "Nucleotide", "ATP", "DNA", "RNA",
        # Famous Chemists
        "DmitriMendeleev", "AntoineLavoisier", "LinusPauling",
        "AlfredNobel", "RobertBoyle", "JohnDalton",
    ],

    # ─────────────────────────────────────────────────────────────────
    "Biology": [
        # Cell Biology
        "CellBiology", "Eukaryote", "Prokaryote", "CellMembrane",
        "Nucleus", "Mitochondria", "Ribosome", "EndoplasmicReticulum",
        "GolgiApparatus", "Lysosome", "Chloroplast", "Cytoplasm",
        # Genetics
        "Genetics", "Gene", "Chromosome", "Allele", "Genotype",
        "Phenotype", "Mitosis", "Meiosis", "Mutation",
        "CRISPR", "GenomeEditing", "Epigenetics", "HumanGenomeProject",
        # Molecular Biology
        "Transcription", "Translation", "DNAReplication",
        "ProteinSynthesis", "PCR", "GeneExpression",
        # Evolution
        "Evolution", "NaturalSelection", "Adaptation", "Speciation",
        "Extinction", "CommonAncestor", "Phylogenetics",
        "CharlesDarwin", "AlfredWallace", "GregorMendel",
        # Ecology
        "Ecology", "Ecosystem", "FoodChain", "FoodWeb",
        "Biodiversity", "Symbiosis", "Parasitism", "Mutualism",
        "Predator", "Prey", "Habitat", "Niche",
        # Anatomy & Physiology
        "Anatomy", "Physiology", "Heart", "Brain", "Lung",
        "Liver", "Kidney", "Skeleton", "MuscularSystem",
        "NervousSystem", "DigestiveSystem", "CirculatorySystem",
        # Microbiology
        "Microbiology", "Bacteria", "Virus", "Fungi", "Protozoa",
        "Antibiotic", "Vaccine", "Pathogen", "Microbiome",
        # Botany & Zoology
        "Photosynthesis", "Pollination", "Germination",
        "Vertebrate", "Invertebrate", "Mammal", "Reptile",
    ],

    # ─────────────────────────────────────────────────────────────────
    "Medicine": [
        # Medical Specialties
        "Cardiology", "Neurology", "Oncology", "Pediatrics",
        "Dermatology", "Orthopedics", "Ophthalmology", "Psychiatry",
        "Radiology", "Pathology", "Surgery", "Anesthesiology",
        "EmergencyMedicine", "InternalMedicine", "Gastroenterology",
        # Diseases
        "Cancer", "Diabetes", "Hypertension", "Stroke",
        "Alzheimer", "Parkinson", "Asthma", "Pneumonia",
        "Tuberculosis", "Malaria", "HIV", "COVID19",
        "Influenza", "Hepatitis", "Epilepsy", "Arthritis",
        # Treatments
        "Chemotherapy", "Radiotherapy", "Immunotherapy",
        "Antibiotics", "Antivirals", "Surgery", "Transplant",
        "Dialysis", "Prosthetics", "GeneTherapy", "StemCell",
        # Diagnostics
        "MRI", "CTScan", "Ultrasound", "XRay", "Biopsy",
        "Endoscopy", "BloodTest", "Electrocardiogram",
        # Pharmacology
        "Pharmacology", "DrugInteraction", "Dosage",
        "Pharmacokinetics", "ClinicalTrial", "Placebo",
        "FDAApproval", "Bioavailability",
        # Public Health
        "Epidemiology", "Pandemic", "Quarantine", "Vaccination",
        "PublicHealth", "WorldHealthOrganization",
        # Famous Physicians
        "Hippocrates", "EdwardJenner", "AlexanderFleming",
        "JosephLister", "WilliamHarvey", "LouisPasteur",
        "RobertKoch", "FlorenNightingale",
    ],

    # ─────────────────────────────────────────────────────────────────
    "History": [
        # Ancient Civilizations
        "AncientEgypt", "AncientGreece", "AncientRome",
        "Mesopotamia", "IndusValleyCivilization", "AncientChina",
        "PersianEmpire", "ByzantineEmpire", "MongolEmpire",
        "OttomanEmpire", "RomanRepublic", "Carthage",
        "Phoenicia", "Assyria", "Babylon", "MayaCivilization",
        "AztecEmpire", "IncaEmpire", "MauryaEmpire", "GuptaEmpire",
        # Medieval & Renaissance
        "MedievalEurope", "Feudalism", "Crusades", "BlackDeath",
        "Renaissance", "Reformation", "HolyRomanEmpire",
        "HundredYearsWar", "MagnaCarta", "Vikings",
        # Modern History
        "FrenchRevolution", "AmericanRevolution", "IndustrialRevolution",
        "Colonialism", "Imperialism", "Abolition", "SlaveTradeHistory",
        "WorldWarOne", "WorldWarTwo", "Holocaust", "ColdWar",
        "VietnamWar", "KoreanWar", "BerlinWall", "SovietUnion",
        "Decolonization", "CivilRightsMovement", "Apartheid",
        "ArabSpring", "NuclearAge", "SpaceRace", "MoonLanding",
        # Historical Figures
        "AlexanderTheGreat", "JuliusCaesar", "Cleopatra",
        "GenghisKhan", "NapoleonBonaparte", "QueenVictoria",
        "AbrahamLincoln", "MahatmaGandhi", "NelsonMandela",
        "WinstonChurchill", "MartinLutherKingJr", "MaoZedong",
        "SimonBolivar", "OttoBismarck", "SunYatSen",
        # Civilizational Concepts
        "Silk Road", "Treaty", "Diplomacy", "Constitution",
        "Monarchy", "Republic", "Empire", "Revolution",
    ],

    # ─────────────────────────────────────────────────────────────────
    "Philosophy": [
        # Branches
        "Ontology", "Epistemology", "Ethics", "Aesthetics",
        "Logic", "Metaphysics", "PoliticalPhilosophy",
        "PhilosophyOfMind", "PhilosophyOfScience",
        "PhilosophyOfLanguage", "PhilosophyOfReligion",
        # Schools of Thought
        "Empiricism", "Rationalism", "Idealism", "Materialism",
        "Pragmatism", "Positivism", "Existentialism", "Absurdism",
        "Nihilism", "Stoicism", "Epicureanism", "Hedonism",
        "Utilitarianism", "Deontology", "VirtueEthics",
        "Phenomenology", "Hermeneutics", "Dialectics",
        "Determinism", "FreeWill", "Compatibilism",
        "Dualism", "Monism", "Solipsism", "Skepticism",
        "Relativism", "Constructivism", "Structuralism",
        "Poststructuralism", "Deconstructionism",
        # Famous Philosophers
        "Socrates", "Plato", "Aristotle", "Confucius",
        "LaoTzu", "SiddharthaGautama", "Epicurus",
        "MarcusAurelius", "ThomasAquinas", "ReneDescartes",
        "ImmanuelKant", "GeorgHegel", "FriedrichNietzsche",
        "JeanPaulSartre", "SimoneDeBeauvoir", "KarlMarx",
        "JohnLocke", "DavidHume", "BertrandRussell",
        "LudwigWittgenstein", "MichelFoucault", "JacquesDerrida",
        "HannahArendt", "JohnRawls", "PeterSinger",
        # Key Concepts
        "CategoricalImperative", "SocialContract", "AllegoryOfTheCave",
        "TrolleyProblem", "Cogito", "WillToPower", "EternalReturn",
        "Qualia", "TabularRasa", "OriginalPosition",
    ],

    # ─────────────────────────────────────────────────────────────────
    "Economics": [
        # Microeconomics
        "SupplyAndDemand", "Elasticity", "MarketEquilibrium",
        "MarketFailure", "Externality", "PublicGood",
        "Monopoly", "Oligopoly", "PerfectCompetition",
        "PriceDiscrimination", "ConsumerSurplus", "ProducerSurplus",
        "UtilityTheory", "IndifferenceCurve", "MarginalCost",
        # Macroeconomics
        "GDP", "GNP", "Inflation", "Deflation", "Recession",
        "Unemployment", "FiscalPolicy", "MonetaryPolicy",
        "InterestRate", "ExchangeRate", "BalanceOfPayments",
        "Stagflation", "Austerity", "QuantitativeEasing",
        "NationalDebt", "TradeDeficit", "EconomicGrowth",
        # Schools of Economic Thought
        "KeynesianEconomics", "Neoclassical", "AustrianSchool",
        "Monetarism", "BehavioralEconomics", "Marxism",
        "SupplySide", "InstitutionalEconomics",
        # Finance
        "StockMarket", "Bond", "Derivative", "Futures",
        "Options", "HedgeFund", "MutualFund", "Cryptocurrency",
        "Bitcoin", "CentralBank", "FederalReserve",
        "WorldBank", "IMF", "Inflation",
        # Trade
        "FreeTrade", "Protectionism", "Tariff", "Subsidy",
        "Globalization", "WTO", "NAFTA",
        # Famous Economists
        "AdamSmith", "JohnMaynardKeynes", "MiltonFriedman",
        "KarlMarx", "DavidRicardo", "FriedrichHayek",
        "JosephStiglitz", "PaulKrugman", "ThomasPiketty",
        "AmartyaSen", "DanielKahneman",
    ],

    # ─────────────────────────────────────────────────────────────────
    "PoliticalScience": [
        # Systems of Government
        "Democracy", "Autocracy", "Oligarchy", "Theocracy",
        "Monarchy", "Republic", "Federalism", "Confederation",
        "ParliamentarySystem", "PresidentialSystem",
        "ConstitutionalMonarchy", "DirectDemocracy",
        # Political Ideologies
        "Liberalism", "Conservatism", "Socialism", "Communism",
        "Fascism", "Anarchism", "Libertarianism", "Populism",
        "Nationalism", "Progressivism", "Centrism",
        "SocialDemocracy", "Neoliberalism",
        # Institutions
        "UnitedNations", "EuropeanUnion", "NATO",
        "InternationalCourt", "SecurityCouncil",
        "WorldTradeOrganization", "Parliament", "Congress",
        "SupremeCourt", "Constitution", "BillOfRights",
        # Concepts
        "SeparationOfPowers", "ChecksAndBalances", "RuleOfLaw",
        "Sovereignty", "Legitimacy", "SocialContract",
        "HumanRights", "CivilLiberties", "FreedomOfSpeech",
        "Suffrage", "Election", "Referendum",
        "Geopolitics", "Diplomacy", "SoftPower", "HardPower",
        "Deterrence", "Sanctions", "Embargo",
        # Law
        "CriminalLaw", "CivilLaw", "ConstitutionalLaw",
        "InternationalLaw", "HumanitarianLaw",
        "IntellectualProperty", "Patent", "Copyright",
        # Political Thinkers
        "NiccoloMachiavelli", "ThomasHobbes", "JohnLocke",
        "JeanJacquesRousseau", "Montesquieu", "JohnStuartMill",
        "MaxWeber", "NoamChomsky",
    ],

    # ─────────────────────────────────────────────────────────────────
    "Psychology": [
        # Schools
        "Behaviorism", "CognitivePsychology", "Psychoanalysis",
        "HumanisticPsychology", "GestaltPsychology",
        "EvolutionaryPsychology", "PositivePsychology",
        # Core Concepts
        "ClassicalConditioning", "OperantConditioning",
        "Reinforcement", "Punishment", "Habituation",
        "CognitiveDissonance", "Conformity", "Obedience",
        "BystanderEffect", "MilgramExperiment", "StanfordPrisonExperiment",
        # Cognitive
        "Memory", "Attention", "Perception", "Learning",
        "Intelligence", "Creativity", "DecisionMaking",
        "CognitiveBias", "ConfirmationBias", "AnchoringBias",
        "DunningKrugerEffect", "HaloEffect",
        "WorkingMemory", "LongTermMemory", "Encoding",
        # Developmental
        "DevelopmentalPsychology", "Attachment", "PiagetStages",
        "CriticalPeriod", "AdolescentDevelopment",
        # Personality
        "BigFivePersonality", "MyersBriggs",
        "Introversion", "Extraversion", "Neuroticism",
        # Clinical
        "Anxiety", "Depression", "PTSD", "Schizophrenia",
        "BipolarDisorder", "Autism", "ADHD", "OCD",
        "CognitiveBehavioralTherapy", "Psychotherapy",
        # Social Psychology
        "SocialInfluence", "GroupThink", "Stereotyping",
        "Prejudice", "Discrimination",
        # Famous Psychologists
        "SigmundFreud", "CarlJung", "BFSkinner",
        "IvanPavlov", "AbrahamMaslow", "CarlRogers",
        "JeanPiaget", "AlbertBandura", "DanielKahneman",
        "WilliamJames", "ElizabethLoftus",
    ],

    # ─────────────────────────────────────────────────────────────────
    "Linguistics": [
        # Core Areas
        "Phonetics", "Phonology", "Morphology", "Syntax",
        "Semantics", "Pragmatics", "Discourse",
        "Sociolinguistics", "Psycholinguistics", "ComputationalLinguistics",
        "HistoricalLinguistics", "Neurolinguistics",
        # Units of Language
        "Phoneme", "Morpheme", "Lexeme", "Syllable",
        "Vowel", "Consonant", "Diphthong",
        # Grammar
        "Noun", "Verb", "Adjective", "Adverb", "Preposition",
        "Conjunction", "Pronoun", "Tense", "Aspect", "Mood",
        "ActiveVoice", "PassiveVoice", "SubjectVerbAgreement",
        # Language Families
        "IndoEuropean", "SinoTibetan", "Afroasiatic",
        "NigerCongo", "Austronesian", "Dravidian",
        "Uralic", "Turkic", "Semitic",
        # Writing Systems
        "Alphabet", "Logograph", "Syllabary", "Cuneiform",
        "Hieroglyphics", "Braille", "Devanagari",
        # Concepts
        "LanguageAcquisition", "Bilingualism", "CodeSwitching",
        "Pidgin", "Creole", "Dialect", "Accent",
        "SapirWhorfHypothesis", "UniversalGrammar",
        "Metaphor", "Metonymy", "Irony", "Ambiguity",
        "Etymology", "Polysemy", "Homonym",
        "Translation", "Interpretation", "SignLanguage",
        # Famous Linguists
        "NoamChomsky", "FerdinandDeSaussure", "StevenPinker",
        "EdwardSapir", "BenjaminWhorf", "RomanJakobson",
        "LeonardBloomfield",
    ],

    # ─────────────────────────────────────────────────────────────────
    "Arts": [
        # Visual Art Movements
        "Renaissance", "Baroque", "Romanticism", "Impressionism",
        "PostImpressionism", "Expressionism", "Cubism", "Surrealism",
        "Dadaism", "ArtNouveau", "ArtDeco", "PopArt",
        "Minimalism", "ConceptualArt", "AbstractExpressionism",
        # Famous Artists
        "LeonardoDaVinci", "Michelangelo", "Raphael", "Caravaggio",
        "Rembrandt", "Vermeer", "ClaudeMonet", "VincentVanGogh",
        "PabloPicasso", "SalvadorDali", "AndyWarhol",
        "FridaKahlo", "GustavKlimt", "EdvardMunch",
        # Famous Works
        "MonaLisa", "StarryNight", "TheLastSupper", "GuernicaPainting",
        "ThePersistenceOfMemory", "TheScream",
        # Music
        "ClassicalMusic", "Jazz", "Blues", "Rock", "Pop",
        "HipHop", "Electronic", "Folk", "Country", "Reggae",
        "Opera", "Symphony", "Concerto", "Sonata",
        "Harmony", "Melody", "Rhythm", "Counterpoint",
        # Famous Composers
        "JohannSebastianBach", "LudwigVanBeethoven",
        "WolfgangAmadeusMozart", "FredericChopin",
        "IgorStravinsky", "ClaudeDebussy", "PyotrTchaikovsky",
        # Literature
        "WilliamShakespeare", "LeoTolstoy", "FyodorDostoevsky",
        "JaneAusten", "CharlesDickens", "MarkTwain",
        "FranzKafka", "JamesJoyce", "VirginiaWoolf",
        "GabrielGarciaMarquez", "ToniMorrison", "HarukiMurakami",
        # Literary Concepts
        "Novel", "Poetry", "Drama", "Tragedy", "Comedy",
        "Satire", "Allegory", "Metaphor", "Irony",
        # Architecture
        "GothicArchitecture", "RomanesqueArchitecture",
        "ModernArchitecture", "Bauhaus", "FrankLloydWright",
        # Cinema
        "Cinema", "Filmmaking", "AlfredHitchcock", "StanleyKubrick",
        "AkiraKurosawa", "MartinScorsese",
    ],

    # ─────────────────────────────────────────────────────────────────
    "Geography": [
        # Physical Geography
        "Continent", "Ocean", "Mountain", "River", "Desert",
        "Glacier", "Volcano", "Island", "Peninsula", "Plateau",
        "Valley", "Delta", "Canyon", "Reef", "Cave",
        # Major Features
        "Himalayas", "Andes", "Alps", "RockyMountains",
        "Amazon", "Nile", "Mississippi", "Ganges", "Danube",
        "Sahara", "Gobi", "Atacama", "Kalahari",
        "PacificOcean", "AtlanticOcean", "IndianOcean", "ArcticOcean",
        "GreatBarrierReef", "MarianasTrench",
        # Countries (Global Coverage)
        "UnitedStates", "China", "India", "Russia", "Brazil",
        "Japan", "Germany", "UnitedKingdom", "France", "Italy",
        "Canada", "Australia", "SouthKorea", "Mexico", "Indonesia",
        "SaudiArabia", "SouthAfrica", "Nigeria", "Egypt", "Turkey",
        "Argentina", "Thailand", "Vietnam", "Kenya", "NewZealand",
        # Capital Cities
        "Washington", "Beijing", "NewDelhi", "Moscow", "Tokyo",
        "London", "Paris", "Berlin", "Rome", "Canberra",
        "Brasilia", "Ottawa", "Cairo", "Nairobi",
        # Earth Science
        "PlateTectonics", "Earthquake", "Tsunami", "Hurricane",
        "Erosion", "Weathering", "SoilFormation",
        "WaterCycle", "CarbonCycle", "NitrogenCycle",
        "Latitude", "Longitude", "Equator", "Tropics",
        # Oceanography & Meteorology
        "Oceanography", "Meteorology", "Monsoon", "ElNino",
        "JetStream", "TradeWinds", "OceanCurrents",
    ],

    # ─────────────────────────────────────────────────────────────────
    "Engineering": [
        # Civil Engineering
        "CivilEngineering", "StructuralEngineering", "Bridge",
        "Dam", "Tunnel", "Skyscraper", "Foundation",
        "ConcreteReinforcement", "SteelStructure",
        # Mechanical Engineering
        "MechanicalEngineering", "InternalCombustionEngine",
        "SteamEngine", "Turbine", "GearSystem",
        "Hydraulics", "Pneumatics", "Robotics",
        "ThreeDPrinting", "CADDesign", "FiniteElementAnalysis",
        # Electrical Engineering
        "ElectricalEngineering", "Circuit", "Transistor",
        "Diode", "Amplifier", "Oscillator", "Transformer",
        "Microprocessor", "FPGA", "IntegratedCircuit",
        "PowerGrid", "RenewableEnergy", "SmartGrid",
        # Aerospace
        "AerospaceEngineering", "Aerodynamics", "Lift", "Drag",
        "Thrust", "RocketPropulsion", "JetEngine",
        "Satellite", "SpaceStation", "OrbitMechanics",
        # Chemical Engineering
        "ChemicalEngineering", "Reactor", "Distillation",
        "ProcessControl", "MaterialScience", "Nanotechnology",
        # Biomedical Engineering
        "BiomedicalEngineering", "MedicalImaging", "Prosthetics",
        "TissueEngineering", "Biomechanics",
        # Software / Systems
        "SystemsEngineering", "ControlSystems", "PIDController",
        "Feedback", "SignalProcessing", "EmbeddedSystem",
        # Famous Engineers
        "NikolaTesla", "ThomasEdison", "JamesWatt",
        "HenryFord", "ElonMusk", "WernerVonBraun",
    ],

    # ─────────────────────────────────────────────────────────────────
    "Sociology": [
        # Core Concepts
        "Society", "Culture", "SocialNorms", "Values",
        "Socialization", "SocialRole", "SocialStatus",
        "SocialClass", "SocialMobility", "SocialChange",
        "SocialInstitution", "Bureaucracy",
        # Stratification
        "Inequality", "Poverty", "Wealth", "MiddleClass",
        "CasteSystem", "RacialInequality", "GenderInequality",
        "Intersectionality", "Privilege",
        # Family & Kinship
        "Family", "Marriage", "Divorce", "Kinship",
        "Patriarchy", "Matriarchy", "NuclearFamily", "ExtendedFamily",
        # Religion
        "Christianity", "Islam", "Hinduism", "Buddhism",
        "Judaism", "Sikhism", "Taoism", "Confucianism",
        "Shinto", "Zoroastrianism", "Animism",
        "Secularism", "Fundamentalism", "Atheism",
        # Social Movements
        "CivilRightsMovement", "FeministMovement", "LaborMovement",
        "EnvironmentalMovement", "AntiWarMovement",
        "LGBTRightsMovement", "BLM",
        # Anthropology
        "CulturalAnthropology", "PhysicalAnthropology",
        "Ethnography", "Archaeology", "Excavation",
        "HumanEvolution", "Neanderthal", "HomoSapiens",
        "Paleolithic", "Neolithic", "BronzeAge", "IronAge",
        # Famous Sociologists
        "EmileDurkheim", "MaxWeber", "KarlMarx",
        "AugustComte", "TalcottParsons", "PierreBourdieu",
        "ErwingGoffman", "MichelFoucault",
        # Mythology
        "GreekMythology", "NorseMythology", "EgyptianMythology",
        "HinduMythology", "RomanMythology", "CelticMythology",
        "JapaneseMythology", "ChineseMythology",
    ],

    # ─────────────────────────────────────────────────────────────────
    "Astronomy": [
        # Solar System
        "SolarSystem", "Sun", "Mercury", "Venus", "Earth",
        "Mars", "Jupiter", "Saturn", "Uranus", "Neptune",
        "Pluto", "Moon", "Asteroid", "Comet", "Meteor",
        "AsteroidBelt", "KuiperBelt", "OortCloud",
        # Stellar Objects
        "Star", "RedDwarf", "WhiteDwarf", "RedGiant",
        "Supernova", "NeutronStar", "Pulsar", "Magnetar",
        "Protostar", "MainSequence", "StellarNursery",
        "BinaryStarSystem", "Cepheid",
        # Galaxies
        "Galaxy", "MilkyWay", "Andromeda", "SpiralGalaxy",
        "EllipticalGalaxy", "IrregularGalaxy", "ActiveGalacticNucleus",
        "Quasar", "Blazar", "GalaxyCluster",
        # Cosmology
        "BigBang", "CosmicMicrowaveBackground", "DarkMatter",
        "DarkEnergy", "CosmicInflation", "Nucleosynthesis",
        "ExpansionOfUniverse", "Multiverse", "Redshift",
        "HubbleLaw", "CosmologicalConstant",
        # Black Holes
        "BlackHole", "EventHorizon", "Singularity",
        "HawkingRadiation", "AccretionDisk",
        "SupermassiveBlackHole", "StellarBlackHole",
        # Space Exploration
        "NASA", "ESA", "SpaceX", "HubbleTelescope",
        "JamesWebbTelescope", "InternationalSpaceStation",
        "ApolloProgram", "VoyagerProbe", "MarsRover",
        "Exoplanet", "GoldilocksZone", "Astrobiology",
        # Famous Astronomers
        "GalileoGalilei", "JohannesKepler", "NicolausCopernicus",
        "EdwinHubble", "CarlSagan", "StephenHawking",
        "SubrahmanyanChandrasekhar", "VeraRubin",
    ],

    # ─────────────────────────────────────────────────────────────────
    "Sports": [
        # Team Sports
        "Football", "Soccer", "Basketball", "Baseball",
        "Cricket", "Rugby", "Hockey", "Volleyball",
        "AmericanFootball", "Lacrosse", "WaterPolo", "Handball",
        # Individual Sports
        "Tennis", "Badminton", "TableTennis", "Golf",
        "Swimming", "Diving", "Athletics", "Marathon",
        "Sprint", "Cycling", "Triathlon",
        # Combat Sports
        "Boxing", "Wrestling", "Judo", "Karate",
        "Taekwondo", "MMA", "Fencing", "Sumo",
        # Winter Sports
        "Skiing", "Snowboarding", "IceHockey", "FigureSkating",
        "SpeedSkating", "Biathlon", "Curling", "Bobsled",
        # Other
        "Gymnastics", "Weightlifting", "Archery", "Shooting",
        "Equestrian", "Rowing", "Sailing", "Surfing",
        "Skateboarding", "RockClimbing",
        # Competitions
        "OlympicGames", "FIFAWorldCup", "SuperBowl",
        "Wimbledon", "TourdeFrance", "FormulaOne",
        "NBAFinals", "CricketWorldCup", "RugbyWorldCup",
        "CommonwealthGames", "AsianGames",
        # Mind Sports
        "Chess", "Go", "Bridge", "Esports",
        # Famous Athletes
        "MuhammadAli", "MichaelJordan", "LionelMessi",
        "CristianoRonaldo", "UsainBolt", "SachinTendulkar",
        "SerenaWilliams", "RogerFederer", "MichaelPhelps",
        "TigerWoods", "WaynGretzky", "PeleFootball",
    ],

    # ─────────────────────────────────────────────────────────────────
    "Business": [
        # Management
        "Management", "Leadership", "Strategy", "Innovation",
        "OrganizationalBehavior", "HumanResources",
        "SupplyChainManagement", "ProjectManagement",
        "ChangeManagement", "RiskManagement",
        "DecisionMaking", "CorporateGovernance",
        # Marketing
        "Marketing", "Branding", "Advertising", "MarketResearch",
        "DigitalMarketing", "ContentMarketing",
        "SocialMediaMarketing", "SEO", "CustomerSegmentation",
        "ProductDevelopment", "PricingStrategy",
        # Finance
        "CorporateFinance", "VentureCapital", "PrivateEquity",
        "InitialPublicOffering", "MergersAndAcquisitions",
        "BalanceSheet", "IncomeStatement", "CashFlow",
        "ReturnOnInvestment", "EBITDA",
        # Entrepreneurship
        "Entrepreneurship", "Startup", "BusinessModel",
        "LeanStartup", "MinimumViableProduct", "Pivoting",
        "AngelInvestor", "Crowdfunding", "Bootstrapping",
        "Unicorn", "SiliconValley", "Incubator",
        # Accounting
        "Accounting", "Auditing", "Taxation", "Bookkeeping",
        "DoubleEntry", "DepreciationAccounting",
        # Industries
        "TechIndustry", "HealthcareIndustry", "FinancialServices",
        "Manufacturing", "Retail", "Ecommerce",
        "RealEstate", "Consulting", "Logistics",
        # Famous Companies/Leaders
        "Apple", "Google", "Amazon", "Microsoft", "Tesla",
        "SteveJobs", "BillGates", "JeffBezos", "WarrenBuffett",
        "ElonMusk", "JackMa", "MarkZuckerberg",
    ],

    # ─────────────────────────────────────────────────────────────────
    "EnvironmentalScience": [
        # Climate
        "ClimateChange", "GlobalWarming", "GreenhouseEffect",
        "CarbonDioxide", "Methane", "OzoneLayer",
        "OzoneDepletion", "CarbonFootprint", "CarbonNeutral",
        "ParisAgreement", "KyotoProtocol",
        # Ecosystems
        "TropicalRainforest", "CoralReef", "Wetland",
        "Mangrove", "Tundra", "Savanna", "Taiga",
        "Grassland", "Estuary", "Kelp",
        # Biodiversity
        "EndangeredSpecies", "Extinction", "Conservation",
        "NationalPark", "WildlifeReserve", "IUCNRedList",
        "InvasiveSpecies", "HabitatLoss", "Deforestation",
        "Desertification", "LandDegradation",
        # Pollution
        "AirPollution", "WaterPollution", "SoilPollution",
        "PlasticPollution", "OceanAcidification",
        "AcidRain", "Smog", "Eutrophication",
        "Bioaccumulation", "Biomagnification",
        # Energy
        "RenewableEnergy", "SolarEnergy", "WindEnergy",
        "HydroelectricPower", "GeothermalEnergy", "NuclearEnergy",
        "FossilFuel", "Coal", "NaturalGas", "Petroleum",
        "Biofuel", "HydrogenFuel", "EnergyStorage",
        # Sustainability
        "Sustainability", "CircularEconomy", "GreenBuilding",
        "OrganicFarming", "Permaculture", "WasteManagement",
        "Recycling", "Composting", "CarbonCapture",
        "SustainableDevelopmentGoals",
        # Water
        "WaterScarcity", "Desalination", "Aquifer",
        "Watershed", "WaterTreatment",
        # Famous Environmentalists
        "RachelCarson", "JaneFondaEnvironment", "GretaThunberg",
        "WangariMaathai", "DavidAttenborough", "AlGore",
    ],
}

# ══════════════════════════════════════════════════════════════════════
#  AGGREGATE: DEFAULT_SEEDS and TOPIC_DOMAINS
# ══════════════════════════════════════════════════════════════════════

DEFAULT_SEEDS = []
TOPIC_DOMAINS = {}

for _domain, _seeds in SEEDS_BY_DOMAIN.items():
    for _seed in _seeds:
        if _seed not in TOPIC_DOMAINS:  # Avoid duplicates across domains
            DEFAULT_SEEDS.append(_seed)
            TOPIC_DOMAINS[_seed] = _domain
