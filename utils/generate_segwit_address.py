import hashlib, struct, hmac

ZPUB_VERSION = bytes.fromhex("04b24746")
XPUB_VERSION = bytes.fromhex("0488b21e")
BASE58_CHARS = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
_P     = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
_ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
_G     = (0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
          0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)

# --- bech32 ---
_B32C = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
_B32G = [0x3B6A57B2,0x26508E6D,0x1EA119FA,0x3D4233DD,0x2A1462B3]

def _polymod(v):
    chk=1
    for x in v:
        b=chk>>25; chk=((chk&0x1FFFFFF)<<5)^x
        for i in range(5): chk^=_B32G[i] if (b>>i)&1 else 0
    return chk

def _hrp_expand(hrp):
    return [ord(c)>>5 for c in hrp]+[0]+[ord(c)&31 for c in hrp]

def _convertbits(data,fb,tb):
    acc=bits=0; ret=[]; maxv=(1<<tb)-1
    for v in data:
        acc=((acc<<fb)|v)&0xFFFFFFFF; bits+=fb
        while bits>=tb: bits-=tb; ret.append((acc>>bits)&maxv)
    if bits: ret.append((acc<<(tb-bits))&maxv)
    return ret

def bech32_encode(hrp,witver,witprog):
    data=[witver]+_convertbits(witprog,8,5)
    chk=[(_polymod(_hrp_expand(hrp)+data+[0]*6)^1)>>5*(5-i)&31 for i in range(6)]
    return hrp+"1"+"".join(_B32C[d] for d in data+chk)

# --- base58check ---
def _sha256d(d): return hashlib.sha256(hashlib.sha256(d).digest()).digest()

def b58decode_check(s):
    n=0
    for c in s: n=n*58+BASE58_CHARS.index(c)
    bl=(n.bit_length()+7)//8 if n>0 else 0
    raw=n.to_bytes(bl,"big")
    pad=len(s)-len(s.lstrip("1"))
    raw=b"\x00"*pad+raw
    payload,checksum=raw[:-4],raw[-4:]
    if _sha256d(payload)[:4]!=checksum: raise ValueError("Invalid checksum")
    return payload

# --- secp256k1 ---
def _point_add(p1,p2):
    if p1 is None: return p2
    if p2 is None: return p1
    if p1[0]==p2[0]:
        if p1[1]!=p2[1]: return None
        lam=(3*p1[0]*p1[0]*pow(2*p1[1],_P-2,_P))%_P
    else: lam=((p2[1]-p1[1])*pow(p2[0]-p1[0],_P-2,_P))%_P
    x=(lam*lam-p1[0]-p2[0])%_P; y=(lam*(p1[0]-x)-p1[1])%_P
    return(x,y)

def _scalar_mult(k,pt):
    r,a=None,pt
    while k:
        if k&1: r=_point_add(r,a)
        a=_point_add(a,a); k>>=1
    return r

def _decompress(c):
    x=int.from_bytes(c[1:],"big"); ysq=(pow(x,3,_P)+7)%_P; y=pow(ysq,(_P+1)//4,_P)
    if y%2!=c[0]-2: y=_P-y
    return(x,y)

def _compress(pt):
    return(b"\x02"if pt[1]%2==0 else b"\x03")+pt[0].to_bytes(32,"big")

# --- BIP32 public derivation ---
def derive_child(pk,cc,idx):
    I=hmac.new(cc,pk+struct.pack(">I",idx),hashlib.sha512).digest()
    IL,IR=I[:32],I[32:]
    il=int.from_bytes(IL,"big")
    if il>=_ORDER: raise ValueError("IL>=order")
    pt=_point_add(_scalar_mult(il,_G),_decompress(pk))
    if pt is None: raise ValueError("Point at infinity")
    return _compress(pt),IR

def parse_xpub(raw):
    return raw[45:78],raw[13:45]   # pubkey, chaincode

def zpub_to_raw(zpub):
    raw=b58decode_check(zpub)
    if raw[:4]!=ZPUB_VERSION: raise ValueError(f"Not zpub. Version: {raw[:4].hex()}")
    return XPUB_VERSION+raw[4:]

def pubkey_to_address(pk,hrp="bc"):
    h=hashlib.new("ripemd160",hashlib.sha256(pk).digest()).digest()
    return bech32_encode(hrp,0,list(h))

def generate_addresses(zpub,change=0,start=0,count=10,network="mainnet"):
    hrp="bc" if network=="mainnet" else "tb"
    rpk,rcc=parse_xpub(zpub_to_raw(zpub))
    cpk,ccc=derive_child(rpk,rcc,change)
    out=[]
    for i in range(start,start+count):
        pk,_=derive_child(cpk,ccc,i)
        out.append({"index":i,"path":f"m/84'/0'/0'/{change}/{i}",
                    "address":pubkey_to_address(pk,hrp),"pubkey":pk.hex()})
    return out

if __name__=="__main__":
    import argparse,sys
    p=argparse.ArgumentParser(description="Generate address SegWit BIP84 dari zpub")
    p.add_argument("zpub"); p.add_argument("--change",type=int,default=0)
    p.add_argument("--start",type=int,default=0); p.add_argument("--count",type=int,default=10)
    p.add_argument("--network",default="mainnet",choices=["mainnet","testnet"])
    a=p.parse_args()
    try:
        addrs=generate_addresses(a.zpub,a.change,a.start,a.count,a.network)
    except Exception as e:
        print(f"[ERROR] {e}",file=sys.stderr); sys.exit(1)
    lbl="Receive (external)" if a.change==0 else "Change (internal)"
    print(f"\n{'='*70}")
    print(f"  BIP84 SegWit Address Generator")
    print(f"  Network : {a.network.upper()} | Chain: {lbl}")
    print(f"{'='*70}")
    print(f"  {'Index':<6}  {'Derivation Path':<28}  Address")
    print(f"  {'-'*6}  {'-'*28}  {'-'*44}")
    for x in addrs: print(f"  {x['index']:<6}  {x['path']:<28}  {x['address']}")
    print(f"{'='*70}\n")
