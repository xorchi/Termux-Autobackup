import random
import string
from mnemonic import Mnemonic

def get_single_username():
    words = Mnemonic("english").wordlist
    # Pick 2 random words and capitalize them
    selected = [word.capitalize() for word in random.sample(words, 2)]
    # Append 3 random digits at the end
    nums = ''.join(random.choices(string.digits, k=3))
    
    return f"{''.join(selected)}{nums}"

# Print one username directly
print(get_single_username())
