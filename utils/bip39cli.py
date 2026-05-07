#!/usr/bin/env python3
"""
bip39cli.py - BIP39/Monero Mnemonic Tool
Zero-dependency, Python 3 stdlib only.
Runs interactively (no args) or via CLI arguments.

Usage:
  python3 bip39cli.py                         # interactive mode
  python3 bip39cli.py generate [12|15|18|21|24]
  python3 bip39cli.py generate --xmr
  python3 bip39cli.py validate "<mnemonic>"
  python3 bip39cli.py info "<mnemonic>" [passphrase]
  python3 bip39cli.py derive "<mnemonic>" [passphrase] [--coin btc|eth|bnb|sol|xmr] [--count N] [--mode all|taproot|segwit|wrapped|legacy]
  python3 bip39cli.py monero "<bip39>" [bip39_passphrase] [--passphrase "<monero_offset>"]
"""
import sys, hashlib, hmac as _hmac, struct, unicodedata, secrets, binascii

# ── wordlists ────────────────────────────────────────────
_BIP39  = "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add addict address adjust admit adult advance advice aerobic affair afford afraid again age agent agree ahead aim air airport aisle alarm album alcohol alert alien all alley allow almost alone alpha already also alter always amateur amazing among amount amused analyst anchor ancient anger angle angry animal ankle announce annual another answer antenna antique anxiety any apart apology appear apple approve april arch arctic area arena argue arm armed armor army around arrange arrest arrive arrow art artefact artist artwork ask aspect assault asset assist assume asthma athlete atom attack attend attitude attract auction audit august aunt author auto autumn average avocado avoid awake aware away awesome awful awkward axis baby bachelor bacon badge bag balance balcony ball bamboo banana banner bar barely bargain barrel base basic basket battle beach bean beauty because become beef before begin behave behind believe below belt bench benefit best betray better between beyond bicycle bid bike bind biology bird birth bitter black blade blame blanket blast bleak bless blind blood blossom blouse blue blur blush board boat body boil bomb bone bonus book boost border boring borrow boss bottom bounce box boy bracket brain brand brass brave bread breeze brick bridge brief bright bring brisk broccoli broken bronze broom brother brown brush bubble buddy budget buffalo build bulb bulk bullet bundle bunker burden burger burst bus business busy butter buyer buzz cabbage cabin cable cactus cage cake call calm camera camp can canal cancel candy cannon canoe canvas canyon capable capital captain car carbon card cargo carpet carry cart case cash casino castle casual cat catalog catch category cattle caught cause caution cave ceiling celery cement census century cereal certain chair chalk champion change chaos chapter charge chase chat cheap check cheese chef cherry chest chicken chief child chimney choice choose chronic chuckle chunk churn cigar cinnamon circle citizen city civil claim clap clarify claw clay clean clerk clever click client cliff climb clinic clip clock clog close cloth cloud clown club clump cluster clutch coach coast coconut code coffee coil coin collect color column combine come comfort comic common company concert conduct confirm congress connect consider control convince cook cool copper copy coral core corn correct cost cotton couch country couple course cousin cover coyote crack cradle craft cram crane crash crater crawl crazy cream credit creek crew cricket crime crisp critic crop cross crouch crowd crucial cruel cruise crumble crunch crush cry crystal cube culture cup cupboard curious current curtain curve cushion custom cute cycle dad damage damp dance danger daring dash daughter dawn day deal debate debris decade december decide decline decorate decrease deer defense define defy degree delay deliver demand demise denial dentist deny depart depend deposit depth deputy derive describe desert design desk despair destroy detail detect develop device devote diagram dial diamond diary dice diesel diet differ digital dignity dilemma dinner dinosaur direct dirt disagree discover disease dish dismiss disorder display distance divert divide divorce dizzy doctor document dog doll dolphin domain donate donkey donor door dose double dove draft dragon drama drastic draw dream dress drift drill drink drip drive drop drum dry duck dumb dune during dust dutch duty dwarf dynamic eager eagle early earn earth easily east easy echo ecology economy edge edit educate effort egg eight either elbow elder electric elegant element elephant elevator elite else embark embody embrace emerge emotion employ empower empty enable enact end endless endorse enemy energy enforce engage engine enhance enjoy enlist enough enrich enroll ensure enter entire entry envelope episode equal equip era erase erode erosion error erupt escape essay essence estate eternal ethics evidence evil evoke evolve exact example excess exchange excite exclude excuse execute exercise exhaust exhibit exile exist exit exotic expand expect expire explain expose express extend extra eye eyebrow fabric face faculty fade faint faith fall false fame family famous fan fancy fantasy farm fashion fat fatal father fatigue fault favorite feature february federal fee feed feel female fence festival fetch fever few fiber fiction field figure file film filter final find fine finger finish fire firm first fiscal fish fit fitness fix flag flame flash flat flavor flee flight flip float flock floor flower fluid flush fly foam focus fog foil fold follow food foot force forest forget fork fortune forum forward fossil foster found fox fragile frame frequent fresh friend fringe frog front frost frown frozen fruit fuel fun funny furnace fury future gadget gain galaxy gallery game gap garage garbage garden garlic garment gas gasp gate gather gauge gaze general genius genre gentle genuine gesture ghost giant gift giggle ginger giraffe girl give glad glance glare glass glide glimpse globe gloom glory glove glow glue goat goddess gold good goose gorilla gospel gossip govern gown grab grace grain grant grape grass gravity great green grid grief grit grocery group grow grunt guard guess guide guilt guitar gun gym habit hair half hammer hamster hand happy harbor hard harsh harvest hat have hawk hazard head health heart heavy hedgehog height hello helmet help hen hero hidden high hill hint hip hire history hobby hockey hold hole holiday hollow home honey hood hope horn horror horse hospital host hotel hour hover hub huge human humble humor hundred hungry hunt hurdle hurry hurt husband hybrid ice icon idea identify idle ignore ill illegal illness image imitate immense immune impact impose improve impulse inch include income increase index indicate indoor industry infant inflict inform inhale inherit initial inject injury inmate inner innocent input inquiry insane insect inside inspire install intact interest into invest invite involve iron island isolate issue item ivory jacket jaguar jar jazz jealous jeans jelly jewel job join joke journey joy judge juice jump jungle junior junk just kangaroo keen keep ketchup key kick kid kidney kind kingdom kiss kit kitchen kite kitten kiwi knee knife knock know lab label labor ladder lady lake lamp language laptop large later latin laugh laundry lava law lawn lawsuit layer lazy leader leaf learn leave lecture left leg legal legend leisure lemon lend length lens leopard lesson letter level liar liberty library license life lift light like limb limit link lion liquid list little live lizard load loan lobster local lock logic lonely long loop lottery loud lounge love loyal lucky luggage lumber lunar lunch luxury lyrics machine mad magic magnet maid mail main major make mammal man manage mandate mango mansion manual maple marble march margin marine market marriage mask mass master match material math matrix matter maximum maze meadow mean measure meat mechanic medal media melody melt member memory mention menu mercy merge merit merry mesh message metal method middle midnight milk million mimic mind minimum minor minute miracle mirror misery miss mistake mix mixed mixture mobile model modify mom moment monitor monkey monster month moon moral more morning mosquito mother motion motor mountain mouse move movie much muffin mule multiply muscle museum mushroom music must mutual myself mystery myth naive name napkin narrow nasty nation nature near neck need negative neglect neither nephew nerve nest net network neutral never news next nice night noble noise nominee noodle normal north nose notable note nothing notice novel now nuclear number nurse nut oak obey object oblige obscure observe obtain obvious occur ocean october odor off offer office often oil okay old olive olympic omit once one onion online only open opera opinion oppose option orange orbit orchard order ordinary organ orient original orphan ostrich other outdoor outer output outside oval oven over own owner oxygen oyster ozone pact paddle page pair palace palm panda panel panic panther paper parade parent park parrot party pass patch path patient patrol pattern pause pave payment peace peanut pear peasant pelican pen penalty pencil people pepper perfect permit person pet phone photo phrase physical piano picnic picture piece pig pigeon pill pilot pink pioneer pipe pistol pitch pizza place planet plastic plate play please pledge pluck plug plunge poem poet point polar pole police pond pony pool popular portion position possible post potato pottery poverty powder power practice praise predict prefer prepare present pretty prevent price pride primary print priority prison private prize problem process produce profit program project promote proof property prosper protect proud provide public pudding pull pulp pulse pumpkin punch pupil puppy purchase purity purpose purse push put puzzle pyramid quality quantum quarter question quick quit quiz quote rabbit raccoon race rack radar radio rail rain raise rally ramp ranch random range rapid rare rate rather raven raw razor ready real reason rebel rebuild recall receive recipe record recycle reduce reflect reform refuse region regret regular reject relax release relief rely remain remember remind remove render renew rent reopen repair repeat replace report require rescue resemble resist resource response result retire retreat return reunion reveal review reward rhythm rib ribbon rice rich ride ridge rifle right rigid ring riot ripple risk ritual rival river road roast robot robust rocket romance roof rookie room rose rotate rough round route royal rubber rude rug rule run runway rural sad saddle sadness safe sail salad salmon salon salt salute same sample sand satisfy satoshi sauce sausage save say scale scan scare scatter scene scheme school science scissors scorpion scout scrap screen script scrub sea search season seat second secret section security seed seek segment select sell seminar senior sense sentence series service session settle setup seven shadow shaft shallow share shed shell sheriff shield shift shine ship shiver shock shoe shoot shop short shoulder shove shrimp shrug shuffle shy sibling sick side siege sight sign silent silk silly silver similar simple since sing siren sister situate six size skate sketch ski skill skin skirt skull slab slam sleep slender slice slide slight slim slogan slot slow slush small smart smile smoke smooth snack snake snap sniff snow soap soccer social sock soda soft solar soldier solid solution solve someone song soon sorry sort soul sound soup source south space spare spatial spawn speak special speed spell spend sphere spice spider spike spin spirit split spoil sponsor spoon sport spot spray spread spring spy square squeeze squirrel stable stadium staff stage stairs stamp stand start state stay steak steel stem step stereo stick still sting stock stomach stone stool story stove strategy street strike strong struggle student stuff stumble style subject submit subway success such sudden suffer sugar suggest suit summer sun sunny sunset super supply supreme sure surface surge surprise surround survey suspect sustain swallow swamp swap swarm swear sweet swift swim swing switch sword symbol symptom syrup system table tackle tag tail talent talk tank tape target task taste tattoo taxi teach team tell ten tenant tennis tent term test text thank that theme then theory there they thing this thought three thrive throw thumb thunder ticket tide tiger tilt timber time tiny tip tired tissue title toast tobacco today toddler toe together toilet token tomato tomorrow tone tongue tonight tool tooth top topic topple torch tornado tortoise toss total tourist toward tower town toy track trade traffic tragic train transfer trap trash travel tray treat tree trend trial tribe trick trigger trim trip trophy trouble truck true truly trumpet trust truth try tube tuition tumble tuna tunnel turkey turn turtle twelve twenty twice twin twist two type typical ugly umbrella unable unaware uncle uncover under undo unfair unfold unhappy uniform unique unit universe unknown unlock until unusual unveil update upgrade uphold upon upper upset urban urge usage use used useful useless usual utility vacant vacuum vague valid valley valve van vanish vapor various vast vault vehicle velvet vendor venture venue verb verify version very vessel veteran viable vibrant vicious victory video view village vintage violin virtual virus visa visit visual vital vivid vocal voice void volcano volume vote voyage wage wagon wait walk wall walnut want warfare warm warrior wash wasp waste water wave way wealth weapon wear weasel weather web wedding weekend weird welcome west wet whale what wheat wheel when where whip whisper wide width wife wild will win window wine wing wink winner winter wire wisdom wise wish witness wolf woman wonder wood wool word work world worry worth wrap wreck wrestle wrist write wrong yard year yellow you young youth zebra zero zone zoo".split()
_MONERO = "abbey abducts ability ablaze abnormal abort abrasive absorb abyss academy aces aching acidic acoustic acquire across actress acumen adapt addicted adept adhesive adjust adopt adrenalin adult adventure aerial afar affair afield afloat afoot afraid after against agenda aggravate agile aglow agnostic agony agreed ahead aided ailments aimless airport aisle ajar akin alarms album alchemy alerts algebra alkaline alley almost aloof alpine already also altitude alumni always amaze ambush amended amidst ammo amnesty among amply amused anchor android anecdote angled ankle annoyed answers antics anvil anxiety anybody apart apex aphid aplomb apology apply apricot aptitude aquarium arbitrary archer ardent arena argue arises army around arrow arsenic artistic ascend ashtray aside asked asleep aspire assorted asylum athlete atlas atom atrium attire auburn auctions audio august aunt austere autumn avatar avidly avoid awakened awesome awful awkward awning awoken axes axis axle aztec azure baby bacon badge baffles bagpipe bailed bakery balding bamboo banjo baptism basin batch bawled bays because beer befit begun behind being below bemused benches berries bested betting bevel beware beyond bias bicycle bids bifocals biggest bikini bimonthly binocular biology biplane birth biscuit bite biweekly blender blip bluntly boat bobsled bodies bogeys boil boldly bomb border boss both bounced bovine bowling boxes boyfriend broken brunt bubble buckets budget buffet bugs building bulb bumper bunch business butter buying buzzer bygones byline bypass cabin cactus cadets cafe cage cajun cake calamity camp candy casket catch cause cavernous cease cedar ceiling cell cement cent certain chlorine chrome cider cigar cinema circle cistern citadel civilian claim click clue coal cobra cocoa code coexist coffee cogs cohesive coils colony comb cool copy corrode costume cottage cousin cowl criminal cube cucumber cuddled cuffs cuisine cunning cupcake custom cycling cylinder cynical dabbing dads daft dagger daily damp dangerous dapper darted dash dating dauntless dawn daytime dazed debut decay dedicated deepest deftly degrees dehydrate deity dejected delayed demonstrate dented deodorant depth desk devoid dewdrop dexterity dialect dice diet different digit dilute dime dinner diode diplomat directed distance ditch divers dizzy doctor dodge does dogs doing dolphin domestic donuts doorway dormant dosage dotted double dove down dozen dreams drinks drowning drunk drying dual dubbed duckling dude duets duke dullness dummy dunes duplex duration dusted duties dwarf dwelt dwindling dying dynamite dyslexic each eagle earth easy eating eavesdrop eccentric echo eclipse economics ecstatic eden edgy edited educated eels efficient eggs egotistic eight either eject elapse elbow eldest eleven elite elope else eluded emails ember emerge emit emotion empty emulate energy enforce enhanced enigma enjoy enlist enmity enough enraged ensign entrance envy epoxy equip erase erected erosion error eskimos espionage essential estate etched eternal ethics etiquette evaluate evenings evicted evolved examine excess exhale exit exotic exquisite extra exult fabrics factual fading fainted faked fall family fancy farming fatal faulty fawns faxed fazed feast february federal feel feline females fences ferry festival fetches fever fewest fiat fibula fictional fidget fierce fifteen fight films firm fishing fitting five fixate fizzle fleet flippant flying foamy focus foes foggy foiled folding fonts foolish fossil fountain fowls foxes foyer framed friendly frown fruit frying fudge fuel fugitive fully fuming fungal furnished fuselage future fuzzy gables gadget gags gained galaxy gambit gang gasp gather gauze gave gawk gaze gearbox gecko geek gels gemstone general geometry germs gesture getting geyser ghetto ghost giant giddy gifts gigantic gills gimmick ginger girth giving glass gleeful glide gnaw gnome goat goblet godfather goes goggles going goldfish gone goodbye gopher gorilla gossip gotten gourmet governing gown greater grunt guarded guest guide gulp gumball guru gusts gutter guys gymnast gypsy gyrate habitat hacksaw haggled hairy hamburger happens hashing hatchet haunted having hawk haystack hazard hectare hedgehog heels hefty height hemlock hence heron hesitate hexagon hickory hiding highway hijack hiker hills himself hinder hippo hire history hitched hive hoax hobby hockey hoisting hold honked hookup hope hornet hospital hotel hounded hover howls hubcaps huddle huge hull humid hunter hurried husband huts hybrid hydrogen hyper iceberg icing icon identity idiom idled idols igloo ignore iguana illness imagine imbalance imitate impel inactive inbound incur industrial inexact inflamed ingested initiate injury inkling inline inmate innocent inorganic input inquest inroads insult intended inundate invoke inwardly ionic irate iris irony irritate island isolated issued italics itches items itinerary itself ivory jabbed jackets jaded jagged jailed jamming january jargon jaunt javelin jaws jazz jeans jeers jellyfish jeopardy jerseys jester jetting jewels jigsaw jingle jittery jive jobs jockey jogger joining joking jolted jostle journal joyous jubilee judge juggled juicy jukebox july jump junk jury justice juvenile kangaroo karate keep kennel kept kernels kettle keyboard kickoff kidneys king kiosk kisses kitchens kiwi knapsack knee knife knowledge knuckle koala laboratory ladder lagoon lair lakes lamb language laptop large last later launching lava lawsuit layout lazy lectures ledge leech left legion leisure lemon lending leopard lesson lettuce lexicon liar library licks lids lied lifestyle light likewise lilac limits linen lion lipstick liquid listen lively loaded lobster locker lodge lofty logic loincloth long looking lopped lordship losing lottery loudly love lower loyal lucky luggage lukewarm lullaby lumber lunar lurk lush luxury lymph lynx lyrics macro madness magically mailed major makeup malady mammal maps masterful match maul maverick maximum mayor maze meant mechanic medicate meeting megabyte melting memoir menu merger mesh metro mews mice midst mighty mime mirror misery mittens mixture moat mobile mocked mohawk moisture molten moment money moon mops morsel mostly motherly mouth movement mowing much muddy muffin mugged mullet mumble mundane muppet mural musical muzzle myriad mystery myth nabbing nagged nail names nanny napkin narrate nasty natural nautical navy nearby necklace needed negative neither neon nephew nerves nestle network neutral never newt nexus nibs niche niece nifty nightly nimbly nineteen nirvana nitrogen nobody nocturnal nodes noises nomad noodles northern nostril noted nouns novelty nowhere nozzle nuance nucleus nudged nugget nuisance null number nuns nurse nutshell nylon oaks oars oasis oatmeal obedient object obliged obnoxious observant obtains obvious occur ocean october odds odometer offend often oilfield ointment okay older olive olympics omega omission omnibus onboard oncoming oneself ongoing onion online onslaught onto onward oozed opacity opened opposite optical opus orange orbit orchid orders organs origin ornament orphans oscar ostrich otherwise otter ouch ought ounce ourselves oust outbreak oval oven owed owls owner oxidant oxygen oyster ozone pact paddles pager pairing palace pamphlet pancakes paper paradise pastry patio pause pavements pawnshop payment peaches pebbles peculiar pedantic peeled pegs pelican pencil people pepper perfect pests petals phase pheasants phone phrases physics piano picked pierce pigment piloted pimple pinched pioneer pipeline pirate pistons pitched pivot pixels pizza playful pledge pliers plotting plus plywood poaching pockets podcast poetry point poker polar ponies pool popular portents possible potato pouch poverty powder pram present pride problems pruned prying psychic public puck puddle puffin pulp pumpkins punch puppy purged push putty puzzled pylons pyramid python queen quick quote rabbits racetrack radar rafts rage railway raking rally ramped randomly rapid rarest rash rated ravine rays razor react rebel recipe reduce reef refer regular reheat reinvest rejoices rekindle relic remedy renting reorder repent request reruns rest return reunion revamp rewind rhino rhythm ribbon richly ridges rift rigid rims ringing riots ripped rising ritual river roared robot rockets rodent rogue roles romance roomy roped roster rotate rounded rover rowboat royal ruby rudely ruffled rugged ruined ruling rumble runway rural rustled ruthless sabotage sack sadness safety saga sailor sake salads sample sanity sapling sarcasm sash satin saucepan saved sawmill saxophone sayings scamper scenic school science scoop scrub scuba seasons second sedan seeded segments seismic selfish semifinal sensible september sequence serving session setup seventh sewage shackles shelter shipped shocking shrugged shuffled shyness siblings sickness sidekick sieve sifting sighting silk simplest sincerely sipped siren situated sixteen sizes skater skew skirting skulls skydive slackens sleepless slid slower slug smash smelting smidgen smog smuggled snake sneeze sniff snout snug soapy sober soccer soda software soggy soil solved somewhere sonic soothe soprano sorry southern sovereign sowed soya space speedy sphere spiders splendid spout sprig spud spying square stacking stellar stick stockpile strained stunning stylishly subtly succeed suddenly suede suffice sugar suitcase sulking summon sunken superior surfer sushi suture swagger swept swiftly sword swung syllabus symptoms syndrome syringe system taboo tacit tadpoles tagged tail taken talent tamper tanks tapestry tarnished tasked tattoo taunts tavern tawny taxi teardrop technical tedious teeming tell template tender tepid tequila terminal testing tether textbook thaw theatrics thirsty thorn threaten thumbs thwart ticket tidy tiers tiger tilt timber tinted tipsy tirade tissue titans toaster tobacco today toenail toffee together toilet token tolerant tomorrow tonic toolbox topic torch tossed total touchy towel toxic toyed trash trendy tribal trolling truth trying tsunami tubes tucks tudor tuesday tufts tugs tuition tulips tumbling tunnel turnip tusks tutor tuxedo twang tweezers twice twofold tycoon typist tyrant ugly ulcers ultimate umbrella umpire unafraid unbending uncle under uneven unfit ungainly unhappy union unjustly unknown unlikely unmask unnoticed unopened unplugs unquoted unrest unsafe until unusual unveil unwind unzip upbeat upcoming update upgrade uphill upkeep upload upon upper upright upstairs uptight upwards urban urchins urgent usage useful usher using usual utensils utility utmost utopia uttered vacation vague vain value vampire vane vapidly vary vastness vats vaults vector veered vegan vehicle vein velvet venomous verification vessel veteran vexed vials vibrate victim video viewpoint vigilant viking village vinegar violin vipers virtual visited vitals vivid vixen vocal vogue voice volcano vortex voted voucher vowels voyage vulture wade waffle wagtail waist waking wallets wanted warped washing water waveform waxing wayside weavers website wedge weekday weird welders went wept were western wetsuit whale when whipped whole wickets width wield wife wiggle wildly winter wipeout wiring wise withdrawn wives wizard wobbly woes woken wolf womanly wonders woozy worry wounded woven wrap wrist wrong yacht yahoo yanks yard yawning yearbook yellow yesterday yeti yields yodel yoga younger yoyo zapped zeal zebra zero zesty zigzags zinger zippers zodiac zombie zones zoom".split()
assert len(_BIP39)==2048 and len(_MONERO)==1626
_BIP39_IDX  = {w:i for i,w in enumerate(_BIP39)}
_MONERO_IDX = {w:i for i,w in enumerate(_MONERO)}
_MONERO_WC  = 1626

