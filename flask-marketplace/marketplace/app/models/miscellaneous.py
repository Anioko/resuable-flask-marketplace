from app.utils import db


class EditableHTML(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    editor_name = db.Column(db.String(100), unique=True)
    value = db.Column(db.Text)

    @staticmethod
    def get_editable_html(editor_name):
        editable_html_obj = EditableHTML.query.filter_by(
            editor_name=editor_name).first()

        if editable_html_obj is None:
            editable_html_obj = EditableHTML(editor_name=editor_name, value='')
        return editable_html_obj

    @property
    def serialize(self):
        return {
            'id': self.id,
            'editor_name': self.editor_name,
            'value': self.value
        }
class SeoItems(db.Model):
    __tablename__ = 'seo_items'
    id = db.Column(db.Integer, primary_key=True)
    items = db.Column(db.String(500))


    @staticmethod
    def insert_data():
        items = ('Bird Cage Accessories','Bird Cages & Stands','Bird Food','Bird Gyms & Playstands','Bird Ladders & Perches',
                'Bird Toys','Bird Treats','Cat Apparel','Cat Beds','Cat Food','Cat Furniture','Cat Furniture Accessories',
                'Cat Litter','Cat Litter Box Liners','Cat Litter Box Mats','Cat Litter Boxes','Cat Toys','Cat Treats',
                'Dog Apparel','Dog Beds','Dog Diaper Pads & Liners','Dog Diapers','Dog Food','Dog Houses','Dog Kennel & Run Accessories',
                'Dog Kennels & Runs','Dog Toys','Dog Treadmills','Dog Treats','Aquarium & Pond Tubing','Aquarium Air Stones & Diffusers',
                'Aquarium Cleaning Supplies','Aquarium Decor','Aquarium Filters','Aquarium Fish Nets','Aquarium Gravel & Substrates',
                'Aquarium Lighting','Aquarium Overflow Boxes','Aquarium Stands','Aquarium Temperature Controllers','Aquarium Water Treatments',
                'Aquariums','Aquatic Plant Fertilizers','Fish Feeders','Fish Food','Pet Glucose Meters','Pet Pedometers','Pet Thermometers',
                'Pet Combs & Brushes','Pet Fragrances & Deodorizing Sprays','Pet Hair Clippers & Trimmers','Pet Hair Dryers','Pet Nail Polish',
                'Pet Nail Tools','Pet Shampoo & Conditioner','Pet Wipes','Pet Training Clickers & Treat Dispensers','Pet Training Pad Holders',
                'Pet Training Pads','Pet Training Sprays & Solutions','Reptile & Amphibian Food','Reptile & Amphibian Habitat Accessories',
                'Reptile & Amphibian Habitat Heating & Lighting','Reptile & Amphibian Habitats','Reptile & Amphibian Substrates','Small Animal Bedding',
                'Skirts & Costumes','Hunting Clothing','Martial Arts Shorts','Motorcycle Protective Clothing','Paintball Clothing','Baby & Toddler Bottoms',
                'Baby & Toddler Diaper Covers','Baby & Toddler Dresses','Baby & Toddler Outerwear','Baby & Toddler Outfits','Baby & Toddler Sleepwear',
                'Baby & Toddler Socks & Tights','Baby & Toddler Swimwear','Baby & Toddler Tops','Baby One-Pieces','Toddler Underwear','Jumpsuits & Rompers',
                'Leotards & Unitards','Overalls','Chaps','Coats & Jackets','Rain Pants','Rain Suits','Snow Pants & Suits','Vests','Knee-Length Skirts','Long Skirts',
                'Mini Skirts','Loungewear','Nightgowns','Pajamas','Robes','Pant Suits','Skirt Suits','Tuxedos','Dirndls','Hakama Trousers','Japanese Black Formal Wear',
                'Kimono Outerwear','Kimonos','Religious Ceremonial Clothing','Saris & Lehengas','Traditional Leather Pants','Yukata','Bra Accessories','Bras','Hosiery',
                'Jock Straps','Lingerie','Lingerie Accessories','Long Johns','Petticoats & Pettipants','Shapewear','Socks','Undershirts','Underwear','Underwear Slips',
                'Contractor Pants & Coveralls','Flight Suits','Food Service Uniforms','Military Uniforms','School Uniforms','Security Uniforms','Sports Uniforms','White Coats',
                'Bridal Party Dresses','Wedding Dresses','Baby & Toddler Belts','Baby & Toddler Gloves & Mittens','Baby & Toddler Hats','Baby Protective Wear','Bandanas',
                'Hair Care Wraps','Bridal Veils','Hair Bun & Volume Shapers','Hair Combs','Hair Extensions','Hair Forks & Sticks','Hair Nets','Hair Pins', 'Claws & Clips',
                'Hair Wreaths','Headbands','Ponytail Holders','Tiaras','Wig Accessories','Wigs','Fascinators','Headdresses','Turbans','Scarves','Shawls','Kimono Underclothes',
                'Obi Accessories','Obis','Tabi Socks','Bald Caps','Costume Accessory Sets','Costume Capes','Costume Gloves','Costume Hats','Costume Special Effects','Costume Tobacco Products',
                'Pretend Jewelry','Watch Bands','Watch Stickers & Decals','Watch Winders','Art & Craft Kits','Art & Crafting Materials','Art & Crafting Tool Accessories',
                'Art & Crafting Tools','Craft Organization','Crafting Patterns & Molds','Autographs','Collectible Coins & Currency','Collectible Trading Cards',
                'Collectible Weapons','Postage Stamps','Rocks & Fossils','Scale Model Accessories','Scale Models','Seal Stamps','Sports Collectibles',
                'Vintage Advertisements','Beer Brewing Grains & Malts','Bottling Bottles','Homebrewing & Winemaking Kits','Wine Making','Model Rocketry',
                'Model Train Accessories','Model Trains & Train Sets','Scale Model Kits','Brass Instrument Accessories','Conductor Batons','Electronic Tuners',
                'Metronomes','Music Benches & Stools','Music Lyres & Flip Folders','Music Stand Accessories','Music Stands','Musical Instrument Amplifier Accessories',
                'Musical Instrument Amplifiers','Musical Keyboard Accessories','Percussion Accessories','String Instrument Accessories','Woodwind Instrument Accessories',
                'Accordions & Concertinas','Bagpipes','Brass Instruments','Electronic Musical Instruments','Percussion','Pianos','String Instruments','Woodwinds',
                'Corsage & Boutonnière Pins','Corsages & Boutonnières','Fresh Cut Flowers','Gift Cards & Certificates','Gift Wrapping','Greeting & Note Cards','Advice Cards',
                'Balloon Kits','Balloons','Banners','Birthday Candles','Chair Sashes','Cocktail Decorations','Confetti','Decorative Pom-Poms','Drinking Games','Drinking Straws & Stirrers',
                'Envelope Seals','Event Programs','Fireworks & Firecrackers','Inflatable Party Decorations','Invitations','Noisemakers & Party Blowers','Party Favors','Party Games','Party Hats',
                'Party Streamers & Curtains','Party Supply Kits','Piñatas','Place Card Holders','Place Cards','Response Cards','Sparklers','Special Occasion Card Boxes & Holders','Spray String',
                'Disco Balls','Fog Machines','Special Effects Controllers','Special Effects Light Stands','Special Effects Lighting','Award Certificates','Award Pins & Medals','Award Plaques','Award Ribbons',
                'Trophies','Play Gyms','Play Mats','Baby Cereal','Baby Drinks','Baby Food','Baby Formula','Baby Snacks','Toddler Nutrition Drinks & Shakes','Baby Bottle Liners','Baby Bottle Nipples','Egg Incubators',
                'Livestock Feed','Livestock Feeders & Waterers','Livestock Halters','Dappen Dishes','Dental Mirrors','Dental Tool Sets','Prophy Cups','Prophy Heads','Disposable Serving Trays',
                'Disposable Bowls','Disposable Cups','Disposable Cutlery','Disposable Plates','Hoists', 'Cranes & Trolleys','Jacks & Lift Trucks','Personnel Lifts','Pulleys',
                'Blocks & Sheaves','Winches','Automated External Defibrillators','Gait Belts','Medical Reflex Hammers & Tuning Forks','Medical Stretchers & Gurneys','Otoscopes & Ophthalmoscopes',
                'Patient Lifts','Stethoscopes','Vital Signs Monitor Accessories','Vital Signs Monitors','Chiropractic Tables','Examination Chairs & Tables','Homecare & Hospital Beds','Medical Cabinets',
                'Medical Carts','Surgical Tables','Medical Forceps','Scalpel Blades','Scalpels','Surgical Needles & Sutures','Disposable Gloves','Finger Cots','Medical Needles & Syringes','Ostomy Supplies',
                'Tongue Depressors','Medical & Emergency Response Training Mannequins','Piercing Needles','Tattoo Cover-Ups','Tattooing Inks','Tattooing Machines','Tattooing Needles','Banknote Verifiers',
                'Cash Register & POS Terminal Accessories','Cash Registers & POS Terminals','Coin & Bill Counters','Money Changers','Money Deposit Bags','Paper Coin Wrappers & Bill Straps','Autoclaves','Centrifuges',
                'Dry Ice Makers','Freeze-Drying Machines','Laboratory Blenders','Laboratory Freezers','Laboratory Funnels','Laboratory Hot Plates','Laboratory Ovens','Microscope Accessories','Microscopes','Microtomes',
                'Spectrometer Accessories','Spectrometers','Beakers','Graduated Cylinders','Laboratory Flasks','Petri Dishes','Pipettes','Test Tube Racks','Test Tubes','Wash Bottles','LED Signs','Neon Signs','Dust Masks',
                'Fireman"s Masks','Gas Masks & Respirators','Medical Masks','Camera Lenses','Surveillance Camera Lenses','Video Camera Lenses','Lens & Filter Adapter Rings','Lens Bags','Lens Caps','Lens Converters','Lens Filters',
                'Lens Hoods','Camera Accessory Sets','Camera Bags & Cases','Camera Body Replacement Panels & Doors','Camera Digital Backs','Camera Film','Camera Flash Accessories','Camera Flashes','Camera Focus Devices',
                'Camera Gears','Camera Grips','Camera Image Sensors','Camera Lens Zoom Units','Camera Remote Controls','Camera Replacement Buttons & Knobs','Camera Replacement Screens & Displays','Camera Silencers & Sound Blimps',
                'Camera Stabilizers & Supports','Camera Straps','Camera Sun Hoods & Viewfinder Attachments','Flash Brackets','On-Camera Monitors','Surveillance Camera Accessories','Underwater Camera Housing Accessories',
                'Underwater Camera Housings','Video Camera Lights','Binocular & Monocular Accessories','Optics Bags & Cases','Rangefinder Accessories','Spotting Scope Accessories','Telescope Accessories','Thermal Optic Accessories',
                'Weapon Scope & Sight Accessories','Tripod & Monopod Cases','Tripod & Monopod Heads','Tripod Collars & Mounts','Tripod Handles','Tripod Spreaders','Spotting Scopes','Telescopes','Weapon Scopes & Sights',
                'Developing & Processing Equipment','Enlarging Equipment','Photographic Chemicals','Photographic Paper','Safelights','Light Meter Accessories','Light Meters','Studio Backgrounds','Studio Light & Flash Accessories',
                'Studio Lighting Controls','Studio Lights & Flashes','Studio Stand & Mount Accessories','Studio Stands & Mounts','Audio & Video Receiver Accessories','Headphone & Headset Accessories','Karaoke System Accessories',
                'MP3 Player Accessories','Microphone Accessories','Microphone Stands','Satellite Radio Accessories','Speaker Accessories','Turntable Accessories','Audio & Video Receivers','Audio Amplifiers','Audio Mixers','Audio Transmitters',
                'Channel Strips','Direct Boxes','Headphones & Headsets','Microphones','Signal Processors','Speakers','Studio Recording Bundles','Boomboxes','CD Players & Recorders','Cassette Players & Recorders','Home Theater Systems','Jukeboxes',
                'Karaoke Systems','MP3 Players','MiniDisc Players & Recorders','Multitrack Recorders','Radios','Reel-to-Reel Tape Players & Recorders','Stereo Systems','Turntables & Record Players','Voice Recorders','DJ CD Players','DJ Systems',
                'Wireless Transmitters','Breadboards','Capacitors','Electronic Oscillators','Inductors','Resistors','Camera Circuit Boards','Computer Circuit Boards','Development Boards','Exercise Machine Circuit Boards','Household Appliance Circuit Boards',
                'Pool & Spa Circuit Boards','Printer', 'Copier & Fax Machine Circuit Boards','Scanner Circuit Boards','Television Circuit Boards','Diodes','Integrated Circuits & Chips','Microcontrollers','Transistors','CB Radios','Radio Scanners',
                'Two-Way Radios','Conference Phones','Corded Phones','Cordless Phones','Mobile Phone Accessories','Mobile Phones','Satellite Phones','Telephone Accessories','Audio Converters','Scan Converters','Data Collectors','E-Book Readers',
                'PDAs','Thin Client Computers','Zero Client Computers','Audio & Video Cable Adapters & Couplers','Memory Card Adapters','USB Adapters','Antenna Mounts & Brackets','Antenna Rotators','Satellite LNBs','DVI Splitters & Switches','HDMI Splitters & Switches',
 		'VGA Splitters & Switches','Cable Clips','Cable Tie Guns','Cable Trays','Patch Panels','Wire & Cable Identification Markers','Wire & Cable Sleeves','Wire & Cable Ties','Audio & Video Cables','KVM Cables','Network Cables','Storage & Data Transfer Cables',
		'System & Power Cables','Telephone Cables','Computer Accessory Sets','Computer Covers & Skins','Computer Risers & Stands','Handheld Device Accessories','Keyboard & Mouse Wrist Rests','Keyboard Trays & Platforms','Laptop Docking Stations','Mouse Pads',
		'Stylus Pen Nibs & efills','Stylus Pens','Tablet Computer Docks & Stands','Blade Server Enclosures','Computer Backplates & I/O Shields','Computer Power Supplies','Computer Processors','Computer Racks & Mounts','Computer Starter Kits','Computer System Cooling Parts',
		'Desktop Computer & Server Cases','E-Book Reader Parts','I/O Cards & Adapters','Input Device Accessories','Input Devices','Laptop Parts','Storage Devices','Tablet Computer Parts','USB & FireWire Hubs','Electronics Stickers & Decals','Keyboard Protectors','Privacy Filters',
		'Screen Protectors','Cache Memory','Flash Memory','RAM','ROM','Video Memory','Memory Cases','Batteries','Battery Accessories','Fuel Cells','Power Adapter & Charger Accessories','Power Adapters & Chargers','Power Control Units','Power Strips & Surge Suppressors',
		'Power Supply Enclosures','Surge Protection Devices','Travel Converters & Adapters','UPS','UPS Accessories','GPS Jammers','Mobile Phone Jammers','Radar Jammers','Network Bridges','VoIP Gateways & Routers','Wireless Access Points','Wireless Routers','Printer Consumables',
		'Printer Duplexers','Printer Memory','Printer Stands','Printer', 'Copier & Fax Machine Replacement Parts','Multimedia Projectors','Overhead Projectors','Slide Projectors','Cable TV Receivers','Satellite Receivers','3D Glasses','Computer Monitor Accessories','Projector Accessories',
		'Rewinders','Television Parts & Accessories','DVD & Blu-ray Players','DVD Recorders','Digital Video Recorders','Streaming & Home Media Players','VCRs','Beer','Bitters','Cocktail Mixes','Flavored Alcoholic Beverages','Hard Cider','Liquor & Spirits','Wine','Carbonated Water',
		'Distilled Water','Flat Mineral Water','Spring Water','Bagels','Bakery Assortments','Breads & Buns','Cakes & Dessert Bars','Coffee Cakes','Cookies','Cupcakes','Donuts','Fudge','Ice Cream Cones','Muffins','Pastries & Scones','Pies & Tarts','Taco Shells & Tostadas','Tortillas & Wraps',
		'Cocktail Sauce','Curry Sauce','Dessert Toppings','Fish Sauce','Gravy','Honey','Horseradish Sauce','Hot Sauce','Ketchup','Marinades & Grilling Sauces','Mayonnaise','Mustard','Olives & Capers','Pasta Sauce','Pickled Fruits & Vegetables','Pizza Sauce','Relish & Chutney','Salad Dressing',
		'Satay Sauce','Soy Sauce','Sweet and Sour Sauces','Syrup','Tahini','Tartar Sauce','White & Cream Sauces','Worcestershire Sauce','Baking Chips','Baking Chocolate','Baking Flavors & Extracts','Baking Mixes','Baking Powder','Baking Soda','Batter & Coating Mixes','Bean Paste','Bread Crumbs',
		'Canned & Dry Milk','Cookie Decorating Kits','Cooking Oils','Cooking Starch','Cooking Wine','Corn Syrup','Dough','Edible Baking Decorations','Egg Replacers','Floss Sugar','Flour','Food Coloring','Frosting & Icing','Lemon & Lime Juice','Marshmallows','Meal','Molasses','Pie & Pastry Fillings',
		'Shortening & Lard','Starter Cultures','Sugar & Sweeteners','Tapioca Pearls','Tomato Paste','Unflavored Gelatin','Vinegar','Waffle & Pancake Mixes','Yeast','Butter & Margarine','Cheese','Coffee Creamer','Cottage Cheese','Cream','Sour Cream','Whipped Cream','Yogurt','Apple Butter',
		'Cheese Dips & Spreads','Cream Cheese','Guacamole','Hummus','Jams & Jellies','Nut Butters','Salsa','Tapenade','Vegetable Dip','Ice Cream & Frozen Yogurt','Ice Cream Novelties','Ice Pops','Canned & Jarred Fruits','Canned & Jarred Vegetables','Canned & Prepared Beans','Dried Fruits',
		'Dried Vegetables','Dry Beans','Fresh & Frozen Fruits','Fresh & Frozen Vegetables','Fruit Sauces','Amaranth','Barley','Buckwheat','Cereal & Granola','Couscous','Millet','Oats', 'Grits & Hot Cereal','Quinoa','Rice','Rye','Wheat','Eggs','Meat','Seafood','Prepared Appetizers & Side Dishes',
		'Prepared Meals & Entrées','Herbs & Spices','MSG','Pepper','Salt','Breadsticks','Cereal & Granola Bars','Cheese Puffs','Chips','Crackers','Croutons','Fruit Snacks','Jerky','Popcorn','Pork Rinds','Pretzels','Pudding & Gelatin Snacks','Puffed Rice Cakes','Salad Toppings','Sesame Sticks',
		'Snack Cakes','Sticky Rice Cakes','Trail & Snack Mixes','Cheese Alternatives','Meat Alternatives','Seitan','Tempeh','Tofu','Electronic Cigarettes','Vaporizers','Crib Bumpers & Liners','Crib Conversion Kits','Hope Chests','Toy Chests','Bathroom Vanities','Bedroom Vanities','Art & Drafting Tables',
		'Conference Room Tables','Outdoor Benches','Outdoor Chairs','Outdoor Sectional Sofa Units','Outdoor Sofas','Sunloungers','Coffee Tables','End Tables','Sofa Tables','Acid Neutralizers','Ammonia','Chimney Cleaners','Concrete & Masonry Cleaners','De-icers','Deck & Fence Cleaners','Drain Cleaners',
		'Electrical Freeze Sprays','Lighter Fluid','Septic Tank & Cesspool Treatments','Bricks & Concrete Blocks','Cement', 'Mortar & Concrete Mixes','Grout','Paint','Paint Binders','Primers','Stains','Varnishes & Finishes','Door Bells & Chimes','Door Closers','Door Frames','Door Keyhole Escutcheons',
		'Door Knobs & Handles','Door Knockers','Door Push Plates','Door Stops','Door Strikes','Garage Doors','Home Doors','Gutter Accessories','Gutters','Roof Flashings','Roofing Shingles & Tiles','Window Cranks','Window Frames','Clear Kerosene','Dyed Kerosene','Cabinet & Furniture Keyhole Escutcheons',
		'Cabinet Backplates','Cabinet Catches','Cabinet Doors','Cabinet Knobs & Handles','Bungee Cords','Chains','Pull Chains','Ropes & Hardware Cable','Tie Down Straps','Twine','Utility Wire','Drywall Anchors','Nails','Nuts & Bolts','Rivets','Screw Posts','Screws','Threaded Rods','Washers','Chain Connectors & Links',
		'Gear Ties','Lifting Hooks', 'Clamps & Shackles','Utility Buckles','Garden Hose Storage','Tool & Equipment Belts','Tool Bags','Tool Boxes','Tool Cabinets & Chests','Tool Organizer Liners & Inserts','Tool Sheaths','Work Benches','Control Panels','Humidistats','Thermostats','Gaskets & O-Rings',
		'In-Wall Carriers & Mounting Frames','Nozzles','Pipe Adapters & Bushings','Pipe Caps & Plugs','Pipe Connectors','Plumbing Flanges','Plumbing Pipe Clamps','Plumbing Regulators','Plumbing Valves','Bathtub Accessories','Drain Components','Drains','Faucet Accessories','Fixture Plates','Shower Parts',
		'Sink Accessories','Toilet & Bidet Accessories','Bathroom Suites','Bathtubs','Faucets','Shower Stalls & Kits','Sinks','Toilets & Bidets','In-Line Water Filters','Water Dispensers','Water Distillers','Water Filtration Accessories','Water Softener Salt','Water Softeners','Electrical Conduit',
		'Heat-Shrink Tubing','Light Switches','Specialty Electrical Switches & Relays','Sandblasting Cabinets','Axe Handles','Axe Heads','Nibbler Dies','Drill & Screwdriver Bits','Drill Bit Extensions','Drill Bit Sharpeners','Drill Chucks','Drill Stands & Guides','Hole Saws','Grinding Wheels & Points',
		'Air Hammer Accessories','Hammer Handles','Hammer Heads','Mattock & Pickaxe Handles','Electrical Testing Tool Accessories','Gas Detector Accessories','Measuring Scale Accessories','Multimeter Accessories','Airbrush Accessories','Paint Brush Cleaning Solutions','Paint Roller Accessories',
		'Router Bits','Router Tables','Sandpaper & Sanding Sponges','Band Saw Accessories','Handheld Circular Saw Accessories','Jigsaw Accessories','Miter Saw Accessories','Table Saw Accessories','Shaper Cutters','Soldering Iron Stands','Soldering Iron Tips','Cutter & Scraper Blades','Saw Blades',
		'Saw Stands','Bolt Cutters','Glass Cutters','Handheld Metal Shears & Nibblers','Nippers','Pipe Cutters','Rebar Cutters','Tile & Shingle Cutters','Utility Knives','Augers','Drill Presses','Handheld Power Drills','Mortisers','Pneumatic Drills','Flashlights','Headlamps','Manual Hammers',
		'Powered Hammers','Ladder Carts','Ladders','Scaffolding','Step Stools','Work Platforms','Brick Tools','Cement Mixers','Construction Lines','Floats','Grout Sponges','Masonry Edgers & Groovers','Masonry Jointers','Masonry Trowels','Power Trowels','Air Quality Meters','Altimeters','Anemometers',
		'Barometers','Calipers','Cruising Rods','Distance Meters','Dividers','Electrical Testing Tools','Flow Meters & Controllers','Gas Detectors','Gauges','Geiger Counters','Hygrometers','Infrared Thermometers','Knife Guides','Levels','Measuring Scales','Measuring Wheels','Moisture Meters',
		'Probes & Finders','Protractors','Rebar Locators','Rulers','Seismometer','Sound Meters','Squares','Straight Edges','Stud Sensors','Tape Measures','Theodolites','Thermal Imaging Cameras','Thermocouples & Thermopiles','Transducers','UV Light Meters','Vibration Meters','Weather Forecasters & Stations',
		'pH Meters','Airbrushes','Paint Brushes','Paint Edgers','Paint Rollers','Paint Shakers','Paint Sponges','Paint Sprayers','Paint Strainers','Paint Trays','Rivet Guns','Rivet Pliers','Band Saws','Cut-Off Saws','Hand Saws','Handheld Circular Saws','Jigsaws','Masonry & Tile Saws','Miter Saws',
		'Panel Saws','Reciprocating Saws','Scroll Saws','Table Saws','Hand Tool Sets','Power Tool Combo Sets','Acupuncture Models','Acupuncture Needles','Activity Monitor Accessories','Blood Glucose Meter Accessories','Blood Pressure Monitor Accessories','Body Weight Scale Accessories','Activity Monitors',
		'Blood Glucose Meters','Blood Pressure Monitors','Body Fat Analyzers','Body Weight Scales','Breathalyzers','Cholesterol Analyzers','Fertility Monitors and Ovulation Tests','Medical Thermometers','Prenatal Heart Rate Monitors','Pulse Oximeters','Antiseptics & Cleaning Supplies','Cast & Bandage Protectors',
		'Eye Wash Supplies','First Aid Kits','Hot & Cold Therapies','Medical Tape & Bandages','Nutrition Bars','Nutrition Drinks & Shakes','Nutrition Gels & Chews','Nutritional Food Purées','Tube Feeding Supplements','Vitamins & Supplements','Allergy Test Kits','Blood Typing Test Kits','Drug Tests','HIV Tests',
		'Pregnancy Tests','Urinary Tract Infection Tests','Accessibility Equipment','Accessibility Equipment Accessories','Accessibility Furniture & Fixtures','Walking Aid Accessories','Walking Aids','Electrical Muscle Stimulators','Therapeutic Swings','Nebulizers','Oxygen Tanks','PAP Machines','PAP Masks',
		'Steam Inhalers','Back & Lumbar Support Cushions','Bath & Body','Bath & Body Gift Sets','Cosmetic Sets','Cosmetic Tool Cleansers','Cosmetic Tools','Makeup','Nail Care','Perfume & Cologne','Skin Care','Anti-Perspirant','Deodorant','Ear Candles','Ear Drops','Ear Dryers','Ear Picks & Spoons','Ear Syringes',
		'Ear Wax Removal Kits','Earplug Dispensers','Earplugs','Feminine Deodorant','Feminine Douches & Creams','Feminine Pads & Protectors','Menstrual Cups','Tampons','Bunion Care Supplies','Corn & Callus Care Supplies','Foot Odor Removers','Insoles & Inserts','Toe Spacers','Hair Care Kits','Hair Color',
		'Hair Color Removers','Hair Coloring Accessories','Hair Loss Concealers','Hair Loss Treatments','Hair Permanents & Straighteners','Hair Shears','Hair Steamers & Heat Caps','Hair Styling Products','Hair Styling Tool Accessories','Hair Styling Tools','Shampoo & Conditioner','Back Scratchers','Eye Pillows',
		'Massage Chairs','Massage Oil','Massage Stone Warmers','Massage Stones','Massage Tables','Massagers','Breath Spray','Dental Floss','Dental Mouthguards','Dental Water Jet Replacement Tips','Dental Water Jets','Denture Adhesives','Denture Cleaners','Denture Repair Kits','Dentures','Gum Stimulators','Mouthwash',
		'Orthodontic Appliance Cases','Power Flossers','Teeth Whiteners','Tongue Scrapers','Toothbrush Accessories','Toothbrushes','Toothpaste','Toothpaste Squeezers & Dispensers','Toothpicks','Aftershave','Body & Facial Hair Bleach','Electric Razor Accessories','Electric Razors','Hair Clipper & Trimmer Accessories',
		'Hair Clippers & Trimmers','Hair Removal','Razors & Razor Blades','Shaving Bowls & Mugs','Shaving Brushes','Shaving Cream','Shaving Kits','Styptic Pencils','Eye Masks','Snoring & Sleep Apnea Aids','Travel Pillows','White Noise Machines','Contact Lens Care','Contact Lenses','Eye Drops & Lubricants','Eyeglass Lenses',
		'Eyeglasses','Eyewear Accessories','Sunglass Lenses','Decorative Tapestries','Posters', 'Prints, & Visual Artwork','Sculptures & Statues','Bird Feeders','Butterfly Feeders','Squirrel Feeders','Bat Houses','Birdhouses','Butterfly Houses','Alarm Clocks','Desk & Shelf Clocks','Floor & Grandfather Clocks','Wall Clocks',
		'Flag & Windsock Pole Lights','Flag & Windsock Pole Mounting Hardware & Kits','Flag & Windsock Poles','Fountain & Pond Accessories','Fountains & Waterfalls','Ponds','Candle & Oil Warmers','Candle Holders','Candle Snuffers','Incense Holders','Air Fresheners','Candles','Fragrance Oil','Incense','Potpourri','Wax Tarts',
		'Mailbox Covers','Mailbox Enclosures','Mailbox Flags','Mailbox Posts','Mailbox Replacement Doors','Advent Calendars','Christmas Tree Skirts','Christmas Tree Stands','Easter Egg Decorating Kits','Holiday Ornament Displays & Stands','Holiday Ornament Hooks','Holiday Ornaments','Holiday Stocking Hangers','Holiday Stockings',
		'Japanese Traditional Dolls','Nativity Sets','Seasonal Village Sets & Accessories','Curtain & Drape Rings','Curtain & Drape Rods','Curtain Holdbacks & Tassels','Window Treatment Replacement Parts','Curtains & Drapes','Stained Glass Panels','Window Blinds & Shades','Window Films','Window Screens','Window Valances & Cornices',
		'Carbon Monoxide Detectors','Smoke Detectors','Air Conditioner Covers','Air Conditioner Filters','Air Purifier Filters','Heating Radiator Reflectors','Humidifier Filters','Garment Steamer Accessories','Iron Accessories','Steam Press Accessories','Washer & Dryer Accessories','Patio Heater Covers','Anode Rods','Hot Water Tanks',
		'Water Heater Elements','Water Heater Expansion Tanks','Water Heater Pans','Water Heater Stacks','Water Heater Vents','Air Conditioners','Air Purifiers','Dehumidifiers','Duct Heaters','Evaporative Coolers','Fans','Furnaces & Boilers','Heating Radiators','Humidifiers','Outdoor Misting Systems','Patio Heaters','Space Heaters',
		'Carpet Shampooers','Carpet Steamers','Floor Scrubbers','Steam Mops','Dryers','Garment Steamers','Irons & Ironing Systems','Laundry Combo Units','Steam Presses','Washing Machines','Broom & Mop Handles','Broom Heads','Brooms','Buckets','Carpet Sweepers','Cleaning Gloves','Duster Refills','Dusters','Dustpans',
		'Fabric & Upholstery Protectors','Household Cleaning Products','Mop Heads & Refills','Mops','Scrub Brush Heads & Refills','Scrub Brushes','Shop Towels & General-Purpose Cleaning Cloths','Sponges & Scouring Pads','Squeegees','Facial Tissues','Paper Napkins','Paper Towels','Toilet Paper','Bleach','Clothespins',
		'Dry Cleaning Kits','Drying Racks & Hangers','Fabric Refreshers','Fabric Shavers','Fabric Softeners & Dryer Sheets','Fabric Stain Removers','Fabric Starch','Garment Shields','Iron Rests','Ironing Board Pads & Covers','Ironing Board Replacement Parts','Ironing Boards','Laundry Balls','Laundry Baskets','Laundry Detergent',
		'Laundry Wash Bags & Frames','Lint Rollers','Wrinkle Releasers & Anti-Static Sprays','Fly Swatters','Pest Control Traps','Pesticides','Repellents','Boot Pulls','Shoe Bags','Shoe Brushes','Shoe Care Kits','Shoe Dryers','Shoe Horns & Dressing Aids','Shoe Polishers','Shoe Polishes & Waxes','Shoe Scrapers',
		'Shoe Treatments & Dyes','Shoe Trees & Shapers','Clothing & Closet Storage','Flatware Chests','Household Drawer Organizer Inserts','Household Storage Bags','Household Storage Caddies','Household Storage Containers','Household Storage Drawers','Photo Storage','Storage Hooks & Racks','Dumpsters',
		'Hazardous Waste Containers','Recycling Containers','Trash Cans & Wastebaskets','Waste Container Carts','Waste Container Enclosures','Waste Container Labels & Signs','Waste Container Lids','Waste Container Wheels','Absinthe Fountains','Beer Dispensers & Taps','Beverage Chilling Cubes & Sticks',
		'Beverage Tubs & Chillers','Bottle Caps','Bottle Stoppers & Savers','Coaster Holders','Coasters','Cocktail & Barware Tool Sets','Cocktail Shakers & Tools','Corkscrews','Decanters','Foil Cutters','Wine Aerators','Wine Bottle Holders','Wine Glass Charms','Bakeware','Bakeware Accessories','Cookware',
		'Cookware & Bakeware Combo Sets','Cookware Accessories','Airpots','Canteens','Coolers','Drink Sleeves','Flasks','Insulated Bags','Lunch Boxes & Totes','Picnic Baskets','Replacement Drink Lids','Thermoses','Water Bottles','Wine Carrier Bags','Bread Boxes & Bags','Candy Buckets','Cookie Jars',
		'Food Container Covers','Food Storage Bags','Food Storage Containers','Food Wraps','Honey Jars','Food & Beverage Labels','Food Wrap Dispensers','Oxygen Absorbers','Twist Ties & Bag Clips','Breadmaker Accessories','Coffee Maker & Espresso Machine Accessories','Cooktop', 'Oven & Range Accessories',
		'Cotton Candy Machine Accessories','Deep Fryer Accessories','Dishwasher Parts & Accessories','Electric Kettle Accessories','Electric Skillet & Wok Accessories','Fondue Set Accessories','Food Dehydrator Accessories','Food Grinder Accessories','Food Mixer & Blender Accessories','Freezer Accessories',
		'Garbage Disposal Accessories','Ice Cream Maker Accessories','Ice Crusher & Shaver Accessories','Ice Maker Accessories','Juicer Accessories','Microwave Oven Accessories','Outdoor Grill Accessories','Pasta Maker Accessories','Popcorn Maker Accessories','Portable Cooking Stove Accessories','Range Hood Accessories',
		'Refrigerator Accessories','Soda Maker Accessories','Steam Table Accessories','Toaster Accessories','Vacuum Sealer Accessories','Waffle Iron Accessories','Water Cooler Accessories','Wine Fridge Accessories','Yogurt Maker Accessories','Beverage Warmers','Breadmakers','Chocolate Tempering Machines',
		'Coffee Makers & Espresso Machines','Cooktops','Cotton Candy Machines','Deep Fryers','Deli Slicers','Dishwashers','Electric Griddles & Grills','Electric Kettles','Electric Skillets & Woks','Fondue Pots & Sets','Food Cookers & Steamers','Food Dehydrators','Food Grinders & Mills','Food Mixers & Blenders',
		'Food Smokers','Food Warmers','Freezers','Frozen Drink Makers','Garbage Disposals','Gas Griddles','Hot Drink Makers','Hot Plates','Ice Cream Makers','Ice Crushers & Shavers','Ice Makers','Juicers','Knife Sharpeners','Microwave Ovens','Milk Frothers & Steamers','Mochi Makers','Outdoor Grills','Ovens','Pasta Makers',
		'Popcorn Makers','Portable Cooking Stoves','Range Hoods','Ranges','Refrigerators','Roaster Ovens & Rotisseries','Soda Makers','Soy Milk Makers','Tea Makers','Toasters & Grills','Trash Compactors','Vacuum Sealers','Water Coolers','Water Filters','Wine Fridges','Yogurt Makers','Aprons','Baking Peels','Basters',
		'Basting Brushes','Beverage Dispensers','Cake Decorating Supplies','Cake Servers','Can Crushers','Can Openers','Carving Forks','Channel Knives','Colanders & Strainers','Condiment Dispensers','Cookie Cutters','Cookie Presses','Cooking Thermometer Accessories','Cooking Thermometers','Cooking Timers','Cooking Torches',
		'Cooling Racks','Cutting Boards','Dish Racks & Drain Boards','Dough Wheels','Electric Knife Accessories','Electric Knives','Flour Sifters','Food & Drink Stencils','Food Crackers','Food Dispensers','Food Graters & Zesters','Food Peelers & Corers','Food Steaming Bags','Food Sticks & Skewers','Funnels','Garlic Presses',
		'Gelatin Molds','Ice Cube Trays','Jerky Guns','Kitchen Knives','Kitchen Molds','Kitchen Organizers','Kitchen Scrapers','Kitchen Shears','Kitchen Slicers','Kitchen Utensil Sets','Ladles','Mashers','Measuring Cups & Spoons','Meat Tenderizers','Mixing Bowls','Mortars & Pestles','Oil & Vinegar Dispensers','Oven Bags',
		'Oven Mitts & Pot Holders','Pasta Molds & Stamps','Pastry Blenders','Pastry Cloths','Pizza Cutter Accessories','Pizza Cutters','Ricers','Rolling Pin Accessories','Rolling Pins','Salad Dressing Mixers & Shakers','Salad Spinners','Scoops','Sink Caddies','Sink Mats & Grids','Slotted Spoons','Spatulas','Spice Grinder Accessories',
		'Spice Grinders','Spoon Rests','Sugar Dispensers','Sushi Mats','Tea Strainers','Tongs','Whisks','Coffee & Tea Sets','Coffee Servers & Tea Pots','Dinnerware','Drinkware','Flatware','Salt & Pepper Shakers','Serveware','Serveware Accessories','Tablecloth Clips & Weights','Trivets','Composting','Disease Control','Fertilizers',
		'Garden Pot Saucers & Trays','Gardening Accessories','Gardening Tool Accessories','Gardening Tools','Greenhouses','Herbicides','Landscape Fabric','Landscape Fabric Accessories','Mulch','Plant Cages & Supports','Plant Stands','Pot & Planter Liners','Pots & Planters','Rain Barrels','Sands & Soils','Awning Accessories',
		'Awnings','Hammock Parts & Accessories','Hammocks',
		'Outdoor Blankets','Outdoor Structures','Outdoor Umbrella & Sunshade Accessories','Outdoor Umbrellas & Sunshades','Porch Swing Accessories','Porch Swings','Chainsaws','Grass Edgers','Hedge Trimmers','Lawn Aerators & Dethatchers','Lawn Mowers','Lawn Vacuums','Leaf Blowers','Outdoor Power Equipment Base Units',
		'Outdoor Power Equipment Sets','Power Sweepers','Power Tillers & Cultivators','Pressure Washers','Snow Blowers','Tractors','Weed Trimmers','Chainsaw Accessories','Grass Edger Accessories','Hedge Trimmer Accessories','Lawn Mower Accessories','Leaf Blower Accessories','Multifunction Outdoor Power Equipment Attachments',
		'Outdoor Power Equipment Batteries','Pressure Washer Accessories','Snow Blower Accessories','Tractor Parts & Accessories','Weed Trimmer Accessories','Ice Scrapers & Snow Brushes','Snow Shovels','Garden Hose Fittings & Valves','Garden Hose Spray Nozzles','Garden Hoses','Sprinkler Accessories','Sprinklers & Sprinkler Heads',
		'Watering Can Accesssories','Watering Cans','Watering Globes & Spikes','Compact Fluorescent Lamps','Fluorescent Tubes','Incandescent Light Bulbs','LED Light Bulbs','Cabinet Light Fixtures','Ceiling Light Fixtures','Chandeliers','Wall Light Fixtures','Track Lighting Accessories','Track Lighting Fixtures',
		'Track Lighting Rails','Bed Canopies','Bed Sheets','Bedskirts','Blankets','Duvet Covers','Mattress Protectors','Nap Mats','Pillowcases & Shams','Pillows','Quilts & Comforters','Cloth Napkins','Doilies','Placemats','Table Runners','Table Skirts','Tablecloths','Bath Towels & Washcloths','Beach Towels','Kitchen Towels',
		'Bushes & Shrubs','Landscaping & Garden Plants','Potted Houseplants','Plant & Flower Bulbs','Seeds & Seed Tape','Diving Boards','Pool & Spa Chlorine Generators','Pool & Spa Filters','Pool & Spa Maintenance Kits','Pool Brushes & Brooms','Pool Cleaner Hoses','Pool Cleaners & Chemicals','Pool Cover Accessories',
		'Pool Covers & Ground Cloths','Pool Deck Kits','Pool Floats & Loungers','Pool Heaters','Pool Ladders', 'Steps & Ramps','Pool Liners','Pool Skimmers','Pool Sweeps & Vacuums','Pool Toys','Pool Water Slides','Sauna Buckets & Ladles','Sauna Heaters','Sauna Kits','Ammunition','Ammunition Cases & Holders',
		'Gun Cases & Range Bags','Gun Cleaning','Gun Grips','Gun Holsters','Gun Lights','Gun Rails','Gun Slings','Reloading Supplies & Equipment','Binder Accessories','Binders','Binding Combs & Spines','Binding Machines','Pocket Folders','Report Covers','Padfolios','Portfolios','Correction Fluids','Correction Pens',
		'Correction Tapes','Address Labels','Folder Tabs','Label Clips','Label Tapes & Refill Rolls','Shipping Labels','Shipping Tags','Binder Clips','Paper Clips','Binder Paper','Blank ID Cards','Business Cards','Business Forms & Receipts','Checks','Cover Paper','Envelopes','Index Cards','Notebooks & Notepads',
		'Post Cards','Printer & Copier Paper','Receipt & Adding Machine Paper Rolls','Stationery','Sticky Notes','Basic Calculators','Construction Calculators','Financial Calculators','Graphing Calculators','Scientific Calculators','Marker & Highlighter Ink Refills','Pen Ink & Refills','Pencil Lead & Refills',
		'Art Charcoals','Chalk','Crayons','Markers & Highlighters','Multifunction Writing Instruments','Pastels','Pens & Pencils','Bulletin Board Accessories','Bulletin Boards','Foam Boards','Mounting Boards','Poster Boards','3D Modeling Software','Animation Editing Software','Graphic Design & Illustration Software',
		'Home & Interior Design Software','Home Publishing Software','Media Viewing Software','Music Composition Software','Sound Editing Software','Video Editing Software','Web Design Software','American Football Gloves','American Football Goal Posts','American Football Kicking Tees & Holders','American Football Protective Gear',
		'American Football Training Equipment','American Footballs','Baseball & Softball Bases & Plates','Baseball & Softball Batting Gloves','Baseball & Softball Gloves & Mitts','Baseball & Softball Pitching Mats','Baseball & Softball Pitching Mounds','Baseball & Softball Protective Gear','Baseball Bats','Baseballs',
		'Pitching Machines','Softball Bats','Softballs','Basketball Hoop Parts & Accessories','Basketball Hoops','Basketball Training Aids','Basketballs','Boxing & Martial Arts Protective Gear','Boxing & Martial Arts Training Equipment','Boxing Ring Parts','Boxing Rings','Martial Arts Belts','Martial Arts Weapons',
		'Cheerleading Pom Poms','Captains Armbands','Field & Court Boundary Markers','Flip Coins & Discs','Linesman Flags','Penalty Cards & Flags','Pitch Counters','Referee Stands & Chairs','Referee Wallets','Scoreboards','Sport & Safety Whistles','Umpire Indicators','Cricket Balls','Cricket Bat Accessories','Cricket Bats',
		'Cricket Equipment Sets','Cricket Protective Gear','Cricket Stumps','Ballet Barres','Fencing Protective Gear','Fencing Weapons','Field Hockey & Lacrosse Protective Gear','Field Hockey Balls','Field Hockey Goals','Field Hockey Sticks','Lacrosse Balls','Lacrosse Equipment Sets','Lacrosse Goals','Lacrosse Stick Parts',
		'Lacrosse Sticks','Lacrosse Training Aids','Hockey Balls & Pucks','Hockey Goals','Hockey Protective Gear','Hockey Sledges','Hockey Stick Care','Hockey Stick Parts','Hockey Sticks','Ice Skate Parts & Accessories','Ice Skates','Altitude Training Masks','Athletic Cups','Ball Carrying Bags & Carts','Ball Pump Accessories',
		'Ball Pumps','Exercise & Gym Mat Storage Racks & Carts','Grip Spray & Chalk','Gym Mats','Practice Nets & Screens','Speed & Agility Ladders & Hurdles','Sports & Agility Cones','Sports Megaphones','Sports Mouthguards','Stadium Seats & Cushions','Gymnastics Bars & Balance Beams','Gymnastics Protective Gear','Gymnastics Rings',
		'Gymnastics Springboards','Pommel Horses','Vaulting Horses','Racquetball & Squash Balls','Racquetball & Squash Eyewear','Racquetball & Squash Gloves','Racquetball Racquets','Squash Racquets','Rounders Bats','Rounders Gloves','Rugby Balls','Rugby Gloves','Rugby Posts','Rugby Protective Gear','Rugby Training Aids','FootBalls',
		'Football Corner Flags','Soccer Gloves','Soccer Goal Accessories','Soccer Goals','Soccer Protective Gear','Handballs','Tennis Ball Hoppers & Carts','Tennis Ball Machines','Tennis Ball Savers','Tennis Balls','Tennis Nets','Tennis Racquet Accessories','Tennis Racquets','Discus','High Jump Crossbars','High Jump Pits','Javelins',
		'Pole Vault Pits','Relay Batons','Shot Puts','Starter Pistols','Throwing Hammers','Track Hurdles','Track Starting Blocks','Vaulting Poles','Volleyball Nets','Volleyball Protective Gear','Volleyball Training Aids','Volleyballs','Water Polo Balls','Water Polo Caps','Water Polo Goals','Wrestling Protective Gear',
		'Cardio Machine Accessories','Cardio Machines','Jump Ropes','Foam Roller Storage Bags','Free Weight Accessories','Free Weights','Weight Lifting Belts','Weight Lifting Gloves & Hand Supports','Weight Lifting Machine & Exercise Bench Accessories','Weight Lifting Machines & Racks','Pilates Machines','Yoga & Pilates Blocks',
		'Yoga & Pilates Mats','Yoga & Pilates Towels','Yoga Mat Bags & Straps','Air Hockey Equipment','Air Hockey Table Parts','Air Hockey Tables','Billiard Ball Racks','Billiard Balls','Billiard Cue Accessories','Billiard Cues & Bridges','Billiard Gloves','Billiard Table Lights','Billiard Table Parts & Accessories','Billiard Tables',
		'Bowling Ball Bags','Bowling Balls','Bowling Gloves','Bowling Pins','Bowling Wrist Supports','Foosball Balls','Foosball Table Parts & Accessories','Foosball Tables','Ping Pong Balls','Ping Pong Nets & Posts','Ping Pong Paddle Accessories','Ping Pong Paddles & Sets','Ping Pong Robot Accessories','Ping Pong Robots','Ping Pong Tables',
		'Shuffleboard Tables','Table Shuffleboard Powder','Table Shuffleboard Pucks','Dart Backboards','Dart Parts','Dartboards','Darts','Boating & Rafting','Boating & Water Sport Apparel','Diving & Snorkeling','Kitesurfing','Surfing','Swimming','Towed Water Sports','Watercraft Storage Racks','Windsurfing','Camp Furniture',
		'Camping Cookware & Dinnerware','Camping Lights & Lanterns','Camping Tools','Chemical Hand Warmers','Compression Sacks','Hiking Pole Accessories','Hiking Poles','Mosquito Nets & Insect Screens','Navigational Compasses','Portable Toilets & Showers','Portable Water Filters & Purifiers','Sleeping Bag Liners','Sleeping Bags',
			'Sleeping Pads','Tent Accessories','Tents','Windbreaks','Belay Devices','Carabiners','Climbing Apparel & Accessories','Climbing Ascenders & Descenders','Climbing Chalk Bags','Climbing Crash Pads','Climbing Harnesses','Climbing Protection Devices','Climbing Rope','Climbing Rope Bags','Climbing Webbing','Ice Climbing Tools',
		'Ice Screws','Indoor Climbing Holds','Quickdraws','Bicycle Accessories','Bicycle Parts','Bicycles','Cycling Apparel & Accessories','Tricycle Accessories','Tricycles','Unicycle Accessories','Unicycles','Horse Care','Horse Tack','Horse Tack Accessories','Riding Apparel & Accessories','Bite Alarms','Fishing & Hunting Waders',
		'Fishing Bait & Chum Containers','Fishing Gaffs',
		'Fishing Hook Removal Tools','Fishing Lines & Leaders','Fishing Nets','Fishing Reel Accessories','Fishing Reels','Fishing Rod Accessories','Fishing Rods','Fishing Spears','Fishing Tackle','Fishing Traps','Fly Tying Materials','Live Bait','Tackle Bags & Boxes','Divot Tools','Golf Accessory Sets','Golf Bag Accessories',
		'Golf Bags','Golf Ball Markers','Golf Balls','Golf Club Parts & Accessories','Golf Clubs','Golf Flags','Golf Gloves','Golf Tees','Golf Towels','Golf Training Aids','Air Suits','Hang Gliders','Parachutes','Archery','Clay Pigeon Shooting','Hunting','Hunting & Shooting Protective Gear','Paintball & Airsoft','Shooting & Range Accessories',
		'Inline & Roller Skating Protective Gear','Inline Skate Parts','Inline Skates','Roller Skate Parts','Roller Skates','Roller Skis','Kite Buggies','Kite Buggy Accessories','Badminton','Deck Shuffleboard','Disc Golf','Lawn Games','Paddle Ball Sets','Pickleball','Platform & Paddle Tennis','Tetherball','Skate Rails','Skate Ramps',
		'Skateboard Parts','Skateboarding Protective Gear','Skateboards','Avalanche Safety','Skiing & Snowboarding','Sleds','Snowshoeing','Poker Chip Carriers & Trays','Play Sprinkers','Water Parks & Slides','Water Tables','Ball & Cup Games','Bouncy Balls','Bubble Blowing Solution','Bubble Blowing Toys','Coiled Spring Toys','Marbles',
		'Paddle Ball Toys','Ribbon & Streamer Toys','Spinning Tops','Toy Jacks','Yo-Yo Parts & Accessories','Yo-Yos','Play Dough & Putty','Toy Drawing Tablets','Ball Pit Balls','Construction Set Toys','Foam Blocks','Interlocking Blocks','Marble Track Sets','Wooden Blocks','Action & Toy Figures','Bobblehead Figures',
		'Doll & Action Figure Accessories',
		'Dollhouse Accessories','Dollhouses','Dolls','Paper & Magnetic Dolls','Puppet & Puppet Theater Accessories','Puppet Theaters','Puppets & Marionettes','Stuffed Animals','Toy Playsets','Ant Farms','Astronomy Toys & Models','Bug Collecting Kits','Educational Flash Cards','Reading Toys','Science & Exploration Sets',
		'Toy Abacuses','Magnet Toys','Kite Accessories','Air & Water Rockets','Kites','Toy Gliders','Toy Parachutes','Toy Instruments','Toy Race Car & Track Accessories','Toy Train Accessories','Toy Airplanes','Toy Boats','Toy Cars','Toy Helicopters','Toy Motorcycles','Toy Race Car & Track Sets','Toy Spaceships',
		'Toy Trains & Train Sets','Toy Trucks & Construction Vehicles','Play Money & Banking','Pretend Electronics','Pretend Housekeeping','Pretend Lawn & Garden','Pretend Professions & Role Playing','Pretend Shopping & Grocery','Toy Kitchens & Play Food','Toy Tools','Remote Control Airships & Blimps',
		'Remote Control Boats & Watercraft','Remote Control Cars & Trucks','Remote Control Helicopters','Remote Control Motorcycles','Remote Control Planes','Remote Control Robots','Remote Control Tanks','Electric Riding Vehicles','Hobby Horses','Push & Pedal Riding Vehicles','Rocking & Spring Riding Toys',
		'Wagons','Fitness Toy Accessories','American Football Toys','Baseball Toys','Basketball Toys','Boomerangs','Bowling Toys','Fingerboards & Fingerboard Sets','Fishing Toys','Fitness Toys','Flying Discs','Footbags','Golf Toys','Hockey Toys','Playground Balls','Racquet Sport Toys','Kaleidoscopes','Prisms',
		'Motor Vehicle A/V Players & In-Dash Systems','Motor Vehicle Amplifiers','Motor Vehicle Cassette Adapters','Motor Vehicle Cassette Players','Motor Vehicle Equalizers & Crossovers','Motor Vehicle Parking Cameras','Motor Vehicle Speakerphones','Motor Vehicle Speakers','Motor Vehicle Subwoofers',
		'Motor Vehicle Video Monitor Mounts','Motor Vehicle Braking','Motor Vehicle Carpet & Upholstery','Motor Vehicle Climate Control','Motor Vehicle Controls','Motor Vehicle Engine Oil Circulation','Motor Vehicle Engine Parts','Motor Vehicle Engines','Motor Vehicle Exhaust','Motor Vehicle Frame & Body Parts',
		'Motor Vehicle Fuel Systems','Motor Vehicle Interior Fittings','Motor Vehicle Lighting','Motor Vehicle Mirrors','Motor Vehicle Power & Electrical Systems','Motor Vehicle Seating','Motor Vehicle Sensors & Gauges','Motor Vehicle Suspension Parts','Motor Vehicle Towing','Motor Vehicle Transmission & Drivetrain Parts',
		'Motor Vehicle Wheel Systems','Motor Vehicle Window Parts & Accessories','Portable Fuel Cans','Vehicle Cleaning','Vehicle Covers','Vehicle Decor','Vehicle Fluids','Vehicle Paint','Vehicle Repair & Specialty Tools','Motorcycle Protective Gear','Off-Road & All-Terrain Vehicle Protective Gear',
		'Vehicle Alarms & Locks','Vehicle Safety Equipment','Motor Vehicle Cargo Nets','Motor Vehicle Carrying Rack Accessories','Motor Vehicle Carrying Racks','Motor Vehicle Loading Ramps','Motor Vehicle Trailers','Motorcycle Bags & Panniers','Truck Bed Storage Boxes & Organizers','Vehicle Headrest Hangers & Hooks',
		'Vehicle Organizers','Docking & Anchoring','Sailboat Parts','Watercraft Care','Watercraft Engine Parts','Watercraft Engines & Motors','Watercraft Exhaust Parts','Watercraft Fuel Systems','Watercraft Lighting','Watercraft Steering Parts','Cars', 'Trucks & Vans','Golf Carts','Motorcycles & Scooters',
		'Off-Road and All-Terrain Vehicles','Recreational Vehicles','Snowmobiles','Motor Boats','Personal Watercraft','Sailboats','Yachts')

        for item in items:
            item = SeoItems(items=item)
            db.session.add(item)
        db.session.commit()
        print('Added Seo Items!')

        
class SeoLocations(db.Model):
    __tablename__ = 'seo_locations'
    id = db.Column(db.Integer, primary_key=True)
    locations = db.Column(db.String(500))

    @staticmethod
    def insert_data():   
        locations = ('Abia State','Aba','Arochukwu','Umuahia','Adamawa State','Jimeta','Mubi','Numan',
                'Yola','Akwa Ibom State','Ikot Abasi','Ikot Ekpene','Oron','Uyo','Anambra State',
                'Awka','Onitsha','Bauchi State','Azare','Bauchi','Jama′are','Katagum','Misau',
                'Bayelsa State','Brass','BenueState','Makurdi','Borno State','Biu','Dikwa','Maiduguri',
                'Cross River State','Calabar','Ogoja','Delta State','Asaba','Burutu','Koko','Sapele',
                'Ughelli','Warri','Ebonyi State','Abakaliki','Edo State','BeninCity','Ekiti State',
                'Ado-Ekiti','Effon-Alaiye','Ikere-Ekiti','Enugu State','Enugu','Nsukka','Abuja',
                'Gombe State','Deba Habe','Gombe','Kumo','Imo State','Owerri','Jigawa State',
                'Birnin Kudu','Dutse','Gumel','Hadejia','Kazaure','KadunaState','Jemaa','Kaduna',
                'Zaria','KanoState','Kano','KatsinaState','Daura','Katsina','KebbiState','Argungu','Birnin Kebbi',
                    'Gwandu','Yelwa','KogiState','Idah','Kabba','Lokoja','Okene','KwaraState','Ilorin',
                'Jebba','Lafiagi','Offa','Pategi','Lagos State','Badagry','Epe','Ikeja','Ikorodu','Lagos','Mushin',
                'Shomolu','Nasarawa State','Keffi','Lafia','Nasarawa','NigerState','Agaie','Baro','Bida','Kontagora',
                'Lapai','Minna','Suleja','Ogun State','Abeokuta','Ijebu-Ode','Ilaro','Shagamu','OndoState','Akure','Ikare',
                'Oka-Akoko','Ondo','Owo',
                'OsunState','Ede','Ikire','Ikirun','Ila','Ile-Ife','Ilesha','Ilobu','Inisa','Iwo','Oshogbo','OyoState',
                'Ibadan','Iseyin','Ogbomosho','Oyo','Saki','Plateau State','Bukuru','Jos','Vom','Wase','RiversState',
                'Bonny','Degema','Okrika','Port Harcourt','Sokoto State','Sokoto','Taraba State','Ibi','Jalingo','Muri',
                'Yobe State','Damaturu','Nguru','Zamfara State','Gusau','Kaura Namoda')

        for location in locations:
            location = SeoLocations(locations=location)
            db.session.add(location)
        db.session.commit()
        print('Added Seo Locations. Get rankings in!')
