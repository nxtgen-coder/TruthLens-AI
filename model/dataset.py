"""
Dataset generator for TruthLens AI.
Generates a diverse, realistic labelled dataset of Real (1) and Fake (0) news
articles across multiple domains including politics, health, technology, science,
economics, world affairs, conspiracies, and sensational clickbait.
"""

import csv
import os
import random

# Base seed for deterministic generation
random.seed(42)

REAL_ARTICLES = [
    # Politics & Governance
    (
        "Senate Passes Bipartisan Infrastructure Investment and Modernization Bill",
        "The United States Senate voted 69 to 30 on Tuesday to approve a comprehensive 1.2 trillion dollar infrastructure package. "
        "The legislation provides federal funding for highway repairs, public transit systems, clean drinking water access, "
        "and broadband network expansion across underserved rural communities. According to Senate Majority Leader Chuck Schumer, "
        "the bill represents one of the largest federal investments in public works in decades. The measure now moves to the House "
        "of Representatives for further consideration before heading to the President's desk for signature into law."
    ),
    (
        "Federal Reserve Holds Interest Rates Steady Amid Cooling Inflation Indicators",
        "Federal Reserve officials concluded their two-day policy meeting on Wednesday, voting unanimously to maintain the benchmark "
        "federal funds rate in the current target range. Fed Chair Jerome Powell stated during a press briefing that while headline "
        "inflation has moderated significantly over recent quarters, policymakers remain attentive to ongoing labor market trends and "
        "consumer expenditure indicators before committing to policy easing. Economists at Goldman Sachs and JPMorgan noted that "
        "the decision aligns with market consensus and reflects a cautious, data-driven approach to economic stability."
    ),
    (
        "European Union Approves Landmark AI Act Establishing Risk-Based Regulations",
        "The European Parliament ratified the European Union's Artificial Intelligence Act in Strasbourg with an overwhelming majority. "
        "The regulatory framework imposes stringent compliance obligations on high-risk AI deployments, including biometric identification "
        "and critical infrastructure systems, while banning unconstrained social scoring applications. European Commissioner Thierry Breton "
        "commented that Europe has established the first comprehensive legal standards for responsible artificial intelligence governance, "
        "balancing consumer protection with technological innovation."
    ),
    (
        "Supreme Court Hears Oral Arguments in Major Clean Water Act Regulatory Case",
        "The Supreme Court heard oral arguments on Monday concerning the jurisdictional scope of the Environmental Protection Agency "
        "under the Clean Water Act. The plaintiffs argue that federal oversight should strictly apply only to continuous surface waters, "
        "while government attorneys contend that adjacent wetlands directly affect hydrological systems and ecological integrity. "
        "A written opinion from the justices is expected by late June following confidential deliberations."
    ),
    (
        "Ministry of Foreign Affairs Releases Statement on Bilateral Trade Summit",
        "Officials from the Ministry of Foreign Affairs confirmed that bilateral trade discussions concluded fruitfully in Tokyo. "
        "Delegations agreed on tariff reductions for clean energy components and established reciprocal customs processing standards. "
        "Trade volume between the two nations is projected to increase by 8.4 percent over the next fiscal cycle, according to government data."
    ),
    (
        "Global Climate Summit Concludes With Agreement on Renewable Capacity Targets",
        "Delegates from over 190 nations reached a consensus agreement at the United Nations Climate Conference to triple global renewable "
        "energy capacity by 2030. The final declaration calls for accelerated phasing down of unabated coal power and increased international "
        "financing for developing countries vulnerable to extreme weather events. Scientists from the Intergovernmental Panel on Climate "
        "Change welcomed the ambitious targets while emphasizing that national implementation policies must promptly follow."
    ),
    (
        "Department of Transportation Issues New Flight Delay Compensation Rules",
        "The Department of Transportation published a final rule mandating that airlines provide automatic cash refunds to passengers "
        "whose flights are significantly delayed or cancelled. Transportation Secretary Pete Buttigieg stated that passengers deserve "
        "fair treatment and prompt reimbursement without navigating burdensome claim submission portals. Airline trade associations "
        "stated they will review operational procedures to ensure full regulatory compliance."
    ),
    (
        "Electoral Commission Publishes Audited Voter Turnout Statistics",
        "Following an independent verification review, the national Electoral Commission released certified voter turnout figures for "
        "the recent general election. Overall participation stood at 67.2 percent of registered electors, reflecting an increase of 2.1 "
        "percentage points compared to the previous election cycle. Independent election observer groups validated the tallying protocols "
        "and reported that voting procedures across regional polling stations complied with constitutional mandates."
    ),

    # Science & Space Exploration
    (
        "James Webb Space Telescope Discovers Oldest Known Galaxy in Deep Field Survey",
        "Astronomers analyzing observations from the James Webb Space Telescope have identified a distant galaxy that existed merely "
        "350 million years after the Big Bang. The discovery, published in the peer-reviewed journal Nature Astronomy, provides unprecedented "
        "insights into early stellar formation and cosmic reionization. Dr. Brant Robertson of the University of California, Santa Cruz, "
        "co-author of the study, explained that the spectral redshift data reveals a surprisingly luminous galaxy enriched with early stars."
    ),
    (
        "NASA Artemis Mission Successfully Completes Critical Lunar Orbit Trajectory Burn",
        "NASA mission controllers at the Johnson Space Center executed an orbital insertion burn on Thursday, placing the uncrewed Orion "
        "spacecraft into distant retrograde orbit around the Moon. Telemetry data confirmed all propulsion subsystems operated within "
        "nominal parameters. The Artemis program objective is to establish sustainable exploration architecture on the lunar surface "
        "in collaboration with international commercial partners."
    ),
    (
        "Physicists at CERN Observe Rare Higgs Boson Decay Mode in Proton Collisions",
        "Researchers at the European Organization for Nuclear Research announced the first experimental observation of the Higgs boson "
        "decaying into a photon and a Z boson at the Large Hadron Collider. The statistical significance of the detection surpassed five "
        "standard deviations, confirming theoretical predictions of the Standard Model of particle physics. The results were presented "
        "during the International Conference on High Energy Physics."
    ),
    (
        "NOAA Upgrades Ocean Monitoring Satellite Constellation for Hurricane Forecasting",
        "The National Oceanic and Atmospheric Administration launched an advanced microwave radiometer satellite to augment its ocean "
        "surface tracking network. The instrument provides real-time measurements of sea surface temperatures, atmospheric moisture, "
        "and wind vector patterns. Meteorologists at the National Hurricane Center indicated the enhanced data stream will improve "
        "hurricane intensity forecasting precision by up to 15 percent."
    ),
    (
        "Geological Survey Detects Deep Magma Reservoir Beneath Cascade Volcanic Arc",
        "Geophysicists utilizing high-resolution seismic tomography have mapped a magma accumulation zone twelve kilometers beneath Mount "
        "Rainier. The United States Geological Survey clarified that the finding reflects normal geological processes and that monitoring "
        "sensors show no anomalous seismic activity or signs of imminent volcanic eruption. The findings were documented in Geophysical Research Letters."
    ),

    # Health & Medicine
    (
        "Clinical Trial Demonstrates 40 Percent Reduction in Early-Stage Alzheimer's Cognitive Decline",
        "Results from a phase three randomized clinical trial published in the New England Journal of Medicine showed that a novel monoclonal "
        "antibody treatment slowed cognitive decline by 38.6 percent compared to placebo in patients diagnosed with mild Alzheimer's disease. "
        "The trial enrolled 1,800 participants across fifty academic medical centers over eighteen months. Principal investigator Dr. Christopher "
        "Rowe noted that while the therapeutic offers meaningful clinical benefit, potential side effects such as localized brain swelling require "
        "careful magnetic resonance imaging monitoring."
    ),
    (
        "World Health Organization Authorizes Second Malaria Vaccine for High-Risk Regions",
        "The World Health Organization has recommended the R21/Matrix-M malaria vaccine for prevention of malaria in children living in endemic areas. "
        "Clinical trials conducted across Burkina Faso, Kenya, Mali, and Tanzania demonstrated 75 percent efficacy over a 12-month period when "
        "administered prior to the peak transmission season. Public health officials anticipate the cost-effective vaccine will significantly "
        "reduce infant mortality across sub-Saharan Africa."
    ),
    (
        "FDA Approves First CRISPR-Based Gene Therapy for Sickle Cell Disease",
        "The Food and Drug Administration granted regulatory approval for Casgevy, the world's first medical therapy utilizing CRISPR-Cas9 "
        "gene editing technology. The therapeutic edits patient hematopoietic stem cells to boost fetal hemoglobin production, effectively "
        "eliminating debilitating vaso-occlusive crises in clinical trial cohorts. Medical ethicists and hematologists hailed the milestone "
        "as a transformative therapeutic advance."
    ),
    (
        "Study in Lancet Links Regular Aerobic Exercise to Improved Cardiovascular Longevity",
        "An epidemiological cohort study tracking 120,000 adults over twenty-five years revealed that individuals engaging in at least 150 "
        "minutes of moderate aerobic activity weekly experienced a 24 percent lower hazard ratio for all-cause cardiovascular mortality. "
        "Researchers controlled for dietary patterns, socioeconomic factors, and baseline comorbidities. The findings reinforce current "
        "preventative cardiology guidelines."
    ),
    (
        "CDC Reports Seasonal Influenza Transmission Levels Consistent With Decadal Medians",
        "The Centers for Disease Control and Prevention published its weekly surveillance report indicating influenza-like illness rates "
        "are tracking in alignment with five-year historical averages. Hospitalization rates among vulnerable demographics remain stable, "
        "and circulating viral strains show high antigenic match to the current season's quadrivalent vaccine formulation, according to public health laboratorians."
    ),

    # Technology & Cybersecurity
    (
        "Cybersecurity Agency Issues Advisory on Critical Zero-Day Vulnerability in Web Framework",
        "The Cybersecurity and Infrastructure Security Agency released an emergency directive warning enterprise system administrators "
        "of a remote code execution vulnerability discovered in widespread open-source logging libraries. Security researchers identified "
        "proof-of-concept exploits active on public networks and urged immediate application of vendor security patches to mitigate intrusion risks."
    ),
    (
        "Semiconductor Foundry Begins Mass Production of High-Efficiency 2-Nanometer Microchips",
        "Taiwan Semiconductor Manufacturing Company announced commercial volume production of its next-generation 2-nanometer process node. "
        "The architecture integrates nanosheet gate-all-around field-effect transistors, providing up to a 15 percent speed enhancement and a "
        "30 percent reduction in power consumption compared to existing 3-nanometer fabrication. Initial shipments will supply consumer electronics "
        "and data center accelerators."
    ),
    (
        "Consortium of Tech Firms Publishes Open Standard for Digital Content Provenance",
        "A coalition of media organizations and software developers finalized the Coalition for Content Provenance and Authenticity 2.0 specification. "
        "The open standard embeds cryptographically signed metadata into digital photographs and video recordings, enabling viewers to inspect "
        "the creation timestamp, editing history, and capture device. Adobe, Microsoft, and Nikon announced immediate product compatibility."
    ),
    (
        "Autonomous Electric Ferry Begins Regular Commercial Passenger Operations in Oslo",
        "Maritime transit authorities in Oslo inaugurated scheduled passenger service for the first fully electric, autonomous commuter ferry. "
        "The vessel employs lidar sensors, thermal cameras, and redundant navigation controllers supervised remotely by a certified maritime "
        "operations center. Municipal leaders stated the vessel produces zero direct emissions and halves crossing times."
    ),

    # Economics & Business
    (
        "Global Container Shipping Rates Moderate as Supply Chain Capacity Normalizes",
        "Ocean freight spot rates on major transpacific and Asia-Europe shipping lanes fell by 12 percent month-over-month, returning toward "
        "pre-pandemic baselines. Maritime analytics firm Drewry reported that newly delivered container vessels have expanded global fleet "
        "capacity, easing congestive bottlenecks at major ports including Long Beach and Rotterdam."
    ),
    (
        "Department of Labor Reports Addition of 215,000 Nonfarm Payroll Jobs in April",
        "The Bureau of Labor Statistics reported that total nonfarm payroll employment rose by 215,000 in April, while the national unemployment "
        "rate held steady at 3.9 percent. Job gains were concentrated in healthcare, professional business services, and public administration, "
        "while manufacturing employment remained essentially unchanged. Average hourly earnings increased by 0.2 percent over the month."
    ),
    (
        "Renewable Energy Investment Surpasses Fossil Fuel Expenditure for Second Year",
        "The International Energy Agency published its annual World Energy Investment report, finding that global capital expenditure on clean "
        "energy technologies reached 1.7 trillion dollars in the preceding year. Solar photovoltaic installations and electric vehicle manufacturing "
        "accounted for the largest share of new infrastructure capital."
    )
]

