#!/usr/bin/env python3
"""
polyseed.py
===========
Konversi Polyseed 16 kata + passphrase --> Monero spend key + 25-kata seed.

Penggunaan  : python3 polyseed.py
Dependensi  : Python stdlib saja (3.6+)
Air-gap safe: tidak ada network call

Pipeline (spec: tevador/polyseed + cake-tech/polyseed_dart):
  1. Parse 16 kata BIP39 --> indeks
  2. PolyToData: bit[0]=metadata LSB, bit[10:1]=10-bit secret per word
  3. Decrypt: PBKDF2(NFKD(pp), "POLYSEED mask") XOR secret
  4. KDF: PBKDF2(secret+zeros(13), "POLYSEED key"+coin+bday+feat LE32)
  5. sc_reduce32 --> spend key
  6. Derive spend_pub, view_key, view_pub, primary address
  7. Encode 25-kata seed (1 baris siap copy-paste)
"""
import sys, hashlib, struct, unicodedata, binascii, getpass, os

# -- Polyseed wordlist (BIP39 English, 2048 kata) -------------------
_BIP39 = """
    abandon ability able about above absent absorb abstract absurd abuse access accident
    account accuse achieve acid acoustic acquire across act action actor actress actual
    adapt add addict address adjust admit adult advance advice aerobic affair afford
    afraid again age agent agree ahead aim air airport aisle alarm album
    alcohol alert alien all alley allow almost alone alpha already also alter
    always amateur amazing among amount amused analyst anchor ancient anger angle angry
    animal ankle announce annual another answer antenna antique anxiety any apart apology
    appear apple approve april arch arctic area arena argue arm armed armor
    army around arrange arrest arrive arrow art artefact artist artwork ask aspect
    assault asset assist assume asthma athlete atom attack attend attitude attract auction
    audit august aunt author auto autumn average avocado avoid awake aware away
    awesome awful awkward axis baby bachelor bacon badge bag balance balcony ball
    bamboo banana banner bar barely bargain barrel base basic basket battle beach
    bean beauty because become beef before begin behave behind believe below belt
    bench benefit best betray better between beyond bicycle bid bike bind biology
    bird birth bitter black blade blame blanket blast bleak bless blind blood
    blossom blouse blue blur blush board boat body boil bomb bone bonus
    book boost border boring borrow boss bottom bounce box boy bracket brain
    brand brass brave bread breeze brick bridge brief bright bring brisk broccoli
    broken bronze broom brother brown brush bubble buddy budget buffalo build bulb
    bulk bullet bundle bunker burden burger burst bus business busy butter buyer
    buzz cabbage cabin cable cactus cage cake call calm camera camp can
    canal cancel candy cannon canoe canvas canyon capable capital captain car carbon
    card cargo carpet carry cart case cash casino castle casual cat catalog
    catch category cattle caught cause caution cave ceiling celery cement census century
    cereal certain chair chalk champion change chaos chapter charge chase chat cheap
    check cheese chef cherry chest chicken chief child chimney choice choose chronic
    chuckle chunk churn cigar cinnamon circle citizen city civil claim clap clarify
    claw clay clean clerk clever click client cliff climb clinic clip clock
    clog close cloth cloud clown club clump cluster clutch coach coast coconut
    code coffee coil coin collect color column combine come comfort comic common
    company concert conduct confirm congress connect consider control convince cook cool copper
    copy coral core corn correct cost cotton couch country couple course cousin
    cover coyote crack cradle craft cram crane crash crater crawl crazy cream
    credit creek crew cricket crime crisp critic crop cross crouch crowd crucial
    cruel cruise crumble crunch crush cry crystal cube culture cup cupboard curious
    current curtain curve cushion custom cute cycle dad damage damp dance danger
    daring dash daughter dawn day deal debate debris decade december decide decline
    decorate decrease deer defense define defy degree delay deliver demand demise denial
    dentist deny depart depend deposit depth deputy derive describe desert design desk
    despair destroy detail detect develop device devote diagram dial diamond diary dice
    diesel diet differ digital dignity dilemma dinner dinosaur direct dirt disagree discover
    disease dish dismiss disorder display distance divert divide divorce dizzy doctor document
    dog doll dolphin domain donate donkey donor door dose double dove draft
    dragon drama drastic draw dream dress drift drill drink drip drive drop
    drum dry duck dumb dune during dust dutch duty dwarf dynamic eager
    eagle early earn earth easily east easy echo ecology economy edge edit
    educate effort egg eight either elbow elder electric elegant element elephant elevator
    elite else embark embody embrace emerge emotion employ empower empty enable enact
    end endless endorse enemy energy enforce engage engine enhance enjoy enlist enough
    enrich enroll ensure enter entire entry envelope episode equal equip era erase
    erode erosion error erupt escape essay essence estate eternal ethics evidence evil
    evoke evolve exact example excess exchange excite exclude excuse execute exercise exhaust
    exhibit exile exist exit exotic expand expect expire explain expose express extend
    extra eye eyebrow fabric face faculty fade faint faith fall false fame
    family famous fan fancy fantasy farm fashion fat fatal father fatigue fault
    favorite feature february federal fee feed feel female fence festival fetch fever
    few fiber fiction field figure file film filter final find fine finger
    finish fire firm first fiscal fish fit fitness fix flag flame flash
    flat flavor flee flight flip float flock floor flower fluid flush fly
    foam focus fog foil fold follow food foot force forest forget fork
    fortune forum forward fossil foster found fox fragile frame frequent fresh friend
    fringe frog front frost frown frozen fruit fuel fun funny furnace fury
    future gadget gain galaxy gallery game gap garage garbage garden garlic garment
    gas gasp gate gather gauge gaze general genius genre gentle genuine gesture
    ghost giant gift giggle ginger giraffe girl give glad glance glare glass
    glide glimpse globe gloom glory glove glow glue goat goddess gold good
    goose gorilla gospel gossip govern gown grab grace grain grant grape grass
    gravity great green grid grief grit grocery group grow grunt guard guess
    guide guilt guitar gun gym habit hair half hammer hamster hand happy
    harbor hard harsh harvest hat have hawk hazard head health heart heavy
    hedgehog height hello helmet help hen hero hidden high hill hint hip
    hire history hobby hockey hold hole holiday hollow home honey hood hope
    horn horror horse hospital host hotel hour hover hub huge human humble
    humor hundred hungry hunt hurdle hurry hurt husband hybrid ice icon idea
    identify idle ignore ill illegal illness image imitate immense immune impact impose
    improve impulse inch include income increase index indicate indoor industry infant inflict
    inform inhale inherit initial inject injury inmate inner innocent input inquiry insane
    insect inside inspire install intact interest into invest invite involve iron island
    isolate issue item ivory jacket jaguar jar jazz jealous jeans jelly jewel
    job join joke journey joy judge juice jump jungle junior junk just
    kangaroo keen keep ketchup key kick kid kidney kind kingdom kiss kit
    kitchen kite kitten kiwi knee knife knock know lab label labor ladder
    lady lake lamp language laptop large later latin laugh laundry lava law
    lawn lawsuit layer lazy leader leaf learn leave lecture left leg legal
    legend leisure lemon lend length lens leopard lesson letter level liar liberty
    library license life lift light like limb limit link lion liquid list
    little live lizard load loan lobster local lock logic lonely long loop
    lottery loud lounge love loyal lucky luggage lumber lunar lunch luxury lyrics
    machine mad magic magnet maid mail main major make mammal man manage
    mandate mango mansion manual maple marble march margin marine market marriage mask
    mass master match material math matrix matter maximum maze meadow mean measure
    meat mechanic medal media melody melt member memory mention menu mercy merge
    merit merry mesh message metal method middle midnight milk million mimic mind
    minimum minor minute miracle mirror misery miss mistake mix mixed mixture mobile
    model modify mom moment monitor monkey monster month moon moral more morning
    mosquito mother motion motor mountain mouse move movie much muffin mule multiply
    muscle museum mushroom music must mutual myself mystery myth naive name napkin
    narrow nasty nation nature near neck need negative neglect neither nephew nerve
    nest net network neutral never news next nice night noble noise nominee
    noodle normal north nose notable note nothing notice novel now nuclear number
    nurse nut oak obey object oblige obscure observe obtain obvious occur ocean
    october odor off offer office often oil okay old olive olympic omit
    once one onion online only open opera opinion oppose option orange orbit
    orchard order ordinary organ orient original orphan ostrich other outdoor outer output
    outside oval oven over own owner oxygen oyster ozone pact paddle page
    pair palace palm panda panel panic panther paper parade parent park parrot
    party pass patch path patient patrol pattern pause pave payment peace peanut
    pear peasant pelican pen penalty pencil people pepper perfect permit person pet
    phone photo phrase physical piano picnic picture piece pig pigeon pill pilot
    pink pioneer pipe pistol pitch pizza place planet plastic plate play please
    pledge pluck plug plunge poem poet point polar pole police pond pony
    pool popular portion position possible post potato pottery poverty powder power practice
    praise predict prefer prepare present pretty prevent price pride primary print priority
    prison private prize problem process produce profit program project promote proof property
    prosper protect proud provide public pudding pull pulp pulse pumpkin punch pupil
    puppy purchase purity purpose purse push put puzzle pyramid quality quantum quarter
    question quick quit quiz quote rabbit raccoon race rack radar radio rail
    rain raise rally ramp ranch random range rapid rare rate rather raven
    raw razor ready real reason rebel rebuild recall receive recipe record recycle
    reduce reflect reform refuse region regret regular reject relax release relief rely
    remain remember remind remove render renew rent reopen repair repeat replace report
    require rescue resemble resist resource response result retire retreat return reunion reveal
    review reward rhythm rib ribbon rice rich ride ridge rifle right rigid
    ring riot ripple risk ritual rival river road roast robot robust rocket
    romance roof rookie room rose rotate rough round route royal rubber rude
    rug rule run runway rural sad saddle sadness safe sail salad salmon
    salon salt salute same sample sand satisfy satoshi sauce sausage save say
    scale scan scare scatter scene scheme school science scissors scorpion scout scrap
    screen script scrub sea search season seat second secret section security seed
    seek segment select sell seminar senior sense sentence series service session settle
    setup seven shadow shaft shallow share shed shell sheriff shield shift shine
    ship shiver shock shoe shoot shop short shoulder shove shrimp shrug shuffle
    shy sibling sick side siege sight sign silent silk silly silver similar
    simple since sing siren sister situate six size skate sketch ski skill
    skin skirt skull slab slam sleep slender slice slide slight slim slogan
    slot slow slush small smart smile smoke smooth snack snake snap sniff
    snow soap soccer social sock soda soft solar soldier solid solution solve
    someone song soon sorry sort soul sound soup source south space spare
    spatial spawn speak special speed spell spend sphere spice spider spike spin
    spirit split spoil sponsor spoon sport spot spray spread spring spy square
    squeeze squirrel stable stadium staff stage stairs stamp stand start state stay
    steak steel stem step stereo stick still sting stock stomach stone stool
    story stove strategy street strike strong struggle student stuff stumble style subject
    submit subway success such sudden suffer sugar suggest suit summer sun sunny
    sunset super supply supreme sure surface surge surprise surround survey suspect sustain
    swallow swamp swap swarm swear sweet swift swim swing switch sword symbol
    symptom syrup system table tackle tag tail talent talk tank tape target
    task taste tattoo taxi teach team tell ten tenant tennis tent term
    test text thank that theme then theory there they thing this thought
    three thrive throw thumb thunder ticket tide tiger tilt timber time tiny
    tip tired tissue title toast tobacco today toddler toe together toilet token
    tomato tomorrow tone tongue tonight tool tooth top topic topple torch tornado
    tortoise toss total tourist toward tower town toy track trade traffic tragic
    train transfer trap trash travel tray treat tree trend trial tribe trick
    trigger trim trip trophy trouble truck true truly trumpet trust truth try
    tube tuition tumble tuna tunnel turkey turn turtle twelve twenty twice twin
    twist two type typical ugly umbrella unable unaware uncle uncover under undo
    unfair unfold unhappy uniform unique unit universe unknown unlock until unusual unveil
    update upgrade uphold upon upper upset urban urge usage use used useful
    useless usual utility vacant vacuum vague valid valley valve van vanish vapor
    various vast vault vehicle velvet vendor venture venue verb verify version very
    vessel veteran viable vibrant vicious victory video view village vintage violin virtual
    virus visa visit visual vital vivid vocal voice void volcano volume vote
    voyage wage wagon wait walk wall walnut want warfare warm warrior wash
    wasp waste water wave way wealth weapon wear weasel weather web wedding
    weekend weird welcome west wet whale what wheat wheel when where whip
    whisper wide width wife wild will win window wine wing wink winner
    winter wire wisdom wise wish witness wolf woman wonder wood wool word
    work world worry worth wrap wreck wrestle wrist write wrong yard year
    yellow you young youth zebra zero zone zoo
""".split()

