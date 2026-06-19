from typing import List, Set


def parse_pages_spec(spec: str, num_pages: int) -> List[int]:
    """Parse a page specification string into a sorted list of zero-based indices.
    Supported tokens (1-based):
      - Single pages: "1", "7"
      - Ranges: "3-5" (inclusive)
      - Open start: "-5" (from first page through page 5)
      - Open end: "10-" (from page 10 to the last page)
    """
    if num_pages <= 0:
        return []
    tokens = [t.strip() for t in spec.split(',') if t.strip()]
    indices: Set[int] = set()
    for tok in tokens:
        parts = tok.split('-')
        if len(parts) == 1:
            n = _parse_one_index(parts[0], num_pages)
            indices.add(n)
        elif len(parts) == 2:
            start = parts[0].strip()
            end = parts[1].strip()
            s = _parse_bound(start, default=1, num_pages=num_pages)
            e = _parse_bound(end, default=num_pages, num_pages=num_pages)
            s_idx = s - 1
            e_idx = e - 1
            if s_idx < 0 or e_idx < 0 or s_idx >= num_pages or e_idx >= num_pages or s_idx > e_idx:
                raise ValueError(f"Invalid range '{tok}' for document with {num_pages} pages.")
            for i in range(s_idx, e_idx + 1):
                indices.add(i)
        else:
            raise ValueError(f"Invalid token '{tok}'.")
    return sorted(indices)


def parse_order_spec(spec: str, num_pages: int, fill_unlisted: bool = True, strict: bool = False) -> List[int]:
    """Parse an order specification into a list of zero-based indices.
    Supports the same tokens as parse_pages_spec.
    If strict=True, requires listing every page exactly once.
    If fill_unlisted=True, appends pages not listed in original order.
    """
    order_indices: List[int] = []
    listed_set: Set[int] = set()
    for tok in [t.strip() for t in spec.split(',') if t.strip()]:
        if '-' in tok:
            parts = tok.split('-')
            s = _parse_bound(parts[0].strip(), default=1, num_pages=num_pages) - 1
            e = _parse_bound(parts[1].strip(), default=num_pages, num_pages=num_pages) - 1
            if s < 0 or e < 0 or s >= num_pages or e >= num_pages or s > e:
                raise ValueError(f"Invalid range '{tok}' for document with {num_pages} pages.")
            for i in range(s, e + 1):
                order_indices.append(i)
                listed_set.add(i)
        else:
            i = _parse_one_index(tok, num_pages)
            order_indices.append(i)
            listed_set.add(i)
    if strict:
        if len(order_indices) != num_pages:
            raise ValueError("Strict mode requires listing every page exactly once.")
        if sorted(order_indices) != list(range(num_pages)):
            raise ValueError("Strict mode requires each page to appear exactly once.")
    elif fill_unlisted:
        for i in range(num_pages):
            if i not in listed_set:
                order_indices.append(i)
    return order_indices


def _parse_one_index(s: str, num_pages: int) -> int:
    if not s:
        raise ValueError("Empty page token.")
    try:
        n = int(s)
    except ValueError as e:
        raise ValueError(f"Invalid page number '{s}'.") from e
    if n < 1 or n > num_pages:
        raise ValueError(f"Page number '{n}' out of bounds 1..{num_pages}.")
    return n - 1


def _parse_bound(s: str, default: int, num_pages: int) -> int:
    if s == '':
        return default
    try:
        n = int(s)
    except ValueError as e:
        raise ValueError(f"Invalid bound '{s}'.") from e
    if n < 1:
        n = 1
    if n > num_pages:
        n = num_pages
    return n