FAKE_ARTICLES = [
    # Sensational Conspiracies & Fabricated Scenarios
    (
        "BOMBSHELL: Declassified Files PROVE Aliens Are Running The Secret World Government From Underneath Denver Airport!!!",
        "WAKE UP SHEEPLE! A anonymous insider from deep within the military industrial complex has finally leaked the terrifying truth that the "
        "mainstream media is desperate to hide from you! Underground tunnels spanning thousands of miles beneath Denver International Airport "
        "house extraterrestrial reptilian overlords who dictate all global economic policies and presidential elections! They are poisoning the "
        "water supply with mind-control chemicals and synthetic nanotechnology! Share this viral article before the secret police shut down our website forever!!!"
    ),
    (
        "SHOCKING DISCOVERY: 5G Cell Towers Are Actively Transmitting Frequencies That Overwrite Human DNA!",
        "Doctors are stunned and terrified! Renowned whistleblowers have confirmed that 5G millimeter towers are actually covert energy weapons "
        "designed to alter your cellular DNA and cause sudden obedience! The global elite engineered this frequency grid to control our thoughts! "
        "Big Tech is censoring everyone who speaks out! Wear aluminum foil in your hats and drink raw miracle mineral oil to cleanse your biofield immediately!"
    ),
    (
        "SECRET CURE: Eating Lemon Peels Mixed With Baking Soda Cures 100% Of All Cancers In 24 Hours, Big Pharma Panicking!",
        "A brave rogue doctor who was fired from Harvard has just revealed the one simple kitchen trick that cures every stage four cancer "
        "overnight! Pharmaceutical billionaires are furious and trying to erase this page! You will NEVER hear about this on CNN or from your "
        "corrupt doctor because they make trillions keeping you sick! Just blend raw lemons with baking soda and turmeric at midnight! Do not let them silence the truth!"
    ),
    (
        "EXPOSED: Celebrity A-Listers Are Actually Synthetically Cloned Automatons Powered By Artificial Blood!",
        "Hollywood insiders finally broke their silence! Top movie stars and pop musicians died decades ago and have been replaced by exact "
        "robotic clones manufactured in underground bio-labs in Nevada! Look closely at their ears and blinking patterns—it is undeniable proof! "
        "The Illuminati uses these clone puppets to brainwash our youth through backward subliminal audio messages in popular music tracks!"
    ),
    (
        "ALERT: Government Confirms Mandatory Microchipping Law Starting Next Month For All Citizens!",
        "IT IS HAPPENING! Lawmakers just secretly passed an unconstitutional decree in an emergency closed-door midnight vote! Starting next month, "
        "every citizen will be forced by federal marshals to receive an RFID tracking microchip inserted under the skin of their right hand! "
        "If you refuse, your bank accounts will be frozen and you will be barred from grocery stores! Spread this warning to everyone you know!"
    ),
    (
        "MIRACLE DISCOVERY: Ancient Herb Melts 50 Pounds Of Pure Belly Fat In 3 Days Without Diet Or Exercise!",
        "Dietitians HATE this one bizarre ancient Himalayan root! A 54-year-old grandmother accidentally discovered an exotic tea that dissolves "
        "visceral fat while you sleep! No calorie counting, no gym workouts, just guaranteed instant weight loss! The multi-billion dollar diet industry "
        "is suing to ban this miracle plant! Claim your trial bottle now before supplies run out!"
    ),
    (
        "UNBELIEVABLE: NASA Astronaut Claims Earth Is Actually Hollow And Houses Ancient Giants Inside!",
        "In a leaked private radio transmission, a former shuttle astronaut admitted that satellite photos of Earth are completely fabricated "
        "CGI illusions! The Earth is hollow with an internal sun, inhabited by 15-foot ancient giants who built the pyramids with anti-gravity rays! "
        "NASA and world leaders have signed an intergalactic pact to conceal the northern opening at the Arctic pole! The evidence cannot be denied!"
    ),
    (
        "BREAKING: Scientists Invent Device That Lets You Talk Directly To Ghosts Using Bluetooth 5.0!",
        "Paranormal researchers have shocked the scientific establishment by developing a smartphone dongle that connects directly to the spirit "
        "realm via Bluetooth! Deceased historical figures are answering phone calls and warning humanity of impending apocalypse! Mainstream scientists "
        "are baffled and refuse to acknowledge the undeniable supernatural frequency recordings!"
    ),
    (
        "LEAKED FOOTAGE: Time Traveler From Year 3045 Arrives With Video Proof Of Flying Cities And Robot Overlords!",
        "A mysterious man claiming to be an chrononaut from the 31st century has passed a lie detector test with 100% accuracy! He displayed "
        "futuristic holographic video footage showing floating magnetic cities, weather-controlling pyramids, and human enslavement by cybernetic cyborgs! "
        "Intelligence agencies are hunting him down to confiscate his temporal device! Watch the footage before it gets deleted!"
    ),
    (
        "SCANDAL: World Leaders Caught Performing Secret Midnight Rituals Inside Giant Hollowed-Out Redwood Tree!",
        "Hidden camera footage has emerged showing presidents, billionaires, and royalty wearing dark robes and worshipping an ancient pagan idol "
        "in the northern California woods! Whistleblowers allege that critical global wars and stock market crashes are decided during these bizarre "
        "occult ceremonies! The mainstream media refuses to broadcast the horrifying truth! Share this everywhere!"
    ),
    (
        "PROOF: Chemtrail Airplanes Are Spraying Barium Salts To Turn Citizens Into Obedient Servants!",
        "Look up in the sky, people! Those are not condensation trails from commercial airliners—they are toxic chemical aerosol sprays! Former military "
        "pilots have blown the whistle on Operation SkyShroud, a top-secret globalist project to spray heavy metals, barium, and strontium over "
        "metropolitan centers to suppress critical thinking and cause chronic lethargy! Wake up before it is too late!"
    ),
    (
        "SHOCK REPORT: Deep State Creating Artificial Earthquakes Using Weather Weapon In Antarctica!",
        "Geologists who dared to speak out have disappeared! Seismic stations detected unnatural frequency spikes proving that recent massive "
        "earthquakes were deliberately triggered by subterranean ionospheric heaters situated at clandestine Antarctic bases! Globalist elites "
        "are manipulating tectonic plates to destabilize developing economies and enforce martial law!"
    ),
    (
        "AMAZING TRICK: Rubbing Toothpaste On Your Vehicle Battery Gives Unlimited Free Electricity Forever!",
        "Power companies are panicking over this suppressed electrical hack! By coating lead battery terminals with regular mint toothpaste and "
        "copper wire coils, you unlock infinite zero-point quantum energy! You will never pay an electric bill again in your life! Share this secret "
        "hack before utility monopolies lobby politicians to make toothpaste illegal!"
    ),
    (
        "SMOKING GUN: Secret Society Orders Worldwide Internet Blackout To Erase All Banking Records!",
        "Insider sources within central banks warn of a catastrophic impending digital wipeout! The international financial cartel has scheduled a "
        "three-day global blackout next week to erase all customer deposit logs and replace fiat currency with mandatory centralized tracking tokens! "
        "Withdraw all your cash right now and hoard emergency rations before society collapses into total chaos!"
    )
]