# -- Monero wordlist (English, 1626 kata) ---------------------------
_MONERO = """
    abbey abducts ability ablaze abnormal abort abrasive absorb abyss academy aces aching
    acidic acoustic acquire across actress acumen adapt addicted adept adhesive adjust adopt
    adrenalin adult adventure aerial afar affair afield afloat afoot afraid after against
    agenda aggravate agile aglow agnostic agony agreed ahead aided ailments aimless airport
    aisle ajar akin alarms album alchemy alerts algebra alkaline alley almost aloof
    alpine already also altitude alumni always amaze ambush amended amidst ammo amnesty
    among amply amused anchor android anecdote angled ankle annoyed answers antics anvil
    anxiety anybody apart apex aphid aplomb apology apply apricot aptitude aquarium arbitrary
    archer ardent arena argue arises army around arrow arsenic artistic ascend ashtray
    aside asked asleep aspire assorted asylum athlete atlas atom atrium attire auburn
    auctions audio august aunt austere autumn avatar avidly avoid awakened awesome awful
    awkward awning awoken axes axis axle aztec azure baby bacon badge baffles
    bagpipe bailed bakery balding bamboo banjo baptism basin batch bawled bays because
    beer befit begun behind being below bemused benches berries bested betting bevel
    beware beyond bias bicycle bids bifocals biggest bikini bimonthly binocular biology biplane
    birth biscuit bite biweekly blender blip bluntly boat bobsled bodies bogeys boil
    boldly bomb border boss both bounced bovine bowling boxes boyfriend broken brunt
    bubble buckets budget buffet bugs building bulb bumper bunch business butter buying
    buzzer bygones byline bypass cabin cactus cadets cafe cage cajun cake calamity
    camp candy casket catch cause cavernous cease cedar ceiling cell cement cent
    certain chlorine chrome cider cigar cinema circle cistern citadel civilian claim click
    clue coal cobra cocoa code coexist coffee cogs cohesive coils colony comb
    cool copy corrode costume cottage cousin cowl criminal cube cucumber cuddled cuffs
    cuisine cunning cupcake custom cycling cylinder cynical dabbing dads daft dagger daily
    damp dangerous dapper darted dash dating dauntless dawn daytime dazed debut decay
    dedicated deepest deftly degrees dehydrate deity dejected delayed demonstrate dented deodorant depth
    desk devoid dewdrop dexterity dialect dice diet different digit dilute dime dinner
    diode diplomat directed distance ditch divers dizzy doctor dodge does dogs doing
    dolphin domestic donuts doorway dormant dosage dotted double dove down dozen dreams
    drinks drowning drunk drying dual dubbed duckling dude duets duke dullness dummy
    dunes duplex duration dusted duties dwarf dwelt dwindling dying dynamite dyslexic each
    eagle earth easy eating eavesdrop eccentric echo eclipse economics ecstatic eden edgy
    edited educated eels efficient eggs egotistic eight either eject elapse elbow eldest
    eleven elite elope else eluded emails ember emerge emit emotion empty emulate
    energy enforce enhanced enigma enjoy enlist enmity enough enraged ensign entrance envy
    epoxy equip erase erected erosion error eskimos espionage essential estate etched eternal
    ethics etiquette evaluate evenings evicted evolved examine excess exhale exit exotic exquisite
    extra exult fabrics factual fading fainted faked fall family fancy farming fatal
    faulty fawns faxed fazed feast february federal feel feline females fences ferry
    festival fetches fever fewest fiat fibula fictional fidget fierce fifteen fight films
    firm fishing fitting five fixate fizzle fleet flippant flying foamy focus foes
    foggy foiled folding fonts foolish fossil fountain fowls foxes foyer framed friendly
    frown fruit frying fudge fuel fugitive fully fuming fungal furnished fuselage future
    fuzzy gables gadget gags gained galaxy gambit gang gasp gather gauze gave
    gawk gaze gearbox gecko geek gels gemstone general geometry germs gesture getting
    geyser ghetto ghost giant giddy gifts gigantic gills gimmick ginger girth giving
    glass gleeful glide gnaw gnome goat goblet godfather goes goggles going goldfish
    gone goodbye gopher gorilla gossip gotten gourmet governing gown greater grunt guarded
    guest guide gulp gumball guru gusts gutter guys gymnast gypsy gyrate habitat
    hacksaw haggled hairy hamburger happens hashing hatchet haunted having hawk haystack hazard
    hectare hedgehog heels hefty height hemlock hence heron hesitate hexagon hickory hiding
    highway hijack hiker hills himself hinder hippo hire history hitched hive hoax
    hobby hockey hoisting hold honked hookup hope hornet hospital hotel hounded hover
    howls hubcaps huddle huge hull humid hunter hurried husband huts hybrid hydrogen
    hyper iceberg icing icon identity idiom idled idols igloo ignore iguana illness
    imagine imbalance imitate impel inactive inbound incur industrial inexact inflamed ingested initiate
    injury inkling inline inmate innocent inorganic input inquest inroads insult intended inundate
    invoke inwardly ionic irate iris irony irritate island isolated issued italics itches
    items itinerary itself ivory jabbed jackets jaded jagged jailed jamming january jargon
    jaunt javelin jaws jazz jeans jeers jellyfish jeopardy jerseys jester jetting jewels
    jigsaw jingle jittery jive jobs jockey jogger joining joking jolted jostle journal
    joyous jubilee judge juggled juicy jukebox july jump junk jury justice juvenile
    kangaroo karate keep kennel kept kernels kettle keyboard kickoff kidneys king kiosk
    kisses kitchens kiwi knapsack knee knife knowledge knuckle koala laboratory ladder lagoon
    lair lakes lamb language laptop large last later launching lava lawsuit layout
    lazy lectures ledge leech left legion leisure lemon lending leopard lesson lettuce
    lexicon liar library licks lids lied lifestyle light likewise lilac limits linen
    lion lipstick liquid listen lively loaded lobster locker lodge lofty logic loincloth
    long looking lopped lordship losing lottery loudly love lower loyal lucky luggage
    lukewarm lullaby lumber lunar lurk lush luxury lymph lynx lyrics macro madness
    magically mailed major makeup malady mammal maps masterful match maul maverick maximum
    mayor maze meant mechanic medicate meeting megabyte melting memoir menu merger mesh
    metro mews mice midst mighty mime mirror misery mittens mixture moat mobile
    mocked mohawk moisture molten moment money moon mops morsel mostly motherly mouth
    movement mowing much muddy muffin mugged mullet mumble mundane muppet mural musical
    muzzle myriad mystery myth nabbing nagged nail names nanny napkin narrate nasty
    natural nautical navy nearby necklace needed negative neither neon nephew nerves nestle
    network neutral never newt nexus nibs niche niece nifty nightly nimbly nineteen
    nirvana nitrogen nobody nocturnal nodes noises nomad noodles northern nostril noted nouns
    novelty nowhere nozzle nuance nucleus nudged nugget nuisance null number nuns nurse
    nutshell nylon oaks oars oasis oatmeal obedient object obliged obnoxious observant obtains
    obvious occur ocean october odds odometer offend often oilfield ointment okay older
    olive olympics omega omission omnibus onboard oncoming oneself ongoing onion online onslaught
    onto onward oozed opacity opened opposite optical opus orange orbit orchid orders
    organs origin ornament orphans oscar ostrich otherwise otter ouch ought ounce ourselves
    oust outbreak oval oven owed owls owner oxidant oxygen oyster ozone pact
    paddles pager pairing palace pamphlet pancakes paper paradise pastry patio pause pavements
    pawnshop payment peaches pebbles peculiar pedantic peeled pegs pelican pencil people pepper
    perfect pests petals phase pheasants phone phrases physics piano picked pierce pigment
    piloted pimple pinched pioneer pipeline pirate pistons pitched pivot pixels pizza playful
    pledge pliers plotting plus plywood poaching pockets podcast poetry point poker polar
    ponies pool popular portents possible potato pouch poverty powder pram present pride
    problems pruned prying psychic public puck puddle puffin pulp pumpkins punch puppy
    purged push putty puzzled pylons pyramid python queen quick quote rabbits racetrack
    radar rafts rage railway raking rally ramped randomly rapid rarest rash rated
    ravine rays razor react rebel recipe reduce reef refer regular reheat reinvest
    rejoices rekindle relic remedy renting reorder repent request reruns rest return reunion
    revamp rewind rhino rhythm ribbon richly ridges rift rigid rims ringing riots
    ripped rising ritual river roared robot rockets rodent rogue roles romance roomy
    roped roster rotate rounded rover rowboat royal ruby rudely ruffled rugged ruined
    ruling rumble runway rural rustled ruthless sabotage sack sadness safety saga sailor
    sake salads sample sanity sapling sarcasm sash satin saucepan saved sawmill saxophone
    sayings scamper scenic school science scoop scrub scuba seasons second sedan seeded
    segments seismic selfish semifinal sensible september sequence serving session setup seventh sewage
    shackles shelter shipped shocking shrugged shuffled shyness siblings sickness sidekick sieve sifting
    sighting silk simplest sincerely sipped siren situated sixteen sizes skater skew skirting
    skulls skydive slackens sleepless slid slower slug smash smelting smidgen smog smuggled
    snake sneeze sniff snout snug soapy sober soccer soda software soggy soil
    solved somewhere sonic soothe soprano sorry southern sovereign sowed soya space speedy
    sphere spiders splendid spout sprig spud spying square stacking stellar stick stockpile
    strained stunning stylishly subtly succeed suddenly suede suffice sugar suitcase sulking summon
    sunken superior surfer sushi suture swagger swept swiftly sword swung syllabus symptoms
    syndrome syringe system taboo tacit tadpoles tagged tail taken talent tamper tanks
    tapestry tarnished tasked tattoo taunts tavern tawny taxi teardrop technical tedious teeming
    tell template tender tepid tequila terminal testing tether textbook thaw theatrics thirsty
    thorn threaten thumbs thwart ticket tidy tiers tiger tilt timber tinted tipsy
    tirade tissue titans toaster tobacco today toenail toffee together toilet token tolerant
    tomorrow tonic toolbox topic torch tossed total touchy towel toxic toyed trash
    trendy tribal trolling truth trying tsunami tubes tucks tudor tuesday tufts tugs
    tuition tulips tumbling tunnel turnip tusks tutor tuxedo twang tweezers twice twofold
    tycoon typist tyrant ugly ulcers ultimate umbrella umpire unafraid unbending uncle under
    uneven unfit ungainly unhappy union unjustly unknown unlikely unmask unnoticed unopened unplugs
    unquoted unrest unsafe until unusual unveil unwind unzip upbeat upcoming update upgrade
    uphill upkeep upload upon upper upright upstairs uptight upwards urban urchins urgent
    usage useful usher using usual utensils utility utmost utopia uttered vacation vague
    vain value vampire vane vapidly vary vastness vats vaults vector veered vegan
    vehicle vein velvet venomous verification vessel veteran vexed vials vibrate victim video
    viewpoint vigilant viking village vinegar violin vipers virtual visited vitals vivid vixen
    vocal vogue voice volcano vortex voted voucher vowels voyage vulture wade waffle
    wagtail waist waking wallets wanted warped washing water waveform waxing wayside weavers
    website wedge weekday weird welders went wept were western wetsuit whale when
    whipped whole wickets width wield wife wiggle wildly winter wipeout wiring wise
    withdrawn wives wizard wobbly woes woken wolf womanly wonders woozy worry wounded
    woven wrap wrist wrong yacht yahoo yanks yard yawning yearbook yellow yesterday
    yeti yields yodel yoga younger yoyo zapped zeal zebra zero zesty zigzags
    zinger zippers zodiac zombie zones zoom
""".split()

