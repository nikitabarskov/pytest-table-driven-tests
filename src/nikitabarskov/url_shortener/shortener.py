import hashlib
import string

from pydantic import HttpUrl

SHORT_CODE_LENGTH = 6
ALPHABET = string.ascii_letters + string.digits
ALPHABET_LENGTH = len(ALPHABET)


def generate_short_code(url: HttpUrl, length: int = SHORT_CODE_LENGTH) -> str:
    hash_digest = hashlib.sha256(url.unicode_string().encode()).hexdigest()
    hash_int = int(hash_digest, 16)

    chars = []
    for _ in range(SHORT_CODE_LENGTH):
        hash_int, remainder = divmod(hash_int, ALPHABET_LENGTH)
        chars.append(ALPHABET[remainder])

    return "".join(reversed(chars)).rjust(SHORT_CODE_LENGTH, "0")