# Variations and thematic builders to generate a robust dataset of 600+ articles
DOMAINS = ["politics", "economy", "science", "health", "technology", "environment"]

REAL_TEMPLATES = [
    (
        "Officials in {location} Announce New {initiative} Aimed at {goal}",
        "Government representatives in {location} announced on {day} the implementation of a comprehensive {initiative} designed to {goal}. "
        "According to official statements released by the agency, the program will receive {funding} in public funding over the next five years. "
        "Independent policy analysts from {institution} commended the initiative, noting that preliminary studies project a {stat}% improvement "
        "in operational efficiency and citizen accessibility. Implementation is scheduled to commence within the upcoming quarter following standard regulatory review."
    ),
    (
        "Researchers at {institution} Publish Findings on {topic} in Peer-Reviewed Journal",
        "A multidisciplinary team of scientists at {institution} has published new research in the journal of {journal}, providing valuable "
        "data regarding {topic}. The peer-reviewed study, conducted over a period of {duration}, analyzed data from more than {sample_size} participants. "
        "Lead author Dr. {scientist} emphasized that while the findings represent a meaningful milestone in understanding {topic}, further replicated trials "
        "are necessary before clinical guidelines can be revised. The research received funding from the National Science Foundation."
    ),
    (
        "Central Bank Reports {economic_trend} as {indicator} Shows Steady Progress",
        "Economic indicators released by the central monetary authority on {day} showed that {economic_trend} has continued for the third consecutive quarter. "
        "The consumer price metric registered a modest adjustment of {pct} percent, aligning closely with forecasts from leading financial institutions. "
        "Chief economist {economist} stated during a press briefing that monetary policy settings will remain calibrated to ensure sustainable growth and "
        "employment stability. Financial market indices responded with moderate gains following the announcement."
    ),
    (
        "International Summit Concludes With Multilateral Agreement on {global_issue}",
        "Delegates representing forty member states finalized a multilateral agreement addressing {global_issue} during diplomatic talks held in {city}. "
        "The treaty establishes standardized reporting protocols, shared monitoring standards, and coordinated resource allocation mechanisms. "
        "United Nations High Commissioner {diplomat} commended the collaborative spirit of the negotiations, stating that collective international action "
        "is paramount to addressing transnational challenges effectively."
    ),
    (
        "Regulatory Authority Approves Safety Standards for Commercial {tech_topic}",
        "The national safety oversight commission issued comprehensive regulatory guidance regarding commercial operations in {tech_topic}. "
        "The finalized safety code requires rigorous third-party auditing, fail-safe redundant architectures, and regular data compliance filings. "
        "Industry stakeholders and consumer advocacy organizations participated in public commentary hearings prior to final codification. "
        "The rules take effect at the start of the next fiscal year."
    ),
    (
        "Public Health Institute Reports Significant Progress in Combating {disease}",
        "Surveillance metrics released by the national Institute of Public Health indicate that transmission rates for {disease} have declined by "
        "{pct} percent year-over-year. Health officials attribute the sustained downturn to widespread vaccination programs, enhanced diagnostic "
        "screening, and community outreach campaigns. Medical Director Dr. {doctor} urged the public to maintain routine preventive checkups as seasonal trends continue."
    )
]