assert len(_BIP39)==2048 and len(_MONERO)==1626

# -- Konstanta ------------------------------------------------------
_L          = 2**252 + 27742317777372353535851937790883648493
_ENC_MASK   = 0x10
_CLEAR_MASK = 0x3F
_COIN_XMR   = 0

# -- Keccak-256 pure Python ------------------------------------------
_KC_RC=[0x0000000000000001,0x0000000000008082,0x800000000000808A,0x8000000080008000,
        0x000000000000808B,0x0000000080000001,0x8000000080008081,0x8000000000008009,
        0x000000000000008A,0x0000000000000088,0x0000000080008009,0x000000008000000A,
        0x000000008000808B,0x800000000000008B,0x8000000000008089,0x8000000000008003,
        0x8000000000008002,0x8000000000000080,0x000000000000800A,0x800000008000000A,
        0x8000000080008081,0x8000000000008080,0x0000000080000001,0x8000000080008008]
_KC_ROT=[[0,36,3,41,18],[1,44,10,45,2],[62,6,43,15,61],[28,55,25,21,56],[27,20,39,8,14]]
_KC_M64=(1<<64)-1

def _kc_f(st):
    for rc in _KC_RC:
        C=[st[x][0]^st[x][1]^st[x][2]^st[x][3]^st[x][4] for x in range(5)]
        D=[C[(x-1)%5]^((C[(x+1)%5]<<1|(C[(x+1)%5]>>63))&_KC_M64) for x in range(5)]
        st=[[st[x][y]^D[x] for y in range(5)] for x in range(5)]
        B=[[0]*5 for _ in range(5)]
        for x in range(5):
            for y in range(5):
                r=_KC_ROT[x][y]; v=st[x][y]
                B[y][(2*x+3*y)%5]=((v<<r)|(v>>(64-r)))&_KC_M64
        st=[[B[x][y]^((~B[(x+1)%5][y])&B[(x+2)%5][y]) for y in range(5)] for x in range(5)]
        st[0][0]^=rc
    return st

