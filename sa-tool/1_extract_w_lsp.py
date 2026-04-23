import concurrent.futures
import threading
import datetime
import argparse
import subprocess
import json
import uuid
import math
import os
import time
import re
import select
import colored
import debugpy
import threading
import zlib
from typing import List, Dict
import copy
import collections
import queue
import socket
import shutil
import heapq

import tree_sitter_asm as tsasm
import tree_sitter_typescript as tstsx
import tree_sitter_c_sharp as tscsharp
from tree_sitter import Language, Parser


# =========================================================================
# PATCH P5.1 — Synthetic-symbol classifier.
#
# Ghidra, ILSpy, and JADX all emit predictable synthetic names that pollute
# callstacks and var refs when the decompiler output is scanned as source.
# `classify_synthetic(name)` returns a tag (or None) so callers can drop or
# visually fold these in downstream outputs.
#
# Safe-by-default: we only classify; we do NOT filter here. The extractor
# already emits tagging info; the VS Code extension can choose to fold.
# =========================================================================

_SYNTHETIC_PATTERNS = [
    # Ghidra pseudo-C decompilation
    ("ghidra.fn",     re.compile(r"^(?:FUN|SUB|thunk_FUN)_[0-9a-fA-F]{4,}$")),
    ("ghidra.data",   re.compile(r"^(?:DAT|PTR|UNK|s|u)_[0-9a-fA-F]{4,}$")),
    ("ghidra.label",  re.compile(r"^LAB_[0-9a-fA-F]{4,}$")),
    ("ghidra.extern", re.compile(r"^EXT_[0-9a-fA-F]{4,}$")),
    # ILSpy / dnSpy synthetic names (compiler-generated)
    ("ilspy.display", re.compile(r"^<>c__DisplayClass\d")),
    ("ilspy.anon",    re.compile(r"^<>f__AnonymousType\d")),
    ("ilspy.cached",  re.compile(r"^<>9__\d")),
    ("ilspy.closure", re.compile(r"^<>c$")),
    ("ilspy.lambda",  re.compile(r"^<[\w$]+>b__\d")),
    ("ilspy.async",   re.compile(r"^<[\w$]+>d__\d")),
    ("ilspy.priv",    re.compile(r"^<PrivateImplementationDetails>")),
    ("ilspy.method",  re.compile(r"^\$\$method0x[0-9a-fA-F]+$")),
    ("ilspy.tvar",    re.compile(r"^<[\w$]+>j__TPar$")),
    # JADX decompiled APKs
    ("jadx.r",        re.compile(r"^R\$\w+$")),
    ("jadx.lambda",   re.compile(r"\$Lambda\$\d")),
    ("jadx.anon",     re.compile(r"\$\d+$")),
    ("jadx.bridge",   re.compile(r"^access\$\d+$")),
]


def classify_synthetic(name):
    """Return a tag like 'ilspy.display' if `name` is a synthetic decompiler
    identifier, else None. O(len(patterns)) — cheap enough to call per symbol."""
    if not isinstance(name, str) or not name:
        return None
    for tag, pat in _SYNTHETIC_PATTERNS:
        if pat.search(name):
            return tag
    return None


def is_ghidra_decompiled_file(filepath):
    """PATCH P5.3 — detect Ghidra's pseudo-C dump by the distinctive
    `undefined*` typedef block + FUN_XXXX function naming in the first
    ~200 bytes of the associated .h file. Cheap header peek."""
    try:
        if not filepath.endswith((".c", ".h")):
            return False
        # Check matching .h if we were handed a .c
        peek_paths = [filepath]
        if filepath.endswith(".c"):
            peek_paths.append(filepath[:-2] + ".h")
        for p in peek_paths:
            if not os.path.exists(p):
                continue
            with open(p, "rb") as fh:
                head = fh.read(4096)
            text = head.decode("utf-8", errors="replace")
            if "typedef unsigned char" in text and "undefined" in text:
                return True
            if re.search(r"FUN_[0-9a-fA-F]{4,}", text):
                return True
    except OSError:
        return False
    return False


## Global data structuresimport threading
class ThreadSafePriorityQueue:
    def __init__(self):
        self.heap = []
        self.counter = 0
        self.lock = threading.Lock()

    def _priority(self, item: str) -> int:
        if item.startswith("fnsOnly~"):
            return 0   # highest priority
        elif item.startswith("1~"):
            return 1
        elif item.startswith("~"):
            return 2
        else:
            return 3   # lowest priority

    def put(self, item: str):
        with self.lock:
            prio = self._priority(item)
            heapq.heappush(self.heap, (prio, self.counter, item))
            self.counter += 1

    def get(self):
        with self.lock:
            if not self.heap:
                raise IndexError("empty")
            return heapq.heappop(self.heap)[2]

    def peek(self):
        with self.lock:
            if not self.heap:
                raise IndexError("empty")
            return self.heap[0][2]

    def empty(self):
        with self.lock:
            return not self.heap
        with self.lock:
            return len(self.heap) == 0

    def qsize(self) -> int:
        with self.lock:
            return len(self.heap)


class ThreadSafeDict:
    def __init__(self):
        self.lock = threading.Lock()
        self.dict = {}

    def __getitem__(self, key):
        with self.lock:
            return self.dict[key]

    def __setitem__(self, key, value):
        with self.lock:
            self.dict[key] = value

    def __delitem__(self, key):
        with self.lock:
            del self.dict[key]

    
    def get(self, key, default=None):
        with self.lock:
            return self.dict.get(key, default)

    def items(self):
        with self.lock:
            return list(self.dict.items())
        
    def copy(self):
        with self.lock:
            return copy.deepcopy(self.dict)

    def __contains__(self, key):
        with self.lock:
            return key in self.dict

    def setdefault(self, key, default):
        with self.lock:
            return self.dict.setdefault(key, default)

    def __iter__(self):
        with self.lock:
            return iter(list(self.dict))  # or just `iter(self.dict.copy()

    def __len__(self):
        with self.lock:
            return len(self.dict)

    def to_dict(self, values_to_list=False):
        with self.lock:
            ret = copy.deepcopy(self.dict)
            if values_to_list:
                for key, value in ret.items():
                    ret[key] = list(value)
            
            return ret

    def from_dict(self, d, values_to_set=False):
        with self.lock:
            self.dict = dict(d)

            if values_to_set:
                for key, value in self.dict.items():
                    self.dict[key] = set(value)



# only to be used with funcs/scopes with 'id' key
# may cause issues if funcs/scopes have the same id
class ThreadSafeList:
    def __init__(self):
        self._list = []
        self._map = {}  # key = item["id"], value = item
        self._filepath_map = {}  # key = filepath, value = True
        self._lock = threading.Lock()

    def append(self, item):
        with self._lock:
            item_id = item["id"]
            if item_id not in self._map:
                self._list.append(item)
            else:
                # Replace existing in-place
                idx = next(i for i, x in enumerate(self._list) if x["id"] == item_id)
                self._list[idx] = item
            self._map[item_id] = item
            self._filepath_map[item_id.split(",")[-1].split("#")[0]] = True
            
    def extend_by_id(self, items):
        with self._lock:
            for item in items:
                item_id = item["id"]
                if item_id in self._map:
                    # Replace in-place in the list
                    idx = next(i for i, x in enumerate(self._list) if x["id"] == item_id)
                    self._list[idx] = item
                else:
                    self._list.append(item)
                self._map[item_id] = item
                self._filepath_map[item_id.split(",")[-1].split("#")[0]] = True

    def contains_filepath(self, filepath):
        with self._lock:
            return self._filepath_map.get(filepath, False)

    def get(self, index):
        with self._lock:
            return self._list[index]





    # def remove(self, item):
    #     with self._lock:
    #         item_id = item["id"]
    #         self._map.pop(item_id, None)
    #         self._list = [x for x in self._list if x["id"] != item_id]
    ### I don't remove, if we do we need to optimize how filepath references are removed based on remaining list

    def __len__(self):
        with self._lock:
            return len(self._list)

    def __iter__(self):
        with self._lock:
            return iter(self._list[:])
        
    def to_list(self):
        with self._lock:
            return self._list[:]  # shallow copy

    def from_list(self, items):
        with self._lock:
            self._list = items[:]  # shallow copy to avoid reference issues
            self._map = {item["id"]: item for item in self._list}
            self._filepath_map = {item["id"].split(",")[-1].split("#")[0]: True for item in self._list}




g_textHighlights = ThreadSafeDict()
g_function_calls = ThreadSafeDict()
g_class_inheritance = ThreadSafeDict()
g_seen_files = ThreadSafeDict()
g_seen_files_for_refs = ThreadSafeDict()
g_var_ref_map = ThreadSafeDict()
g_functions = ThreadSafeList() # todo
g_scopes = ThreadSafeList()  # todo
g_data_updated = False


opened_file_queues_map = {}
current_script_path = os.path.dirname(os.path.abspath(__file__))


## global funcs
# def push_to_vscode_extension():
#     # python3 /app/2_build_callstacks.py


#     # python3 /app/3_add_decorators.py
#     print("Pushing data to VSCode extension...")
#     try:
#         subprocess.run(["python3", f"{current_script_path}/2_build_callstacks.py"], check=True, cwd=args.project_dir)
#         print("Data pushed successfully.")
#     except subprocess.CalledProcessError as e:
#         print(f"Error pushing data to VSCode extension: {e}")
#         raise 
    
#     os.makedirs(f"{args.project_dir}/.vscode/ext-static-analysis/graphs", exist_ok=True)

#     # # TODO: retain additional decorators/notes from overwritten functions_html.json

#     shutil.copy(f"{args.project_dir}/functions_html.json", f"{args.project_dir}/.vscode/ext-static-analysis/functions_html.json")
#     shutil.copy(f"{args.project_dir}/decorations.json", f"{args.project_dir}/.vscode/ext-static-analysis/decorations.json")
#     shutil.copy(f"{args.project_dir}/callstacks.json", f"{args.project_dir}/.vscode/ext-static-analysis/callstacks.json")
#     shutil.copy(f"{args.project_dir}/scope_summaries_html.json", f"{args.project_dir}/.vscode/ext-static-analysis/scope_summaries_html.json")
#     shutil.copy(f"{args.project_dir}/inheritance_graph.json", f"{args.project_dir}/.vscode/ext-static-analysis/graphs/inheritance_graph.json")

#     try:
#         subprocess.run(["python3", f"{current_script_path}/3_add_decorators.py"], check=True, cwd=args.project_dir)
#         print("Data pushed successfully.")
#     except subprocess.CalledProcessError as e:
#         print(f"Error pushing data to VSCode extension: {e}")
#         raise 


    


def contains_more_than_search_str(s, search_str):
    # Tokenize the string by identifying words and ignoring punctuation
    tokens = re.findall(r'\b\w+\b', s)
    
    # Check if search_str appears as a standalone word using regex
    search_str_occurrences = len(re.findall(rf'\b{re.escape(search_str)}\b', s))
    
    # Return True if there are more words than just the search_str
    return len(tokens) > search_str_occurrences


file_content_map = {}
def get_file_content( filepath, startline=None, endline=None, startchar=None, endchar=None):
    filepath = unquote(filepath)
    try:
        if not file_content_map.get(filepath, None):
            content = []
            try:
                content = open(filepath, 'r').read().split("\n")
            except:
                pass
            file_content_map[filepath] = content


        if not startline:
            return "\n".join(file_content_map[filepath])
        if not endline:
            endline = startline

        
        if startline == endline:
            return file_content_map[filepath][startline][startchar:endchar]
        return "\n".join(file_content_map[filepath][startline:endline])
    except IndexError:
        return ""


def build_func_id_params(uri, line, char):
    obj = {
        "name": "",
        "kind": 6, # method
        "location": {
            "uri": uri,
            "range": {
                "start": {
                    "line": line,
                    "character": char
                },
                "end": {
                    "line": line,
                    "character": char
                }
            }
        }
    }
    return obj









## START arg parsing
class StoreWithDefaultCheck(argparse.Action):
    """Custom action to track if an argument was explicitly provided."""
    def __call__(self, parser, namespace, values, option_string=None):
        # Set the value normally
        setattr(namespace, self.dest, values)
        # Track that the user explicitly provided this argument
        if not hasattr(namespace, "_explicit_args"):
            namespace._explicit_args = set()
        namespace._explicit_args.add(self.dest)

class ArgumentParserWithTracking(argparse.ArgumentParser):
    """Custom ArgumentParser that automatically adds StoreWithDefaultCheck."""
    def add_argument(self, *args, **kwargs):
        # If action is not already specified, use StoreWithDefaultCheck
        if 'action' not in kwargs:
            kwargs['action'] = StoreWithDefaultCheck
        return super().add_argument(*args, **kwargs)

def was_explicitly_passed(arg_name, args):
    """Check if the argument was explicitly provided by the user."""
    return arg_name in getattr(args, "_explicit_args", set())

## END arg parsing


print_lock = threading.Lock()

def print_thread_safe(*args, **kwargs):
    with print_lock:
        print(*args, **kwargs)


def in_scope(path):
    global EXCLUDE_FUNC_CALL_FILEPATHS
    global INCLUDE_FILEPATHS
    return (len(INCLUDE_FILEPATHS) == 0 or any([re.search(p, path, re.IGNORECASE) for p in INCLUDE_FILEPATHS])) and not any([re.search(p, path, re.IGNORECASE) for p in EXCLUDE_FUNC_CALL_FILEPATHS])

def dict_to_frozenset(d):
    """Convert a dictionary to a frozenset of key-value pairs."""
    return frozenset(
        (k, dict_to_frozenset(v) if isinstance(v, dict) else v)
        for k, v in d.items()
    )

def join_and_dedupe(lists):
    """Joins multiple lists of dictionaries and removes duplicates efficiently."""
    seen = set()
    result = []

    # Prepare the data by converting dictionaries to frozensets
    all_items = [item for sublist in lists for item in sublist]

    for item in all_items:
        item_frozenset = dict_to_frozenset(item)
        if item_frozenset not in seen:
            seen.add(item_frozenset)
            result.append(item)

    return result


def lists_are_equivalent(list1: List[Dict], list2: List[Dict]) -> bool:
    """Check if two lists of dictionaries are equivalent, regardless of the order."""
    if len(list1) != len(list2):
        return False

    # Convert each dictionary to a frozenset of key-value pairs
    set1 = {dict_to_frozenset(d) for d in list1}
    set2 = {dict_to_frozenset(d) for d in list2}

    return set1 == set2




import sys
import select

def input_with_timeout(prompt, timeout, default_val=None):
    sys.stdout.write(prompt)
    sys.stdout.flush()

    rlist, _, _ = select.select([sys.stdin], [], [], timeout)
    if rlist:
        return sys.stdin.readline().rstrip("\n")
    else:
        print("\nInput timed out!")
        return default_val


def decrement_line_in_id(f_id):
    s = "#".join(f_id.split("#")[0:-1])
    line = f_id.split("#")[-1]
    new_line = max(0, int(line) - 1)
    return f"{s}#{new_line}"

def increment_lines_in_id(f_id):
    ret = ""
    # f_name_and_filepath 
    ret += "#".join(f_id.split("#")[0:-1])

    start_line, start_col, end_line, end_col = None, None, None, None
    try:
        start_line = f_id.split("#")[-1].split(":")[0]
        start_col = f_id.split("#")[-1].split(":")[1]
        end_line = f_id.split("#")[-1].split(":")[2]
        end_col = f_id.split("#")[-1].split(":")[3]
    except: 
        pass
    
    if start_line:
        ret += f"#{int(start_line) + 1}"
    if start_col:
        ret += f":{int(start_col) + 1}"
    if end_line:
        ret += f":{int(end_line) + 1}"
    if end_col:
        ret += f":{int(end_col) + 1}"
    
    return ret


# from python_jsonrpc_server import dispatchers

# ISSUES: 
# - line / char returned from symbols is not consistant
#   - sometimes need to incremenet line by 1
#   - increment char by 5 or some offset
# - name is not consistant
#   - e.g.: var test = func() => LSP will return `func()` as the name of the function

import bisect
from urllib.parse import unquote



# TODO: Auto install LSP servers based on file extension / code
# mason packages (metadata for install?): https://github.com/mason-org/mason-registry/tree/main/packages
# 

# seconds to periodically pause to let LSP catch up in processing
PAUSE_TIME = .33


global errors
global errors_counter_map
errors = []
errors_counter_map = {}

FUNC_NAME_OFFSET = 0 # 5 (for go)

global EXCLUDE_FUNC_CALL_FILEPATHS
global INCLUDE_FILEPATHS
# EXCLUDE_FUNC_CALL_FILEPATHS = ['/usr/local/go/src', 'mock', 'test', '/accounts', '/appveyor.yml', '/AUTHORS', '/beacon', '/build', '/circle.yml', '/cmd', '/common', '/consensus', '/console', '/COPYING', '/COPYING.LESSER', '/crypto', '/Dockerfile', '/Dockerfile.alltools', '/docs', '/ethclient', '/ethdb', '/ethstats', '/event', '/go.mod', '/go.sum', '/graphql', '/interfaces.go', '/internal', '/log', '/Makefile', '/metrics', '/miner', '/node', '/oss-fuzz.sh', '/p2p', '/params', '/README.md', '/rlp', '/SECURITY.md', '/signer', '/swarm', '/tests', '/trie', '/triedb']
EXCLUDE_FUNC_CALL_FILEPATHS = ['/go/pkg', '/usr/lib/', '/usr/local/go/src', '/venv/', '/python\\d+\\.\\d+/site-packages/', 'mock', 'test', 'cache', 'rustlib', '.cargo', '.gradle', '.d.ts', '.vscode-server', 'node_modules', '.ccls-cache']
EXCLUDE_REF_FILEPATHS = ['.ccls-cache']
INCLUDE_FILEPATHS = []