FAKE_TEMPLATES = [
    (
        "CONFIDENTIAL LEAK: {conspiracy} EXPOSED by Brave Whistleblower Before Being Arrested!!!",
        "DO NOT SCROLL PAST THIS! An anonymous senior operative has just risked their life to smuggle out secret top-secret documents revealing that {conspiracy}! "
        "The mainstream corrupt media has been instructed by global billionaires to never speak of this forbidden truth! Every major social media company "
        "is actively shadowbanning our account to keep you completely blind! If you value your freedom and family, share this urgent bombshell report "
        "to every Facebook group and chat immediately before they take down the internet!!!"
    ),
    (
        "DOCTORS TERRIFIED: Bizarre Kitchen Item Cures {disease_fake} In Minutes But Big Pharma Hides It!",
        "You will NEVER believe what ordinary household ingredient cures {disease_fake} completely within twenty-four hours! High-ranking pharmaceutical "
        "executives are furious and spending millions of dollars in bribes to keep this miracle discovery buried! Your greedy doctor will never tell you this "
        "because they make billions prescribing expensive toxic pills! Simply take two spoonfuls of {fake_remedy} mixed with warm rainwater before bed! "
        "Act fast before corrupt government agents confiscate the supplies!"
    ),
    (
        "PROOF: {villain_group} Caught Planning Mass Depopulation Using {tech_fake} Weapons!",
        "WAKE UP PEOPLE! The sinister {villain_group} has finalized their evil plan to enslave the planet using covert {tech_fake} arrays! "
        "Eyewitnesses have spotted unmarked black helicopters transporting strange glowing containers across rural states! Scientific shills claim it is "
        "normal weather, but anyone with a working brain knows it is a weapon of mass deception! Stock up on canned beans, silver coins, and emergency water "
        "before the planned global blackout strikes next week!!!"
    ),
    (
        "BOMBSHELL EVIDENCE: {famous_entity} Was Never Real—Actor Replaced By High-Tech Hologram!",
        "The illusion is crumbling right before our eyes! Computer graphics experts have analyzed slow-motion video footage and discovered indisputable proof "
        "that {famous_entity} is completely simulated! Look at the pixel artifacts around the collarbone and notice how the eyes never reflect sunlight! "
        "The puppet masters are laughing at how gullible the public has become! Spread the viral truth and awaken the sleeping masses today!"
    ),
    (
        "UNBELIEVABLE: Secret Time Portal Discovered Under {monument} Allows Travel to {ancient_time}!",
        "Government excavators secretly breached an ancient underground chamber beneath {monument} and stumbled into an active dimensional rift! "
        "Special forces operatives who entered the vortex reported communicating directly with entities from {ancient_time}! Scientists who refused to sign "
        "non-disclosure agreements are currently missing! The Pentagon is desperately trying to suppress the satellite telemetry! Share before it is scrubbed!"
    ),
    (
        "MIRACLE ENERGY: Turn Your Ordinary Household Salt Into Infinite Free Electricity with This One Weird Trick!",
        "Energy cartels are terrified of this revolutionary discovery! By simply dissolving ordinary table salt into a magnetic glass bowl with copper pennies, "
        "you can power your entire home and air conditioning forever without paying a single dime! Utility executives have filed emergency injunctions to "
        "ban salt purchases nationwide! Try this viral hack tonight before the electric companies cut off your neighborhood grid!"
    )
]