# ── secp256k1 ────────────────────────────────────────────
_P  = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
_N  = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
_Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
_Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8

def _padd(A,B):
    if A is None: return B
    if B is None: return A
    x1,y1=A; x2,y2=B
    if x1==x2:
        if y1!=y2: return None
        m=3*x1*x1*pow(2*y1,-1,_P)%_P
    else: m=(y2-y1)*pow(x2-x1,-1,_P)%_P
    x3=(m*m-x1-x2)%_P; y3=(m*(x1-x3)-y1)%_P
    return x3,y3

def _pmul(k,G=None):
    if G is None: G=(_Gx,_Gy)
    r=None
    while k:
        if k&1: r=_padd(r,G)
        G=_padd(G,G); k>>=1
    return r

def _pub(k):
    x,y=_pmul(k)
    return (b'\x02' if y%2==0 else b'\x03')+x.to_bytes(32,'big')

def _pub_unc(k):
    x,y=_pmul(k)
    return b'\x04'+x.to_bytes(32,'big')+y.to_bytes(32,'big')

# ── Ed25519 ───────────────────────────────────────────────
_ED_P = 2**255-19
_ED_D = -121665*pow(121666,-1,_ED_P)%_ED_P
_ED_L = 2**252+27742317777372353535851937790883648493

def _ed_base():
    y=4*pow(5,-1,_ED_P)%_ED_P
    x2=(y*y-1)*pow(_ED_D*y*y+1,-1,_ED_P)%_ED_P
    x=pow(x2,(_ED_P+3)//8,_ED_P)
    if (x*x-x2)%_ED_P!=0: x=x*pow(2,(_ED_P-1)//4,_ED_P)%_ED_P
    if x%2!=0: x=_ED_P-x
    return (x,y,1,x*y%_ED_P)

def _ed_add(P,Q):
    x1,y1,z1,t1=P; x2,y2,z2,t2=Q
    A=(y1-x1)*(y2-x2)%_ED_P; B=(y1+x1)*(y2+x2)%_ED_P
    C=t1*2*_ED_D*t2%_ED_P; D=z1*2*z2%_ED_P
    E=B-A; F=D-C; G2=D+C; H=B+A
    return E*F%_ED_P,G2*H%_ED_P,F*G2%_ED_P,E*H%_ED_P

def _ed_mul(k,P):
    R=(0,1,1,0)
    while k:
        if k&1: R=_ed_add(R,P)
        P=_ed_add(P,P); k>>=1
    return R

def _ed_pub_from_scalar(s32):
    """Monero: pub = scalar * B (scalar as little-endian, no hashing)."""
    a=int.from_bytes(s32,'little'); B=_ed_base(); R=_ed_mul(a,B)
    x,y,z,_=R; zi=pow(z,-1,_ED_P); ax=x*zi%_ED_P; ay=y*zi%_ED_P
    out=bytearray(ay.to_bytes(32,'little')); out[31]|=(ax&1)<<7
    return bytes(out)

def _ed_pub_from_privkey(priv32):
    """Standard Ed25519 pubkey (for SOL): hash then scalar mul."""
    h=hashlib.sha512(priv32).digest()
    a=bytearray(h[:32]); a[0]&=248; a[31]&=127; a[31]|=64
    ai=int.from_bytes(a,'little')
    B=_ed_base(); R=_ed_mul(ai,B)
    x,y,z,_=R; zi=pow(z,-1,_ED_P); ax=x*zi%_ED_P; ay=y*zi%_ED_P
    out=bytearray(ay.to_bytes(32,'little')); out[31]|=(ax&1)<<7
    return bytes(out)

def _ed_point_decode(b32):
    """Decode Ed25519 compressed point."""
    y=int.from_bytes(b32,'little')&~(1<<255); sign=b32[31]>>7
    x2=(y*y-1)*pow(_ED_D*y*y+1,-1,_ED_P)%_ED_P
    x=pow(x2,(_ED_P+3)//8,_ED_P)
    if (x*x-x2)%_ED_P!=0: x=x*pow(2,(_ED_P-1)//4,_ED_P)%_ED_P
    if x%2!=sign: x=_ED_P-x
    return (x,y,1,x*y%_ED_P)

def _ed_point_encode(P):
    x,y,z,_=P; zi=pow(z,-1,_ED_P); ax=x*zi%_ED_P; ay=y*zi%_ED_P
    out=bytearray(ay.to_bytes(32,'little')); out[31]|=(ax&1)<<7
    return bytes(out)

# ── keccak256 ────────────────────────────────────────────
def _keccak256(data):
    RC=[0x0000000000000001,0x0000000000008082,0x800000000000808A,0x8000000080008000,
        0x000000000000808B,0x0000000080000001,0x8000000080008081,0x8000000000008009,
        0x000000000000008A,0x0000000000000088,0x0000000080008009,0x000000008000000A,
        0x000000008000808B,0x800000000000008B,0x8000000000008089,0x8000000000008003,
        0x8000000000008002,0x8000000000000080,0x000000000000800A,0x800000008000000A,
        0x8000000080008081,0x8000000000008080,0x0000000080000001,0x8000000080008008]
    ROT=[[0,36,3,41,18],[1,44,10,45,2],[62,6,43,15,61],[28,55,25,21,56],[27,20,39,8,14]]
    def rot(x,n): return ((x<<n)|(x>>(64-n)))&0xFFFFFFFFFFFFFFFF
    msg=bytearray(data)+b'\x01'
    msg+=b'\x00'*(136-len(msg)%136-1)+b'\x80'
    A=[[0]*5 for _ in range(5)]
    for i in range(0,len(msg),136):
        for j in range(17):
            xj,yj=j%5,j//5; A[xj][yj]^=int.from_bytes(msg[i+j*8:i+j*8+8],'little')
        for r in range(24):
            C=[A[x][0]^A[x][1]^A[x][2]^A[x][3]^A[x][4] for x in range(5)]
            D=[C[(x+4)%5]^rot(C[(x+1)%5],1) for x in range(5)]
            for x in range(5):
                for y in range(5): A[x][y]^=D[x]
            B=[[0]*5 for _ in range(5)]
            for x in range(5):
                for y in range(5): B[y][(2*x+3*y)%5]=rot(A[x][y],ROT[x][y])
            for x in range(5):
                for y in range(5): A[x][y]=B[x][y]^((~B[(x+1)%5][y])&B[(x+2)%5][y])
            A[0][0]^=RC[r]
    out=bytearray()
    for y in range(4):
        for x in range(5):
            if len(out)>=32: break
            out+=A[x][y].to_bytes(8,'little')
    return bytes(out[:32])

# ── hash helpers ─────────────────────────────────────────
def _h160(d): return hashlib.new('ripemd160',hashlib.sha256(d).digest()).digest()
def _sc_reduce32(b): return (int.from_bytes(b,'little')%_ED_L).to_bytes(32,'little')
def _hash_to_scalar(b): return _sc_reduce32(_keccak256(b))

# ── base58 ───────────────────────────────────────────────
_B58='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

def _b58chk(p):
    chk=hashlib.sha256(hashlib.sha256(p).digest()).digest()[:4]
    b=p+chk; n=int.from_bytes(b,'big')
    lz=len(b)-len(b.lstrip(b'\x00')); r=[]
    while n: n,rem=divmod(n,58); r.append(_B58[rem])
    return '1'*lz+''.join(reversed(r))

def _b58plain(data):
    n=int.from_bytes(data,'big')
    lz=len(data)-len(data.lstrip(b'\x00')); r=[]
    while n: n,rem=divmod(n,58); r.append(_B58[rem])
    return '1'*lz+''.join(reversed(r))

def _p2pkh(pub): return _b58chk(b'\x00'+_h160(pub))
def _p2sh(pub):  return _b58chk(b'\x05'+_h160(b'\x00\x14'+_h160(pub)))

# ── bech32 / bech32m ─────────────────────────────────────
_BC='qpzry9x8gf2tvdw0s3jn54khce6mua7l'

def _bech32_encode(hrp, prog, witver=0, const=1):
    def conv(d,f,t):
        acc=bits=0; r=[]
        for v in d:
            acc=(acc<<f)|v; bits+=f
            while bits>=t: bits-=t; r.append((acc>>bits)&((1<<t)-1))
        if bits: r.append((acc<<(t-bits))&((1<<t)-1))
        return r
    data=[witver]+conv(prog,8,5)
    ex=[ord(c)>>5 for c in hrp]+[0]+[ord(c)&31 for c in hrp]
    def pm(v):
        GEN=[0x3b6a57b2,0x26508e6d,0x1ea119fa,0x3d4233dd,0x2a1462b3]; c=1
        for vv in v:
            b=c>>25; c=(c&0x1ffffff)<<5^vv
            for i in range(5):
                if (b>>i)&1: c^=GEN[i]
        return c
    p=pm(ex+data+[0]*6)^const
    return hrp+'1'+''.join(_BC[d] for d in data)+''.join(_BC[(p>>5*i)&31] for i in range(5,-1,-1))

def _p2wpkh(pub): return _bech32_encode('bc',_h160(pub))

def _p2tr(priv32):
    """BIP86 Taproot: P = priv*G, tweak t=H(TapTweak||Px), Q=(priv+t)*G."""
    x,_=_pmul(int.from_bytes(priv32,'big'))
    internal_x=x.to_bytes(32,'big')
    h=hashlib.sha256(b'TapTweak').digest()
    t=hashlib.sha256(h+h+internal_x).digest()
    t_int=int.from_bytes(t,'big')%_N
    tweaked=(int.from_bytes(priv32,'big')+t_int)%_N
    tx,_=_pmul(tweaked)
    return _bech32_encode('bc',tx.to_bytes(32,'big'),witver=1,const=0x2bc830a3)

# ── ETH/BSC address ──────────────────────────────────────
def _eth_addr(priv32):
    h=_keccak256(_pub_unc(int.from_bytes(priv32,'big'))[1:])
    addr=h[-20:].hex()
    chk=_keccak256(addr.encode()).hex()
    return '0x'+''.join(c.upper() if int(chk[i],16)>=8 else c for i,c in enumerate(addr))

# ── Monero base58 (block-based) ──────────────────────────
def _xmr_b58(data):
    LAST={1:2,2:3,3:5,4:6,5:7,6:9,7:10,8:11}
    result=''; i=0
    while i+8<=len(data):
        val=int.from_bytes(data[i:i+8],'big')
        chars=['1']*11
        for j in range(10,-1,-1): val,rem=divmod(val,58); chars[j]=_B58[rem]
        result+=''.join(chars); i+=8
    rem=data[i:]
    if rem:
        out_len=LAST[len(rem)]; val=int.from_bytes(rem,'big')
        chars=['1']*out_len
        for j in range(out_len-1,-1,-1): val,r2=divmod(val,58); chars[j]=_B58[r2]
        result+=''.join(chars)
    return result

def _xmr_addr(spend_pub, view_pub, network=0x12):
    data=bytes([network])+spend_pub+view_pub
    return _xmr_b58(data+_keccak256(data)[:4])

def _xmr_subaddr(view_sec, spend_pub, major, minor):
    """Compute Monero subaddress for (major, minor) index."""
    data=b"SubAddr\x00"+view_sec+major.to_bytes(4,'little')+minor.to_bytes(4,'little')
    m=_hash_to_scalar(data); m_int=int.from_bytes(m,'little')
    B=_ed_base()
    mG=_ed_mul(m_int,B)
    sp=_ed_point_decode(spend_pub)
    D=_ed_add(sp,mG)
    spend_sub=_ed_point_encode(D)
    v_int=int.from_bytes(view_sec,'little')
    view_sub=_ed_point_encode(_ed_mul(v_int,D))
    return _xmr_addr(spend_sub,view_sub,network=42)  # 42 decimal = 0x2a

# ── Monero seed encoding ──────────────────────────────────
def _xmr_encode25(spend32):
    """Encode 32-byte spend key to 25-word Monero seed."""
    WC=_MONERO_WC; idxs=[]
    for i in range(8):
        x=int.from_bytes(spend32[i*4:i*4+4],'little')
        w0=x%WC; w1=(x//WC+w0)%WC; w2=(x//WC//WC+w1)%WC
        idxs+=[w0,w1,w2]
    pfx=''.join(_MONERO[i][:3] for i in idxs)
    crc=binascii.crc32(pfx.encode())&0xFFFFFFFF
    idxs.append(idxs[crc%24])
    return ' '.join(_MONERO[i] for i in idxs)

def _xmr_decode25(seed25):
    """Decode 25-word Monero seed to 32-byte spend key."""
    ws=seed25.strip().split()
    if len(ws)!=25: raise ValueError(f"Expected 25 words, got {len(ws)}")
    WC=_MONERO_WC
    key=bytearray()
    for i in range(0,24,3):
        w0,w1,w2=_MONERO_IDX[ws[i]],_MONERO_IDX[ws[i+1]],_MONERO_IDX[ws[i+2]]
        x=w0+WC*((w1-w0)%WC)+WC*WC*((w2-w1)%WC)
        key+=x.to_bytes(4,'little')
    return bytes(key)

def _xmr_validate25(seed25):
    """Validate Monero 25-word seed (checksum check)."""
    ws=seed25.strip().split()
    if len(ws)!=25: return False,f"Expected 25 words, got {len(ws)}"
    for w in ws:
        if w not in _MONERO_IDX: return False,f"Unknown word: '{w}'"
    idxs=[_MONERO_IDX[w] for w in ws[:24]]
    pfx=''.join(_MONERO[i][:3] for i in idxs)
    crc=binascii.crc32(pfx.encode())&0xFFFFFFFF
    expected=idxs[crc%24]
    if _MONERO_IDX[ws[24]]!=expected:
        return False,"Invalid checksum"
    return True,"Valid"

def _xmr_validate_offset_words(words):
    """Check all offset words exist in Monero wordlist."""
    bad=[w for w in words if w not in _MONERO_IDX]
    if bad: return False, f"Not in Monero wordlist: {', '.join(bad)}"
    return True, "ok"

def _xmr_apply_offset(seed25, passphrase_words):
    """Apply Monero native passphrase offset."""
    ws=seed25.strip().split()[:24]
    seed_idxs=[_MONERO_IDX[w] for w in ws]
    pass_idxs=[_MONERO_IDX[p] for p in passphrase_words]
    if not pass_idxs: return seed25
    new_idxs=[(seed_idxs[i]+pass_idxs[i%len(pass_idxs)])%_MONERO_WC for i in range(24)]
    pfx=''.join(_MONERO[i][:3] for i in new_idxs)
    crc=binascii.crc32(pfx.encode())&0xFFFFFFFF
    new_idxs.append(new_idxs[crc%24])
    return ' '.join(_MONERO[i] for i in new_idxs)

def _xmr_keys_from_spend(spend_sec):
    """Derive all Monero keys from spend secret key."""
    view_sec=_hash_to_scalar(spend_sec)
    spend_pub=_ed_pub_from_scalar(spend_sec)
    view_pub=_ed_pub_from_scalar(view_sec)
    return spend_sec,view_sec,spend_pub,view_pub

# ── SLIP-0010 Ed25519 (SOL) ──────────────────────────────
def _slip10_child(k,c,idx):
    data=b'\x00'+k+struct.pack('>I',idx|0x80000000)
    I=_hmac.new(c,data,hashlib.sha512).digest()
    return I[:32],I[32:]

def _slip10_derive(seed,path):
    I=_hmac.new(b'ed25519 seed',seed,hashlib.sha512).digest()
    k,c=I[:32],I[32:]
    for seg in path.split('/')[1:]:
        idx=int(seg.rstrip("'"))
        k,c=_slip10_child(k,c,idx)
    return k,c

# ── BIP32 secp256k1 ──────────────────────────────────────
HARD=0x80000000

def _child(k,c,idx):
    data=(b'\x00'+k if idx>=HARD else _pub(int.from_bytes(k,'big')))+struct.pack('>I',idx)
    I=_hmac.new(c,data,hashlib.sha512).digest()
    ck=((int.from_bytes(I[:32],'big')+int.from_bytes(k,'big'))%_N).to_bytes(32,'big')
    return ck,I[32:]

def _derive(seed,path):
    I=_hmac.new(b'Bitcoin seed',seed,hashlib.sha512).digest()
    k,c=I[:32],I[32:]
    for seg in path.split('/')[1:]:
        hard=seg.endswith("'"); idx=int(seg.rstrip("'"))+(HARD if hard else 0)
        k,c=_child(k,c,idx)
    return k,c

def _xpub_ser(k,c,ver=b'\x04\x88\xB2\x1E'):
    return _b58chk(ver+b'\x00'+b'\x00'*4+b'\x00'*4+c+_pub(int.from_bytes(k,'big')))
def _zpub_ser(k,c): return _xpub_ser(k,c,ver=b'\x04\xb2\x47\x46')

# ── BIP39 ────────────────────────────────────────────────
_WC={12:128,15:160,18:192,21:224,24:256}

def _bip39_generate(wc=12):
    eb=_WC.get(wc)
    if not eb: raise ValueError("Word count must be 12/15/18/21/24")
    ent=secrets.token_bytes(eb//8)
    h=hashlib.sha256(ent).digest()
    bits=[]
    for b in ent:
        for i in range(7,-1,-1): bits.append((b>>i)&1)
    for i in range(eb//32): bits.append((h[i//8]>>(7-i%8))&1)
    words=[]
    for i in range(len(bits)//11):
        idx=0
        for b in bits[i*11:i*11+11]: idx=(idx<<1)|b
        words.append(_BIP39[idx])
    return ' '.join(words)

def _bip39_validate(phrase):
    ws=phrase.strip().lower().split()
    if len(ws) not in _WC: return False,f"Invalid word count: {len(ws)}"
    for w in ws:
        if w not in _BIP39_IDX: return False,f"Unknown word: '{w}'"
    total=len(ws)*11; cs=len(ws)//3; eb=total-cs
    bits=[]
    for w in ws:
        idx=_BIP39_IDX[w]
        for i in range(10,-1,-1): bits.append((idx>>i)&1)
    ent=bytes(int(''.join(str(b) for b in bits[i*8:i*8+8]),2) for i in range(eb//8))
    h=hashlib.sha256(ent).digest()
    for i in range(cs):
        if bits[eb+i]!=(h[i//8]>>(7-i%8))&1: return False,"Invalid checksum"
    return True,"Valid"

def _bip39_entropy_hex(phrase):
    ws=phrase.strip().lower().split()
    total=len(ws)*11; cs=len(ws)//3; eb=total-cs
    bits=[]
    for w in ws:
        idx=_BIP39_IDX[w]
        for i in range(10,-1,-1): bits.append((idx>>i)&1)
    return bytes(int(''.join(str(b) for b in bits[i*8:i*8+8]),2) for i in range(eb//8)).hex()

def _bip39_to_seed(phrase,pp=''):
    return hashlib.pbkdf2_hmac('sha512',
        unicodedata.normalize('NFKD',phrase).encode(),
        ('mnemonic'+pp).encode(),2048)

# ── Detect input type ─────────────────────────────────────
def _detect_mnemonic(phrase):
    """Returns 'bip39', 'xmr25', or None."""
    ws=phrase.strip().lower().split()
    if len(ws)==25 and all(w in _MONERO_IDX for w in ws):
        ok,_=_xmr_validate25(phrase.strip().lower())
        if ok: return 'xmr25'
    if len(ws) in _WC and all(w in _BIP39_IDX for w in ws):
        ok,_=_bip39_validate(phrase)
        if ok: return 'bip39'
    return None

# ── Output helpers ────────────────────────────────────────
W=44
def _hr(t=''):
    if not t: print('-'*W); return
    s=(W-len(t)-2)//2; r=W-len(t)-2-s
    print('-'*s+f' {t} '+'-'*r)

def _row(k,v): print(f"  {k+':':<14} {v}")
def _ask(prompt): return input(f"  {prompt}: ").strip()
def _choose(prompt, options):
    """Show numbered menu, return chosen index (0-based)."""
    print(f"\n  {prompt}")
    for i,o in enumerate(options,1): print(f"    {i}. {o}")
    while True:
        try:
            n=int(input("  > "))
            if 1<=n<=len(options): return n-1
        except (ValueError,EOFError): pass
        print(f"  Enter 1-{len(options)}")

# ════════════════════════════════════════════════════════
# CORE FUNCTIONS
# ════════════════════════════════════════════════════════

def do_generate_bip39(wc):
    phrase=_bip39_generate(wc)
    _hr('NEW MNEMONIC')
    print(f"  {phrase}")
    print(f"\n  ({wc} words | {_WC[wc]} bits of entropy)")
    _hr()
    return phrase

def do_generate_xmr():
    """Generate a fresh Monero 25-word seed directly."""
    spend_sec=secrets.token_bytes(32)
    # Reduce mod l for a valid scalar
    spend_sec=_sc_reduce32(spend_sec)
    seed25=_xmr_encode25(spend_sec)
    _hr('NEW MONERO SEED')
    print(f"  {seed25}")
    _hr()
    return seed25

def do_validate(phrase):
    mtype=_detect_mnemonic(phrase)
    if mtype=='xmr25':
        ok,msg=_xmr_validate25(phrase)
        _hr('VALIDATE MONERO SEED')
        print(f"  Type   : Monero 25-word seed")
        print(f"  Status : {msg}")
    elif mtype=='bip39':
        ok,msg=_bip39_validate(phrase)
        ws=phrase.split()
        _hr('VALIDATE BIP39')
        print(f"  Type   : BIP39 ({len(ws)} words | {_WC[len(ws)]} bits)")
        print(f"  Status : {msg}")
    else:
        _hr('VALIDATE')
        print("  Error  : Unrecognized mnemonic type")
        ok=False
    _hr()
    return ok

def do_info(phrase, pp=''):
    ok,msg=_bip39_validate(phrase)
    if not ok: print(f"  Error: {msg}"); return
    sd=_bip39_to_seed(phrase,pp)
    I=_hmac.new(b'Bitcoin seed',sd,hashlib.sha512).digest()
    kr,cr=I[:32],I[32:]
    ws=phrase.split()
    _hr('MNEMONIC INFO')
    _row('Words',f"{len(ws)} | {_WC[len(ws)]} bits")
    _row('Passphrase',repr(pp) if pp else '(none)')
    _row('Entropy',_bip39_entropy_hex(phrase))
    _row('Seed',sd.hex())
    _row('Root xpub',_xpub_ser(kr,cr))
    _hr()

def do_derive_bip39(phrase, pp, coin, count, mode):
    ok,msg=_bip39_validate(phrase)
    if not ok: print(f"  Error: {msg}"); return
    sd=_bip39_to_seed(phrase,pp)

    def show_btc(base,label,afn,xfn=None,taproot=False):
        k,c=_derive(sd,base)
        ek,ec=_child(k,c,0)
        _hr(label)
        ser=(xfn or _xpub_ser)(ek,ec)
        print(f"  {'zpub' if xfn else 'xpub'}:")
        print(f"  {ser}\n")
        for j in range(count):
            ck,_=_child(ek,ec,j)
            pub=_pub(int.from_bytes(ck,'big'))
            print(f"  [{j}] {base}/0/{j}")
            if taproot:
                print(f"  Address : {_p2tr(ck)}")
            else:
                print(f"  Address : {afn(pub)}")
            print()

    if coin=='btc':
        if mode in ('all','taproot'): show_btc("m/86'/0'/0'","BIP86 Taproot (bc1p)",None,taproot=True)
        if mode in ('all','segwit'):  show_btc("m/84'/0'/0'","BIP84 SegWit (bc1q)",_p2wpkh,_zpub_ser)
        if mode in ('all','wrapped'): show_btc("m/49'/0'/0'","BIP49 SegWit-wrapped (3...)",_p2sh)
        if mode in ('all','legacy'):  show_btc("m/44'/0'/0'","BIP44 Legacy (1...)",_p2pkh)
    elif coin in ('eth','bnb'):
        label='ETH' if coin=='eth' else 'BNB BSC (BEP20)'
        k,c=_derive(sd,"m/44'/60'/0'")
        ek,ec=_child(k,c,0)
        _hr(label)
        print(f"  xpub:\n  {_xpub_ser(ek,ec)}\n")
        for j in range(count):
            ck,_=_child(ek,ec,j)
            print(f"  [{j}] m/44'/60'/0'/0/{j}")
            print(f"  Address : {_eth_addr(ck)}\n")
    elif coin=='sol':
        _hr('Solana')
        for j in range(count):
            k,_=_slip10_derive(sd,f"m/44'/501'/{j}'")
            pub=_ed_pub_from_privkey(k)
            print(f"  [{j}] m/44'/501'/{j}'")
            print(f"  Address : {_b58plain(pub)}\n")
    elif coin=='xmr':
        do_monero_from_bip39(phrase, pp)

def _do_show_xmr(spend_sec, header='Monero', subaddr_count=1):
    """Show Monero addresses and seed from a spend secret key."""
    _,view_sec,spend_pub,view_pub=_xmr_keys_from_spend(spend_sec)
    primary=_xmr_addr(spend_pub,view_pub)
    seed25=_xmr_encode25(spend_sec)
    if header: _hr(header)
    _row('Spend pub',spend_pub.hex())
    _row('View pub',view_pub.hex())
    print()
    _row('Primary addr',primary)
    for i in range(1, subaddr_count+1):
        sub=_xmr_subaddr(view_sec,spend_pub,0,i)
        _row(f'Subaddr (0,{i})',sub)
    print()
    print("  Seed (25 words):")
    print(f"  {seed25}")
    _hr()

def do_derive_xmr25(seed25, offset_words=None, subaddr_count=1):
    """Derive Monero addresses from a 25-word Monero seed."""
    ok,msg=_xmr_validate25(seed25)
    if not ok: print(f"  Error: {msg}"); return
    spend_sec=_xmr_decode25(seed25)
    if offset_words:
        ok_off,msg_off=_xmr_validate_offset_words(offset_words)
        if not ok_off: print(f"  Error: {msg_off}"); return
        actual_seed=_xmr_apply_offset(seed25,offset_words)
        ok2,msg2=_xmr_validate25(actual_seed)
        if not ok2: print(f"  Error in offset seed: {msg2}"); return
        spend_sec=_xmr_decode25(actual_seed)
        _hr('Monero (offset passphrase)')
        print(f"  Offset seed:")
        print(f"  {actual_seed}\n")
        _do_show_xmr(spend_sec, header=None, subaddr_count=subaddr_count)
    else:
        _do_show_xmr(spend_sec, 'Monero', subaddr_count=subaddr_count)

def do_monero_from_bip39(phrase, bip39_pp='', offset_words=None, subaddr_count=1):
    """Convert BIP39 mnemonic to Monero keys."""
    ok,msg=_bip39_validate(phrase)
    if not ok: print(f"  Error: {msg}"); return
    sd=_bip39_to_seed(phrase,bip39_pp)
    k,c=_derive(sd,"m/44'/128'/0'/0/0")
    spend_sec=_sc_reduce32(_keccak256(k))
    seed25_base=_xmr_encode25(spend_sec)
    if offset_words:
        ok_off,msg_off=_xmr_validate_offset_words(offset_words)
        if not ok_off: print(f"  Error: {msg_off}"); return
        seed25=_xmr_apply_offset(seed25_base,offset_words)
        ok2,_=_xmr_validate25(seed25)
        if ok2: spend_sec=_xmr_decode25(seed25)
        _hr('Monero from BIP39 (offset)')
        print(f"  Base seed  : {seed25_base}")
        print(f"  Offset seed: {seed25}\n")
        _do_show_xmr(spend_sec, header=None, subaddr_count=subaddr_count)
    else:
        _do_show_xmr(spend_sec, 'Monero from BIP39', subaddr_count=subaddr_count)

# ════════════════════════════════════════════════════════
# CLI HANDLERS
# ════════════════════════════════════════════════════════

def cli_generate(args):
    if '--xmr' in args:
        do_generate_xmr()
        return
    wc=int(args[0]) if args else 12
    if wc not in _WC: sys.exit("Error: word count must be 12/15/18/21/24")
    do_generate_bip39(wc)

def cli_validate(args):
    if not args: sys.exit("Error: provide mnemonic")
    ok=do_validate(args[0])
    sys.exit(0 if ok else 1)

def cli_info(args):
    if not args: sys.exit("Error: provide mnemonic")
    do_info(args[0], args[1] if len(args)>1 else '')

def cli_derive(args):
    if not args: sys.exit("Error: provide mnemonic")
    phrase=args[0]; coin='btc'; count=5; mode='all'; pp=''
    i=1
    if i<len(args) and not args[i].startswith('--'): pp=args[i]; i+=1
    offset_words=None
    while i<len(args):
        a=args[i]
        if   a=='--coin'       and i+1<len(args): coin=args[i+1].lower(); i+=2
        elif a=='--count'      and i+1<len(args): count=int(args[i+1]); i+=2
        elif a=='--mode'       and i+1<len(args): mode=args[i+1]; i+=2
        elif a=='--passphrase' and i+1<len(args):
            offset_words=args[i+1].strip().lower().split(); i+=2
        else: i+=1
    mtype=_detect_mnemonic(phrase)
    if mtype=='xmr25':
        do_derive_xmr25(phrase, offset_words, subaddr_count=count)
    elif mtype=='bip39':
        if coin=='xmr':
            do_monero_from_bip39(phrase, pp, offset_words, subaddr_count=count)
        else:
            do_derive_bip39(phrase, pp, coin, count, mode)
    else:
        sys.exit("Error: unrecognized mnemonic")

def cli_monero(args):
    if not args: sys.exit("Error: provide BIP39 mnemonic")
    phrase=args[0]; bip39_pp=''; offset_words=None; count=1
    i=1
    if i<len(args) and not args[i].startswith('--'): bip39_pp=args[i]; i+=1
    while i<len(args):
        if args[i]=='--passphrase' and i+1<len(args):
            offset_words=args[i+1].strip().lower().split(); i+=2
        elif args[i]=='--count' and i+1<len(args):
            count=int(args[i+1]); i+=2
        else: i+=1
    do_monero_from_bip39(phrase, bip39_pp, offset_words, subaddr_count=count)

# ════════════════════════════════════════════════════════
# INTERACTIVE MODE
# ════════════════════════════════════════════════════════

def interactive():
    print()
    print("  BIP39/Monero Mnemonic Tool")
    print("  " + "="*(W-2))
    while True:
        idx=_choose("Select action:", [
            "Generate BIP39 mnemonic",
            "Generate Monero seed (25 words)",
            "Validate mnemonic",
            "Show mnemonic info (BIP39)",
            "Derive addresses from BIP39",
            "Derive addresses from Monero seed",
            "Convert BIP39 to Monero seed",
            "Exit",
        ])
        print()
        if idx==0:
            wc=_choose("Word count:",[str(w) for w in [12,15,18,21,24]])
            do_generate_bip39([12,15,18,21,24][wc])
        elif idx==1:
            do_generate_xmr()
        elif idx==2:
            p=_ask("Enter mnemonic")
            do_validate(p)
        elif idx==3:
            p=_ask("Enter BIP39 mnemonic")
            pp=_ask("BIP39 passphrase (leave blank for none)")
            do_info(p,pp)
        elif idx==4:
            p=_ask("Enter BIP39 mnemonic")
            pp=_ask("BIP39 passphrase (leave blank for none)")
            ci=_choose("Coin:",['BTC','ETH','BNB BSC','SOL','XMR'])
            coin=['btc','eth','bnb','sol','xmr'][ci]
            if coin=='btc':
                mi=_choose("Address type:",['All','Taproot (bc1p)','SegWit (bc1q)','Wrapped SegWit (3...)','Legacy (1...)'])
                mode=['all','taproot','segwit','wrapped','legacy'][mi]
            else:
                mode='all'
            try: count=int(_ask("Number of addresses [5]" if coin!='xmr' else "Number of subaddresses [1]") or ('5' if coin!='xmr' else '1'))
            except ValueError: count=5 if coin!='xmr' else 1
            if coin=='xmr':
                do_monero_from_bip39(p,pp,subaddr_count=count)
            else:
                do_derive_bip39(p,pp,coin,count,mode)
        elif idx==5:
            p=_ask("Enter Monero 25-word seed")
            try: sc=int(_ask("Number of subaddresses [1]") or '1')
            except ValueError: sc=1
            use_offset=_choose("Apply offset passphrase?",['No','Yes'])
            offset_words=None
            if use_offset==1:
                while True:
                    raw=_ask("Offset passphrase (space-separated Monero words)")
                    ow=raw.strip().lower().split()
                    ok_off,msg_off=_xmr_validate_offset_words(ow)
                    if ok_off: offset_words=ow; break
                    print(f"  Error: {msg_off}. Try again.")
            do_derive_xmr25(p,offset_words,subaddr_count=sc)
        elif idx==6:
            p=_ask("Enter BIP39 mnemonic")
            pp=_ask("BIP39 passphrase (leave blank for none)")
            try: sc=int(_ask("Number of subaddresses [1]") or '1')
            except ValueError: sc=1
            use_offset=_choose("Apply Monero offset passphrase?",['No','Yes'])
            offset_words=None
            if use_offset==1:
                while True:
                    raw=_ask("Offset passphrase (space-separated Monero words)")
                    ow=raw.strip().lower().split()
                    ok_off,msg_off=_xmr_validate_offset_words(ow)
                    if ok_off: offset_words=ow; break
                    print(f"  Error: {msg_off}. Try again.")
            do_monero_from_bip39(p,pp,offset_words,subaddr_count=sc)
        elif idx==7:
            print("  Goodbye.")
            break
        print()

# ════════════════════════════════════════════════════════
# HELP & MAIN
# ════════════════════════════════════════════════════════

HELP="""
bip39cli.py - BIP39/Monero Mnemonic Tool
--------------------------------------------

No arguments -> interactive menu

Commands:

  generate [12|15|18|21|24]
    Generate BIP39 mnemonic. Default: 12.

  generate --xmr
    Generate Monero 25-word seed directly.

  validate "<mnemonic>"
    Validate BIP39 or Monero 25-word seed.

  info "<mnemonic>" [passphrase]
    BIP39 seed hex + root xpub.

  derive "<mnemonic>" [passphrase]
    Derive addresses. Auto-detects BIP39
    or Monero 25-word input.

    Options (BIP39 only):
      --coin btc|eth|bnb|sol|xmr
      --count N           (default: 5)
      --mode all|taproot|segwit|wrapped|legacy

    Option (Monero 25-word input):
      --passphrase "<offset words>"

  monero "<bip39>" [bip39_passphrase]
    Convert BIP39 to Monero seed + addresses.

    Option:
      --passphrase "<offset words>"

Examples:
  python3 bip39cli.py generate 24
  python3 bip39cli.py generate --xmr
  python3 bip39cli.py validate "..."
  python3 bip39cli.py derive "..." "" --coin btc
  python3 bip39cli.py derive "..." "" --coin eth --count 3
  python3 bip39cli.py derive "<monero 25 words>"
  python3 bip39cli.py derive "<monero 25 words>" --passphrase "abbey ability"
  python3 bip39cli.py monero "..." "" --passphrase "abbey ability"

WARNING: Use only on trusted offline devices.
"""

if __name__=='__main__':
    if len(sys.argv)<2:
        interactive()
    elif sys.argv[1] in ('-h','--help','help'):
        print(HELP)
    else:
        sub=sys.argv[1]; rest=sys.argv[2:]
        if   sub=='generate': cli_generate(rest)
        elif sub=='validate': cli_validate(rest)
        elif sub=='info':     cli_info(rest)
        elif sub=='derive':   cli_derive(rest)
        elif sub=='monero':   cli_monero(rest)
        else: sys.exit(f"Unknown command '{sub}'. Use --help.")