class LSPClient:
    def __init__(self, 
                language_id, 
                file_extensions, 
                server_cmd,
                force_references=False,
                force_callHierarchy=False,
                max_ref_tracking_count=50,
                disable_get_id_from_ref=False,
                disable_selectionRange=False,
                disable_incoming_calls=False,
                disable_outgoing_calls=False, 
                disable_inheritance=False,
                only_functions=False,
                pause_for_verification=False, 
                guess_ref_read_write=True, 
                resp_pause=0,
                resp_timeout=180,
                init_timeout=45,
                init_pause=2,
                verbose=False,
                stderr_to_file=False,
                ls_file_queue=None,
                streaming_mode=False,
                streaming_mode_disable_recursive_ref_search=False,
                parallel_requests=5
                ):
        self.NUM_THREADS = 6

        self.server_cmd = server_cmd

        self.process = subprocess.Popen(
            self.server_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=open('error_log.txt', 'w'),  # Always capture stderr to surface silent LSP failures (e.g. Solargraph/RuboCop LoadError). clangd also requires file-based stderr (hangs with subprocess.PIPE).
            bufsize=0,
            # shell=True  # TODO: remove if this breaks stuf? What did this fix? c?
        )

        
        
        # https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#textDocumentItem
        self.language_id = language_id
        self.file_extensions = file_extensions
        self.max_ref_tracking_count = max_ref_tracking_count
        self.force_references = force_references
        self.force_callHierarchy = force_callHierarchy
        self.get_id_from_ref = not disable_get_id_from_ref
        self.disable_selectionRange = disable_selectionRange
        self.disable_incoming_calls = disable_incoming_calls
        self.disable_outgoing_calls = disable_outgoing_calls
        self.disable_inheritance = disable_inheritance
        self.only_functions = only_functions
        self.pause_for_verification = pause_for_verification
        self.guess_ref_read_write = guess_ref_read_write
        self.resp_timeout = resp_timeout
        self.resp_pause = resp_pause
        self.init_timeout = init_timeout
        self.init_pause = init_pause
        self._verbose_flag = verbose
        self._verbose_sentinel = None  # set in analyze() once project_dir is known
        self._verbose_sentinel_cached = False
        self._verbose_sentinel_last_check = 0
        self._pause_sentinel = None  # set in analyze() once project_dir is known
        self._pause_sentinel_cached = False
        self._pause_sentinel_last_check = 0
        self.ls_file_queue = ls_file_queue
        self.streaming_mode = streaming_mode
        self.streaming_mode_disable_recursive_ref_search = streaming_mode_disable_recursive_ref_search

        self.parallel_requests = parallel_requests
        self._pending_requests = {}  # id -> {"event": threading.Event(), "response": None}
        self._stdin_lock = threading.RLock()  # RLock because _send_message -> didOpen -> _send_message is reentrant
        self._reader_thread = None
        self._reader_running = False

        self.opened_docs = set()
        self.had_error = False
        self.completed_function_ids = set(decrement_line_in_id(f['id']) for f in g_functions.to_list()) # may need to update to only be local functions?
        self.completed_w_err_function_ids = set()
        self.seen_classes = set()
        self.seen_functions = set()
        self.seen_functions_from_files_ids = set()
        # g_var_ref_map = {}
        self.capabilities = {}
        self.function_call_refs = {} # to be converted to function_calls later
        # self.dispatcher = dispatchers.MethodDispatcher()
        # self.def_to_func_map = {} # map of function definitions to functions
        self.definition_cache = {}
        self.def_to_func_map = {}
        self.function_references = {}
        self.function_details = {}

        if len(g_functions) > 0:
            for f in g_functions.to_list():
                f_id = decrement_line_in_id(f['id'])
                self.function_details[f_id] = { "start_line": f['startLine'] - 1, "end_line": f['endLine'] - 1, "start_char": f['startCol'], "end_char": f['startCol'] }

        # cache
        self.seen_strings = set()
        self.doc_symbols_map = {}
        self.queued_files = set()
        self.evaled_files = set(g_seen_files.to_dict().keys())
        self.seen_files_for_refs = set(g_seen_files_for_refs.to_dict().keys())
        self.last_opened_doc = None
        self.get_function_in_file_cache = {}

        self.seen_textHighlights = []
        # data for color highlighting
        
        main_opacity = "0.3"
        self.colors = [
            f"rgba(139, 0, 0, {main_opacity})",    # darkred
            f"rgba(0, 0, 255, {main_opacity})",    # blue
            f"rgba(0, 100, 0, {main_opacity})",    # darkgreen
            f"rgba(218, 165, 32, {main_opacity})", # goldenrod
            f"rgba(128, 0, 128, {main_opacity})",  # purple
            f"rgba(255, 140, 0, {main_opacity})",  # darkorange
            f"rgba(165, 42, 42, {main_opacity})",  # brown
            f"rgba(0, 139, 139, {main_opacity})",  # darkcyan
            f"rgba(139, 0, 139, {main_opacity})",  # darkmagenta
            f"rgba(0, 128, 128, {main_opacity})",  # teal
            f"rgba(128, 0, 0, {main_opacity})",    # maroon
            f"rgba(0, 0, 128, {main_opacity})",    # navy
            f"rgba(128, 128, 0, {main_opacity})",  # olive
            f"rgba(0, 255, 255, {main_opacity})",  # aqua
            f"rgba(255, 0, 255, {main_opacity})"   # fuchsia
        ]

        if "typescript-language-server" in self.server_cmd[0]: # and "typescript" in self.language_id:
            TSX_LANGUAGE = Language(tstsx.language_tsx()) # tsx should work for ts as well for most cases
            self.parser = Parser(TSX_LANGUAGE)

        if "csharp-ls" in self.server_cmd[0] or "OmniSharp" in self.server_cmd[0]:
            CSHARP_LANGUAGE = Language(tscsharp.language())
            self.parser = Parser(CSHARP_LANGUAGE)

        # OmniSharp native protocol state
        self.is_omnisharp = "OmniSharp" in self.server_cmd[0]
        self._omnisharp_seq = 0
        self._omnisharp_response_cache = {}  # seq -> response data for out-of-order responses

        if "asm-lsp" in self.server_cmd[0]:
            ASM_LANGUAGE = Language(tsasm.language())
            self.parser = Parser(ASM_LANGUAGE)


    @property
    def verbose(self):
        if self._verbose_sentinel:
            now = time.monotonic()
            if now - self._verbose_sentinel_last_check > 2:
                self._verbose_sentinel_cached = os.path.exists(self._verbose_sentinel)
                self._verbose_sentinel_last_check = now
            if self._verbose_sentinel_cached:
                return True
        return self._verbose_flag

    @verbose.setter
    def verbose(self, value):
        self._verbose_flag = value

    @property
    def paused(self):
        if self._pause_sentinel:
            now = time.monotonic()
            if now - self._pause_sentinel_last_check > 2:
                self._pause_sentinel_cached = os.path.exists(self._pause_sentinel)
                self._pause_sentinel_last_check = now
            if self._pause_sentinel_cached:
                return True
        return False

    def wait_if_paused(self):
        if not self.paused:
            return
        print(f"[PAUSED] Scan paused. Remove {self._pause_sentinel} to resume.")
        while self.paused:
            time.sleep(2)
        print("[RESUMED] Scan resumed.")

    def parse_func_objects(self, functions, include_top_level_func=False):
        seen_scopes = set()
        scope_objs = []


        if include_top_level_func:
            for f_id in functions.copy():
                top_level_filepath = f_id.split(",")[-1].split("#")[0]
                top_level_id = f"__TOP_LEVEL__,{top_level_filepath}#0"
                functions.add(top_level_id)
                    
            # TODO: ?? should also get top level of scopes?

        function_objs = []
        for f_id in functions:
            # get real function
            f_id = self.def_to_func_map.get(f_id, f_id)

            functionName = ",".join(f_id.split(",")[:-1])
            if not functionName:
                continue

            path = f_id.split(",")[-1]
            filename = path.split("/")[-1]

            scope_name = path.split("#")[0].split("/")[-1]
            scope_id = f"{scope_name},{path.split('#')[0]}"

            startLine = self.function_details.get(f_id, {}).get('start_line', 0)
            startChar = self.function_details.get(f_id, {}).get('start_char', 0)
            endLine = self.function_details.get(f_id, {}).get('end_line', 0)
            endChar = self.function_details.get(f_id, {}).get('end_char', 0)

            f = {}
            f['id'] = f_id
            f['functionName'] = functionName
            f['scope_id'] = scope_id
            f['scopeName'] = scope_name
            f['functionParameters'] = ""
            f['functionReturns'] = ""
            f['startLine'] = startLine
            f['endLine'] = endLine
            f['startCol'] = startChar
            f['filepath'] = path
            f['filepath_body'] = path
            f['qualifiedName_full'] = f"{filename}.{functionName}"
            f['qualifiedName'] = ""
            f['filename'] = path.split("/")[-1].split("#")[0]
            f['decorator'] = ""
            f['function_notes'] = ""
            f['modifiers'] = []
            f['entrypoint_callstacks'] = []
            f['exit_callstacks'] = []
            f['other_callstacks'] = []
            f['state_vars_summary_html'] = ""
            f['function_summary_html'] = ""
            f['tainted_locations_count'] = 0
            f['tainted_locations_html'] = ""
            f['checkbox_ids_to_check'] = []
            f['is_inherited'] = False
            f['is_shadowed'] = False
            f['additional_info_html'] = ""
            f['called_at'] = list(self.function_references.get(f_id, []))

            function_objs.append(f)




            if scope_id not in seen_scopes:
                seen_scopes.add(scope_id)
                s = {
                    "id": scope_id,
                    "name": scope_name,
                    "type": "file",
                    "state_vars_html": "",
                    "inherits": [],
                    "inherits_recursive": [],
                    "backgroundColor": "",
                    "storage_slots_html": "",
                    "fuzz_testing_html": "",
                    "modifiers_html": "",
                    "functions_html": "",
                    "scope_summary_html": "",
                    "inherits_from": [],
                    "inherits_from_recursive": []
                }
                scope_objs.append(s)


        return function_objs, list(scope_objs)

    def normalize_location_link(self, item):
        """Normalize LocationLink format (targetUri/targetRange/targetSelectionRange) to Location format (uri/range).

        PATCH P2.2 — previously gated on ruby-lsp only. In practice `gopls`,
        `rust-analyzer`, and `clangd` can also return `LocationLink` objects
        for `textDocument/definition` when the client advertises support.
        Making this normaliser unconditional is safe (fast-path returns the
        input unmodified when `targetUri` isn't present)."""
        if isinstance(item, dict):
            # Handle LocationLink -> Location conversion
            if 'targetUri' in item and 'uri' not in item:
                normalized = dict(item)  # shallow copy
                normalized['uri'] = item['targetUri']
                if 'targetRange' in item and 'range' not in item:
                    normalized['range'] = item['targetRange']
                if 'targetSelectionRange' in item and 'selectionRange' not in item:
                    normalized['selectionRange'] = item['targetSelectionRange']
                # Preserve name/kind if present
                return normalized
        return item

    def get_range(self,item):
        item = self.normalize_location_link(item)
        location_base = item['location'] if 'location' in item else item
        location_base = self.normalize_location_link(location_base)
        # java, range: start line 2 -> 4. selectionRange: line start = 17, end = 4 ??????
        range = item['selectionRange'] if 'selectionRange' in location_base and not self.disable_selectionRange else location_base['range']
        return range


    def add_textHighlight(self, color_index, filepath, start_line, start_char, end_char, var_name = ""):
        o = {
                "name": var_name,
                "type": "statevar",
                "line": int(start_line),
                "start": int(start_char),
                "end": int(start_char) + len(var_name)
            }
        o_id = str(o)
        if o_id in self.seen_textHighlights:
            return
        self.seen_textHighlights.append(o_id)

        g_textHighlights \
            .setdefault(filepath.split("#")[0], {}) \
            .setdefault(f"background-color: {self.colors[color_index % len(self.colors)]}", []) \
            .append(o)



    def symbol_to_loc(self, symbol, include_name=False, include_start_char=True):
        symbol = self.normalize_location_link(symbol)
        name = f"{symbol.get('name', '')}," if include_name else ""
        base_location = symbol['location'] if 'location' in symbol else symbol
        base_location = self.normalize_location_link(base_location)
        start_char = f":{self.get_range(symbol)['start']['character']}" if include_start_char else ""
        return f"{name}{base_location['uri'].replace('file://', '')}#{self.get_range(symbol)['start']['line']}{start_char}"
        

    def get_id(self, item, from_def=None): # True fixes Java, False fixes clangd?
        from_def = from_def if from_def is not None else self.get_id_from_ref

        # ISSUE: calling self.get_id() twice will result in bad offset for line number
        item = self.normalize_location_link(item)
        location_base = item['location'] if 'location' in item else item
        location_base = self.normalize_location_link(location_base)
        real_symbol = item

        # if item.get('kind', None) in [6, 9, 12] and not any([p for p in EXCLUDE_FUNC_CALL_FILEPATHS if p.lower() in location_base['uri'].lower()]):
        if item.get('kind', None) in [6, 9, 12] and not any([re.search(p, location_base['uri'], re.IGNORECASE) for p in EXCLUDE_FUNC_CALL_FILEPATHS]):
            # do lookups for functions that are not in excluded paths (downside is we will not get code start/end lines for these functions)
            symbols = self.get_symbols_in_file(location_base['uri'])

            for symbol in symbols:
                symbol_location_base = symbol['location'] if 'location' in symbol else symbol
                if item['name'] in symbol['name'] and self.get_range(location_base)['start']['line'] == self.get_range(symbol_location_base)['start']['line'] and symbol['kind'] in [6, 9, 12]: # method | function | constructor
                    # self.get_range(symbol_location_base)['start']['line'] = self.get_range(location_base)['start']['line'] + 1
                    # self.get_range(symbol_location_base)['end']['line'] = self.get_range(location_base)['end']['line'] + 1
                    real_symbol = symbol
                    break
            # cache doc symbols
            # return func with same name,uri#lineStart
            if not real_symbol:
                # (Go) could be anonymous func?
                # TODO: param `type` if function and no found symbol, return line 0? (maybe not?)
                print("COULD NOT FIND REAL SYMBOL - USING ITEM (source mapping will fail)")
                

        # content = get_file_content(real_symbol_location_base['uri'].replace("file://", ""), self.get_range(real_symbol_location_base)['start']['line'])
        # line_offset = 0
        # if not content.index(f"{real_symbol.get('name', '').split('.')[-1].split('(')[0]}("):
        #     line_offset = 1
        ret_symbol = real_symbol.copy()
        if from_def:
            # should be for functions, thus we parse func name (for Java Language Server)
            ret_symbol = self.get_func_definition(real_symbol)[0]
            ret_symbol['name'] = self.parse_func_name(real_symbol.get('name', "__NO_NAME__"))

            # NOTE: Should we do this for all? c# may need it, or looking at defs by ref... ??
            if "typescript-language-server" in self.server_cmd[0]:
                real_symbol = ret_symbol

        real_symbol_location_base = real_symbol['location'] if 'location' in real_symbol else real_symbol
        real_symbol_location_base = self.normalize_location_link(real_symbol_location_base)
        ret_symbol_location_base = ret_symbol['location'] if 'location' in ret_symbol else ret_symbol
        ret_symbol_location_base = self.normalize_location_link(ret_symbol_location_base)

        range_end_line = real_symbol_location_base['range']['end']['line'] if real_symbol_location_base['range']['end']['line'] > ret_symbol_location_base['range']['end']['line'] else ret_symbol_location_base['range']['end']['line']

        ret_normalized_range = self.get_range(ret_symbol_location_base)
        real_normalized_range = self.get_range(real_symbol_location_base)
        # TODO: validate line number, do we need to add by 1?
        # return f"{real_symbol.get('name', '')},{real_symbol_location_base['uri'].replace('file://', '')}#{self.get_range(real_symbol_location_base)['start']['line'] + line_offset}:{self.get_range(real_symbol_location_base)['start']['character']}:{self.get_range(real_symbol_location_base)['end']['line'] + line_offset}:{self.get_range(real_symbol_location_base)['end']['character']}"

        # start_line = ret_normalized_range['start']['line']
        start_line = ret_normalized_range['start']['line'] if ret_normalized_range['start']['line'] > real_normalized_range['start']['line'] else real_normalized_range['start']['line'] # start_line at latest line to skip comments
        end_line = ret_normalized_range['end']['line'] if ret_normalized_range['end']['line'] > real_normalized_range['end']['line'] else real_normalized_range['end']['line']
        end_line = end_line if end_line > range_end_line else range_end_line
        # TODO: get real start_char (for accurate jump to)
        # start_char = ret_normalized_range['start']['character']
        start_char = ret_normalized_range['start']['character'] if ret_normalized_range['start']['character'] > real_normalized_range['start']['character'] else real_normalized_range['start']['character']
        end_char = ret_normalized_range['end']['character']
        # end_char = end_char if end_char > real_normalized_range['end']['character'] else real_normalized_range['end']['character']

        # TODO: fix self.parse_func_name breaks stuff here for java and maybe other languages, works for powershell
        # id = f"{self.parse_func_name(ret_symbol.get('name', ''))},{location_base['uri'].replace('file://', '')}#{start_line}"
        id = f"{self.parse_func_name(ret_symbol.get('name', ''))},{ret_symbol_location_base['uri'].replace('file://', '')}#{start_line}"

        if not self.function_details.get(id, None) or end_line > self.function_details.get(id, {}).get('end_line', 0):
            self.function_details[id] = {
                "start_line": start_line,
                "end_line": end_line,
                "start_char": start_char,
                "end_char": end_char
            }

        return id
    


    def parse_func_name(self, s):
        # (typescipt?)  s = "deprecate('The multipleResolves event has been deprecated.', 'DEP0160') callback"
        # (go)          s = "(*authTest).Run"
        # NOTE: should be ok if this is ran on a reference name as they should not contain these characters in their name??
        new_func_name = s.split("(")[0].split(".")[-1].split("::")[-1].split("<")[0]
        if new_func_name == "":
            # handle go
            new_func_name = s.split(")")[-1].split(".")[-1].split("::")[-1]
        

        if s not in self.seen_strings and self.verbose:
            print(f"Parsed func names: {s} -> {new_func_name}")
        self.seen_strings.add(s)

        return new_func_name.replace("function ", "").strip()

        # return s.split(".")[-1].split("(")[0]   # works for go?
        # return s.split(".")[-1].split("(")[0]   # works for go?


    # Map LSP method names from registerCapability to capability keys used in initialize response
    LSP_METHOD_TO_CAPABILITY = {
        "textDocument/documentSymbol": "documentSymbolProvider",
        "textDocument/definition": "definitionProvider",
        "textDocument/references": "referencesProvider",
        "textDocument/typeDefinition": "typeDefinitionProvider",
        "callHierarchy/incomingCalls": "callHierarchyProvider",
        "callHierarchy/outgoingCalls": "callHierarchyProvider",
        "textDocument/prepareCallHierarchy": "callHierarchyProvider",
        "typeHierarchy/supertypes": "typeHierarchyProvider",
        "typeHierarchy/subtypes": "typeHierarchyProvider",
        "textDocument/prepareTypeHierarchy": "typeHierarchyProvider",
        "textDocument/completion": "completionProvider",
        "textDocument/hover": "hoverProvider",
        "textDocument/signatureHelp": "signatureHelpProvider",
        "textDocument/formatting": "documentFormattingProvider",
        "textDocument/rename": "renameProvider",
        "textDocument/foldingRange": "foldingRangeProvider",
        "textDocument/codeAction": "codeActionProvider",
        "textDocument/codeLens": "codeLensProvider",
        "textDocument/implementation": "implementationProvider",
        "textDocument/declaration": "declarationProvider",
        "workspace/symbol": "workspaceSymbolProvider",
    }

    def _handle_server_request(self, response):
        """Handle server-to-client requests (messages with 'id' and 'method').
        Returns True if the message was handled (and should be skipped in the receive loop)."""
        method = response.get('method', '')

        if method == 'client/registerCapability':
            registrations = response.get('params', {}).get('registrations', [])
            for reg in registrations:
                reg_method = reg.get('method', '')
                cap_key = self.LSP_METHOD_TO_CAPABILITY.get(reg_method)
                if cap_key:
                    reg_options = reg.get('registerOptions', True)
                    self.capabilities[cap_key] = reg_options if reg_options else True
                    print(f"[registerCapability] {reg_method} -> {cap_key}: {colored.fg('green')}registered{colored.attr('reset')}")
                else:
                    print(f"[registerCapability] {reg_method} (unmapped, ignoring)")

            # ACK the request — server expects a response with matching id
            ack = {"jsonrpc": "2.0", "id": response['id'], "result": None}
            ack_str = json.dumps(ack)
            ack_bytes = ack_str.encode('utf-8')
            header = f"Content-Length: {len(ack_bytes)}\r\n\r\n"
            self.process.stdin.write(header.encode('utf-8') + ack_bytes)
            self.process.stdin.flush()
            return True

        if method == 'window/workDoneProgress/create':
            # ACK progress token creation
            ack = {"jsonrpc": "2.0", "id": response['id'], "result": None}
            ack_str = json.dumps(ack)
            ack_bytes = ack_str.encode('utf-8')
            header = f"Content-Length: {len(ack_bytes)}\r\n\r\n"
            self.process.stdin.write(header.encode('utf-8') + ack_bytes)
            self.process.stdin.flush()
            return True

        return False

    # ── OmniSharp native protocol helpers ──────────────────────────────
    def _omnisharp_send(self, command, arguments):
        """Send an OmniSharp native protocol request and return the response body."""
        self._omnisharp_seq += 1
        seq = self._omnisharp_seq
        msg = json.dumps({"Command": command, "Arguments": arguments, "Seq": seq, "Type": "request"}) + "\n"
        if self.verbose:
            print(f"[omnisharp] >> {command} seq={seq} args={json.dumps(arguments)[:200]}")

        if self._reader_running:
            # Async path: register pending, write, wait on event
            pending = {"event": threading.Event(), "response": None}
            self._pending_requests[seq] = pending
            with self._stdin_lock:
                self.process.stdin.write(msg.encode('utf-8'))
                self.process.stdin.flush()
            if not pending["event"].wait(timeout=self.resp_timeout):
                self._pending_requests.pop(seq, None)
                if self.verbose:
                    print(f"[omnisharp] timeout waiting for {command} seq={seq}")
                return None
            self._pending_requests.pop(seq, None)
            return pending["response"]

        # Drain any buffered responses/events before sending (prevents stale response buildup)
        poll_drain = select.poll()
        poll_drain.register(self.process.stdout, select.POLLIN)
        while True:
            evts = poll_drain.poll(0)  # non-blocking
            if not evts:
                break
            raw = self.process.stdout.readline()
            if not raw:
                break
            # Check if a stale response arrived that we can cache
            try:
                data = json.loads(raw.decode('utf-8', errors='replace').strip())
                if data.get("Type") == "response":
                    self._omnisharp_response_cache[data.get("Request_seq")] = data
            except:
                pass

        self.process.stdin.write(msg.encode('utf-8'))
        self.process.stdin.flush()

        # Check if response was already in the cache (from a previous drain)
        if seq in self._omnisharp_response_cache:
            data = self._omnisharp_response_cache.pop(seq)
            if data.get("Success"):
                return data.get("Body", {})
            else:
                print(f"[omnisharp] {command} failed: {data.get('Message', 'unknown error')}")
                return None

        # Read lines until we get our response
        poll_obj = select.poll()
        poll_obj.register(self.process.stdout, select.POLLIN)
        deadline = time.time() + self.resp_timeout
        while time.time() < deadline:
            events = poll_obj.poll(5000)
            if not events:
                continue
            raw = self.process.stdout.readline()
            if not raw:
                continue
            line = raw.decode('utf-8', errors='replace').strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except Exception as e:
                if self.verbose:
                    print(f"[omnisharp] json parse error: {e} line={line[:100]}")
                continue
            if data.get("Type") == "response":
                if data.get("Request_seq") == seq:
                    if data.get("Success"):
                        return data.get("Body", {})
                    else:
                        if self.verbose:
                            print(f"[omnisharp] {command} seq={seq} failed: success={data.get('Success')} msg={data.get('Message', 'unknown error')[:200]}")
                        return None
                else:
                    # Cache stale response for potential future use
                    self._omnisharp_response_cache[data.get("Request_seq")] = data
            # Skip events (log, diagnostics, etc.)
        if self.verbose:
            print(f"[omnisharp] timeout waiting for {command} seq={seq}")
        return None

    def _omnisharp_wait_started(self):
        """Wait for OmniSharp to fully initialize: start, load projects, compile.

        Strategy: purely idle-based. OmniSharp emits events continuously while
        working (ProjectAdded, log, ProjectConfiguration, etc.). When it goes
        silent for `init_timeout` seconds, it's done. No hard cap — large
        solutions just take longer. One quick probe at the end to verify.
        """
        idle_timeout = self.init_timeout  # seconds of silence = done
        print(f"[omnisharp] waiting for server to start (idle_timeout={idle_timeout}s)...")

        # Phase 1: Wait for "started" event
        projects = []
        started = False
        last_msg = time.time()
        while True:
            idle = time.time() - last_msg
            if idle >= idle_timeout:
                print(f"[omnisharp] no 'started' event after {idle_timeout}s of silence, proceeding...")
                break
            poll = select.poll()
            poll.register(self.process.stdout, select.POLLIN)
            events = poll.poll(5000)
            if not events:
                continue
            line = self.process.stdout.readline().decode('utf-8').strip()
            if not line:
                continue
            last_msg = time.time()
            try:
                data = json.loads(line)
            except:
                continue
            if data.get("Event") == "started":
                print("[omnisharp] server started")
                started = True
                break
            elif data.get("Event") == "log":
                msg = data.get("Body", {}).get("Message", "")
                if "failed" in msg.lower() or "error" in msg.lower():
                    print(f"[omnisharp] {msg[:200]}")

        # Phase 2: Wait for all events to stop (project loading + Roslyn compilation).
        # Reset idle timer on every message from OmniSharp.
        print(f"[omnisharp] waiting for project loading and compilation (idle_timeout={idle_timeout}s)...")
        last_msg = time.time()
        last_heartbeat = time.time()
        project_set = set()  # deduplicate project names
        while True:
            idle = time.time() - last_msg
            if idle >= idle_timeout:
                break
            # Print heartbeat every 30s so user knows we're still waiting
            if time.time() - last_heartbeat >= 30:
                print(f"[omnisharp] waiting for init (silence: {idle:.1f}s / {idle_timeout}s, {len(project_set)} projects loaded)...")
                last_heartbeat = time.time()
            poll = select.poll()
            poll.register(self.process.stdout, select.POLLIN)
            events = poll.poll(5000)
            if not events:
                continue
            line = self.process.stdout.readline().decode('utf-8').strip()
            if not line:
                continue
            last_msg = time.time()  # reset idle timer on ANY message
            try:
                data = json.loads(line)
                # Count projects from any relevant event type
                proj_name = None
                event_type = data.get("Event", "")
                if event_type == "ProjectAdded":
                    proj = data.get("Body", {}).get("MsBuildProject", {})
                    proj_name = proj.get("AssemblyName", "?")
                elif event_type == "MsBuildProjectDiagnostics":
                    body = data.get("Body", {})
                    diag_file = body.get("FileName", "?").split("/")[-1]
                    errors = body.get("Errors", [])
                    warnings = body.get("Warnings", [])
                    if errors:
                        print(f"[omnisharp] BUILD ERRORS in {diag_file}: {len(errors)} error(s)")
                        for e in errors[:3]:
                            print(f"[omnisharp]   {e.get('Message', str(e))[:150]}")
                    if warnings and self.verbose:
                        print(f"[omnisharp] BUILD WARNINGS in {diag_file}: {len(warnings)} warning(s)")
                elif event_type == "ProjectConfiguration":
                    pass  # silently count — too noisy to log
                elif event_type == "error":
                    err_body = data.get("Body", "")
                    if err_body:
                        print(f"[omnisharp] EVENT ERROR: {str(err_body)[:200]}")
                elif event_type == "log":
                    msg = data.get("Body", {}).get("Message", "")
                    level = data.get("Body", {}).get("LogLevel", "")
                    # OmniSharp logs "Adding project '/path/to/foo.csproj'" when loaded
                    if "Adding project '" in msg:
                        proj_name = msg.split("Adding project '")[1].split("'")[0]
                    if level in ("ERROR", "CRITICAL"):
                        print(f"[omnisharp] ERROR: {msg[:200]}")
                    elif level == "WARNING":
                        print(f"[omnisharp] WARN: {msg[:200]}")
                if proj_name and proj_name not in project_set:
                    project_set.add(proj_name)
                    if len(project_set) == 1:
                        print(f"[omnisharp] first project loaded: {proj_name.split('/')[-1]}")
                    elif len(project_set) % 50 == 0:
                        print(f"[omnisharp] loaded {len(project_set)} projects...")
            except:
                pass
        projects = list(project_set)
        print(f"[omnisharp] {len(projects)} projects loaded, OmniSharp idle for {idle_timeout}s — assuming ready.")

        # Validate that OmniSharp loaded projects
        if len(projects) == 0:
            print("[omnisharp] WARNING: 0 projects loaded — OmniSharp cannot resolve symbols.")
            print("[omnisharp] Check that a valid .sln exists and FrameworkPathOverride is set.")
            print("[omnisharp] Falling back to csharp-ls (Roslyn)...")
            self.process.terminate()
            self.process.wait()
            self.is_omnisharp = False
            self.server_cmd = ["/usr/local/bin/csharp-ls"]
            self.process = subprocess.Popen(
                self.server_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=open('error_log.txt', 'w') if self.verbose else open('/dev/null', 'w'),
                bufsize=0,
            )
            return

        # Phase 3: One quick probe to verify symbols resolve.
        _probe_dir = None
        for i, arg in enumerate(self.server_cmd):
            if arg == "-s" and i + 1 < len(self.server_cmd):
                _probe_dir = os.path.dirname(self.server_cmd[i + 1])
                break
        if not _probe_dir:
            print("[omnisharp] probe SKIPPED: cannot determine project directory")
            return

        _skip_names = {'AssemblyInfo.cs', 'GlobalSuppressions.cs', 'Resources.Designer.cs'}
        _skip_dir_parts = {'/obj/', '/bin/', '/Properties/'}
        cs_files = []
        for root, dirs, files in os.walk(_probe_dir):
            dirs[:] = [d for d in dirs if d not in ('obj', 'bin')]
            for f in files:
                if f.endswith('.cs') and f not in _skip_names and 'AssemblyAttributes' not in f:
                    fpath = os.path.join(root, f)
                    if not any(sp in fpath for sp in _skip_dir_parts):
                        cs_files.append(fpath)
                        if len(cs_files) >= 10:
                            break
            if len(cs_files) >= 10:
                break

        probe_ok = False
        _saved_resp_timeout = self.resp_timeout
        self.resp_timeout = 10  # short timeout for probes — we retry anyway
        # Probe with retries — Roslyn compilation may still be running after
        # OmniSharp goes silent (it doesn't emit events during compilation).
        # Try each probe file up to max_retries_per_file times before moving to the next.
        # If no file works after trying all, warn and proceed anyway.
        max_retries_per_file = 60  # 60 retries * 5s = 5 min per file
        print(f"[omnisharp] probing for semantic readiness ({len(cs_files)} candidate files, "
              f"{max_retries_per_file * 5}s max per file)...")
        _probe_start = time.time()
        _total_probes = 0
        for _probe_file in cs_files:
            for _retry in range(max_retries_per_file):
                _total_probes += 1
                body = self._omnisharp_send("/v2/codestructure", {"FileName": _probe_file})
                if body and body.get("Elements"):
                    elapsed = int(time.time() - _probe_start)
                    print(f"[omnisharp] probe OK: {_probe_file.split('/')[-1]} returned "
                          f"{len(body['Elements'])} elements (after {_total_probes} probes, {elapsed}s)")
                    probe_ok = True
                    break
                else:
                    if _retry == 0 or (_retry + 1) % 10 == 0:
                        elapsed = int(time.time() - _probe_start)
                        print(f"[omnisharp] probe #{_total_probes} ({elapsed}s): "
                              f"{_probe_file.split('/')[-1]} — waiting for Roslyn...")
                    time.sleep(5)
            if probe_ok:
                break
            else:
                elapsed = int(time.time() - _probe_start)
                print(f"[omnisharp] probe: {_probe_file.split('/')[-1]} failed after "
                      f"{max_retries_per_file} retries ({elapsed}s), trying next file...")
        self.resp_timeout = _saved_resp_timeout  # restore
        if not probe_ok:
            elapsed = int(time.time() - _probe_start)
            print(f"[omnisharp] probe FAILED: none of {len(cs_files)} files returned elements "
                  f"after {_total_probes} probes ({elapsed}s)")
            print("[omnisharp] OmniSharp may have failed to compile this solution.")
            print("[omnisharp] Check for duplicate AssemblyName projects or circular dependencies.")
            print("[omnisharp] Proceeding anyway — extraction will work for tree-sitter parsed functions.")

    def _omnisharp_quickfixes_to_lsp(self, quickfixes):
        """Convert OmniSharp QuickFixes array to LSP Location array."""
        if not quickfixes:
            return []
        results = []
        for qf in quickfixes:
            fname = qf.get("FileName", "")
            if not fname:
                continue
            results.append({
                "uri": f"file://{fname}",
                "range": {
                    "start": {"line": qf.get("Line", 1) - 1, "character": qf.get("Column", 1) - 1},
                    "end": {"line": qf.get("EndLine", qf.get("Line", 1)) - 1, "character": qf.get("EndColumn", qf.get("Column", 1)) - 1}
                }
            })
        return results

    def _omnisharp_symbols_to_lsp(self, quickfixes):
        """Convert OmniSharp /findsymbols QuickFixes to LSP DocumentSymbol array."""
        KIND_MAP = {"Method": 6, "Constructor": 9, "Class": 5, "Interface": 11, "Property": 7,
                    "Field": 8, "Enum": 10, "Struct": 23, "Event": 24, "Delegate": 5, "EnumMember": 22}
        if not quickfixes:
            return []
        results = []
        for qf in quickfixes:
            fname = qf.get("FileName", "")
            kind_str = qf.get("Kind", "Method")
            line = qf.get("Line", 1) - 1
            col = qf.get("Column", 1) - 1
            end_line = qf.get("EndLine", qf.get("Line", 1)) - 1
            end_col = qf.get("EndColumn", qf.get("Column", 1)) - 1
            rng = {"start": {"line": line, "character": col}, "end": {"line": end_line, "character": end_col}}
            results.append({
                "name": qf.get("Text", ""),
                "kind": KIND_MAP.get(kind_str, DEFAULT_KIND),
                "location": {"uri": f"file://{fname}", "range": rng},
                "range": rng,
                "selectionRange": rng
            })
        return results
    def _omnisharp_send_lsp(self, method, params):
        """Translate an LSP method+params to OmniSharp native protocol and return LSP-shaped response."""
        # Extract file/line/col from LSP params (handles both textDocument and item formats)
        td = params.get("textDocument", params.get("item", {}))
        uri = td.get("uri", "")
        fname = uri.replace("file://", "") if uri else ""
        pos = params.get("position", {})
        line = pos.get("line", 0) + 1   # LSP 0-based -> OmniSharp 1-based
        col = pos.get("character", 0) + 1
        loc_args = {"FileName": fname, "Line": line, "Column": col}

        if method == "initialize":
            # No handshake for OmniSharp — return synthetic capabilities
            return {"result": {"capabilities": {
                "documentSymbolProvider": True, "definitionProvider": True,
                "referencesProvider": True, "implementationProvider": True,
            }}}

        if method == "textDocument/documentSymbol":
            # Use /codestructure for per-file symbols — returns all symbol types
            # including fields/properties for variable tracking in secondary pass
            body = self._omnisharp_send("/v2/codestructure", {"FileName": fname})
            if body and "Elements" in body:
                return {"result": self._omnisharp_codestructure_to_symbols(body["Elements"], fname)}
            # Fallback: /findsymbols filtered by file
            body = self._omnisharp_send("/findsymbols", {"Filter": "", "MinFilterLength": 0})
            if body:
                all_syms = body.get("QuickFixes", [])
                file_syms = [s for s in all_syms if s.get("FileName", "") == fname]
                return {"result": self._omnisharp_symbols_to_lsp(file_syms)}
            return {"result": []}

        if method == "textDocument/references":
            body = self._omnisharp_send("/findusages", loc_args)
            if body:
                return {"result": self._omnisharp_quickfixes_to_lsp(body.get("QuickFixes", []))}
            return {"result": []}

        if method == "textDocument/definition":
            body = self._omnisharp_send("/gotodefinition", loc_args)
            if body and body.get("FileName"):
                return {"result": self._omnisharp_quickfixes_to_lsp([body])}
            return {"result": []}

        if method == "textDocument/implementation":
            body = self._omnisharp_send("/findimplementations", loc_args)
            if body:
                return {"result": self._omnisharp_quickfixes_to_lsp(body.get("QuickFixes", []))}
            return {"result": []}

        # callHierarchy/typeHierarchy — not supported, return empty
        if "callHierarchy" in method or "typeHierarchy" in method:
            return {"result": []}

        # Default: unsupported method
        if self.verbose:
            print(f"[omnisharp] unsupported LSP method: {method}")
        return {"result": []}

    def _omnisharp_codestructure_to_symbols(self, elements, fname, depth=0):
        """Convert OmniSharp /v2/codestructure elements to LSP DocumentSymbol array."""
        # LSP SymbolKind: 5=class, 6=method, 7=property, 8=field, 9=constructor,
        # 10=enum, 11=interface, 14=constant, 22=enumMember, 23=struct, 24=event, 25=operator
        # NOTE: default is 13 (variable) — NOT 6 (method), so unknown kinds don't leak
        # into call graph analysis which filters on kind in [6, 9, 12]
        KIND_MAP = {"class": 5, "interface": 11, "struct": 23, "enum": 10, "method": 6,
                    "constructor": 9, "property": 7, "field": 8, "event": 24, "delegate": 5,
                    "enumMember": 22, "namespace": 3, "constant": 14, "operator": 25}
        DEFAULT_KIND = 13  # variable — won't match method filters [6, 9, 12]
        results = []
        for el in (elements or []):
            kind_str = el.get("Kind", "method").lower()
            name = el.get("DisplayName", el.get("Name", ""))
            ranges = el.get("Ranges", {}) or {}
            full = ranges.get("full", ranges.get("name", {}))
            children = el.get("Children", [])

            # Some elements (namespaces) have no Ranges — just recurse into children
            if not full:
                child_syms = self._omnisharp_codestructure_to_symbols(children, fname, depth + 1)
                # Wrap namespace as a symbol with children if it has a name
                if name and child_syms:
                    sym = {"name": name, "kind": KIND_MAP.get(kind_str, 3), "_omnisharp_kind": kind_str, "children": child_syms}
                    results.append(sym)
                else:
                    results.extend(child_syms)
                continue

            name_range = ranges.get("name", full)
            start_line = full.get("Start", {}).get("Line", 1) - 1
            start_col = full.get("Start", {}).get("Column", 1) - 1
            end_line = full.get("End", {}).get("Line", start_line + 2) - 1
            end_col = full.get("End", {}).get("Column", 1) - 1
            name_start_line = name_range.get("Start", {}).get("Line", start_line + 1) - 1
            name_start_col = name_range.get("Start", {}).get("Column", start_col + 1) - 1
            rng = {"start": {"line": start_line, "character": start_col}, "end": {"line": end_line, "character": end_col}}
            sel_rng = {"start": {"line": name_start_line, "character": name_start_col}, "end": {"line": name_start_line, "character": name_start_col + len(name)}}
            sym = {
                "name": name,
                "kind": KIND_MAP.get(kind_str, DEFAULT_KIND),
                "_omnisharp_kind": kind_str,
                "location": {"uri": f"file://{fname}", "range": rng},
                "range": rng,
                "selectionRange": sel_rng
            }
            if children:
                sym["children"] = self._omnisharp_codestructure_to_symbols(children, fname, depth + 1)
            results.append(sym)
        return results
    # ── End OmniSharp helpers ──────────────────────────────────────────

    def print_requried_capabilities(self):
        REQUIRED_CAPABILITIIS = ["documentSymbolProvider", "definitionProvider", "referencesProvider", "callHierarchyProvider", "typeHierarchyProvider"]
        # print colored text based on capability
        for cap in REQUIRED_CAPABILITIIS:
            if self.capabilities.get(cap, False):
                print(f"{cap}: {colored.fg('green')}{self.capabilities.get(cap, False)}{colored.attr('reset')}")
            else:
                print(f"{cap}: {colored.fg('red')}{self.capabilities.get(cap, False)}{colored.attr('reset')}")
            
    def poll_and_reboot_LSP(self):
        self.process.poll()
        if self.process.returncode is not None:
            print("Process has terminated, rebooting")
            self.process = subprocess.Popen(
                self.server_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=0
            )
            if self.is_omnisharp:
                self._omnisharp_wait_started()
            else:
                response = self.send_request("initialize", self.init_params)
                print("Initialize response:", response)

                self.send_notification("initialized", {})

                self.wait_for_initialization()

            # for doc in self.opened_docs:
            #     did_open_params = {
            #         "textDocument": {
            #             "uri": doc
            #         }
            #     }
            #     self.send_notification("textDocument/didOpen", did_open_params)
            return True
        return False
    
    def send_request(self, method, params):
        global errors

        # ── OmniSharp native protocol path ──
        if self.is_omnisharp:
            return self._omnisharp_send_lsp(method, params)

        id = str(uuid.uuid4())
        message = {
            "jsonrpc": "2.0",
            "id": id,
            "method": method,
            "params": params
        }

        # skip if more than X errors in page w/ same method
        ERROR_LIMIT = 3
        error_key = f"{message['params']['item']['uri'] if 'item' in message['params'] else ''};{message['method']}"
        if errors_counter_map.get(error_key, 0) > ERROR_LIMIT: # seen same error in file > X times
            response = {'result': "", 'error': {'message': 'skipped - too many errors'}}
            return response

        if self._reader_running:
            # Async path: register pending, write, wait on event
            pending = {"event": threading.Event(), "response": None}
            self._pending_requests[id] = pending
            with self._stdin_lock:
                self._send_message(message)
            if not pending["event"].wait(timeout=self.resp_timeout):
                self._pending_requests.pop(id, None)
                response = {'result': '', 'error': {'message': 'timeout'}}
            else:
                response = pending["response"]
                self._pending_requests.pop(id, None)
        else:
            # Synchronous path (during init)
            self._send_message(message)
            # time.sleep(.1)
            response = self._receive_response(id)

        if method == "initialize" and not 'error' in response and response['result'].get('capabilities', None):
            self.capabilities = response['result']['capabilities']
            self.print_requried_capabilities()

            if self.pause_for_verification:
                input("Press Enter to continue...")


        if response.get('error'):
            errors.append(message)
            # print last 10 errors, adding newline for each 
            if self.verbose:
                x = 10
                print(f"Last {x} Errors: ", "\n\t".join([e['method'] for e in errors[-x:]]))
            # always count errors so repeated failures on the same uri+method get skipped after ERROR_LIMIT
            errors_counter_map[error_key] = errors_counter_map.get(error_key, 0) + 1
            is_content_modified_error = response.get('error', {}).get('message') == "content modified"
            if response['error'].get('message', "") in ["no views", "reboot", "timeout"] or is_content_modified_error:
                # had_error state variable to retry, removing because retrying a request that crashes LSP will result in infinite loop
                # self.had_error = True

                # get uri and handle errors and non existant key
                # uri = ""
                # if 'textDocument' in params:
                #     uri = params['textDocument']['uri']
                # elif 'item' in params:
                #     uri = params['item']['uri']

                # did_open_params = {
                #     "textDocument": {
                #         "uri": uri,
                #         "languageId": self.language_id,
                #         "version": 1,
                #         "text": open(uri.replace("file://", ""), 'r').read()
                #     }
                # }
                # print("ERR: resending didOpen")
                # self.send_notification("textDocument/didOpen", did_open_params)
                id = str(uuid.uuid4())
                message['id'] = id
                if self._reader_running:
                    pending = {"event": threading.Event(), "response": None}
                    self._pending_requests[id] = pending
                    with self._stdin_lock:
                        self._send_message(message)
                    if not pending["event"].wait(timeout=self.resp_timeout):
                        self._pending_requests.pop(id, None)
                        response = {'result': '', 'error': {'message': 'timeout'}}
                    else:
                        response = pending["response"]
                        self._pending_requests.pop(id, None)
                else:
                    self._send_message(message)
                    response = self._receive_response(id)

        if self.verbose or response.get('error'):
            print("response: ", response, "\n")

        # if method == "textDocument/documentSymbol":
        #     for loc in response.get('result', []):
        #         loc['location']['range']['start']['line'] += 1
        #         loc['location']['range']['end']['line'] += 1

        return response

    def send_request_async(self, method, params):
        """Send an LSP request without waiting for the response. Returns (id, pending) or None on skip.
        Call collect_response(id, pending) to get the result later.
        Only works when background reader is running. Falls back to synchronous otherwise."""
        if not self._reader_running:
            return None

        if self.is_omnisharp:
            # OmniSharp async: translate LSP method to native command and fire without waiting
            td = params.get("textDocument", params.get("item", {}))
            uri = td.get("uri", "")
            fname = uri.replace("file://", "") if uri else ""
            pos = params.get("position", {})
            line = pos.get("line", 0) + 1  # LSP 0-based -> OmniSharp 1-based
            col = pos.get("character", 0) + 1
            loc_args = {"FileName": fname, "Line": line, "Column": col}

            if method == "textDocument/definition":
                cmd = "/gotodefinition"
            elif method == "textDocument/references":
                cmd = "/findusages"
            elif method == "callHierarchy/incomingCalls":
                cmd = "/findusages"  # OmniSharp approximation
            elif method == "callHierarchy/outgoingCalls":
                cmd = "/findusages"
            else:
                return None  # Unsupported method for async

            self._omnisharp_seq += 1
            seq = self._omnisharp_seq
            msg = json.dumps({"Command": cmd, "Arguments": loc_args, "Seq": seq, "Type": "request"}) + "\n"
            pending = {"event": threading.Event(), "response": None}
            self._pending_requests[seq] = pending
            with self._stdin_lock:
                self.process.stdin.write(msg.encode('utf-8'))
                self.process.stdin.flush()
            return (seq, pending)

        global errors
        id = str(uuid.uuid4())
        message = {
            "jsonrpc": "2.0",
            "id": id,
            "method": method,
            "params": params
        }

        # Skip if too many errors for this uri+method
        ERROR_LIMIT = 3
        error_key = f"{message['params']['item']['uri'] if 'item' in message['params'] else ''};{message['method']}"
        if errors_counter_map.get(error_key, 0) > ERROR_LIMIT:
            return None

        pending = {"event": threading.Event(), "response": None}
        self._pending_requests[id] = pending
        with self._stdin_lock:
            self._send_message(message)
        return (id, pending)

    def collect_response(self, async_handle):
        """Wait for and return the response from a send_request_async call."""
        if async_handle is None:
            return {'result': '', 'error': {'message': 'skipped'}}

        id, pending = async_handle
        if not pending["event"].wait(timeout=self.resp_timeout):
            self._pending_requests.pop(id, None)
            return {'result': '', 'error': {'message': 'timeout'}}

        response = pending["response"]
        self._pending_requests.pop(id, None)

        if response is None:
            return {'result': '', 'error': {'message': 'no response'}}

        if self.is_omnisharp and isinstance(response, dict):
            # OmniSharp bg reader stores raw Body dict — wrap in LSP format
            # /gotodefinition returns Definitions, /findusages returns QuickFixes
            defs = response.get("Definitions", [])
            qf = response.get("QuickFixes", [])
            if defs:
                # Convert OmniSharp Definitions to LSP Location format
                result = []
                for d in defs:
                    result.append({
                        "uri": "file://" + d.get("FileName", ""),
                        "range": {
                            "start": {"line": d.get("Line", 1) - 1, "character": d.get("Column", 1) - 1},
                            "end": {"line": d.get("EndLine", d.get("Line", 1)) - 1, "character": d.get("EndColumn", d.get("Column", 1)) - 1}
                        }
                    })
                return {"result": result}
            elif qf:
                result = []
                for q in qf:
                    result.append({
                        "uri": "file://" + q.get("FileName", ""),
                        "range": {
                            "start": {"line": q.get("Line", 1) - 1, "character": q.get("Column", 1) - 1},
                            "end": {"line": q.get("EndLine", q.get("Line", 1)) - 1, "character": q.get("EndColumn", q.get("Column", 1)) - 1}
                        }
                    })
                return {"result": result}
            else:
                return {"result": []}

        return response

    def send_notification(self, method, params):
        if self.is_omnisharp:
            return  # OmniSharp auto-indexes all files; no didOpen/didClose needed
        if method == "textDocument/didOpen":
            # close last doc if new doc is opened
            if self.last_opened_doc:
                # close last opened doc
                did_close_params = {
                    "textDocument": {
                        "uri": self.last_opened_doc
                    }
                }

                self.send_notification("textDocument/didClose", did_close_params)
            self.last_opened_doc = params['textDocument']['uri']             


        message = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params
        }
        self._send_message(message)

        if method == "textDocument/didOpen" and params['textDocument']['uri'] not in self.opened_docs:
            print("opened doc: ", params['textDocument']['uri'])
            self.opened_docs.add(params['textDocument']['uri'])
            time.sleep(PAUSE_TIME) # wait for server to settle (process opening new doc), was receiving empty results when querying too fast after opening a new doc
            

    def _send_message(self, message):
        with self._stdin_lock:
            if self.is_omnisharp:
                # OmniSharp native protocol: newline-delimited JSON, no Content-Length
                message_str = json.dumps(message) + "\n"
                self.process.stdin.write(message_str.encode('utf-8'))
                self.process.stdin.flush()
                return
            if message['method'] != "textDocument/didOpen" and message['method'] != "textDocument/didClose":
                # if file is not opened, open it
                req_filepath = message.get('params', {}).get('textDocument', {}).get('uri', self.last_opened_doc)
                if req_filepath != self.last_opened_doc:
                    content = ""
                    try:
                        content = open(unquote(req_filepath.replace("file://", "")), 'r', encoding='utf-8').read()
                    except:
                        pass

                    # Send didOpen notification
                    did_open_params = {
                        "textDocument": {
                            "uri": req_filepath,
                            "languageId": self.language_id,
                            "version": 1,
                            "text": content
                        }
                    }
                    self.send_notification("textDocument/didOpen", did_open_params)


            if self.verbose:
                print("\nLast opened doc: ", self.last_opened_doc)
                print("request: ", message)

            message_str = json.dumps(message)
            message_bytes = message_str.encode('utf-8')
            header = f"Content-Length: {len(message_bytes)}\r\n\r\n"
            self.process.stdin.write(header.encode('utf-8') + message_bytes)
            self.process.stdin.flush()

    def _receive_response(self, id=None, timeout=None):
        # if did not reboot, keep waiting for response (may result in infinite loop if server never responds)
        while True:
            # check if process is running or defunct
            headers = self._read_headers(timeout=timeout)

            if 'Content-Length' not in headers:
                # log failures?
                print("Error: no content length in headers")
                time.sleep(2) # wait for server to settle
                did_reboot = self.poll_and_reboot_LSP()
                if did_reboot:
                    response = {'result': "", 'error': {'message': 'reboot'}}
                else:
                    response = {'result': "", 'error': {'message': 'timeout'}}

                # break, will retry again
                break


            content_length = int(headers.get('Content-Length', 0))

            # if content_length == 0:
            #     # WARNING: will loop forever if server crashes 
            #     continue

            body = b''
            while True:
                body += self.process.stdout.read(content_length - len(body))
                if len(body) == content_length:
                    break
            if self.verbose:
                print("b: ", body)

            try:
                response = json.loads(body)
            except:
                print("Error parsing response, defulting to null: ", body)
                did_reboot = self.poll_and_reboot_LSP()
                response = {'result': ""}
                break

            # Handle server-to-client requests (registerCapability, workDoneProgress, etc.)
            if 'method' in response and 'id' in response:
                if self._handle_server_request(response):
                    continue  # handled, keep waiting for our actual response

            if id:
                if response.get('id') == id:
                    if self.verbose:
                        print("matched request/response") 
                    break
            else:
                # loop until not publishing diagnostics
                if response.get('method') not in ["textDocument/publishDiagnostics"]:
                    break
            
        
        time.sleep(self.resp_pause)
        return response

    def _read_headers(self, timeout = None):
        # def read_with_timeout(process, timeout):
        #     poll = select.poll()
        #     poll.register(process.stdout, select.POLLIN)
        #     events = poll.poll(timeout * 1000)  # timeout in milliseconds

        #     if events:
        #         return process.stdout.readline().decode('utf-8').strip()
        #     else:
        #         # raise TimeoutError("Read operation timed out")
        #         print("Read operation timed out")
        #         return ""

        def read_with_timeout(process, timeout):
            poll = select.poll()
            poll.register(process.stdout, select.POLLIN)
            start_time = time.time()

            while (time.time() - start_time) < timeout:
                events = poll.poll(5000)

                if events:
                    s = process.stdout.readline().decode('utf-8').strip()
                    if self.verbose:
                        print("s: ", s)
                    return s
                
                did_reboot = process.returncode is not None
                if did_reboot:
                    print("server rebooted, retrying")
                    # force exit if server rebooted, no longer neeed to wait for response. Check if return value should be changed to retry (returning "" for now)
                    return ""
            
            print("Read operation timed out")
            return ""





        headers = {}
        lines = []
        while True:
            # rust-analyzer (rust) took 2.25min to return results for callHierarchy/incomingCalls
            line = read_with_timeout(self.process, timeout if timeout else self.resp_timeout)  
            if line == "":
                break
            lines.append(line)
            try: 
                key, value = line.split(": ", 1)
                # hacky solution for gopls issue
                # joining messages without newline: e.x., 
                # '{"jsonrpc":"2.0","method":"window/logMessage","params":{"type":3,"message":"2024/06/21 17:00:30 go/packages.Load #46\\n\\tsnapshot=162\\n\\tdirectory=file://~/tools/slither-custom-tooling/genaric/lsp/go/go-ethereum\\n\\tpackage=\\"github.com/ethereum/go-ethereum/core/forkid\\"\\n\\tfiles=[~/tools/slither-custom-tooling/genaric/lsp/go/go-ethereum/core/forkid/forkid.go]\\n"}}Content-Length: 665'
                # am I not flushing the buffer correctly to accomodate log messages?
                headers[key] = value
            except Exception as e:
                print("Error reading headers: ", e, line)
        return headers

    # ── Background reader for concurrent LSP requests ──────────────────
    def _start_background_reader(self):
        """Start background thread that reads LSP responses and dispatches to waiting callers."""
        if self._reader_running:
            return
        self._reader_running = True
        self._reader_thread = threading.Thread(target=self._background_reader_loop, daemon=True)
        self._reader_thread.start()

    def _stop_background_reader(self):
        """Stop the background reader and signal all pending requests."""
        self._reader_running = False
        if self._reader_thread:
            self._reader_thread.join(timeout=5)
            self._reader_thread = None
        # Signal any remaining pending requests with error
        for req_id, entry in list(self._pending_requests.items()):
            if not entry["event"].is_set():
                entry["response"] = {"result": "", "error": {"message": "reader stopped"}}
                entry["event"].set()

    def _background_reader_loop(self):
        """Continuously read from LSP stdout and dispatch responses."""
        while self._reader_running:
            try:
                if self.is_omnisharp:
                    self._bg_read_omnisharp()
                else:
                    self._bg_read_lsp()
            except Exception as e:
                if self._reader_running:
                    print(f"[background reader] error: {e}")
                    time.sleep(0.1)

    def _bg_read_lsp(self):
        """Read one LSP message (Content-Length framed) and dispatch."""
        poll = select.poll()
        poll.register(self.process.stdout, select.POLLIN)
        events = poll.poll(1000)  # 1s poll interval
        if not events:
            return

        # Read headers
        headers = {}
        while True:
            line = self.process.stdout.readline().decode('utf-8').strip()
            if not line:
                break  # empty line = end of headers
            if ": " in line:
                key, value = line.split(": ", 1)
                headers[key] = value

        if 'Content-Length' not in headers:
            return

        content_length = int(headers['Content-Length'])
        body = b''
        while len(body) < content_length:
            body += self.process.stdout.read(content_length - len(body))

        try:
            response = json.loads(body)
        except:
            return

        # Server-to-client request (registerCapability, etc.)
        if 'method' in response and 'id' in response:
            with self._stdin_lock:
                self._handle_server_request(response)
            return

        # Notification (no id) — discard
        if 'method' in response and 'id' not in response:
            return

        # Response with id — dispatch to waiting caller
        resp_id = response.get('id')
        if resp_id and resp_id in self._pending_requests:
            entry = self._pending_requests[resp_id]
            entry["response"] = response
            entry["event"].set()

    def _bg_read_omnisharp(self):
        """Read one OmniSharp message (newline JSON) and dispatch."""
        poll = select.poll()
        poll.register(self.process.stdout, select.POLLIN)
        events = poll.poll(1000)
        if not events:
            return

        raw = self.process.stdout.readline()
        if not raw:
            return
        line = raw.decode('utf-8', errors='replace').strip()
        if not line:
            return

        try:
            d = json.loads(line)
        except:
            return

        # Events — discard
        if d.get("Type") == "event":
            return

        # Response — dispatch by Request_seq
        if d.get("Type") == "response":
            seq = d.get("Request_seq")
            if seq is not None and seq in self._pending_requests:
                entry = self._pending_requests[seq]
                entry["response"] = d.get("Body")
                entry["event"].set()

    def wait_for_initialization(self):
        silence_timeout = self.init_timeout  # how long to wait with no messages before considering init done
        poll_interval = 5  # how often to poll for responses
        print(f"waiting for init.. will proceed after {silence_timeout}s of silence from the server.")

        # wait for initialization: keep reading messages until the server goes quiet for silence_timeout seconds
        last_message_time = time.time()
        while True:
            response = self._receive_response(timeout=poll_interval)
            is_timeout = response.get('error', {}).get('message', '') == 'timeout'

            if not is_timeout:
                last_message_time = time.time()
                print("(received response while waiting for init) response: ", response)

            if response.get("method") == "window/showMessage" and "finished" in response.get("params", {}).get("message", "").lower():
                print("Server signaled initialization finished.")
                break

            silence_duration = time.time() - last_message_time
            if silence_duration >= silence_timeout:
                print(f"No messages for {round(silence_duration, 1)}s, assuming initialization is done.")
                break

            print(f"waiting for init (silence: {round(silence_duration, 1)}s / {silence_timeout}s)...")


    def get_symbols_in_file(self, uri):
        symbols = self.doc_symbols_map.get(uri, None)
        if not symbols:
            doc_symbol_params = {
                "textDocument": {
                    "uri": uri
                }
            }
            symbol_response = self.send_request("textDocument/documentSymbol", doc_symbol_params)
            symbols = symbol_response.get('result', []) or []
            self.doc_symbols_map[uri] = symbols


            # unroll children, particularly for children in a class
            for symbol in symbols:
                if 'children' in symbol:
                    for child in symbol['children']:
                        symbols.append(child)

            # NOTE | TODO: preventing looking up functions in dependency files as it can take forever, this may affect output for some cases, investigate deeper
            # add to seen functions


            if 'typescript-language-server' not in self.server_cmd[0]:
                for symbol in [s for s in symbols if s['kind'] in [6, 9, 12]]:
                    if 'uri' not in symbol:
                        symbol['uri'] = uri
                    _sym_id = self.get_id(symbol)
                    self.seen_functions_from_files_ids.add(_sym_id)
                    symbol['_cached_id'] = _sym_id  # Cache for reuse in OmniSharp batched path

                    # map to function from definition to get start/end lines when outputting function
                    # NOTE: No longer used, would need to get definition first
                    # self.def_to_func_map[self.get_id(symbol)] = self.get_id(symbol, False)       

            # add classes to seen classes
            for symbol in [c for c in symbols if c['kind'] in [5]]:
                if 'uri' not in symbol:
                    symbol['uri'] = uri

                if self.capabilities.get("typeHierarchyProvider", False) and not self.disable_inheritance:
                    self.get_inhheritance_of_symbol(symbol)


                self.seen_classes.add(self.get_id(symbol))

        return symbols
        

    def get_function_in_file(self, file_path, name, line):
        functions = self.get_functions_in_file(file_path)
        return [f for f in functions if f['name'] == name and self.get_range(f)['start']['line'] == line]

    
    def get_functions_in_file(self, file_path):
        if file_path in self.get_function_in_file_cache:
            return self.get_function_in_file_cache[file_path]

        functions = []

        uri = f"file://{file_path}"

        # self.wait_for_initialization()

        # does this logic need to move to eval_file??
        if 'typescript-language-server' in self.server_cmd[0]:
            # specific for typescript
            code = get_file_content(file_path)

            tree = self.parser.parse(bytes(code, "utf8"))
            root = tree.root_node
            # functions = set()

            def walk(node):
                if node.type == 'function_declaration' or node.type == 'method_definition' or (node.type == "variable_declarator" and b"=>" in node.text): # can write more specific regex for arrow functions, if needed
                    isFunc = True
                    label_node = next((c for c in node.children if c.type == "identifier" or c.type == "property_identifier"), None)
                    if label_node:
                        f_str = label_node.text.decode('utf-8')
                        if node.type == "variable_declarator" and not re.search(r'\w+\s*=\s*\([^)]*\)\s*=>', f_str): # Matches arrow functions and function assignments
                            isFunc = False
                        if isFunc:
                            f_id = f"{f_str},{file_path}#{node.start_point[0]}"  # Placeholder for filepath
                            functions.append(f_id)
                            self.function_details[f_id] = {
                                "start_line": node.start_point[0],
                                "end_line": node.end_point[0],
                                "start_char": node.start_point[1],
                                "end_char": node.end_point[1]
                            }
                for child in node.children:
                    walk(child)

            walk(root)
        else:
            # Request document symbols
            symbols = self.get_symbols_in_file(uri)

            for symbol in symbols:
                if "ocamllsp" in self.server_cmd and symbol['kind'] == 13:
                    functions.append(symbol)

                # kinds: https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#documentSymbolParams
                if symbol['kind'] in [6, 9, 12]:  # Method / Function kind
                    # ignore for typescript-language-server?
                    functions.append(symbol)
                    
                    ## NEEDED?? map definitions to function for future lookups
                    # f_defs = self.get_func_definition(symbol)
                    # for f_def in f_defs:
                    #     self.def_to_func_map.append(f_def)


        for f_id_or_symbol in functions:
            f_id = f_id_or_symbol
            if type(f_id) is not str:
                f_id = self.get_id(f_id)
            if f_id not in self.seen_functions_from_files_ids:
                self.seen_functions_from_files_ids.add(f_id)

        self.get_function_in_file_cache[file_path] = functions
        return functions

    def get_references_of_symbol(self, uri, line, char):
        references = []

        # Prepare references params
        prepare_references_params = {
            "textDocument": {
                "uri": uri
            },
            "position": {
                "line": line,
                "character": char
            },
            "context": {
                "includeDeclaration": True
            }
        }

        prepare_references_response = self.send_request("textDocument/references", prepare_references_params)
        references = prepare_references_response.get('result', []) or []

        return references

    def _prepare_definition_item(self, item):
        """Normalize item and apply Rust line-search workaround. Returns (normalized_item, location_base, json_key)."""
        item = self.normalize_location_link(item)
        json_item = json.dumps(item)
        location_base = item['location'] if 'location' in item else item
        location_base = self.normalize_location_link(location_base)

        if 'name' in item:
            MAX_LINES_TO_SEARCH = 20
            lines = 0
            while lines < MAX_LINES_TO_SEARCH:
                try:
                    content = get_file_content(location_base['uri'].replace("file://", ""), self.get_range(item)['start']['line'] + lines)
                    func_name = self.parse_func_name(item['name'])
                    match = re.search(rf"{re.escape(func_name)}", content)
                    self.get_range(item)['start']['character'] = match.start() if match else self.get_range(item)['start']['character']
                    if match:
                        break
                    lines += 1
                except:
                    break
            if lines != MAX_LINES_TO_SEARCH:
                self.get_range(item)['start']['line'] += lines

        return item, location_base, json_item

    def _build_definition_request(self, location_base):
        """Build the LSP method and params for a definition request."""
        method = "textDocument/definition"
        params = {
            "textDocument": {"uri": location_base['uri']},
            "position": {
                "line": self.get_range(location_base)['start']['line'],
                "character": self.get_range(location_base)['start']['character']
            }
        }
        if "typescript-language-server" in self.server_cmd[0]:
            method = "workspace/executeCommand"
            params = {
                "command": "_typescript.goToSourceDefinition",
                "arguments": [
                    location_base['uri'],
                    {"line": self.get_range(location_base)['start']['line'], "character": self.get_range(location_base)['start']['character']}
                ]
            }
        return method, params

    def _process_definition_response(self, response, item, json_item):
        """Process definition response, normalize LocationLinks, cache and return."""
        ret = response['result'] if response.get('result', []) else [item]
        if type(ret) is not list:
            ret = [ret]
        ret = [self.normalize_location_link(r) for r in ret]
        self.definition_cache[json_item] = ret
        return ret

    def get_func_definition(self, item):
        item, location_base, json_item = self._prepare_definition_item(item)

        if self.definition_cache.get(json_item, None):
            return self.definition_cache[json_item]

        method, params = self._build_definition_request(location_base)
        response = self.send_request(method, params)

        return self._process_definition_response(response, item, json_item)


    def get_func_calls(self, name, uri, line, char):
        # get char offset
        # content = get_file_content(uri.replace("file://", ""), line)
        # index_of_func = content.index(f"{name.split('.')[-1]}(")  # NOTE: language specific?
        # offset = index_of_func - char
        # char += offset
        
        if self.only_functions:
            return

        # Skip if already processed. Uses get_id() format "name,path#line".
        # NOTE: does not include char — two overloaded functions with the same
        # name on the same line would collide. This is intentional: get_id()
        # resolves both to the same ID anyway (it matches by name+line in
        # get_symbols_in_file). The authoritative check after get_id() (below)
        # catches any edge cases where get_id() resolves differently.
        _candidate_id = f"{self.parse_func_name(name)},{uri.replace('file://', '')}#{line}"
        if _candidate_id in self.completed_function_ids or _candidate_id in self.completed_w_err_function_ids:
            return


        f_item = {
            "name": name,
            "kind": 6, # method
            "location": {
                "uri": uri,
                "range": {
                    "start": {
                        "line": line,
                        "character": char
                    },
                    "end": {
                        "line": line,
                        "character": char
                    }
                }
            }
        }
        func_id = self.get_id(f_item)

        # Authoritative check with the real func_id (get_id may resolve to
        # a different start_line via definition lookup)
        if func_id in self.completed_function_ids or func_id in self.completed_w_err_function_ids:
            return

        if any([re.search(p, uri, re.IGNORECASE) for p in EXCLUDE_FUNC_CALL_FILEPATHS]):
            self.completed_function_ids.add(func_id)
            return


        # rust LSP considers start of comments to be the start of the function
        # does not return selectionRange like spec indicates.
        # loop through lines to find start of function (janky)
        MAX_LINES_TO_SEARCH = 20

        ix = 0
        add_lines = 0
        while ix < MAX_LINES_TO_SEARCH:
            # get offset to function name
            content = get_file_content(uri.replace("file://", ""), line + ix)
            func_name = self.parse_func_name(name)
            try:
                # match = re.search(rf"{func_name}\s*\(", content)
                # NOTE: commenting out since languages like Ruby do not have parentheses
                match = re.search(rf"{re.escape(func_name)}", content)
            except Exception as e:
                # error in regexx such as (unbalanced parenthases) due to 'content', keep searching
                continue

            if match:
                char = match.start() if match else char  # update char to real position, if it can be found
                add_lines = ix
                break
            ix += 1
        line += add_lines


        if (self.capabilities.get("callHierarchyProvider", False) or self.force_callHierarchy) and not self.force_references:
            # Prepare call hierarchy
            prepare_call_hierarchy_params = {
                "textDocument": {
                    "uri": uri
                },
                # "position": function_range['start']
                "position": {
                    "line": line,
                    "character": char
                }
            }

            prepare_response = self.send_request("textDocument/prepareCallHierarchy", prepare_call_hierarchy_params)
            call_hierarchy_items = prepare_response.get('result', []) or []
            if prepare_response.get('error'):
                self.had_error = True

            for item in call_hierarchy_items:
                if item['kind'] not in [6, 9, 12]:  # method | constructor | Function kind
                    continue

                item_id = self.get_id(item)


                # self.seen_functions.add(item_id)
                self.seen_functions_from_files_ids.add(item_id)
                func_id = f"{self.get_id(item)}"
                # self.seen_functions.add(func_id)
                self.seen_functions_from_files_ids.add(func_id)

                call_hierarchy_params = {
                    "item": item
                }

                if self._reader_running and self.parallel_requests > 1:
                    # ── Batched: fire incoming + outgoing concurrently (same file) ──
                    incoming_handle = None
                    outgoing_handle = None
                    if not self.disable_incoming_calls:
                        incoming_handle = self.send_request_async("callHierarchy/incomingCalls", call_hierarchy_params)
                    if not self.disable_outgoing_calls:
                        outgoing_handle = self.send_request_async("callHierarchy/outgoingCalls", call_hierarchy_params)

                    # Collect incoming
                    if incoming_handle is not None:
                        call_hierarchy_response = self.collect_response(incoming_handle)
                    elif not self.disable_incoming_calls:
                        call_hierarchy_response = self.send_request("callHierarchy/incomingCalls", call_hierarchy_params)
                    else:
                        call_hierarchy_response = {'result': []}
                    incoming_calls = call_hierarchy_response.get('result', []) or []
                    if call_hierarchy_response.get('error'):
                        self.had_error = True
                    callee_func_id = self.get_id(f_item)
                    for call in incoming_calls:
                        caller_func_id = f"{self.get_id(call['from'])}"
                        g_function_calls.setdefault(increment_lines_in_id(caller_func_id), set()).add(increment_lines_in_id(callee_func_id))
                        self.seen_functions_from_files_ids.add(caller_func_id)

                    # Collect outgoing
                    if outgoing_handle is not None:
                        call_hierarchy_response = self.collect_response(outgoing_handle)
                    elif not self.disable_outgoing_calls:
                        call_hierarchy_response = self.send_request("callHierarchy/outgoingCalls", call_hierarchy_params)
                    else:
                        call_hierarchy_response = {'result': []}
                    outgoing_calls = call_hierarchy_response.get('result', []) or []
                    if call_hierarchy_response.get('error'):
                        self.had_error = True
                    caller_func_id = self.get_id(f_item)
                    for call in outgoing_calls:
                        callee_func_id = f"{self.get_id(call['to'])}"
                        g_function_calls.setdefault(increment_lines_in_id(caller_func_id), set()).add(increment_lines_in_id(callee_func_id))
                        self.seen_functions_from_files_ids.add(callee_func_id)
                else:
                    # ── Sequential path ──
                    ## Incoming calls
                    if not self.disable_incoming_calls:
                        call_hierarchy_response = self.send_request("callHierarchy/incomingCalls", call_hierarchy_params)
                        incoming_calls = call_hierarchy_response.get('result', []) or []
                        if call_hierarchy_response.get('error'):
                            self.had_error = True

                        callee_func_id = self.get_id(f_item)


                        for call in incoming_calls:
                            caller_func_id = f"{self.get_id(call['from'])}"
                            g_function_calls.setdefault(increment_lines_in_id(caller_func_id), set()).add(increment_lines_in_id(callee_func_id))

                            self.seen_functions_from_files_ids.add(caller_func_id)

                    ## Outgoing calls
                    if not self.disable_outgoing_calls:
                        call_hierarchy_response = self.send_request("callHierarchy/outgoingCalls", call_hierarchy_params)
                        outgoing_calls = call_hierarchy_response.get('result', []) or []
                        if call_hierarchy_response.get('error'):
                            self.had_error = True

                        caller_func_id = self.get_id(f_item)

                        for call in outgoing_calls:
                            callee_func_id = f"{self.get_id(call['to'])}"
                            g_function_calls.setdefault(increment_lines_in_id(caller_func_id), set()).add(increment_lines_in_id(callee_func_id))
                            self.seen_functions_from_files_ids.add(callee_func_id)

        # find references of function
        references = self.get_references_of_symbol(uri, line, char)
        for ref in references:
            ref_loc = self.symbol_to_loc(ref)
            self.function_references.setdefault(func_id, set()).add(ref_loc)

            if self.force_references or self.had_error or (not self.capabilities.get("callHierarchyProvider", False) and not self.force_callHierarchy):
                # TODO: fix this to resolve normalized (definition) ids
                self.function_call_refs.setdefault(func_id, []).append(ref)
                # does not append seen_functions because we don't know if the calling function has been seen


        if not self.had_error:
            self.completed_function_ids.add(func_id)
        else:
            self.completed_w_err_function_ids.add(func_id)
            
        if self.had_error:
            self.poll_and_reboot_LSP()
            self.had_error = False

    def eval_file(self, file_path):
        self.wait_if_paused()
        if any([re.search(p, file_path, re.IGNORECASE) for p in EXCLUDE_FUNC_CALL_FILEPATHS]):  # this will not scan the file at all, may want a specific variable for this
            print("Excluding file from eval: ", file_path)
            return

        if file_path in self.evaled_files:
            print("Already evaluated file: ", file_path)
            return
        print("Evaluating file: ", file_path)
        self.evaled_files.add(file_path)

        uri = f"file://{file_path}"

        # # Send didOpen notification
        # did_open_params = {
        #     "textDocument": {
        #         "uri": uri,
        #         "languageId": self.language_id,
        #         "version": 1,
        #         "text": open(file_path, 'r', encoding='utf-8').read()
        #     }
        # }
        # self.send_notification("textDocument/didOpen", did_open_params)

        # Request document symbols
        symbols = self.get_symbols_in_file(uri)

        # streaming mode: TODO: for all symbols, add all files to queue to be evaled
        if self.streaming_mode and not self.streaming_mode_disable_recursive_ref_search:
            for symbol in symbols:
                refs = self.get_references_of_symbol(uri, self.get_range(symbol)['start']['line'], self.get_range(symbol)['start']['character'])
                unique_refs = set({self.normalize_location_link(ref).get('uri', ref.get('targetUri', '')) for ref in refs})  # unique references, may error if uri is listed under 'location' key
                for ref_path in unique_refs:
                    path = ref_path.replace("file://", "")
                    if path in self.evaled_files or path in self.queued_files:
                        continue
                    print(f"Adding ref path to scan from refs: {ref_path}")
                    self.ls_file_queue.put("~" + path) # no prefix before ~ means it is a full scan
                    self.queued_files.add(path)


        # get start/end lines for functions in csharp
        if 'csharp-ls' in self.server_cmd[0] or self.is_omnisharp:
            file_path = uri.replace("file://", "")
            # specific for csharp
            code = get_file_content(file_path)

            tree = self.parser.parse(bytes(code, "utf8"))
            root = tree.root_node

            def walk(node):
                if node.type in ['method_declaration', 'constructor_declaration', 'function_declaration', 'destructor_declaration', 'local_function_declaration']:
                    label_node = next((c for c in reversed(node.children) if c.type == "identifier"), None)  # get last identifier as prefixes may occur "example: Async Task myMethod"
                    if label_node:
                        f_str = label_node.text.decode('utf-8')
                        identifier_node = [n for n in node.children if n.type == 'identifier'][0]
                        f_id = f"{f_str},{file_path}#{identifier_node.start_point[0]}"
                        self.function_details[f_id] = {
                            "start_line": identifier_node.start_point[0],
                            "end_line": node.end_point[0],
                            "start_char": identifier_node.start_point[1],
                            "end_char": identifier_node.end_point[1]
                        }
                for child in node.children:
                    walk(child)
            walk(root)

        # TODO: get lines for ls-asm
        if 'asm-lsp' in self.server_cmd[0]:
            file_path = uri.replace("file://", "")
            code = get_file_content(file_path)

            tree = self.parser.parse(bytes(code, "utf8"))
            root = tree.root_node

            label_nodes = []

            def walk(node):
                if node.type == 'label':
                    label_nodes.append(node)
                for child in node.children:
                    walk(child)

            walk(root)

            for i, node in enumerate(label_nodes):
                label_text = node.text.decode('utf-8').rstrip(':')
                f_id = f"{label_text},{file_path}#{node.start_point[0]}"
                end_line = (
                    label_nodes[i+1].start_point[0] - 1
                    if i + 1 < len(label_nodes)
                    else root.end_point[0]
                )

                self.function_details[f_id] = {
                    "start_line": node.start_point[0],
                    "end_line": end_line,
                    "start_char": node.start_point[1],
                    "end_char": node.end_point[1]
                }


        # TODO: typescript, get functions and what functions are called
        # get_id() for each called function
        # add to to map of relationships
        # add file of called func (from def) to be scanned (if not done already)
        # ... creating function in functions list should happen automatically when source file is scanned (make sure relationships have proper IDs)
        if "typescript-language-server" in self.server_cmd[0] and not any([re.search(p, file_path, re.IGNORECASE) for p in EXCLUDE_FUNC_CALL_FILEPATHS]):
            code = get_file_content(file_path)

            tree = self.parser.parse(bytes(code, "utf8"))
            root = tree.root_node
            filenames = set()
            def walk(node, current_function=None):
                if node.type == 'function_declaration' or node.type == 'method_definition' or node.type == "variable_declarator":
                    isFunc = True
                    label_node = next((c for c in node.children if c.type == "identifier" or c.type == "property_identifier"), None)
                    if label_node:
                        f_str = label_node.text.decode('utf-8')
                        if node.type == "variable_declarator" and not re.search(r'\w+\s*=\s*\([^)]*\)\s*=>', f_str): # Matches arrow functions and function assignments
                            isFunc = False
                        if isFunc:
                            # Set current function context for child nodes
                            current_function = {
                                'name': f_str,
                                'line': label_node.start_point[0], 
                                'column': label_node.start_point[1]
                            }
                    
                if node.type == 'call_expression':
                    called = node.child_by_field_name('function')
                    line = node.start_point[0]  # 0-indexed → 1-indexed
                    column = node.start_point[1] + 1
                    end_column = node.end_point[1] + 1
                    # print('Function call:', code[called.start_byte:called.end_byte], "at line", line, "column", column)
                    
                    # Get called function ID
                    called_params = {
                        "location": {
                            "uri": uri,
                            "range": {
                                "start": {
                                    "line": line,
                                    "character": column
                                }
                            }
                        },
                    }
                    # print("getting def for: ", code[called.start_byte:called.end_byte], "at line", line, "column", column)
                    f_def = self.get_func_definition(called_params)
                    f_def = f_def[0]
                    
                    if f_def != called_params:
                        # if lookup was successful

                        location_base = f_def['location'] if 'location' in f_def else f_def
                        location_base = self.normalize_location_link(location_base)
                        called_id = f"{code[called.start_byte:called.end_byte]},{location_base['uri'].replace('file://', '')}#{location_base['range']['start']['line']}"

                        # Get caller function ID if we're in a function context
                        caller_id = f"__TOP_LEVEL__,{file_path}#0"
                        if current_function:
                            caller_params = {
                                "name": current_function['name'],
                                "kind": 6,  # method
                                "location": {
                                    "uri": uri,
                                    "range": {
                                        "start": {
                                            "line": current_function['line'],
                                            "character": current_function['column']
                                        },
                                        "end": {
                                            "line": current_function['line'],
                                            "character": current_function['column']
                                        }
                                    }
                                }
                            }
                            caller_id = self.get_id(caller_params)

                        # print("\ncaller_id", caller_id)
                        # print("called_id", called_id)
                        # Add callstack with caller
                        
                        # NOTE: eval_file important here before next steps of adding functions & callstacks (maybe remove __TOP_LEVEL__ / failed lookup?)
                        if called_id in self.get_functions_in_file(called_id.split(",")[1].split("#")[0]): # or "__TOP_LEVEL__" in called_id:
                            # if valid fucntion, add callstack
                            g_function_calls.setdefault(increment_lines_in_id(caller_id), set()).add(increment_lines_in_id(called_id))
                        else:
                            # self.seen_functions_from_files_ids.add(called_id)  # maybe add as temporary and only resolve at the end for valid functions
                            print("WARNING: caller_id not seen, skipping callstack for:\n\tcaller_id: ", caller_id, "\n\tcalled_id: ", called_id)

                for child in node.children:
                    walk(child, current_function)

            walk(root)


        time.sleep(PAUSE_TIME)

        # Get function calls
        if 'typescript-language-server' in self.server_cmd[0]:
            for f_id in self.get_functions_in_file(file_path):
                self.seen_functions_from_files_ids.add(f_id)
                details = self.function_details.get(f_id)
                if details:
                    f_name = f_id.split(",")[0]
                    self.get_func_calls(f_name, uri, int(details['start_line']), int(details['start_char']))
        elif self.is_omnisharp and self._reader_running and self.parallel_requests > 1:
            # ── OmniSharp batched /findusages path ──
            # Phase A: Prepare all functions (sequential — get_id needs sync LSP)
            prepared = []  # (func_id, uri, line, char)
            for symbol in symbols:
                if symbol['kind'] not in [6, 9, 12]:
                    continue
                base_location = symbol['location'] if 'location' in symbol else symbol
                s_name = symbol['name']
                s_line = self.get_range(base_location)['start']['line']
                s_char = self.get_range(base_location)['start']['character']

                # Replicate get_func_calls preparation (lines 2188-2251)
                if self.only_functions:
                    continue
                _candidate_id = f"{self.parse_func_name(s_name)},{uri.replace('file://', '')}#{s_line}"
                if _candidate_id in self.completed_function_ids or _candidate_id in self.completed_w_err_function_ids:
                    continue

                # Reuse the func_id cached by get_symbols_in_file (avoids a
                # duplicate /gotodefinition call — the cache key changes after
                # _prepare_definition_item mutates the symbol in-place).
                func_id = symbol.get('_cached_id') or self.get_id(symbol)

                if func_id in self.completed_function_ids or func_id in self.completed_w_err_function_ids:
                    continue
                if any([re.search(p, uri, re.IGNORECASE) for p in EXCLUDE_FUNC_CALL_FILEPATHS]):
                    self.completed_function_ids.add(func_id)
                    continue

                # Rust-style line search for real function name position
                adj_line, adj_char = s_line, s_char
                func_name = self.parse_func_name(s_name)
                for ix in range(20):
                    content = get_file_content(uri.replace("file://", ""), s_line + ix)
                    try:
                        match = re.search(rf"{re.escape(func_name)}", content)
                    except:
                        continue
                    if match:
                        adj_char = match.start()
                        adj_line = s_line + ix
                        break

                prepared.append((func_id, uri, adj_line, adj_char))

            # Phase B: Batch /findusages in groups of parallel_requests
            for batch_start in range(0, len(prepared), self.parallel_requests):
                batch = prepared[batch_start:batch_start + self.parallel_requests]

                # Fire all requests
                pending = []
                for func_id, b_uri, b_line, b_char in batch:
                    params = {
                        "textDocument": {"uri": b_uri},
                        "position": {"line": b_line, "character": b_char},
                        "context": {"includeDeclaration": True}
                    }
                    handle = self.send_request_async("textDocument/references", params)
                    pending.append((func_id, b_uri, b_line, b_char, handle))

                # Collect all responses
                had_batch_error = False
                for func_id, b_uri, b_line, b_char, handle in pending:
                    if handle is not None:
                        response = self.collect_response(handle)
                        references = response.get('result', []) or []
                        resp_error = bool(response.get('error'))
                    else:
                        # Fallback to sync
                        references = self.get_references_of_symbol(b_uri, b_line, b_char)
                        resp_error = False

                    # Process references — same logic as get_func_calls lines 2362-2370
                    for ref in references:
                        ref_loc = self.symbol_to_loc(ref)
                        self.function_references.setdefault(func_id, set()).add(ref_loc)
                        if self.force_references or resp_error or (not self.capabilities.get("callHierarchyProvider", False) and not self.force_callHierarchy):
                            self.function_call_refs.setdefault(func_id, []).append(ref)

                    if not resp_error:
                        self.completed_function_ids.add(func_id)
                    else:
                        self.completed_w_err_function_ids.add(func_id)
                        had_batch_error = True

                if had_batch_error:
                    self.poll_and_reboot_LSP()
                    self.had_error = False
        else:
            # ── Sequential path (non-OmniSharp servers) ──
            for symbol in symbols:
                if symbol['kind'] in [6, 9, 12] or (self.server_cmd and "ocamllsp" in self.server_cmd[0] and symbol['kind'] == 13):  # Method | Constructor | Function kind
                    if 'typescript-language-server' in self.server_cmd[0] and ("jsonContentType" in symbol.get('containerName', "") or "<unknown>" in symbol.get('containerName', "")): # TODO: can remove
                        # skip internal functions
                        continue
                    base_location = symbol['location'] if 'location' in symbol else symbol
                    self.get_func_calls(symbol['name'], uri, self.get_range(base_location)['start']['line'], self.get_range(base_location)['start']['character'])
                    # self.get_func_calls(symbol['name'], uri, symbol['location']['range']['start']['line'], symbol['location']['range']['start']['character'] + FUNC_NAME_OFFSET)


        # loop while seen != completed
        while True:
            completed_before = len(self.completed_function_ids)
            seen_functions_copy = self.seen_functions.copy()
            for func in seen_functions_copy:
                # NOTE: line - 1 to accomodate for adding 1 before
                name, uri = f'{",".join(func.split(",")[0:-1])}', f'file://{func.split("#")[0].split(",")[-1]}'
                line = int(self.function_details[func]['start_line'])
                char = int(self.function_details[func]['start_char'])
                self.get_func_calls(name, uri, line, char) # add offset?... TODO: Fix line number off by 1
            if len(self.completed_function_ids) == completed_before:
                break

    def get_inhheritance_of_symbol(self, symbol):
        symbol = self.normalize_location_link(symbol)
        base_location = symbol['location'] if 'location' in symbol else symbol
        base_location = self.normalize_location_link(base_location)
        prepare_type_hierarchy_params = {
            "textDocument": {
                "uri": base_location['uri']
            },
            # "position": function_range['start']
            "position": {
                "line": self.get_range(base_location)['start']['line'],
                "character": self.get_range(base_location)['start']['character']
            }
        }

        prepare_response = self.send_request("textDocument/prepareTypeHierarchy", prepare_type_hierarchy_params)
        type_hierarchy_items = prepare_response.get('result', []) or []

        for item in type_hierarchy_items:
            item_id = self.get_id(item)
            # typeHierarchy/subtypes
            subtypes_supertypes_params = {
                "item": item
            }

            ## Incoming calls
            subtypes_response = self.send_request("typeHierarchy/subtypes", subtypes_supertypes_params)
            subtypes = subtypes_response.get('result', []) or []

            for subtype in subtypes:
                subtype_id = self.get_id(subtype, from_def=False)
                g_class_inheritance.setdefault(item_id, set()).add(subtype_id)


            # supertypes
            supertypes_response = self.send_request("typeHierarchy/supertypes", subtypes_supertypes_params)
            supertypes = supertypes_response.get('result', []) or []

            for supertype in supertypes:
                supertype_id = self.get_id(supertype, from_def=False)
                g_class_inheritance.setdefault(supertype_id, set()).add(item_id)
            # class_inheritance[item_id] = subtypes
            


    def analyze_files(self, project_dir):
        if any([project_dir.endswith(ext) for ext in self.file_extensions]): # and file.endswith("exec_linux.go"):
            self.eval_file(project_dir)


        total_files = sum([len(files) for _ , _, files in os.walk(project_dir)]) or 1
        counter = 1
        # flatten array of arrays

        for root, _, files in os.walk(project_dir):
            # if any([path in root.lower() for path in EXCLUDE_FUNC_CALL_FILEPATHS])
            # if not in_scope(root):
            #     counter += len(files)
            #     continue
            
            for file in files:
                counter += 1
                file_path = os.path.join(root, file)

                if any([file.endswith(ext) for ext in self.file_extensions]) and in_scope(file_path): # and file.endswith("exec_linux.go"):
                    self.eval_file(file_path)
                    
            
            # if counter % 10 == 0:
            print(f"(get callstacks in files) done with file (original): {counter} / {total_files}\n")

        print(f"(get callstacks in files) done with file (original): {counter} / {total_files}\n")

        if self.only_functions:
            return


        ## LOOP REFERENCES + CALLSTACKS, GET FUNC CALLSTACKS
        # completed_ref_files = set()  # replaced with g_seen_files_for_refs .. revert if this breaks something. In theory, we only need to eval each file once for references
        loop = 0
        lookedup_files = set()
        while True:
            len_completed_before = len(self.completed_function_ids)
            len_seen_functions_before = len(self.seen_functions)


            # get references of each var
            seen_function_files = [f.split(",")[1].split("#")[0] for f in self.completed_function_ids]
            self.doc_symbols_map_copy = self.doc_symbols_map.copy()
            # PATCH P2.1 — per-language VAR_KINDS. LSP symbol kinds the server
            # emits for "module/class-level variable" are NOT standardised; the
            # old hardcoded set dropped legitimate symbols for several
            # languages (see EXTRACTOR_CHANGES_APPLIED.md for per-language
            # reasoning). Each language gets its own set; union is the fallback.
            _VAR_KINDS_UNION = {7, 8, 10, 11, 13, 14, 15, 16, 17, 18, 19, 20, 22, 23, 24, 25, 26}
            _VAR_KINDS_PER_LANG = {
                # solidity-language-server emits `Variable=13` for state vars
                # and `Property=7` for public state; include `Field=8` too.
                "solidity":   {7, 8, 13, 14, 22},
                # ruby-lsp emits Constant=14 for top-level consts, Variable=13
                # for class/instance vars, Property=7 for attr_accessor.
                "ruby":       {7, 8, 13, 14, 22},
                # pyright: Variable=13, Constant=14, Field=8.
                "python":     {8, 13, 14, 22},
                # kotlin-language-server: Variable=13, Field=8, Constant=14,
                # Property=7 (for `var`/`val` at top level).
                "kotlin":     {7, 8, 13, 14, 22},
                # lua-language-server: Variable=13, Field=8, Constant=14.
                "lua":        {8, 13, 14, 22},
                # PowerShellEditorServices: Variable=13; $script: vars come
                # back as Field=8 in some paths.
                "powershell": {8, 13, 14, 22},
            }
            _active_lang = getattr(self, "language_id", None)
            VAR_KINDS = _VAR_KINDS_PER_LANG.get(_active_lang, _VAR_KINDS_UNION)
            if os.environ.get("SA_DUMP_UNKNOWN_KINDS") == "1":
                # Debug aid: list every symbol kind the current LSP emitted,
                # so we can widen the per-language set when we see a miss.
                _kinds_seen = {}
                for _fp, _syms in self.doc_symbols_map.items():
                    for _s in _syms:
                        _kinds_seen.setdefault(_s.get('kind'), 0)
                        _kinds_seen[_s.get('kind')] += 1
                print(f"[P2.1] lang={_active_lang} kinds_seen={_kinds_seen} VAR_KINDS={sorted(VAR_KINDS)}")

            def _process_var_refs(symbol, filepath, references):
                """Post-process references for a variable symbol."""
                base_location = symbol['location'] if 'location' in symbol else symbol
                if "uri" not in base_location:
                    base_location['uri'] = filepath

                new_references = []
                for r in references:
                    self.get_range(r)['start']['line'] += 1
                    self.get_range(r)['end']['line'] += 1
                    self.get_range(r)['start']['character'] += 1
                    self.get_range(r)['end']['character'] += 1
                    if 'func_id' not in r:
                        r['func_id'] = "#0"
                    r = self.normalize_location_link(r)
                    if any([re.search(p, r['uri'], re.IGNORECASE) for p in EXCLUDE_REF_FILEPATHS]):
                        continue
                    new_references.append(r)

                g_var_ref_map[increment_lines_in_id(self.symbol_to_loc(symbol, include_name=True))] = new_references

                for ref in new_references:
                    ref_filepath = ref['uri'].replace("file://", "")
                    if ref_filepath not in seen_function_files and ref_filepath not in lookedup_files:
                        if any([re.search(p, ref_filepath, re.IGNORECASE) for p in EXCLUDE_FUNC_CALL_FILEPATHS]):
                            continue
                        print(f"NOT IN SEEN FUNCTION FILES: {ref_filepath}")
                        fs = self.get_functions_in_file(ref_filepath)
                        for f in fs:
                            f_id = self.get_id(f) if 'typescript-language-server' not in self.server_cmd[0] else f
                            if f_id not in self.seen_functions:
                                self.seen_functions_from_files_ids.add(f_id)
                        lookedup_files.add(ref_filepath)

            def _retry_var_refs(symbol, filepath):
                """Rust LSP workaround: search next lines for the real symbol position."""
                base_location = symbol['location'] if 'location' in symbol else symbol
                MAX_LINES_TO_SEARCH = 20
                ix = 0
                add_lines = 0
                while ix < MAX_LINES_TO_SEARCH:
                    try:
                        content = get_file_content(base_location['uri'].replace("file://", ""), self.get_range(symbol)['start']['line'] + ix)
                        var_name = symbol['name'].split(".")[-1]
                        match = re.search(rf"{re.escape(var_name)}", content)
                        self.get_range(symbol)['start']['character'] = match.start() if match else self.get_range(symbol)['start']['character']
                        if match:
                            add_lines = ix
                            break
                        ix += 1
                    except:
                        break
                self.get_range(symbol)['start']['line'] += add_lines
                return self.get_references_of_symbol(filepath, self.get_range(base_location)['start']['line'], self.get_range(base_location)['start']['character'])

            for i, filepath in enumerate(self.doc_symbols_map_copy):
                if filepath in self.seen_files_for_refs or any([re.search(p, filepath, re.IGNORECASE) for p in EXCLUDE_FUNC_CALL_FILEPATHS]):
                    continue

                var_symbols = [s for s in self.doc_symbols_map[filepath] if s['kind'] in VAR_KINDS]

                if self.parallel_requests > 1 and self._reader_running and var_symbols:
                    # ── Batched path: fire N references at once per file (file already open from Phase 1) ──
                    for batch_start in range(0, len(var_symbols), self.parallel_requests):
                        batch = var_symbols[batch_start:batch_start + self.parallel_requests]
                        # Fire all requests in this batch
                        pending_batch = []  # (symbol, async_handle)
                        for symbol in batch:
                            base_location = symbol['location'] if 'location' in symbol else symbol
                            params = {
                                "textDocument": {"uri": filepath},
                                "position": {
                                    "line": self.get_range(base_location)['start']['line'],
                                    "character": self.get_range(base_location)['start']['character']
                                },
                                "context": {"includeDeclaration": True}
                            }
                            handle = self.send_request_async("textDocument/references", params)
                            pending_batch.append((symbol, handle))

                        # Collect responses and process
                        for symbol, handle in pending_batch:
                            if handle is None:
                                # Fell back to sync or was skipped
                                base_location = symbol['location'] if 'location' in symbol else symbol
                                references = self.get_references_of_symbol(filepath, self.get_range(base_location)['start']['line'], self.get_range(base_location)['start']['character'])
                            else:
                                response = self.collect_response(handle)
                                references = response.get('result', []) if not response.get('error') else []

                            # Retry with line search if empty (Rust LSP workaround)
                            if not references and 'name' in symbol:
                                references = _retry_var_refs(symbol, filepath)

                            _process_var_refs(symbol, filepath, references)
                else:
                    # ── Sequential path ──
                    for symbol in var_symbols:
                        base_location = symbol['location'] if 'location' in symbol else symbol
                        references = self.get_references_of_symbol(filepath, self.get_range(base_location)['start']['line'], self.get_range(base_location)['start']['character'])

                        if not references and 'name' in symbol:
                            references = _retry_var_refs(symbol, filepath)

                        _process_var_refs(symbol, filepath, references)

                self.seen_files_for_refs.add(filepath)
                print(f"(get callstacks in files) done with file (secondary): {(i + 1) } / {len(self.doc_symbols_map_copy)}\n")
        
            # get callstacks for all functions that have been seen but not completed
            seen_functions_copy = self.seen_functions.copy()
            for func in seen_functions_copy:
                name, uri = f'{",".join(func.split(",")[0:-1])}', f'file://{func.split("#")[0].split(",")[-1]}'
                line = int(self.function_details[func]['start_line'])
                char = int(self.function_details[func]['start_char'])

                self.get_func_calls(name, uri, line, char)

            
            
            if len_completed_before == len(self.completed_function_ids) and len_seen_functions_before == len(self.seen_functions):
                break
            else:
                loop += 1
                print(f"LOOPING {loop} : {len(self.completed_function_ids.union(self.completed_w_err_function_ids))} != {len(self.seen_functions)}")
                time.sleep(3)
                


    def close(self):
        self.process.terminate()

    def analyze(self, project_dir):
        global g_textHighlights
        global g_function_calls
        global g_class_inheritance
        global g_seen_files
        global g_seen_files_for_refs
        global g_var_ref_map
        global g_functions
        global g_scopes
        global g_data_updated
        global EXCLUDE_REF_FILEPATHS

        self._verbose_sentinel = os.path.join(project_dir, ".verbose")
        self._pause_sentinel = os.path.join(project_dir, ".pause")

        print("[+] Starting LSP Client w/ arguments:")
        print(f"\tProject Directory: {project_dir}")
        print(f"\tVerbose sentinel: touch {self._verbose_sentinel} to enable, rm to disable")
        print(f"\tPause sentinel:   touch {self._pause_sentinel} to pause, rm to resume")
        print(f"\tLanguage: {self.language_id}")
        print(f"\tExtensions: {self.file_extensions}")
        print(f"\tCommand Override: {self.server_cmd}")
        print(f"\tDisable Selection Range: {self.disable_selectionRange}")


        start = datetime.datetime.now()
    
        # php
        self.init_params = {
            "processId": None,
            "rootUri": f"file://{project_dir}",
            "workspaceFolders": [{
                "name": "project",
                "uri": f"file://{project_dir}"
            }],
            "capabilities": {
                "textDocument": {
                    "formatting": {
                        "dynamicRegistration": True
                    },
                    "typeHierarchy": {
                        "dynamicRegistration": True
                    },
                    "callHierarchy": {
                        "dynamicRegistration": True
                    },
                    "references": {
                        "dynamicRegistration": True
                    },
                    "definition": {
                        "dynamicRegistration": True
                    },
                    "documentSymbol": {
                        "dynamicRegistration": True
                    }
                }
            }
        }

        time.sleep(self.init_pause)

        if self.is_omnisharp:
            self._omnisharp_wait_started()

        if self.is_omnisharp:
            # OmniSharp loaded successfully — set synthetic capabilities
            self.capabilities = {
                "documentSymbolProvider": True, "definitionProvider": True,
                "referencesProvider": True, "implementationProvider": True,
            }
        else:
            # Standard LSP init (also used after OmniSharp fallback to csharp-ls)
            print("sending init")
            response = self.send_request("initialize", self.init_params)
            print("Initialize response:", response)

            self.send_notification("initialized", {})

            self.wait_for_initialization()

        # Start background reader for concurrent requests
        if self.parallel_requests > 1:
            self._start_background_reader()

        #### parallel: START LOOP
        # read from queue for files to analyze
        files_fns_retrieved = set()
        while True:
            self.wait_if_paused()
            if not self.streaming_mode:
                self.analyze_files(project_dir)
            else:
                # streaming mode, analyze files from queue
                # get analyze all files in queue for this language server before looping
                # if no files found, pause for 2sec before checking again
                has_evaled_files = False
                evaled_fnsOnly = False
                evaled_priority1_file = False
                while True:
                    # break early if forcing update
                    # check for file .vscode/ext-static-analysis/cache/force_update
                    if os.path.exists("./.vscode/ext-static-analysis/cache/force_update"):
                        os.remove("./.vscode/ext-static-analysis/cache/force_update")

                        if has_evaled_files:
                            print("Forcing update after evaling files...")
                            break
                        else:
                            print("Force update not needed, no newly evaled files")

                    if not self.ls_file_queue.empty():
                        cmd_and_file_path = self.ls_file_queue.peek()
                        if not cmd_and_file_path.startswith("fnsOnly~") and evaled_fnsOnly:
                            # next file is not fnsOnly and we have already evaled fnsOnly files, break to send funcs to frontend ASAP
                            break

                        if not cmd_and_file_path.startswith("~") and evaled_priority1_file:
                            # early break, evaled priority file and full scan, non-priority file is next to be evaled
                            break

                        cmd_and_file_path = self.ls_file_queue.get()
                        cmd = cmd_and_file_path.split("~")[0]
                        file_path = "~".join(cmd_and_file_path.split("~")[1:])
                        if file_path in self.evaled_files:
                            print(f"Skipping already seen file: {file_path}")
                            continue

                        print(f"({self.ls_file_queue.qsize()} left) Analyzing project file from queue: (cmd: {cmd}) {file_path}")

                        if cmd == "fnsOnly":
                            # if already have functions for this filename, skip
                            if g_functions.contains_filepath(file_path) or file_path in files_fns_retrieved:
                                print(f"Skipping already seen functions for file: {file_path}")
                                continue
                            evaled_fnsOnly = True
                            self.get_functions_in_file(file_path)
                            files_fns_retrieved.add(file_path)
                        else:
                            if cmd == "1":
                                evaled_priority1_file = True
                            # default is a full scan
                            self.analyze_files(file_path)
                        has_evaled_files = True
                    else:
                        if has_evaled_files:
                            break
                        print("No files in queue, waiting for 4 seconds...")
                        time.sleep(4)


            func_ids_w_callstacks = set()
            for caller in g_function_calls:
                func_ids_w_callstacks.add(caller)
                for callee in g_function_calls[caller]:
                    func_ids_w_callstacks.add(callee)

            # all_functions = self.completed_function_ids + self.seen_functions_from_files_ids
            all_seen_functions = self.completed_function_ids.union(self.completed_w_err_function_ids).union(self.seen_functions_from_files_ids)
            functions, scopes = self.parse_func_objects(all_seen_functions, True)
            # remove functions in EXCLUDE_FUNC_CALL_FILEPATHS
            functions = [f for f in functions if not any([re.search(p, f['id'], re.IGNORECASE) for p in EXCLUDE_FUNC_CALL_FILEPATHS])] # or f['id'] in func_ids_w_callstacks]
            functions_map = {}
            for f in functions:
                functions_map[f['id']] = f
            scopes_map = {}
            for s in scopes:
                scopes_map[s['id']] = s


            # for symbol in g_var_ref_map:
            #     for ref in g_var_ref_map[symbol]:
            #         print(f"symbol: {symbol} ref: {ref}")


            # prepare function objects for quick lookup (could be done in a more efficiently @ time of lookup)
            function_objs = {}
            for f in self.completed_function_ids.union(self.completed_w_err_function_ids).union(self.seen_functions_from_files_ids):
            # for f in self.completed_function_ids:
                f = self.def_to_func_map.get(f, f)
                filepath = f.split(",")[-1].split("#")[0]
                
                obj = {
                    'id': f,
                    'name': f.split(",")[0],
                    "startLine": int(self.function_details.get(f, {}).get('start_line', 0)) + 1,  # apply +1 offset for vscode, specific per language server? this change was made for python
                    "endLine": int(self.function_details.get(f, {}).get('end_line', 0)) + 1  # apply +1 offset for vscode, specific per language server? this change was made for python
                }
                function_objs.setdefault(filepath, []).append(obj)


            start_lines = {}
            for filepath in function_objs:
                function_objs[filepath] = sorted(function_objs[filepath], key=lambda f: f['startLine'])
                start_lines[filepath] = list(map(lambda f: f['startLine'], function_objs[filepath]))


            def find_function(filepath, line):
                if filepath not in start_lines:
                    # TODO, QUERY FILE? Double check if this breaks finding valid functions. Ideally, this only resolves references that are not in a function
                    return f"__TOP_LEVEL__,{filepath}#0"

                # Find the insertion point for the line number
                idx = bisect.bisect_right(start_lines[filepath], line) - 1
                # startline and endline may be equal based on language server response
                if idx >= 0 and (function_objs[filepath][idx]['startLine'] == function_objs[filepath][idx]['endLine'] or function_objs[filepath][idx]['startLine'] <= line <= function_objs[filepath][idx]['endLine']):
                    return function_objs[filepath][idx]['id']
                return f"__TOP_LEVEL__,{filepath}#0"



            # find what function each ref was in and append to g_function_calls (came from /references not /incomingCalls|/outgoingCalls)
            total_call_refs = sum(len(refs) for refs in self.function_call_refs.values())
            processed_call_refs = 0
            _definition_dedup = {}  # (uri, line, char) -> definition result

            # Phase 1: Resolve which function each reference lives in.
            # For OmniSharp, /findusages is semantic — we trust the result and wire
            # edges directly without a /gotodefinition verification step. This avoids
            # column-offset bugs with C# member access (obj.Method), chained calls,
            # LINQ, extension methods, etc. where /gotodefinition at the reference
            # position resolves to the wrong symbol.
            refs_needing_lookup = []  # (f, ref, caller_func, dedup_key) — only for non-OmniSharp
            for f in self.function_call_refs:
                for ref in self.function_call_refs[f]:
                    processed_call_refs += 1
                    if processed_call_refs % 5000 == 0:
                        print_thread_safe(f"Processing function_call_refs (phase 1): {processed_call_refs} / {total_call_refs}")
                    caller_func = find_function(ref['uri'].replace("file://", ""), self.get_range(ref)['start']['line'])
                    if caller_func.split(":")[0] != f.split(":")[0]:
                        if self.is_omnisharp:
                            # OmniSharp: /findusages is Roslyn-powered semantic analysis.
                            # Wire edge directly — skip /gotodefinition verification because
                            # OmniSharp returns reference positions at the member access dot
                            # (e.g., "helper.DoWork" → column points to "."), which causes
                            # /gotodefinition to resolve to the variable, not the method.
                            # This affects obj.Method(), chained calls, null-conditional (?.)
                            # extension methods, LINQ, etc. Roslyn's /findusages already
                            # resolves the exact symbol (including overload resolution and
                            # interface implementations), so verification is redundant.
                            if caller_func and not caller_func.startswith("#"):
                                g_function_calls.setdefault(increment_lines_in_id(caller_func), set()).add(increment_lines_in_id(f))
                        else:
                            ref_range = self.get_range(ref)
                            dedup_key = (ref.get('uri', ''), ref_range['start']['line'], ref_range['start']['character'])
                            if dedup_key in _definition_dedup:
                                # Cache hit — process immediately
                                def_id = _definition_dedup[dedup_key].copy()
                                def_id['kind'] = 6
                                def_id['name'] = f.split(",")[0]
                                ref_def_lookup = self.get_id(def_id)
                                if ref_def_lookup == f:
                                    g_function_calls.setdefault(increment_lines_in_id(caller_func), set()).add(increment_lines_in_id(f))
                            else:
                                refs_needing_lookup.append((f, ref, caller_func, dedup_key))

            # Phase 2: Definition lookups for uncached refs
            if refs_needing_lookup:
                print_thread_safe(f"Processing function_call_refs (phase 2): {len(refs_needing_lookup)} uncached lookups")

            if self.is_omnisharp and self._reader_running and self.parallel_requests > 1:
                # ── OmniSharp batched path: no didOpen needed, can batch freely across files ──
                for batch_start in range(0, len(refs_needing_lookup), self.parallel_requests):
                    batch = refs_needing_lookup[batch_start:batch_start + self.parallel_requests]

                    pending = []  # (f, caller_func, dedup_key, handle, item, json_item)
                    for f, ref, caller_func, dedup_key in batch:
                        if dedup_key in _definition_dedup:
                            # Cache hit
                            def_id = _definition_dedup[dedup_key].copy()
                            def_id['kind'] = 6
                            def_id['name'] = f.split(",")[0]
                            if self.get_id(def_id) == f:
                                g_function_calls.setdefault(increment_lines_in_id(caller_func), set()).add(increment_lines_in_id(f))
                            continue

                        item, location_base, json_item = self._prepare_definition_item(ref)
                        if self.definition_cache.get(json_item, None):
                            _definition_dedup[dedup_key] = self.definition_cache[json_item][0]
                            def_id = _definition_dedup[dedup_key].copy()
                            def_id['kind'] = 6
                            def_id['name'] = f.split(",")[0]
                            if self.get_id(def_id) == f:
                                g_function_calls.setdefault(increment_lines_in_id(caller_func), set()).add(increment_lines_in_id(f))
                            continue

                        method, params = self._build_definition_request(location_base)
                        handle = self.send_request_async(method, params)
                        if handle is None:
                            response = self.send_request(method, params)
                            _definition_dedup[dedup_key] = self._process_definition_response(response, item, json_item)[0]
                            def_id = _definition_dedup[dedup_key].copy()
                            def_id['kind'] = 6
                            def_id['name'] = f.split(",")[0]
                            if self.get_id(def_id) == f:
                                g_function_calls.setdefault(increment_lines_in_id(caller_func), set()).add(increment_lines_in_id(f))
                        else:
                            pending.append((f, caller_func, dedup_key, handle, item, json_item))

                    for f, caller_func, dedup_key, handle, item, json_item in pending:
                        response = self.collect_response(handle)
                        if response is None:
                            response = {"result": []}
                        _definition_dedup[dedup_key] = self._process_definition_response(response, item, json_item)[0]
                        def_id = _definition_dedup[dedup_key].copy()
                        def_id['kind'] = 6
                        def_id['name'] = f.split(",")[0]
                        if self.get_id(def_id) == f:
                            g_function_calls.setdefault(increment_lines_in_id(caller_func), set()).add(increment_lines_in_id(f))

                    if (batch_start + len(batch)) % 1000 < len(batch):
                        print_thread_safe(f"Processing function_call_refs (phase 2): {batch_start + len(batch)} / {len(refs_needing_lookup)}")
            else:
                # ── Sequential path (all non-OmniSharp servers) ──
                for i, (f, ref, caller_func, dedup_key) in enumerate(refs_needing_lookup):
                    if i % 1000 == 0 and i > 0:
                        print_thread_safe(f"Processing function_call_refs (phase 2): {i} / {len(refs_needing_lookup)}")
                    if dedup_key not in _definition_dedup:
                        _definition_dedup[dedup_key] = self.get_func_definition(ref)[0]
                    def_id = _definition_dedup[dedup_key].copy()
                    def_id['kind'] = 6
                    def_id['name'] = f.split(",")[0]
                    ref_def_lookup = self.get_id(def_id)
                    if ref_def_lookup == f:
                        g_function_calls.setdefault(increment_lines_in_id(caller_func), set()).add(increment_lines_in_id(f))



            ####################
            ##### START #####
            ####################
            # consolidate references (typscript shinanigans) - may break other languages?
            # this may botch ref accuracy!??!
                    

            def process_var(var_id, refs, refs_w_valid_refs):
                new_refs = set()
                for ref in refs:
                    sub_refs = refs_w_valid_refs.get(ref, set())
                    for sub_r in sub_refs:
                        if sub_r not in refs:
                            new_refs.add(sub_r)
                return var_id, new_refs




            refs_w_valid_refs = {
                var_id: set(
                    f"{','.join(var_id.split(',')[:-1])},{self.symbol_to_loc(ref)}"
                    for ref in refs if g_var_ref_map.get(f"{','.join(var_id.split(',')[:-1])},{self.symbol_to_loc(ref)}", [])
                )
                for var_id, refs in g_var_ref_map.items() if any([var_id.split("#")[0].endswith(ext) for ext in self.file_extensions])
            }  

            # Main loop to consolidate references
            print_thread_safe('Consolidating references...')
            j = 0

            while True:
                refs_to_add = {}
                with concurrent.futures.ThreadPoolExecutor(max_workers=self.NUM_THREADS) as executor:
                    futures = {
                        executor.submit(process_var, var_id, refs, refs_w_valid_refs): var_id
                        for var_id, refs in refs_w_valid_refs.items()
                    }
                    i = 0
                    for future in concurrent.futures.as_completed(futures):
                        var_id, new_refs = future.result()
                        if new_refs:
                            refs_to_add.setdefault(var_id, set()).update(new_refs)

                        # Increment iteration counter and print periodic progress
                        i += 1
                        if i % 5000 == 0:
                            print_thread_safe(
                                f"Consolidating references (vars complete): {i} / {len(refs_w_valid_refs)}"
                            )
                    for f in futures:
                        f.result()  # This blocks until each task is done

                if not refs_to_add:
                    break

                print_thread_safe('Had refs to add (update)')
                for var_id in refs_to_add:
                    refs_w_valid_refs[var_id] = refs_w_valid_refs[var_id].union(refs_to_add[var_id])

                j += 1
                print_thread_safe(f"Consolidating references (iterations): {j}")



            # sort refs in each node
            print_thread_safe("Sorting references...")
            def sort_refs(var_id, refs):
                return var_id, sorted(refs)
            new_refs_w_valid_refs = {}
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.NUM_THREADS) as executor:
                futures = {
                    executor.submit(sort_refs, var_id, refs): var_id
                    for var_id, refs in refs_w_valid_refs.items()
                }

                # Collect results as they complete
                for future in concurrent.futures.as_completed(futures):
                    var_id, new_refs = future.result()
                    new_refs_w_valid_refs[var_id] = new_refs

                for f in futures:
                    f.result()  # This blocks until each task is done
            refs_w_valid_refs = new_refs_w_valid_refs


            # remove vars that only point to self
            print_thread_safe("Removing self-references and empty-references...")
            new_refs_w_valid_refs = {}
            for var_id, refs in refs_w_valid_refs.items():
                if refs != [var_id] and len(refs) > 1:
                    new_refs_w_valid_refs[var_id] = refs
            refs_w_valid_refs = new_refs_w_valid_refs



            # track groups of vars that have the same refs
            print_thread_safe("Grouping variables with the same references...")
            group_hash_map = {}
            for var_id, refs in refs_w_valid_refs.items():
                group_hash = hash(frozenset(refs))
                group_hash_map.setdefault(group_hash, set()).add(var_id)


            print("Joining references (by group)...")
            # join references using group_hash_map as cache to not repeat work
            i = 0
            for group_hash, group_vars in group_hash_map.items():
                lists = [g_var_ref_map[var_id] for var_id in group_vars]
                # Fast dedup using (uri, line, char) tuple instead of full dict_to_frozenset
                seen_locs = set()
                joined_refs = []
                for sublist in lists:
                    for item in sublist:
                        rng = item.get('range', {}).get('start', {})
                        key = (item.get('uri', ''), rng.get('line', 0), rng.get('character', 0))
                        if key not in seen_locs:
                            seen_locs.add(key)
                            joined_refs.append(item)
                for var_id in group_vars:
                    g_var_ref_map[var_id] = joined_refs
                i += 1
                if i % 100 == 0:
                    print_thread_safe(f"Joining references: {i} / {len(group_hash_map)}")



            ####################
            ##### END #####
            ####################
            

            
            # for each reference, find the function it is in
            for var_id in g_var_ref_map:
                if not any([var_id.split("#")[0].endswith(ext) for ext in self.file_extensions]):
                    # skip vars not in this language server's responsibility
                    continue
                for ref in g_var_ref_map[var_id]:
                    # filepath = ref['uri'].replace("file://", "")
                    # line = self.get_range(ref)['start']['line']
                    if any([ref['uri'].endswith(ext) for ext in self.file_extensions]):
                        func = find_function(ref['uri'].replace("file://", ""), self.get_range(ref)['start']['line'])
                        ref['func_id'] = func  # "func" should be in "functions", if not, add it
            
            
            # keep only references that are in multiple functions/files
            for var_id in g_var_ref_map.copy():
                if not any([var_id.split("#")[0].endswith(ext) for ext in self.file_extensions]):
                    # skip vars not in this language server's responsibility
                    continue
                line = 0
                try: 
                    line = int(var_id.split('#')[1].split(':')[0])
                except:
                    pass
                var_func = find_function(var_id.split(',')[-1].split('#')[0], line)
                if len(set(r['func_id'] for r in g_var_ref_map[var_id]) | {var_func}) < 2: # only delete vars for languages this languge server is responsible for
                    del g_var_ref_map[var_id]

            # add state vars to functions
            for var_id in g_var_ref_map:
                if not any([var_id.split("#")[0].endswith(ext) for ext in self.file_extensions]):
                    # skip vars not in this language server's responsibility
                    continue


                for ref in g_var_ref_map[var_id]:
                    # add func if doesnt exist?
                    if ref['func_id'] not in functions_map:
                        funcs, f_scopes = self.parse_func_objects([ref['func_id']])
                        for f in funcs:
                            functions_map[f['id']] = f
                            functions.append(f)
                        for s in f_scopes:
                            if s['id'] not in scopes_map:
                                scopes_map[s['id']] = s
                                scopes.append(s)

                    functions_map.get(ref['func_id'], {}).setdefault('vars', set()).add(var_id)




            def increment_lines_in_symbol(symbol):
                self.get_range(symbol)['start']['line'] += 1
                self.get_range(symbol)['start']['character'] += 1
                self.get_range(symbol)['end']['line'] += 1
                self.get_range(symbol)['end']['character'] += 1
                # symbol['func_id'] = increment_lines_in_id(symbol['func_id'])
                return symbol

            # add lines to each function / state var references
            for f in functions:
                f['id'] = increment_lines_in_id(f['id'])
                f['filepath'] = increment_lines_in_id(f['filepath'])
                f['filepath_body'] = increment_lines_in_id(f['filepath_body'])
                f['startLine'] = int(f['startLine']) + 1
                f['endLine'] = int(f['endLine']) + 1
                f['vars'] = set([v for v in f.get('vars', [])])  # already incremented when setting references


            # swap function definitions in callstacks to real funcs 
            new_function_calls = ThreadSafeDict()
            for caller in g_function_calls:
                real_caller = self.def_to_func_map.get(caller, caller)
                ## NOTE: May want to add these conditionals back in to reduce size of output file or clutter in output (e.g.: .d.ts files) - however, may compromise other features like typescript source defs
                if any([re.search(p, real_caller, re.IGNORECASE) for p in EXCLUDE_FUNC_CALL_FILEPATHS]):
                    continue

                
                callees = set()
                for callee in g_function_calls[caller]:
                    real_callee = self.def_to_func_map.get(callee, callee)
                    # if not any([re.search(p, real_callee, re.IGNORECASE) for p in EXCLUDE_FUNC_CALL_FILEPATHS]):  # maybe remove .d.ts?
                    callees.add(real_callee)

                new_function_calls.setdefault(real_caller, set()).update(callees)
            g_function_calls = new_function_calls



            # incremenet lines for vscode to have accurate line numbers
            # NOTE: this breaks when running again via appending
            # new_client_func_calls = ThreadSafeDict()
            # for caller in g_function_calls:
            #     new_client_func_calls[increment_lines_in_id(caller)] = set([increment_lines_in_id(callee) for callee in copy.deepcopy(g_function_calls[caller])])
            # g_function_calls = new_client_func_calls

            # new_client_var_ref_map = ThreadSafeDict()
            # for var_id in g_var_ref_map:
            #     # new_client_var_ref_map[increment_lines_in_id(var_id)] = g_var_ref_map[var_id]
            #     new_client_var_ref_map[increment_lines_in_id(var_id)] = [increment_lines_in_symbol(ref_symbol) for ref_symbol in copy.deepcopy(g_var_ref_map[var_id])]
            # g_var_ref_map = new_client_var_ref_map
            # update vars


            # for each function, add vars w/ references to scope (combine w/ above)
            for f in functions:
                scope = scopes_map.get(f['scope_id'], None)
                if not scope:
                    continue
                for var_id in f.get('vars', []):
                    scope.setdefault('vars', set()).add(var_id)
            
            # sort vars in each scope
            for s in scopes:
                if 'vars' in s:
                    s['vars'] = sorted(s['vars'], key=lambda v_id: f"{','.join(v_id.split(',')[0:-1])}#{v_id.split('#')[1].split(':')[0].zfill(5)}")


            # cleanup vars for each scope
            vars_group = {}
            for s in scopes:
                for var_id in s.get('vars', []):
                    # sort var_ids by func_id (may need to pad startline with zeros to sort correctly)
                    g_var_ref_map[var_id] = sorted(g_var_ref_map.get(var_id, []), key=lambda r: f"{','.join(r['func_id'].split(',')[0:-1])}#{r['func_id'].split('#')[1].split(':')[0].zfill(5)}")

                    # group vars if all have same references
                    # accounts for lsp servers that return all instances of a symbol in document/symbols instead of just declarations
                    ref_locations = tuple([self.symbol_to_loc(r) for r in g_var_ref_map[var_id]])
                    
                    vars_group.setdefault(ref_locations, set()).add(var_id)



            # generate HTML + state var text highlights
            for s in scopes:
                s['scope_summary_html'] = s.get('scope_summary_html', "")
                scope_filepath = s['id'].split(",")[-1].split("#")[0]
                state_vars_html = ""
                state_vars_html_header = ""
                for var_i, var_id in enumerate(s.get('vars', [])):
                    ref_locations = tuple([self.symbol_to_loc(r) for r in g_var_ref_map[var_id]])
                    grouped_vars = vars_group.get(ref_locations, [var_id])
                    grouped_vars_locs = [v.split(',')[-1] for v in grouped_vars]

                    # continue if already seen this set of vars
                    if len(grouped_vars) > 1 and var_id != next(iter(grouped_vars)):
                        continue

                    var_name = var_id.split(",")[0]
                    state_vars_html_header += f"<input type='checkbox' id='statevar-toc-{var_name}'><a href='scrollTo:a[value^=\"{var_id},\"]'>{var_name}</a><br>"
                    
                    # print grouped vars or var_id if no group is found
                    # NOTE: consider deleting from ref if found in grouped var_id
                    for grouped_var_id in grouped_vars:
                        var_name = grouped_var_id.split(",")[0]
                        var_func = functions_map.get(grouped_var_id, {})
                        var_filepath = grouped_var_id.split(",")[-1]
                        var_filename = var_filepath.split("/")[-1]
                        start_line = var_filepath.split("#")[1].split(":")[0]
                        start_char = var_filepath.split("#")[1].split(":")[1]

                        init_filepath, lines = var_filepath.split("#")
                        init_line = lines.split(":")[0]
                        content = get_file_content(init_filepath, int(init_line) - 1).strip()
                        
                        state_vars_html += f"<div><a value='{var_id}' href='file://{var_filepath}'>{var_filename} | {var_name}</a> | {content}</div>"

                        self.add_textHighlight(var_i, var_filepath, int(start_line), int(start_char), int(start_char) + len(var_name), var_name)

                    state_var_html_arr = []
                    for i, ref in enumerate(g_var_ref_map[var_id]):
                        ref_id = self.symbol_to_loc(ref)
                        if ref_id in grouped_vars_locs:
                            continue

                        ref_filepath = ref_id.split(",")[-1]
                        ref_filename = ref_filepath.split("/")[-1]
                        if ref_filepath in var_filepath:
                            # skip reference to declaration based on location
                            continue

                        if i > self.max_ref_tracking_count:
                            state_var_html_arr.append(f"<div class='collapsable'>...max references reached ({len(g_var_ref_map[var_id])})...<br></div>")
                            break

                        self.add_textHighlight(var_i, ref['uri'].replace("file://", ""), int(self.get_range(ref)['start']['line']), int(self.get_range(ref)['start']['character']), int(self.get_range(ref)['end']['character']), var_name)

                        # get content
                        ref_func = functions_map.get(ref['func_id'], {})
                        ref_content = get_file_content(ref['uri'].replace("file://", ""), self.get_range(ref)['start']['line'] - 1)

                        # skip if content does not contain more than var_name... may be a declaration that was not grouped (this may break stuff)
                        # if not contains_more_than_search_str(ref_content, var_name):
                        #     continue


                        # guess if node is read/write
                        read_write_guess = ""
                        if self.guess_ref_read_write and ref_content:
                            # NOTE: THIS WILL NOT WORK FOR ALL LANGUAGES
                            trimmed_content = ref_content.split("'")[0].split('"')[0].split("`")[0].split("==")[0].split(">=")[0].split(">=")[0].split("!=")[0]  # look before quotes and equalities
                            trimmed_var_name = var_name.split(".")[-1].split("$")[-1]  # accomodate for how LSP's may disable root name vs. how it's referenced
                            read_write_guess = "(w)" if "=" in trimmed_content and trimmed_var_name in trimmed_content.split("=")[0] else "(r)" # guess (w) if var is left of assignment operator
                            # look to the left of a single =. accomodate languages where no spaces are required. Don't include equalities such as >= <=.

                            # PATCH P2.5 — compound-assignment and mutator-call
                            # detection. The original heuristic misses:
                            #   - `x += 1` / `-=` / `|=` / `&=` / `<<=` / `>>=`
                            #   - Rust atomic mutators: `.store(...)` `.swap(...)`
                            #     `.fetch_add(...)` `.compare_exchange(...)`
                            #   - Java `AtomicInteger.set(...)` / `getAndAdd(...)`
                            #   - setter-style method names: `set_foo(...)`,
                            #     `SetFoo(...)`, `write_foo(...)`, `put(...)`.
                            # These are extremely common in real code and
                            # systematically get mis-classified as reads today.
                            _COMPOUND_OPS = ("+=", "-=", "*=", "/=", "%=", "|=", "&=", "^=", "<<=", ">>=", "??=", ".=")
                            _MUTATOR_METHOD_RE = re.compile(
                                rf"(?:{re.escape(trimmed_var_name)}|[\w$]+)\s*\.\s*"
                                r"(set_?\w*|write_?\w*|put|push|store|swap|assign|clear|reset|"
                                r"fetch_(?:add|sub|and|or|xor|update|max|min)|"
                                r"compare_(?:and_swap|exchange|exchange_weak)|"
                                r"getAndSet|getAndAdd|getAndIncrement|getAndDecrement|compareAndSet|"
                                r"getAndUpdate|accumulateAndGet|lazySet|"
                                r"add(?!ress|r)|remove|delete|erase|pop|shift|unshift|replace|splice)"
                                r"\s*\(",
                                re.IGNORECASE,
                            )
                            if read_write_guess == "(r)":
                                # 1. compound assignments like `x += 1`
                                _left = trimmed_content.split("=", 1)[0]
                                if any(op in ref_content for op in _COMPOUND_OPS) and trimmed_var_name in _left + "=":
                                    read_write_guess = "(w)"
                                # 2. mutator method called on the var
                                elif _MUTATOR_METHOD_RE.search(ref_content):
                                    read_write_guess = "(w*)"   # "writeish" — called a mutator

                            # if regex (.*trimmed_var_name.*)
                            if read_write_guess == "(r)" and re.search(rf"[a-zA-Z0-9_$]+\(.*{re.escape(trimmed_var_name)}.*\)", ref_content):
                                read_write_guess = "(r*)"

                        # id='{v.name}~{get_loc_id(loc.function)}'
                        func_link_html = f"<input type='checkbox' id='{var_name}~{ref_func.get('id', '')}' style='vertical-align: middle'> <a href='#{ref_func['id']}' data-scope='{ref_func['id']}'>🔗<a> " if ref_func else ""
                        state_var_html_arr.append(f"<div class='collapsable'>&emsp;{read_write_guess}{func_link_html}<a href='file://{ref_id.split(',')[-1]}' value='{ref_func.get('id', '')}'>{ref_func.get('qualifiedName_full', f'{ref_filename}.__TOP_LEVEL__')}#{self.get_range(ref)['start']['line']}</a> | {ref_content}</div>") # ref html
                        # <a value='scooby,~/tools/slither-custom-tooling/solidity/solidity_test_files/test.sol#659:5' href='file://~/tools/slither-custom-tooling/solidity/solidity_test_files/test.sol#669:9'>test_contract.scooby | \ud83c\udfaf\ud83d\udfe2#L669</a>
                    
                    state_var_html_arr = list(dict.fromkeys(state_var_html_arr))  # remove duplicates
                    state_var_html_arr = sorted(state_var_html_arr, reverse=True)
                    state_var_html_to_add = "".join(state_var_html_arr)
                    # do not add if trimmed references does not contain current scope filepath
                    if scope_filepath in state_var_html_to_add:
                        state_vars_html += state_var_html_to_add

                    if state_vars_html != "":
                        state_vars_html += "<br>"
                
                # if state_vars_html:
                #     # print("state vars in scope: ", s['id'])
                #     # compress to reduce change of out of memory exceptions
                #     s['scope_summary_html'] += f"<h2>State Vars</h2>{state_vars_html_header}<br><br>{state_vars_html}"

                ## add functions to scope
                s['functions'] = [f['id'] for f in functions if f['scope_id'] == s['id']]
                func_html = ""
                for f in [f2 for f2 in functions if f2['scope_id'] == s['id']]:
                    func_link_html = f"<input type='checkbox' id='function-{f.get('id', '')}' style='vertical-align: middle'> <a href='#{f['id']}' data-scope='{f['id']}'>🔗</a>"
                    func_html += f"<div>{func_link_html} <a href='file://{f['filepath']}:{f['startCol']}' value='{f['id']}'>{f['qualifiedName_full']}</a></div>"
                
                # if func_html:
                #     s['scope_summary_html'] += f"<h2>Functions</h2>{func_html}"

                # compress to reduce change of out of memory exceptions
                # NOTE: Commenting out as we are rebuilding using sqlite, may add back if needed
                # s['scope_summary_html'] = zlib.compress(s.get('scope_summary_html', '').encode()).hex()


                





            
            # convert to list (to allow JSON serialization for output)
            # for caller in g_function_calls:
            #     g_function_calls[caller] = list(g_function_calls[caller])

            # for parent in g_class_inheritance:
            #     g_class_inheritance[parent] = list(g_class_inheritance[parent])


            ## IS THIS BROKEN NOW? DO I NEED TO UPDATE THREADSAFEDICT (similar to g_function_calls & g_class_inheritance)?
            # convert to list for json output
            scopes_map = {}
            for s in scopes:
                scopes_map[s['id']] = s

            for f in functions:
                if 'vars' in f:
                    f['vars'] = list(f['vars'])
                if f['scope_id'] in scopes_map:
                    if f['id'] not in scopes_map[f['scope_id']].get('functions', []):
                        scopes_map[f['scope_id']].setdefault('functions', []).append(f['id'])
            for s in scopes:
                if 'vars' in s:
                    s['vars'] = list(s['vars'])
                if 'functions' not in s:
                    s['functions'] = []

                    
            ## parallel: may need to reset functions/scopes from here
            # join functions / scopes, dedupe

            # note: this may break if new references are found in each function such that each function has different metadata / hash
            for filepath in self.evaled_files:
                g_seen_files[filepath] = True # only add file to seen after it's data has been fully processed

            for filepath in self.seen_files_for_refs:
                g_seen_files_for_refs[filepath] = True # only add file to seen after it's data has been fully processed
                
            # PATCH P5.1 — tag synthetic decompiler symbols before emit so
            # downstream renderers can fold them. Non-destructive: the tag
            # just lives on the dict; existing consumers ignore unknown keys.
            for _f in functions:
                _n = _f.get('name') or _f.get('label') or ''
                _tag = classify_synthetic(_n.split('.')[-1])
                if _tag:
                    _f['synthetic'] = _tag
            for _s in scopes:
                _n = _s.get('name') or _s.get('label') or ''
                _tag = classify_synthetic(_n.split('.')[-1])
                if _tag:
                    _s['synthetic'] = _tag

            g_scopes.extend_by_id(scopes)
            g_functions.extend_by_id(functions)
            
            # if args.append_output_file:
            #     def try_open_file(filepath):
            #         try:
            #             return json.loads(open(filepath, "r").read())
            #         except:
            #             return None
                    
            #     current_functions_html = try_open_file(f"{args.output_file_prefix}functions_html.json") or []
            #     current_scope_summaries_html = try_open_file(f"{args.output_file_prefix}scope_summaries_html.json") or []
            #     current_function_calls = try_open_file(f"{args.output_file_prefix}function_calls.json") or {}
            #     current_class_inheritance = try_open_file(f"{args.output_file_prefix}class_inheritance.json") or {}


            # functions = current_functions_html + functions if args.append_output_file else functions
            # scopes = current_scope_summaries_html + scopes if args.append_output_file else scopes
            # g_function_calls = {**current_function_calls, **g_function_calls} if args.append_output_file else g_function_calls
            # g_class_inheritance = {**current_class_inheritance, **g_class_inheritance} if args.append_output_file else g_class_inheritance


            # open(f"{args.output_file_prefix}decorations.json", 'w').write(json.dumps(self.textHighlights))
            # open(f"{args.output_file_prefix}functions_html.json", "w").write(json.dumps(list(functions)))
            # open(f"{args.output_file_prefix}scope_summaries_html.json", "w").write(json.dumps(list(scopes)))
            # open(f"{args.output_file_prefix}function_calls.json", "w").write(json.dumps(g_function_calls))
            # open(f"{args.output_file_prefix}class_inheritance.json", "w").write(json.dumps(g_class_inheritance))

            # open(f"{args.output_file_prefix}errors.json", "w").write(json.dumps(errors))



            # parallel, shold never reach here

            g_data_updated = True
            # break out of inifinite loop if not in streaming mode
            if not args.streaming_mode:
                break
            

        print("done.")
        end = datetime.datetime.now()
        minutes = (end - start).total_seconds() / 60
        print(f"Time taken: {math.floor(minutes / 60)} hours ({minutes % 60} minutes) to complete. ({minutes} total minutes)")