# Vocabulary banks for synthetic combinations
CITIES = ["Berlin", "Tokyo", "London", "Washington", "Canberra", "Ottawa", "Singapore", "Geneva", "Stockholm", "Seoul"]
INSTITUTIONS = ["Oxford University", "Stanford Institute of Science", "Max Planck Society", "MIT Research Laboratories", "Johns Hopkins Medical Center", "National Academy of Sciences"]
JOURNALS = ["Nature Medicine", "The Lancet", "Science Advances", "Physical Review Letters", "Journal of the American Medical Association"]
TOPICS = ["carbon capture technology", "battery energy density", "renewable grid reliability", "deep space cosmological radiation", "pediatric immunization safety"]
INITIATIVES = ["Clean Water Modernization Project", "High-Speed Rail Expansion", "Rural Telehealth Initiative", "Urban Air Quality Standards", "National Cyber Resilience Strategy"]
GOALS = ["reduce regional carbon emissions", "expand digital healthcare access", "strengthen supply chain resilience", "enhance water conservation", "modernize regional energy grids"]

CONSPIRACIES = [
    "global satellites are projecting false stars onto an artificial dome ceiling",
    "secret lunar bases are harvesting electromagnetic life-force from sleeping humans",
    "the world's leaders are synthetic biomechanical androids manufactured in underground vaults",
    "all modern wireless routers are emitting frequencies to paralyze your spiritual third eye",
    "ancient subterranean lizards control the price of gold and stock market indexes"
]
FAKE_REMEDIES = ["raw onion paste with cayenne pepper", "activated charcoal fermented in vinegar", "crushed pine needles and baking soda", "magnetic energized mineral water"]
VILLAIN_GROUPS = ["The Secret Davos Cabal", "Globalist High Council", "The Shadow Syndicate", "The Trilateral World Oligarchy"]
TECH_FAKES = ["Atmospheric Geo-Strobe", "Quantum Mind-Disruption", "Sub-Harmonic Drone", "Sub-Atomic Weather-Shift"]
MONUMENTS = ["The Great Sphinx of Giza", "The Washington Monument", "The Eiffel Tower", "The Hoover Dam", "Stonehenge"]

