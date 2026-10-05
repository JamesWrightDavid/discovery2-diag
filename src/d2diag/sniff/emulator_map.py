"""Parse the NanoCom Evolution emulator's page graph into a menu tree.

The emulator (Black Box Solutions) ships a single ``emulator.json`` describing every
screen as ``pages/<path>/{image, title, areas:[{coords, label, action}]}``. Navigation is
by clickable ``areas`` whose ``action`` is ``{"type":"navigate","target":"<path>"}``;
list/menu entries carry an ``"Open <name>"`` label, while pagination carries
``"Next page"`` / ``"Previous page"`` / ``"Back"``.

We treat the **path nesting** as the menu hierarchy (it mirrors the emulator's own menu
grouping) and fold in the human ``"Open <name>"`` labels as display names. The result is a
deterministic, OCR-free map of *which functions exist per module* — the structure behind
the per-module feature maps in ``references/nanocom/``.

This reads a third-party reference kept out of git under ``captures/nanocom/``; only the
**derived** tree is committed. The leaf screens' exact field lists live in the page images,
transcribed separately.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List

# The Discovery 2 Td5 variant subtree. The petrol (motronic) variant and the CAN-bus
# vehicles share the same JSON but are out of scope here. Cruise (Hella) only appears under
# the motronic branch, so we pull it in explicitly as the reference for the Td5 car's cruise.
TD5_ROOT = "homepage/discovery/td5"
CRUISE_PATH = "homepage/discovery/motronic/hella_cc"

# Hotspot labels that are navigation chrome, not menu entries.
_NAV_LABELS = {"next page", "previous page", "back", ""}


def load_pages(json_path: str) -> "Dict[str, dict]":
    """Return ``{page_path: page_node}`` for every ``kind == "page"`` in the emulator JSON."""
    with open(json_path, encoding="utf-8") as fh:
        data = json.load(fh)
    pages: "Dict[str, dict]" = {}

    def walk(node: Any, pre: str = "") -> None:
        if isinstance(node, dict) and node.get("kind") == "page":
            pages[pre.strip("/")] = node
            return
        if isinstance(node, dict):
            for key, val in node.items():
                walk(val, pre + "/" + key)

    walk(data.get("pages", {}))
    return pages


def _open_labels(pages: "Dict[str, dict]") -> "Dict[str, str]":
    """Map ``target_path -> "nice name"`` from every ``"Open <name>"`` hotspot.

    The emulator labels a menu entry ``Open td5 engine``; its navigate target is that
    submenu's page. We strip the ``Open `` prefix to recover the display name of the node.
    """
    names: "Dict[str, str]" = {}
    for node in pages.values():
        for area in node.get("areas", []):
            label = (area.get("label") or "").strip()
            action = area.get("action") or {}
            target = action.get("target")
            if not target or label.lower() in _NAV_LABELS:
                continue
            if label.lower().startswith("open "):
                names.setdefault(target, label[5:].strip())
    return names


def _display_name(seg: str, node_path: str, open_names: "Dict[str, str]") -> str:
    """Best display name for a menu segment: the ``Open <name>`` label for one of its pages,
    else the path segment with underscores spaced out."""
    # a menu node is addressed by its first page (``.../seg/page1``); any page under it may
    # be the navigate target that carried the Open label.
    for target, nice in open_names.items():
        if target == node_path or target.startswith(node_path + "/"):
            if target[len(node_path):].count("/") <= 1:  # the node's own page, not deeper
                return nice
    return seg.replace("_", " ")


def build_subtree(pages: "Dict[str, dict]", root: str) -> "dict":
    """Build a nested menu tree for ``root`` from the page paths.

    A node is ``{name, label, path, pages:[{path,image}], children:[node,...]}``. Leaf
    functions are nodes whose only children are ``pageN`` pagination (folded into ``pages``).
    """
    open_names = _open_labels(pages)
    members = [p for p in pages if p == root or p.startswith(root + "/")]

    def is_page_seg(seg: str) -> bool:
        return seg.startswith("page") and seg[4:].isdigit()

    def node_for(prefix: str, seg: str) -> "dict":
        path = prefix + "/" + seg if prefix else seg
        # direct children segments (one level down), split into pagination vs submenus
        child_segs: "Dict[str, None]" = {}
        own_pages: "List[dict]" = []
        for member in members:
            if not member.startswith(path + "/"):
                if member == path:  # the node is itself a page (rare)
                    own_pages.append({"path": member, "image": pages[member].get("image", "")})
                continue
            rest = member[len(path) + 1:].split("/")
            head = rest[0]
            if is_page_seg(head) and len(rest) == 1:
                own_pages.append({"path": member, "image": pages[member].get("image", "")})
            else:
                child_segs.setdefault(head, None)
        children = [node_for(path, cs) for cs in child_segs if not is_page_seg(cs)]
        own_pages.sort(key=lambda d: d["path"])
        children.sort(key=lambda n: n["path"])
        return {
            "name": seg,
            "label": _display_name(seg, path, open_names),
            "path": path,
            "pages": own_pages,
            "children": children,
        }

    base_prefix, _, base_seg = root.rpartition("/")
    return node_for(base_prefix, base_seg)


def td5_tree(json_path: str) -> "dict":
    """The Discovery 2 Td5 menu tree plus the (shared) cruise module, from the emulator JSON."""
    pages = load_pages(json_path)
    tree = build_subtree(pages, TD5_ROOT)
    cruise = build_subtree(pages, CRUISE_PATH)
    cruise["label"] = "Hella cruise control (shared with V8 variant)"
    tree["children"].append(cruise)
    tree["children"].sort(key=lambda n: n["path"])
    return tree


def iter_functions(tree: "dict", _trail: "List[str] | None" = None):
    """Yield ``(trail, node)`` for every leaf function node (a node with page images and no
    submenu children) — the sniff/UI unit of work."""
    trail = (_trail or []) + [tree["label"]]
    if tree["pages"] and not tree["children"]:
        yield trail, tree
    for child in tree["children"]:
        yield from iter_functions(child, trail)


def to_markdown(tree: "dict") -> str:
    """Render the tree as an indented Markdown outline with page counts and image names."""
    lines: "List[str]" = []

    def render(node: "dict", depth: int) -> None:
        pad = "  " * depth
        total = _count_pages(node)
        bullet = f"{pad}- **{node['label']}**"
        if total:
            bullet += f" — {total} page(s)"
        lines.append(bullet)
        for pg in node["pages"]:
            img = pg["image"].rsplit("/", 1)[-1]
            lines.append(f"{pad}  - `{pg['path'].split('/', 2)[-1]}` · {img}")
        for child in node["children"]:
            render(child, depth + 1)

    render(tree, 0)
    return "\n".join(lines) + "\n"


def _count_pages(node: "dict") -> int:
    return len(node["pages"]) + sum(_count_pages(c) for c in node["children"])