def _keccak256(data):
    rate=136; msg=bytearray(data); msg.append(0x01)
    while len(msg)%rate!=0: msg.append(0)
    msg[-1]|=0x80; st=[[0]*5 for _ in range(5)]
    for i in range(0,len(msg),rate):
        blk=msg[i:i+rate]
        for j in range(rate//8):
            x,y=j%5,j//5; st[x][y]^=int.from_bytes(blk[j*8:j*8+8],"little")
        st=_kc_f(st)
    out=b""
    for y in range(5):
        for x in range(5):
            out+=st[x][y].to_bytes(8,"little")
            if len(out)>=32: return out[:32]

# -- Ed25519 scalar multiplication ----------------------------------
_ED_P=2**255-19
_ED_D=-121665*pow(121666,_ED_P-2,_ED_P)%_ED_P

def _ed_add(P,Q):
    X1,Y1,Z1,T1=P; X2,Y2,Z2,T2=Q
    A=(Y1-X1)*(Y2-X2)%_ED_P; B=(Y1+X1)*(Y2+X2)%_ED_P
    C=T1*2*_ED_D*T2%_ED_P; D=Z1*2*Z2%_ED_P
    E=B-A; F=D-C; G=D+C; H=B+A
    return(E*F%_ED_P,G*H%_ED_P,F*G%_ED_P,E*H%_ED_P)

def _ed_smul(k,P):
    R=(0,1,1,0)
    while k:
        if k&1: R=_ed_add(R,P)
        P=_ed_add(P,P); k>>=1
    return R

def _ed_pt2b(P):
    X,Y,Z,_=P; Zi=pow(Z,_ED_P-2,_ED_P)
    x=X*Zi%_ED_P; y=Y*Zi%_ED_P
    b=bytearray(y.to_bytes(32,"little"))
    if x&1: b[31]|=0x80
    return bytes(b)

_Gy=4*pow(5,_ED_P-2,_ED_P)%_ED_P
_Gx2=(_Gy*_Gy-1)*pow(_ED_D*_Gy*_Gy+1,_ED_P-2,_ED_P)%_ED_P
_Gx=pow(_Gx2,(_ED_P+3)//8,_ED_P)
if(_Gx*_Gx-_Gx2)%_ED_P!=0: _Gx=_Gx*pow(2,(_ED_P-1)//4,_ED_P)%_ED_P
if _Gx%2!=0: _Gx=_ED_P-_Gx
_G=(_Gx,_Gy,1,_Gx*_Gy%_ED_P)

# -- Monero key derivation ------------------------------------------
def _sc_reduce32(b):
    return(int.from_bytes(b,"little")%_L).to_bytes(32,"little")

def _xmr_keys(spend_key):
    spend_pub=_ed_pt2b(_ed_smul(int.from_bytes(spend_key,"little"),_G))
    vk_raw=_keccak256(spend_key)
    view_key=(int.from_bytes(vk_raw,"little")%_L).to_bytes(32,"little")
    view_pub=_ed_pt2b(_ed_smul(int.from_bytes(view_key,"little"),_G))
    return spend_pub,view_key,view_pub

# -- Monero Base58 --------------------------------------------------
_XMR_ALPHA=b"123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
_XMR_ENC_SZ=[0,2,3,5,6,7,9,10,11,13]

def _b58_enc_block(data):
    n=int.from_bytes(data,"big"); sz=_XMR_ENC_SZ[len(data)]
    out=[]
    for _ in range(sz): out.append(_XMR_ALPHA[n%58]); n//=58
    return bytes(reversed(out))

def _xmr_base58(data):
    full,rem=divmod(len(data),8); res=b""
    for i in range(full): res+=_b58_enc_block(data[i*8:i*8+8])
    if rem: res+=_b58_enc_block(data[full*8:])
    return res.decode()

def _xmr_address(spend_pub,view_pub):
    payload=bytes([0x12])+spend_pub+view_pub
    return _xmr_base58(payload+_keccak256(payload)[:4])

# -- Monero 25-kata encoding ----------------------------------------
def _xmr_encode25(spend_key):
    N=len(_MONERO); idxs=[]
    for i in range(8):
        x=struct.unpack("<I",spend_key[i*4:i*4+4])[0]
        w1=x%N; w2=(x//N+w1)%N; w3=(x//N//N+w2)%N
        idxs+=[w1,w2,w3]
    pfx=''.join(_MONERO[i][:3] for i in idxs)
    crc=binascii.crc32(pfx.encode())&0xFFFFFFFF
    idxs.append(idxs[crc%24])
    return " ".join(_MONERO[i] for i in idxs)  # 1 baris siap copy-paste

def _xmr_verify25(seed25):
    lu={w:i for i,w in enumerate(_MONERO)}
    ws=seed25.strip().split()
    if len(ws)!=25: return False
    if any(w not in lu for w in ws): return False
    idxs=[lu[w] for w in ws[:24]]
    pfx=''.join(_MONERO[i][:3] for i in idxs)
    crc=binascii.crc32(pfx.encode())&0xFFFFFFFF
    return lu[ws[24]]==idxs[crc%24]

# -- Polyseed engine ------------------------------------------------

# GF(2048) untuk hitung checksum polyseed
# ElemMul2: kalikan elemen dengan 2 di GF(2048)
# MUL2_TABLE dari spec polyseed (irred. poly x^11+x^10+x^9+x+1)
_GF_MUL2_TABLE = [5,7,1,3,13,15,9,11]

def _gf_mul2(x):
    if x < 1024: return 2*x
    return _GF_MUL2_TABLE[x%8] + 16*((x-1024)//8)

def _gf_poly_eval(coeffs):
    """Evaluasi polynomial di x=2 (Horner's method) → checksum."""
    r = coeffs[15]
    for i in range(14,-1,-1):
        r = _gf_mul2(r) ^ coeffs[i]
    return r

def _data_to_poly(secret, birthday, features):
    """
    DataToPoly: port dari polyseed_data_to_poly (gf.c).
    secret   : 19 bytes
    birthday : 10-bit int
    features : 5-bit int
    Returns  : list 16 koefisien (coeffs[0]=0, diisi checksum setelahnya)
    """
    extra_val  = (features << 10) | birthday
    extra_bits = 15   # 5 feature + 10 birthday
    wb = wv = 0
    si = 0; sv = secret[0]; sb = 8; rem = 150-8
    coeffs = [0]*16
    for i in range(15):   # 15 data words → coeffs[1..15]
        while wb < 10:
            if sb == 0:
                si += 1; sb = min(rem,8); sv = secret[si]; rem -= sb
            ch = min(sb, 10-wb)
            sb -= ch; wb += ch
            wv = (wv<<ch) | ((sv>>sb)&((1<<ch)-1))
        wv = (wv<<1)
        extra_bits -= 1
        wv |= (extra_val>>extra_bits)&1
        coeffs[1+i] = wv
        wv = wb = 0
    coeffs[0] = _gf_poly_eval(coeffs)   # hitung checksum
    return coeffs

# Konstanta birthday
_EPOCH     = 1635768000   # Nov 2021
_TIME_STEP = 2629746      # ~1 bulan
_DATE_MASK = 0x3FF        # 10 bit

def _birthday_encode(ts):
    """Unix timestamp → 10-bit birthday."""
    if ts < _EPOCH: return 0
    return ((ts - _EPOCH) // _TIME_STEP) & _DATE_MASK

def polyseed_generate(passphrase=""):
    """
    Generate Polyseed 16 kata baru secara acak.
    Jika passphrase diberikan, seed akan dienkripsi.
    Returns dict: mnemonic, address, spend_key, view_key, seed25.
    """
    import time, secrets as _sec
    # 1. Generate 19 byte entropy acak
    entropy = bytearray(_sec.token_bytes(19))
    entropy[18] &= _CLEAR_MASK   # clear 2 MSB

    # 2. Hitung birthday dari waktu sekarang
    birthday = _birthday_encode(int(time.time()))

    # 3. Features: 0 (tidak terenkripsi) atau _ENC_MASK jika ada passphrase
    features = _ENC_MASK if passphrase else 0

    # 4. Enkripsi entropy jika ada passphrase
    sec_plain = bytes(entropy)
    if passphrase:
        pp   = unicodedata.normalize("NFKD", passphrase).encode("utf-8")
        salt = b"POLYSEED mask" + bytes([0x00,0xFF,0xFF])
        mask = hashlib.pbkdf2_hmac("sha256", pp, salt, 10000, dklen=32)
        enc  = bytearray(sec_plain)
        for i in range(19): enc[i] ^= mask[i]
        enc[18] &= _CLEAR_MASK
        sec_enc = bytes(enc)
    else:
        sec_enc = sec_plain

    # 5. DataToPoly → 16 koefisien (termasuk checksum GF)
    coeffs = _data_to_poly(sec_enc, birthday, features)

    # 6. Coin XOR untuk Monero (coin=0, no-op)
    coeffs[1] ^= _COIN_XMR

    # 7. Map koefisien → kata BIP39
    mnemonic = " ".join(_BIP39[c] for c in coeffs)

    # 8. Derive wallet dari secret plain (tanpa enkripsi)
    feat_dec = features ^ _ENC_MASK if passphrase else features
    spend_key = _poly_kdf(sec_plain, feat_dec, birthday)
    spend_pub, view_key, view_pub = _xmr_keys(spend_key)

    return dict(
        mnemonic  = mnemonic,
        spend_key = spend_key.hex(),
        spend_pub = spend_pub.hex(),
        view_key  = view_key.hex(),
        view_pub  = view_pub.hex(),
        address   = _xmr_address(spend_pub, view_pub),
        seed25    = _xmr_encode25(spend_key),
        birthday  = birthday,
        encrypted      = bool(passphrase),
        has_passphrase = bool(passphrase),
    )

def _poly_parse(mnemonic):
    words=unicodedata.normalize("NFC",mnemonic.strip().lower()).split()
    if len(words)!=16:
        raise ValueError(f"Polyseed butuh 16 kata, ditemukan {len(words)}")
    lu={w:i for i,w in enumerate(_BIP39)}
    out=[]
    for w in words:
        if w in lu: out.append(lu[w])
        else:
            c=[v for k,v in lu.items() if k.startswith(w[:4])]
            if len(c)==1: out.append(c[0])
            elif not c:   raise ValueError(f'Kata tidak dikenali: "{w}"')
            else:         raise ValueError(f'Kata ambigu "{w[:4]}": "{w}"')
    out[1]^=_COIN_XMR
    return out

def _poly_to_data(coeffs):
    secret=bytearray(19); si=sb=ev=0
    for i in range(1,16):
        wv=coeffs[i]; ev=(ev<<1)|(wv&1); wv>>=1; wb=10
        while wb>0:
            if sb==8: si+=1; sb=0
            ch=min(wb,8-sb); wb-=ch
            if ch<8: secret[si]<<=ch
            secret[si]|=(wv>>wb)&((1<<ch)-1); sb+=ch
    return bytes(secret),ev&0x3FF,ev>>10

def _poly_decrypt(secret,features,passphrase):
    if not(features&_ENC_MASK): return secret,features
    pp=unicodedata.normalize("NFKD",passphrase).encode("utf-8")
    salt_mask=b"POLYSEED mask" + bytes([0x00,0xFF,0xFF])
    mask=hashlib.pbkdf2_hmac("sha256",pp,salt_mask,10000,dklen=32)
    dec=bytearray(secret)
    for i in range(19): dec[i]^=mask[i]
    dec[18]&=_CLEAR_MASK
    return bytes(dec),features^_ENC_MASK

def _poly_kdf(secret,features,birthday):
    salt_kdf=b"POLYSEED key" + bytes([0x00,0xFF,0xFF,0xFF])
    salt=bytearray(32)
    salt[0:16]=salt_kdf
    struct.pack_into("<I",salt,16,_COIN_XMR)
    struct.pack_into("<I",salt,20,birthday)
    struct.pack_into("<I",salt,24,features)
    pw=secret+bytes(13)
    raw=hashlib.pbkdf2_hmac("sha256",pw,bytes(salt),10000,dklen=32)
    return _sc_reduce32(raw)

def polyseed_convert(mnemonic,passphrase=""):
    coeffs=_poly_parse(mnemonic)
    sec_enc,bday,feat_enc=_poly_to_data(coeffs)
    sec_dec,feat_dec=_poly_decrypt(sec_enc,feat_enc,passphrase)
    spend_key=_poly_kdf(sec_dec,feat_dec,bday)
    spend_pub,view_key,view_pub=_xmr_keys(spend_key)
    return dict(
        spend_key = spend_key.hex(),
        spend_pub = spend_pub.hex(),
        view_key  = view_key.hex(),
        view_pub  = view_pub.hex(),
        address   = _xmr_address(spend_pub,view_pub),
        seed25    = _xmr_encode25(spend_key),
        birthday       = bday,
        encrypted      = bool(feat_enc&_ENC_MASK),
        has_passphrase = bool(passphrase),
    )

# -- Self-test -------------------------------------------------------
def _selftest():
    assert _keccak256(b"").hex()=="c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470","Keccak256 gagal"
    assert _sc_reduce32(_L.to_bytes(32,"little"))==(0).to_bytes(32,"little"),"sc_reduce32 gagal"
    TV_MN="town push core dog update labor cave pyramid next embark plunge real piano mother avoid grace"
    TV_PP="test"
    TV_AD="47hvNJyLzLj9H3TDpBMeRi4rSsYcMtyZadG1mPx5mCzK86mWpyZKFtHMiKmwNbNtWo1P7EboJ7XwF2JaPNNFgyz65XzbKEC"
    r=polyseed_convert(TV_MN,TV_PP)
    assert r["address"]==TV_AD,f"Address mismatch: {r['address']}"
    assert _xmr_verify25(r["seed25"]),"Checksum 25-kata gagal"
    print("  [OK] Keccak256")
    print("  [OK] sc_reduce32")
    print("  [OK] Polyseed test vector (Cake Wallet, passphrase=test)")
    print("  [OK] Monero 25-kata checksum")

# -- Main -----------------------------------------------------------
def _input_passphrase(label="Masukkan passphrase (Enter jika tidak ada):"):
    print(f"\n{label}")
    try:    pp=getpass.getpass("  Passphrase: ")
    except: pp=input("  Passphrase: ")
    if pp:
        try:    pp2=getpass.getpass("  Konfirmasi : ")
        except: pp2=input("  Konfirmasi : ")
        if pp!=pp2: print("\n✗ Passphrase tidak cocok."); return None
        print("  ✓ Dikonfirmasi")
    else:
        print("  (Tanpa passphrase)")
    return pp

def _print_result(r, title="HASIL"):
    sk=r["spend_key"]
    print()
    print("="*62)
    print(f"  {title}")
    print("="*62)
    print(f"\n  Polyseed 16-kata:")
    if "mnemonic" in r:
        print(f"  {r['mnemonic']}")
    print(f"\n  Spend Key (hex):")
    print(f"  {sk[:32]}")
    print(f"  {sk[32:]}")
    print(f"\n  Monero 25-kata Seed:")
    print(f"  {r['seed25']}")
    print(f"\n  Primary Address:")
    print(f"  {r['address']}")
    print(f"\n  View Key : {r['view_key']}")
    enc  = r.get('encrypted', False)
    happ = r.get('has_passphrase', enc)
    print(f"  Birthday : {r['birthday']}   |   Seed encrypted: {enc}   |   Passphrase used: {happ}")
    print()

def _save_result(r):
    try:    ans=input("Simpan ke ~/polyseed_result.txt? [y/N] ").strip().lower()
    except: ans="n"
    if ans!="y": return
    sk=r["spend_key"]
    out=os.path.expanduser("~/polyseed_result.txt")
    with open(out,"w") as f:
        f.write("=== polyseed.py result ===\n\n")
        if "mnemonic" in r:
            f.write(f"Polyseed 16-kata:\n{r['mnemonic']}\n\n")
        f.write(f"Spend Key:\n{sk[:32]}\n{sk[32:]}\n\n")
        f.write(f"Monero 25-kata Seed:\n{r['seed25']}\n\n")
        f.write(f"Primary Address:\n{r['address']}\n\n")
        f.write(f"View Key: {r['view_key']}\n")
    print(f"  ✓ Disimpan: {out}")
    print("  ⚠  Hapus file ini setelah mencatat!")

def _do_generate():
    """Menu: Generate Polyseed baru."""
    pp=_input_passphrase("Passphrase untuk enkripsi seed (Enter jika tidak ada):")
    if pp is None: return
    print("\nMembuat Polyseed baru...")
    r=polyseed_generate(pp)
    _print_result(r, "POLYSEED BARU")
    print("⚠  Catat 16 kata di atas di tempat yang aman!")
    print("⚠  Import ke Cake Wallet untuk verifikasi address.\n")
    _save_result(r)

def _do_convert():
    """Menu: Konversi Polyseed → Monero 25-kata."""
    print("\nMasukkan 16 kata Polyseed (satu baris, pisah spasi):")
    try:    mnemonic=input("> ").strip()
    except(EOFError,KeyboardInterrupt): print("\nDibatalkan."); return
    pp=_input_passphrase()
    if pp is None: return
    print("\nMemproses...")
    try:
        r=polyseed_convert(mnemonic,pp)
    except ValueError as e:
        print(f"\n✗ ERROR: {e}"); return
    except Exception:
        import traceback; traceback.print_exc(); return
    r["mnemonic"]=mnemonic
    _print_result(r, "HASIL KONVERSI")
    print("-"*62)
    print("  VERIFIKASI ADDRESS")
    print("-"*62)
    print("\n  Tempel primary address dari Cake Wallet Anda:")
    print("  (Enter untuk lewati)")
    try:    known=input("  Address: ").strip()
    except: known=""
    if not known:
        print("\n  Dilewati. Pastikan address cocok sebelum menggunakan")
        print("  seed 25-kata ini sebagai backup permanen.")
    elif known==r["address"]:
        print("\n  ✓ COCOK -- konversi berhasil!")
        print("    Seed 25-kata di atas adalah backup yang valid.")
    else:
        print("\n  ✗ TIDAK COCOK")
        print(f"    Dihasilkan : {r['address']}")
        print(f"    Dari wallet: {known}")
        print("\n    Kemungkinan: passphrase salah atau wallet berbeda.")
        print("    JANGAN gunakan seed 25-kata ini sebagai backup!")
    print()
    _save_result(r)

def main():
    print("="*62)
    print("  Polyseed Tool")
    print("  Pure Python stdlib | Zero dependency | Air-gap safe")
    print("="*62)
    print()
    print("Menjalankan self-test...")
    try:
        _selftest()
    except AssertionError as e:
        print(f"  [FAIL] {e}"); sys.exit(1)
    print()
    while True:
        print("Pilih aksi:")
        print("  1. Generate Polyseed 16-kata baru")
        print("  2. Konversi Polyseed 16-kata → Monero 25-kata")
        print("  3. Keluar")
        try:    choice=input("> ").strip()
        except(EOFError,KeyboardInterrupt): print("\nKeluar."); break
        if choice=="1":   _do_generate()
        elif choice=="2": _do_convert()
        elif choice=="3": print("Keluar."); break
        else: print("  Pilihan tidak valid.")

if __name__=="__main__":
    main()