def generate_dataset(csv_path: str, count_per_class: int = 300):
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    rows = []

    # 1. Add curated seeds
    for title, text in REAL_ARTICLES:
        rows.append({"title": title.strip(), "text": text.strip(), "label": 1}) # 1 = Real

    for title, text in FAKE_ARTICLES:
        rows.append({"title": title.strip(), "text": text.strip(), "label": 0}) # 0 = Fake

    # 2. Synthesize Real Articles
    while sum(1 for r in rows if r["label"] == 1) < count_per_class:
        tmpl = random.choice(REAL_TEMPLATES)
        city = random.choice(CITIES)
        inst = random.choice(INSTITUTIONS)
        journal = random.choice(JOURNALS)
        topic = random.choice(TOPICS)
        init = random.choice(INITIATIVES)
        goal = random.choice(GOALS)
        day = random.choice(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
        funding = f"${random.randint(15, 850)} million"
        pct = random.randint(12, 45)
        stat = random.randint(15, 60)
        duration = f"{random.randint(2, 7)} years"
        sample_size = f"{random.randint(1200, 35000):,}"
        scientist = random.choice(["Elena Rostova", "Marcus Vance", "Sarah Chen", "Julian Thorne", "Devi Patel"])
        economist = random.choice(["Robert Henderson", "Clara Schmidt", "Kenji Takahashi", "Amara Okafor"])
        diplomat = random.choice(["Hans Van Der Bilt", "Maria Santos", "Arjun Mehta", "Camille Laurent"])
        doctor = random.choice(["Miriam Al-Hassan", "David Albright", "Jennifer Wu", "Alexander Moreau"])
        disease = random.choice(["bacterial meningitis", "seasonal influenza", "type-2 diabetic complications", "congestive heart failure"])
        tech_topic = random.choice(["autonomous delivery vehicles", "commercial orbital transport", "grid-scale lithium-iron storage", "biometric aviation screening"])
        trend = random.choice(["moderate expansion", "stabilization of price indices", "resilient labor productivity", "balanced export capacity"])
        indicator = random.choice(["consumer confidence", "manufacturing output", "core price metrics", "interbank lending"])

        title = tmpl[0].format(
            location=city, initiative=init, goal=goal, institution=inst,
            topic=topic, economic_trend=trend, indicator=indicator,
            global_issue=topic, tech_topic=tech_topic, disease=disease
        )
        text = tmpl[1].format(
            location=city, initiative=init, goal=goal, institution=inst,
            topic=topic, journal=journal, duration=duration, sample_size=sample_size,
            scientist=scientist, economic_trend=trend, indicator=indicator,
            day=day, pct=pct, economist=economist, global_issue=topic,
            city=city, diplomat=diplomat, tech_topic=tech_topic,
            disease=disease, doctor=doctor, funding=funding, stat=stat
        )
        rows.append({"title": title.strip(), "text": text.strip(), "label": 1})

    # 3. Synthesize Fake Articles
    while sum(1 for r in rows if r["label"] == 0) < count_per_class:
        tmpl = random.choice(FAKE_TEMPLATES)
        conspiracy = random.choice(CONSPIRACIES)
        disease_fake = random.choice(["All Deadly Viruses", "Every Known Disease", "All Chronic Ailments", "Sudden Cellular Aging"])
        fake_remedy = random.choice(FAKE_REMEDIES)
        villain = random.choice(VILLAIN_GROUPS)
        tech_fake = random.choice(TECH_FAKES)
        famous = random.choice(["World Leader", "Hollywood Megastar", "Billionaire Tech Titan", "Famous News Anchor"])
        monument = random.choice(MONUMENTS)
        ancient_time = random.choice(["Ancient Atlantis in 9000 BC", "The Pyramids of Ancient Egypt", "The Year 4500 AD"])

        title = tmpl[0].format(
            conspiracy=conspiracy.upper(), disease_fake=disease_fake,
            villain_group=villain.upper(), famous_entity=famous,
            monument=monument, ancient_time=ancient_time, tech_fake=tech_fake
        )
        text = tmpl[1].format(
            conspiracy=conspiracy, disease_fake=disease_fake,
            fake_remedy=fake_remedy, villain_group=villain,
            tech_fake=tech_fake, famous_entity=famous,
            monument=monument, ancient_time=ancient_time
        )
        rows.append({"title": title.strip(), "text": text.strip(), "label": 0})

    # Shuffle the dataset
    random.shuffle(rows)

    with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "text", "label"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Dataset generated successfully at {csv_path}: {len(rows)} samples ({sum(1 for r in rows if r['label'] == 1)} Real, {sum(1 for r in rows if r['label'] == 0)} Fake).")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    target_path = os.path.join(os.path.dirname(current_dir), "data", "news_dataset.csv")
    generate_dataset(target_path, count_per_class=350)
