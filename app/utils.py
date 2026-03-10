import hashlib
import difflib

def generate_hash_index(encoded_data: str) -> str:
    """
    Deterministic template index based on content
    Same content => same index
    Any change => new index
    """
    digest = hashlib.sha256(encoded_data.encode()).hexdigest()[:12]
    return f"TIDX-{digest}"

def generate_diff(old_text: str, new_text: str) -> str:
    """
    Generate unified diff between two encoded templates
    """
    diff = difflib.unified_diff(
        old_text.splitlines(),
        new_text.splitlines(),
        fromfile="existing",
        tofile="new",
        lineterm=""
    )
    return "\n".join(diff)