# Usage example
if __name__ == "__main__":
    secondary_init_timeout_default = 30

    lanaguage_defaults_map = {
        "bash": {
            "exts": [".sh"],
            "cmd": ["bash-language-server", "start"]
        },
        "powershell": {
            "exts": [".ps1"],
            "cmd": ["pwsh", "-NoLogo", "-NoProfile", "-Command", "/app/powershell-ls/PowerShellEditorServices/Start-EditorServices.ps1", "-Stdio", "-BundledModulesPath", "/app/powershell-ls"]
        },
        "lua": {
            "exts": [".lua"],
            "cmd": ["lua-language-server"]
        },
        "php": {
            "exts": [".php"],
            "cmd": ["intelephense", "--stdio"],
            "forced_args": [("init_timeout", secondary_init_timeout_default)]
        },
        "go": {
            "exts": [".go"],
            "cmd": ["gopls", "serve"]
        },
        "ruby": {
            "exts": [".rb"],
            # "cmd": ["solargraph", "stdio"]  # works without bundle install but weak cross-file references
            "cmd": ["ruby-lsp"]
        },
        "asm": {
            "exts": [".asm"],
            "cmd": ["asm-lsp"]
        },
        "c": {
            "exts": [".c", ".cc", ".cpp", ".m"],
            "cmd": ["clangd"], # ccls
            "forced_args": [("disable_outgoing_calls", True), ("disable_inheritance", True), ("disable_get_id_from_ref", True)]  # clangd default params
        },
        "c#": {
            "exts": [".cs"],
            "cmd": ["OmniSharp", "--stdio"],  # OmniSharp native protocol; -s <sln> added at runtime
            "forced_args": [
                ("init_timeout", 90),
                ("disable_inheritance", True),     # OmniSharp has no typeHierarchy via native protocol
                ("disable_incoming_calls", True),
                ("disable_outgoing_calls", True),
            ]
        },
        "typescript": {
            # PATCH P6.2 — include `.vue` and `.jsx`. typescript-language-server
            # parses `<script setup lang="ts">` blocks by virtue of the
            # filename extension being whitelisted; full template analysis
            # needs a Vue-specific LSP (volar), which this image doesn't ship.
            "exts": [".js", ".jsx", ".ts", ".tsx", ".vue", ".mjs", ".cjs"],
            "cmd": ["typescript-language-server", "--stdio"]
        },
        "rust": {
            "exts": [".rs"],
            "cmd": ["rust-analyzer"],
            "forced_args": [
                ("disable_outgoing_calls", True),
                ("resp_timeout", 180) # call hierarchy in rust may take multiple minutes to respond
            ]
        },
        "python": {
            "exts": [".py"],
            "cmd": ["pyright-langserver", "--stdio"]
        },
        "kotlin": {
            "exts": [".kt"],
            "cmd": ["kotlin-language-server"],
            "forced_args": [("init_timeout", secondary_init_timeout_default)]
        },
        "java": {
            "exts": [".java"],
            "cmd": [
                "java",
                "-Declipse.application=org.eclipse.jdt.ls.core.id1",
                "-Dosgi.bundles.defaultStartLevel=4",
                "-Declipse.product=org.eclipse.jdt.ls.core.product",
                "-Dlog.level=ALL",
                "-Xmx4G",
                "--add-modules=ALL-SYSTEM",
                "--add-opens", "java.base/java.util=ALL-UNNAMED",
                "--add-opens", "java.base/java.lang=ALL-UNNAMED",
                "-jar", "/app/java-ls/plugins/org.eclipse.equinox.launcher_1.7.100.v20251111-0406.jar", # "/app/java-ls/plugins/org.eclipse.equinox.launcher_*.jar",  # change this
                "-configuration", "/app/java-ls/config_linux",  # change this
                "-data", "/tmp/java-ls-data"   # change this
            ],
            "forced_args": [("disable_selectionRange", True)]
        },
        "groovy": {
            "exts": [".groovy"],
            "cmd": ["groovy-ls"]
        },
        "elixir": {
            "exts": [".ex", ".exs"],
            "cmd": ["expert_linux_amd64"]
        },
        "ocaml": {
            "exts": [".ml", ".mli"],
            "cmd": ["ocamllsp"]
        },
        "zig": {
            "exts": [".zig"],
            "cmd": ["zls"]
        },
        "haskell": {
            "exts": [".hs", ".hs-boot", ".lhs"],
            "cmd": ["haskell-language-server-wrapper", "--lsp"]
        },
        "scala": {
            "exts": [".scala", ".sc"],
            "cmd": ["metals"],
            "forced_args": [
                ("init_timeout", 120),
                ("resp_timeout", 120),
                ("force_references", True)
            ]
        },
        "solidity": {
            "exts": [".sol"],
            # "cmd": ["wake", "lsp", "--port", "1234"]  # wake is installed but only supports tcp connections, this script must be modified to communicate over TCP instead of stdin/stdout
            "cmd": ["nomicfoundation-solidity-language-server", "--stdio"],
            "forced_args": [("init_timeout", secondary_init_timeout_default)]
        },
        # PATCH P6.1 — Swift registration. sourcekit-lsp ships with every
        # Swift toolchain (Xcode on macOS, `swift-lang` deb on Linux). If
        # the image doesn't have a Swift toolchain installed, this entry
        # is harmless — the `swift` language just won't auto-start.
        "swift": {
            "exts": [".swift"],
            "cmd": ["sourcekit-lsp"],
            "forced_args": [("init_timeout", secondary_init_timeout_default)]
        }
    }

    # take input args for project_dir using argparse
    arg_parser = ArgumentParserWithTracking()
    arg_parser.add_argument("--project_dir", "-d", required=True, type=str, help="Project directory to analyze")
    arg_parser.add_argument("--include-paths", "-in", type=str, default="", help="Paths to include in analysis <regex>")
    arg_parser.add_argument("--exclude-paths", "-ex", type=str, default="", help="Paths to exclude from analysis <regex>")
    arg_parser.add_argument("--languages", "-l", type=str, help=f"Language of project, comma delimited. {{{(','.join(['all'] + list(lanaguage_defaults_map.keys())))}}}")
    arg_parser.add_argument("--exclude-languages", "-el", type=str, default="", help=f"Exclude language when using 'all'. Comma delimited {{{','.join(lanaguage_defaults_map.keys())}}}")
    arg_parser.add_argument("--extensions", "-e", type=str, help="Extensions, comma separated (e.g, '.js,.ts,.tsx)")
    arg_parser.add_argument("--cmd-override", "-c", type=str, help="Override command")
    arg_parser.add_argument("--disable-get-id-from-ref", action="store_true", default=False, help="Disable getting id from reference (e.x. clangd will get tripped up on func definitions)")
    arg_parser.add_argument("--max-ref-tracking-count", "-m", type=int, default=50, help="Max number of references to track for a variable")
    arg_parser.add_argument("--force-references", "-fr", action="store_true", default=False, help="Force using references instead of callHierarchy (if LSP does states it supports callHierarchy capability however is not reliable)")
    arg_parser.add_argument("--force-callHierarchy", "-fch", action="store_true", default=False, help="Force using callHierarchy instead of references (if LSP does not state they support callHierarchy capability in init response)")
    arg_parser.add_argument("--disable-default-excludes", "-dde", action="store_true", default=False, help="Disable default excludes (e.g. node_modules, .git, etc.)")
    arg_parser.add_argument("--disable-selectionRange", "-ds", action="store_true", default=False, help="Disable selectionRange (if 'selectionRange' is not accurate for LSP, will use 'range' instead)")
    arg_parser.add_argument("--disable-incoming-calls", "-di", action="store_true", default=False, help="Disable searching incoming calls")
    arg_parser.add_argument("--disable-outgoing-calls", "-do", action="store_true", default=False, help="Disable searching teamsoutgoing calls")
    arg_parser.add_argument("--disable-inheritance", "-dih", action="store_true", default=False, help="Disable searching inheritance")
    arg_parser.add_argument("--only-functions", "-of", action="store_true", default=False, help="Only search for functions (no variables, no classes, no scopes, no inheritance)")
    arg_parser.add_argument("--pause-for-verification", "-p", action="store_true", default=False, help="Pause for capabilities output, show what a lanaguage server supports (may not be accurate, some servers support more than they output as capabilities).")
    arg_parser.add_argument("--guess-ref-read-write", "-g", action="store_false", default=True, help="Guess if a reference is a read or write based on content (may not be accurate).")
    arg_parser.add_argument("--resp-timeout", "-rt", type=float, default=20, help="Response timeout. Amount of time to wait for a response from the language server. Too small timeout will not allow language servers to process requests. Default: 3min")
    arg_parser.add_argument("--resp-pause", "-rp", type=float, default=0, help="Time to wait before sending next request to language server")
    arg_parser.add_argument("--init-timeout", "-it", type=float, default=45, help="Seconds of silence after last server message before assuming initialization is done")
    arg_parser.add_argument("--init-pause", "-ip", type=float, default=2, help="Time to wait before sending init message after starting server")
    arg_parser.add_argument("--output-file-prefix", "-o", type=str, default="./.vscode/ext-static-analysis/cache/", help="Output file prefix")
    arg_parser.add_argument("--append_output_file", "-a", action="store_true", default=False, help="Append to output file")
    arg_parser.add_argument("--prescript", "-ps", type=str, help="Prescript to run before starting language server")
    arg_parser.add_argument("--postscript", "-po", type=str, help="Postscript to run after starting language server")
    arg_parser.add_argument("--auto-accept-all-languages", "-aaal", action="store_true", default=False, help="Auto accept all languages")
    arg_parser.add_argument("--verbose", "-v", action="store_true", default=False, help="Print all requests / responses to & from language server. Can also be toggled at runtime by creating/removing a '.verbose' file in the project directory.")
    arg_parser.add_argument("--stderr-to-file", "-stf", action="store_true", default=False, help="Redirect stderr to file")
    arg_parser.add_argument("--debug", action="store_true", default=False)
    arg_parser.add_argument("--streaming-mode", action="store_true", default=False, help="Enable streaming mode (useful for large projects, will stream results to output file as they are processed / triggered by viewing in editor)")
    arg_parser.add_argument("--streaming-mode-disable-recursive-ref-search", action="store_true", default=False, help="Enable streaming mode (useful for large projects, will stream results to output file as they are processed / triggered by viewing in editor)")
    arg_parser.add_argument("--parallel-requests", "-pr", type=int, default=5, help="Max concurrent LSP requests in flight (default 5)")

    args = arg_parser.parse_args()

    if args.debug:
        print("Waiting for debugger to attach...")
        debugpy.listen(("0.0.0.0", 5678))
        debugpy.wait_for_client()

    # if language is not defined, extensions and cmd_override must be defined

    if not args.languages and not args.extensions and not args.cmd_override:
        print(f"Must define language (-l <{'|'.join((['all'] + list(lanaguage_defaults_map.keys())))}>)   |OR|   extensions (-e '.js') AND cmd_override (-c '<lsp_server>')")
        exit(1)

    if args.languages == "all" and any([args.cmd_override, args.extensions]):
        print("All languages will try to run all default languages and their languaage servers, cannot override command or extensions for all languages")
        exit(1)



    # if .vscode/ext-static-analysis doesn't exist, create it, including all paths if they don't exist
    created_dir = False
    if not os.path.exists(f"{args.project_dir}/.vscode/ext-static-analysis"):
        os.makedirs(f"{args.project_dir}/.vscode/ext-static-analysis", exist_ok=True)
        created_dir = True

    if not os.path.exists(args.output_file_prefix):
        os.makedirs(args.output_file_prefix, exist_ok=True)




    # copy search_templates.json and help.html from /app/templates to .vscode/ext-static-analysis
    try:
        shutil.copy(f"{current_script_path}/templates/search_templates.json", f"{args.project_dir}/.vscode/ext-static-analysis/search_templates.json")
        shutil.copy(f"{current_script_path}/templates/help.html", f"{args.project_dir}/.vscode/ext-static-analysis/help.html")
    except PermissionError:
        print(f"Warning: Could not copy templates to {args.project_dir}/.vscode/ext-static-analysis/ (permission denied), skipping.")
    





    # run prescript wait for completion
    if args.prescript:
        print(f"Running prescript: {args.prescript}")
        subprocess.run(args.prescript, shell=True)

    INCLUDE_FILEPATHS = [p for p in args.include_paths.split(",") if p != ""]

    EXCLUDE_FUNC_CALL_FILEPATHS = args.exclude_paths.split(",") if args.disable_default_excludes else (EXCLUDE_FUNC_CALL_FILEPATHS + args.exclude_paths.split(","))
    EXCLUDE_FUNC_CALL_FILEPATHS = [p for p in EXCLUDE_FUNC_CALL_FILEPATHS if p != ""]
    
    languages = [l for l in lanaguage_defaults_map.keys() if l not in args.exclude_languages.split(',')] if args.languages == "all" else args.languages.split(",")
    
    # if args.project_dir is relative, make it absolute
    args.project_dir = os.path.expanduser(args.project_dir)
    args.project_dir = os.path.abspath(args.project_dir)

    # PATCH P4.4 — read `extra_symbol_search_roots` from the project's
    # .vscode/ext-static-analysis/settings.json. These are additional
    # directories that will be walked for source files when the scan is
    # kicked off, even if they live outside `project_dir`. Needed for
    # scenarios like `_ilspy_dump/` where each DLL is in its own sibling
    # directory and the extractor has to see all of them to resolve
    # cross-assembly references.
    extra_symbol_search_roots = []
    _settings_path = os.path.join(
        args.project_dir, ".vscode", "ext-static-analysis", "settings.json",
    )
    if os.path.exists(_settings_path):
        try:
            with open(_settings_path) as _fh:
                _settings = json.load(_fh)
            for _root in _settings.get("extra_symbol_search_roots", []) or []:
                _abs = os.path.abspath(
                    os.path.join(args.project_dir, os.path.expanduser(_root))
                )
                if os.path.isdir(_abs) and _abs not in extra_symbol_search_roots:
                    extra_symbol_search_roots.append(_abs)
            if extra_symbol_search_roots:
                print(f"[P4.4] extra_symbol_search_roots: {extra_symbol_search_roots}")
        except (OSError, json.JSONDecodeError) as _e:
            print(f"[P4.4] warning: could not parse {_settings_path}: {_e}")


    # process languages to scan
    if args.languages == "all":
        found_languages = []
        for language in languages:
            default_extensions = lanaguage_defaults_map[language].get('exts', []) if language in lanaguage_defaults_map else []
            extra_extensions = [ext.strip() for ext in args.extensions.split(",") if ext.strip() != "" and ext.strip().startswith(".")] if args.extensions else []
            extensions = list(set(default_extensions + extra_extensions))
            # check files in project_dir match extension and not in EXCLUDE_FUNC_CALL_FILEPATHS, include root of filepath
            
            running_for_language = False
            for root, _, files in os.walk(args.project_dir):
                if running_for_language == True:
                    break
                for file in files:
                    filepath = os.path.join(root, file)
                    if any([filepath.endswith(ext) for ext in extensions]) and in_scope(filepath):
                        running_for_language = True
                        break

            if running_for_language:
                # PATCH P5.3 — when we detect a Ghidra/IDA pseudo-C dump,
                # surface it so the operator knows this is reverse-
                # engineering output rather than a real C project.
                if language == "c":
                    _ghidra_files = []
                    for _root, _, _files in os.walk(args.project_dir):
                        for _f in _files:
                            if _f.endswith((".c", ".h")):
                                _fp = os.path.join(_root, _f)
                                if is_ghidra_decompiled_file(_fp):
                                    _ghidra_files.append(_fp)
                                    break
                        if _ghidra_files:
                            break
                    if _ghidra_files:
                        print(f"[P5.3] Ghidra-style decompilation detected (sample: {_ghidra_files[0]}) — "
                              f"FUN_/DAT_/LAB_ symbols will be tagged as synthetic.")
                print(f"Running LSP Client for language: {colored.fg('yellow')}{language}{colored.attr('reset')}")
                found_languages.append(language)
        
        if not args.auto_accept_all_languages:
            while True:
                timeout = 8
                r = input_with_timeout(f"Are you sure you want to run for all languages (auto 'y' in {timeout}sec)? (Y/n): ", timeout, 'y')
                if r.lower() != "y" and len(r) != 0:
                    exit(1)
                break

        languages = found_languages


    def run_language_client(language, ls_file_queue):
        # if not overriding language server, use defaults
        if not args.cmd_override:
            for forced_args in lanaguage_defaults_map[language].get('forced_args', []):
                forced_arg, val = forced_args
                # if currently set to default value, override w/ forced value
                if not was_explicitly_passed(forced_arg, args):
                    setattr(args, forced_arg, val)

        # Java: if no Maven/Gradle build descriptor exists, create Eclipse project files so
        # JDT uses EclipseProjectImporter instead of InvisibleProjectImporter. Without this,
        # JDT infers inconsistent source roots across files, causing package mismatches and
        # null Range errors in callHierarchyIncomingCalls.
        if language == "java" and not args.cmd_override:
            project_dir = os.path.abspath(args.project_dir)
            has_build = any(os.path.exists(os.path.join(project_dir, f))
                            for f in ["pom.xml", "build.gradle", "build.gradle.kts"])
            if not has_build:
                project_name = os.path.basename(project_dir)
                dot_project = os.path.join(project_dir, ".project")
                dot_classpath = os.path.join(project_dir, ".classpath")
                if not os.path.exists(dot_project):
                    print(f"[java] No build descriptor found, creating .project (EclipseProjectImporter)")
                    with open(dot_project, "w") as f:
                        f.write(f"""<?xml version="1.0" encoding="UTF-8"?>
<projectDescription>
  <name>{project_name}</name>
  <buildSpec>
    <buildCommand>
      <name>org.eclipse.jdt.core.javabuilder</name>
    </buildCommand>
  </buildSpec>
  <natures>
    <nature>org.eclipse.jdt.core.javanature</nature>
  </natures>
</projectDescription>""")
                if not os.path.exists(dot_classpath):
                    print(f"[java] No build descriptor found, creating .classpath (source root: {project_dir})")
                    with open(dot_classpath, "w") as f:
                        f.write("""<?xml version="1.0" encoding="UTF-8"?>
<classpath>
  <classpathentry kind="src" path="."/>
  <classpathentry kind="con" path="org.eclipse.jdt.launching.JRE_CONTAINER"/>
  <classpathentry kind="output" path="bin"/>
</classpath>""")

        # C#/OmniSharp: find or generate .sln, convert References to ProjectReferences
        if language == "c#" and not args.cmd_override:
            project_dir = os.path.abspath(args.project_dir)
            sln_path = None
            # Search for .sln in project dir, then parent (for multi-assembly setups)
            search_dirs = [project_dir, os.path.dirname(project_dir)]
            for search_dir in search_dirs:
                for f in sorted(os.listdir(search_dir)):
                    if f.endswith('.sln'):
                        sln_path = os.path.join(search_dir, f)
                        break
                if sln_path:
                    break
            if not sln_path:
                # PATCH P4.2 — when neither the project dir nor its parent
                # has a *.sln, glob the entire tree for *.csproj and
                # synthesise a minimal .sln into the project_dir so
                # OmniSharp has something to load. Needed for fixtures
                # like `csharp_multi_dll/A,B,C` where no shared sln
                # exists. If no csproj is found either, we synthesise
                # a throw-away per-directory csproj too so single-
                # directory ILSpy dumps (`_ilspy_dump/CoreLib.dll/...`)
                # load at all.
                _csproj_files = []
                for _root_walk, _, _files in os.walk(project_dir):
                    for _f in _files:
                        if _f.endswith(".csproj"):
                            _csproj_files.append(os.path.join(_root_walk, _f))

                # For dirs with .cs files but no .csproj, drop a minimal
                # <Project Sdk="Microsoft.NET.Sdk"> and include it.
                _synth_csprojs = []
                if not _csproj_files:
                    _cs_dirs = set()
                    for _root_walk, _, _files in os.walk(project_dir):
                        if any(_f.endswith(".cs") for _f in _files):
                            _cs_dirs.add(_root_walk)
                    for _d in sorted(_cs_dirs):
                        _proj_name = os.path.basename(_d.rstrip("/")) or "proj"
                        _csproj_path = os.path.join(_d, f"_autogen_{_proj_name}.csproj")
                        if not os.path.exists(_csproj_path):
                            try:
                                with open(_csproj_path, "w") as _cf:
                                    _cf.write(
                                        "<Project Sdk=\"Microsoft.NET.Sdk\">\n"
                                        "  <PropertyGroup>\n"
                                        "    <TargetFramework>net8.0</TargetFramework>\n"
                                        "    <RootNamespace>"
                                        + re.sub(r"[^A-Za-z0-9_]", "_", _proj_name)
                                        + "</RootNamespace>\n"
                                        "    <LangVersion>latest</LangVersion>\n"
                                        "    <Nullable>annotations</Nullable>\n"
                                        "  </PropertyGroup>\n"
                                        "</Project>\n"
                                    )
                                _csproj_files.append(_csproj_path)
                                _synth_csprojs.append(_csproj_path)
                            except OSError as _e:
                                print(f"[c#][P4.2] could not synthesise {_csproj_path}: {_e}")

                if _csproj_files:
                    _sln_path = os.path.join(project_dir, "_autogen.sln")
                    _sln_lines = [
                        "Microsoft Visual Studio Solution File, Format Version 12.00",
                        "# Visual Studio Version 17",
                    ]
                    _proj_guid = "9A19103F-16F7-4668-BE54-9A1E7A4F7556"  # .NET SDK csproj GUID
                    for _idx, _cp in enumerate(_csproj_files):
                        _cp_name = os.path.splitext(os.path.basename(_cp))[0]
                        _cp_rel = os.path.relpath(_cp, project_dir).replace("/", "\\")
                        _inst_guid = "{" + "X" * 8 + "-" + "X" * 4 + "-" + "X" * 4 + "-" + "X" * 4 + "-" + "X" * 12 + "}"
                        # Deterministic per-project GUID derived from path.
                        import hashlib as _hl
                        _h = _hl.md5(_cp_rel.encode()).hexdigest().upper()
                        _inst_guid = "{" + f"{_h[0:8]}-{_h[8:12]}-{_h[12:16]}-{_h[16:20]}-{_h[20:32]}" + "}"
                        _sln_lines.append(
                            f'Project("{{{_proj_guid}}}") = "{_cp_name}", "{_cp_rel}", "{_inst_guid}"'
                        )
                        _sln_lines.append("EndProject")
                    try:
                        with open(_sln_path, "w") as _sf:
                            _sf.write("\n".join(_sln_lines) + "\n")
                        sln_path = _sln_path
                        print(
                            f"[c#][P4.2] no .sln found; synthesised {_sln_path} "
                            f"with {len(_csproj_files)} csproj(s)"
                            + (f" (auto-generated {len(_synth_csprojs)} csproj)" if _synth_csprojs else "")
                        )
                    except OSError as _e:
                        print(f"[c#][P4.2] failed to write {_sln_path}: {_e}")

            if not sln_path:
                print(f"[c#] No .sln found. Run 0_detect_project_roots.py first to set up the project:")
                print(f"[c#]   python3 0_detect_project_roots.py -d \"{project_dir}\" -l \"c#\"")
            if sln_path:
                print(f"[c#] Using solution: {sln_path}")
                # Pre-flight validation: check csproj files exist and are valid XML
                _sln_dir = os.path.dirname(sln_path)
                _sln_errors = []
                with open(sln_path) as _sf:
                    _sln_content = _sf.read()
                import xml.etree.ElementTree as _ET
                for _ref in re.findall(r'"([^"]+\.csproj)"', _sln_content):
                    _csproj_full = os.path.join(_sln_dir, _ref)
                    if not os.path.exists(_csproj_full):
                        _sln_errors.append(f"missing csproj: {_ref}")
                    else:
                        try:
                            _ET.parse(_csproj_full)
                        except _ET.ParseError as _e:
                            _sln_errors.append(f"corrupt csproj: {_ref} ({_e})")
                if _sln_errors:
                    print(f"[c#] ⚠ Pre-flight validation found {len(_sln_errors)} issues:")
                    for _e in _sln_errors[:10]:
                        print(f"[c#]   {_e}")
                    if len(_sln_errors) > 10:
                        print(f"[c#]   ... and {len(_sln_errors) - 10} more")
                    print(f"[c#]   OmniSharp may fail to load some projects.")
                else:
                    print(f"[c#] Pre-flight validation passed ✓")
                # Try dotnet restore for deeper validation (non-blocking)
                _dotnet = shutil.which('dotnet')
                if not _dotnet:
                    # Try Docker fallback
                    _docker = shutil.which('docker')
                    if _docker:
                        _restore_cmd = ['docker', 'run', '--rm', '-v', f'{_sln_dir}:{_sln_dir}', '-w', _sln_dir,
                                        'alecmaly/sa-tool', 'dotnet', 'restore', sln_path, '--verbosity', 'quiet']
                    else:
                        _restore_cmd = None
                else:
                    _restore_cmd = [_dotnet, 'restore', sln_path, '--verbosity', 'quiet']
                if _restore_cmd:
                    try:
                        _restore = subprocess.run(_restore_cmd, capture_output=True, text=True, timeout=120)
                        _restore_errors = [l for l in _restore.stderr.splitlines() if 'error' in l.lower() and 'circular dependency' not in l.lower()]
                        if _restore_errors:
                            print(f"[c#] dotnet restore warnings ({len(_restore_errors)} non-circular errors):")
                            for _e in _restore_errors[:5]:
                                print(f"[c#]   {_e.strip()}")
                        else:
                            print(f"[c#] dotnet restore OK ✓ (circular deps ignored)")
                    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as _e:
                        print(f"[c#] dotnet restore skipped ({type(_e).__name__})")
            else:
                print(f"[c#] WARNING: No .sln found. OmniSharp will index single directory only.")
                sln_path = project_dir  # Fall back to directory path

        default_extensions = lanaguage_defaults_map[language].get('exts', []) if language in lanaguage_defaults_map else []
        extra_extensions = [ext.strip() for ext in args.extensions.split(",") if ext.strip() != "" and ext.strip().startswith(".")] if args.extensions else []
        extensions = list(set(default_extensions + extra_extensions))


        print("[+] Running LSP Client for language: ", language)

        cmd = args.cmd_override.split(" ") if args.cmd_override else lanaguage_defaults_map[language]['cmd']

        # C#/OmniSharp: inject -s <sln_path> into command
        if language == "c#" and not args.cmd_override and "OmniSharp" in cmd[0]:
            cmd = [cmd[0], "-s", sln_path] + cmd[1:]

        print(args)

        client = LSPClient(
            language,
            extensions,
            cmd,
            force_references=args.force_references,
            force_callHierarchy=args.force_callHierarchy,
            max_ref_tracking_count=args.max_ref_tracking_count,
            disable_get_id_from_ref=args.disable_get_id_from_ref,
            disable_selectionRange=args.disable_selectionRange,
            disable_incoming_calls=args.disable_incoming_calls,
            disable_outgoing_calls=args.disable_outgoing_calls,
            disable_inheritance=args.disable_inheritance,
            only_functions=args.only_functions,
            pause_for_verification=args.pause_for_verification,
            guess_ref_read_write=args.guess_ref_read_write,
            resp_timeout=args.resp_timeout,
            resp_pause=args.resp_pause,
            init_timeout=args.init_timeout,
            init_pause=args.init_pause,
            verbose=args.verbose,
            stderr_to_file=args.stderr_to_file,
            ls_file_queue=ls_file_queue,
            streaming_mode=args.streaming_mode,
            streaming_mode_disable_recursive_ref_search=args.streaming_mode_disable_recursive_ref_search,
            parallel_requests=args.parallel_requests
        )

        
        client.analyze(args.project_dir)
        # should never get here
        client.close()


    # socket_server.py
    def file_queue_forwarding_server(host='0.0.0.0', port=9999):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            server.bind((host, port))
        except Exception as e:
            print(f"Failed to bind server on {host}:{port}: {e}")
            raise
        server.listen()
        print(f"[Python] Listening on {host}:{port}")

        while True:
            client_socket, addr = server.accept()
            print(f"[Python] Connection from {addr}")

            with client_socket:
                data = b''
                while True:
                    chunk = client_socket.recv(1024)
                    if not chunk:
                        break
                    data += chunk
                    # If we received less than 1024 bytes, we've likely received all data
                    if len(chunk) < 1024:
                        break

                print("Received from VS Code:", data.decode().strip().split("\n"))
                files = data.decode().strip().split("\n")
                for file_path in files:
                    file_path = file_path.strip()

                    # map file_path to language server queue by extension
                    ext = os.path.splitext(file_path)[1]
                    for language, ls_file_queue in opened_file_queues_map.items():                        
                        if ext in lanaguage_defaults_map.get(language, {}).get('exts', []):
                            print("Adding to queue from forwarding server: ", file_path)
                            ls_file_queue.put(file_path)
                            print(f"[Python] Forwarded {file_path} to {language} queue")
                            break

        

    threading.Thread(target=file_queue_forwarding_server, daemon=True).start()

    print("STARTED FILE QUEUE FORWARDING SERVER")


    def data_dump_thread():
        global g_data_updated
        while True:
            # print(f"in data dump thread, waiting for data to dump... {len(g_scopes)} scopes, {len(g_function_calls)} function calls")
            # parallel: should loop for changes, collect data, and write to files

            if g_data_updated:
                g_data_updated = False

                # remove all references .pyi from g_function_calls
                for caller in list(g_function_calls):
                    if ".pyi#" in caller:
                        del g_function_calls[caller]
                        continue
                    callees = g_function_calls[caller]
                    g_function_calls[caller] = {callee for callee in callees if ".pyi#" not in callee}

                # write to files
                print("[data dump thread] Change detected, writing to files...")
                open(f"{args.output_file_prefix}decorations.json", 'w').write(json.dumps(g_textHighlights.to_dict()))
                open(f"{args.output_file_prefix}functions_html.json", "w").write(json.dumps(g_functions.to_list()))
                open(f"{args.output_file_prefix}scope_summaries_html.json", "w").write(json.dumps(g_scopes.to_list()))
                open(f"{args.output_file_prefix}function_calls.json", "w").write(json.dumps(g_function_calls.to_dict(values_to_list=True)))
                open(f"{args.output_file_prefix}class_inheritance.json", "w").write(json.dumps(g_class_inheritance.to_dict(values_to_list=True)))
                open(f"{args.output_file_prefix}seen_files.json", "w").write(json.dumps(g_seen_files.to_dict()))
                data = json.dumps(g_seen_files_for_refs.to_dict())
                gzipped_seen_files_for_refs = zlib.compress(data.encode()).hex()
                open(f"{args.output_file_prefix}seen_files_for_refs.gzip", "w").write(gzipped_seen_files_for_refs)
                data = json.dumps(g_var_ref_map.to_dict())
                gzipped_var_ref_map = zlib.compress(data.encode()).hex()
                open(f"{args.output_file_prefix}var_ref_map.gzip", "w").write(gzipped_var_ref_map)

                try:
                    open(f"{args.project_dir}/.vscode/ext-static-analysis/_updated_data.state", "w").write("true")
                except PermissionError:
                    pass

            if not args.streaming_mode:
                print("Not in streaming mode, breaking data dump thread.")
                break
            
            if errors:
                open(f"{args.output_file_prefix}errors.json", "w").write(json.dumps(errors))
            time.sleep(5)
            

    # if appending, pre-load current state of output files
    # get current files and merge, if necessary, although this will not update internal state of LSPClient so probably not be possible without refactor
    if args.append_output_file:
        def try_open_file(filepath, fmt = 'json'):
            try:
                if fmt == 'json':
                    return json.loads(open(filepath, "r").read())
                elif fmt == 'gzip':
                    gzipped_data = zlib.decompress(bytes.fromhex(open(filepath, "r").read())).decode()
                    return json.loads(gzipped_data)
            except:
                return None
        
        current_decorations = try_open_file(f"{args.output_file_prefix}decorations.json") or None
        current_functions_html = try_open_file(f"{args.output_file_prefix}functions_html.json") or None
        current_scope_summaries_html = try_open_file(f"{args.output_file_prefix}scope_summaries_html.json") or None
        current_function_calls = try_open_file(f"{args.output_file_prefix}function_calls.json") or None
        current_class_inheritance = try_open_file(f"{args.output_file_prefix}class_inheritance.json") or None
        current_seen_files = try_open_file(f"{args.output_file_prefix}seen_files.json") or None
        current_seen_files_for_refs = try_open_file(f"{args.output_file_prefix}seen_files_for_refs.gzip", fmt='gzip') or None
        current_var_ref_map = try_open_file(f"{args.output_file_prefix}var_ref_map.gzip", fmt='gzip') or None


        # functions = current_functions_html + functions if args.append_output_file else functions
        # scopes = current_scope_summaries_html + scopes if args.append_output_file else scopes
        # g_function_calls = {**current_function_calls, **g_function_calls} if args.append_output_file else g_function_calls
        # g_class_inheritance = {**current_class_inheritance, **g_class_inheritance} if args.append_output_file else g_class_inheritance
        if current_decorations:
            g_textHighlights.from_dict(current_decorations)
        if current_functions_html:
            g_functions.from_list(current_functions_html)
        if current_scope_summaries_html:
            g_scopes.from_list(current_scope_summaries_html)
        if current_function_calls:
            g_function_calls.from_dict(current_function_calls, values_to_set=True)
        if current_class_inheritance:
            g_class_inheritance.from_dict(current_class_inheritance, values_to_set=True)
        if current_seen_files:
            g_seen_files.from_dict(current_seen_files)
        if current_seen_files_for_refs:
            g_seen_files_for_refs.from_dict(current_seen_files_for_refs)
        if current_var_ref_map:
            g_var_ref_map.from_dict(current_var_ref_map)

    # start data dump thread
    if args.streaming_mode:
        print("Starting data dump thread...")
        data_dump_thread = threading.Thread(target=data_dump_thread, daemon=True).start()


    # start language server threads
    threads = []
    for i, language in enumerate(languages):
        ls_file_queue = ThreadSafePriorityQueue()
        opened_file_queues_map[language] = ls_file_queue
        t = threading.Thread(target=run_language_client, args=(language, ls_file_queue))
        t.start()
        threads.append(t)


    # wait for all threads to finish
    for t in threads:
        t.join()
    print("All language clients have finished.")

    if not args.streaming_mode:
        data_dump_thread()


    # run prescript wait for completion
    if args.postscript:
        print(f"Running postscript: {args.postscript}")
        subprocess.run(args.postscript, shell=True)
        

    print(args)
    


# if dir was created, it was probably created as root, update ownership
if True:
    # Collect all UID/GID pairs from current directory tree
    uids, gids = zip(*[
        (s.st_uid, s.st_gid)
        for root, dirs, files in os.walk('.')
        for name in files + dirs
        if os.path.exists(p := os.path.join(root, name)) and (s := os.stat(p))
    ])

    # Prefer non-root UID/GID if available
    def most_common_exclude_root(vals):
        filtered = [v for v in vals if v != 0]
        return (collections.Counter(filtered).most_common(1) or collections.Counter(vals).most_common(1))[0][0]

    uid = most_common_exclude_root(uids)
    gid = most_common_exclude_root(gids)

    # Apply recursively to all files and directories under .vscode
    for root, dirs, files in os.walk('.vscode'):
        for name in files + dirs:
            path = os.path.join(root, name)
            try: os.chown(path, uid, gid)
            except: pass
