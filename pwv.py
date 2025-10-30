#!/usr/bin/env python3

import os
import re
import sys
import json
import uuid
import itertools
from datetime import datetime, timezone
from typing import List, Dict, Tuple, Optional, Set

# =============================================================================
# Paths
# =============================================================================

APP_NAME = "PassWeaver"
APP_SHORT = "pwv"

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, "data")
OUTPUT_DIR = os.path.join(DATA_DIR, "output")
SESSIONS_PATH = os.path.join(DATA_DIR, "sessions.json")
RULES_PATH = os.path.join(ROOT_DIR, "rules.txt")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# =============================================================================
# Colors / Styling (ANSI)
# =============================================================================

class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDER = "\033[4m"

    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

def color(text: str, *styles: str) -> str:
    return "".join(styles) + text + C.RESET

# =============================================================================
# Utilities
# =============================================================================

def banner() -> None:
    print(color(r"""
                                                                                
                               ...',;;::::;;,'...                               
                         .,coxO0XNWWMMMMMMMMWWNXKOxoc,.                         
                      'lkKWMMMMMMMMMMMMMMMMMMMMMMMMMMWXkl'                      
                    .dNMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMNx'                    
                   .OMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM0'                   
                   cWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWl                   
                   :NMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWc                   
                   .OMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM0'                   
                    oWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMd                    
                    :NMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWc                    
                    ;XMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMN:                    
                    ;XMMMMMMMMMMWWNNXXXXXXXXNNWWMMMMMMMMMMN:                    
                    cNWNKOkdol:;,''..........'',;:cloxk0XNWl                    
                    ,:,..                               .';'                    
                    ..',;:clloddxxxkkkkkkkkkkxxxddoolc:;,'..                    
            ..;codk0KXNWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWNXK0kdoc;..            
        .;ok0NWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWNKko:.        
     .ckXWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWXkc.     
    ;0WMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMW0;    
    cNMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMNc    
     ,o0NMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMN0d,     
        ':oxOKNWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWNKOxo:'.       
             .',:cod0WMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMXxol:,'.             
                    .xNMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWO,                    
                      'lkXWMMMMMMMMMMMMMMMMMMMMMMMMMMMN0d;.                     
                         .:oOXWMMMMMMMMMMMMMMMMMMMN0dc'.                        
                             .;lxKNMMMMMMMMMMWXOdc'.                            
                                 .':oxkkkkxoc,.                                 
                                                       
                                                       
                                                       
                                                                                 
""".rstrip("\n"), C.BRIGHT_WHITE))
    print(color("Welcome to PassWeaver (pwv) tool", C.BRIGHT_CYAN))
    print(color("Create strong, personalized passwords from names, dates, and more!", C.BRIGHT_CYAN))
    print(color("=" * 60, C.BRIGHT_GREEN))

    print()

def prompt(msg: str, default: Optional[str] = None, show_default_hint: bool = False) -> str:

    if show_default_hint and default not in (None, ""):
        msg = f"{msg} [{default}]"
    print(color(msg, C.BRIGHT_GREEN))
    val = input(color("> ", C.BRIGHT_CYAN)).strip()
    return val if val else (default if default is not None else "")

def yes_no_prompt(msg: str, default_no: bool = True) -> bool:
    default = "y/N" if default_no else "Y/n"
    print(color(f"{msg}? ({default})", C.BRIGHT_GREEN))
    val = input(color("> ", C.BRIGHT_CYAN)).strip().lower()
    if val == "":
        return not default_no
    return val in {"y", "yes"}

def load_sessions() -> List[Dict]:
    if not os.path.exists(SESSIONS_PATH):
        return []
    try:
        with open(SESSIONS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        return []
    except Exception:
        return []

def save_sessions(sessions: List[Dict]) -> None:
    with open(SESSIONS_PATH, "w", encoding="utf-8") as f:
        json.dump(sessions, f, ensure_ascii=False, indent=2)

def generate_session_id() -> str:
    return uuid.uuid4().hex[:12]

def now_iso() -> str:
    # timezone-aware ISO 8601 (UTC)
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

# =============================================================================
# Generator helpers
# =============================================================================

def generate_leet_variants(word: str) -> List[str]:
    leet_mapping = {
        'a': ['a', '@'],
        'e': ['e', '3'],
        'i': ['i', '1'],
        'o': ['o', '0'],
        's': ['s', '$', '5'],
        't': ['t', '7']
    }
    char_options = []
    for ch in word:
        options = leet_mapping.get(ch.lower(), [ch])
        if ch.isupper():
            options = [opt.upper() for opt in options]
        char_options.append(options)
    variants = ["".join(candidate) for candidate in itertools.product(*char_options)]
    return variants

def apply_case_pattern(case_pattern: str, replacement: str) -> str:
    if not case_pattern.startswith("u:"):
        return replacement
    pattern = case_pattern[2:]
    if pattern == "A":
        return replacement.upper()
    if pattern == "N":
        return replacement.lower()
    result = list(replacement.lower())
    positions = pattern.split(",")
    for pos in positions:
        if pos == "L":
            if result:
                result[-1] = result[-1].upper()
        else:
            try:
                idx = int(pos) - 1
                if 0 <= idx < len(result):
                    result[idx] = result[idx].upper()
            except ValueError:
                pass
    return ''.join(result)

def parse_date(date_str: str) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    if not date_str or not isinstance(date_str, str):
        return None, None, None, None
    parts = date_str.split("/")
    if len(parts) != 3:
        return None, None, None, None
    day, month, full_year = parts
    short_year = full_year[-2:]
    return day, month, full_year, short_year

def generate_numbers_from_date(date_str: str) -> List[str]:
    try:
        parts = date_str.split('/')
        if len(parts) != 3:
            return []
        day, month, year = parts
        day_str = str(int(day))
        month_str = str(int(month))
        year_str = year.strip()
        last_two_year = year_str[-2:]
        return [
            year_str,
            last_two_year,
            day_str + month_str,
            day_str + month_str + year_str,
            day_str + month_str + last_two_year,
            month_str + day_str,
            month_str + day_str + year_str,
            month_str + day_str + last_two_year,
            year_str + month_str + day_str,
            last_two_year + month_str + day_str,
            year_str + day_str + month_str,
            last_two_year + day_str + month_str,
        ]
    except Exception:
        return []

def parse_rule(rule_str: str) -> List[Dict]:
    tokens = rule_str.split(" + ")
    rule = []
    for token in tokens:
        if token.startswith("string:") or token.startswith("string_leet:"):
            token_parts = token.split(":", 1)
            token_type = token_parts[0]
            if len(token_parts) > 1 and token_parts[1].startswith("u:"):
                case_pattern = token_parts[1]
            else:
                case_pattern = "u:N"
            rule.append({
                "type": token_type,
                "case_pattern": case_pattern,
                "index": 1
            })
        elif token.startswith("string") and ":u:" in token:
            match = re.match(r'string(\d*):u:', token)
            if match:
                string_idx = int(match.group(1)) if match.group(1) else 1
                case_pattern = "u:" + token.split(":u:")[1]
                rule.append({
                    "type": "string",
                    "case_pattern": case_pattern,
                    "index": string_idx
                })
            else:
                parts = token.split(":", 2)
                rule.append({
                    "type": "string",
                    "case_pattern": "u:" + parts[2],
                    "index": 1
                })
        elif token.startswith("character") and ":u:" in token:
            match = re.match(r'character(\d*):u:', token)
            if match:
                char_idx = int(match.group(1)) if match.group(1) else 1
                case_pattern = "u:" + token.split(":u:")[1]
                rule.append({
                    "type": "character",
                    "case_pattern": case_pattern,
                    "index": char_idx
                })
            else:
                parts = token.split(":", 2)
                rule.append({
                    "type": "character",
                    "case_pattern": "u:" + parts[2],
                    "index": 1
                })
        elif token == "day":
            rule.append({"type": "day"})
        elif token == "month":
            rule.append({"type": "month"})
        elif token == "year":
            rule.append({"type": "year"})
        elif token == "short_year":
            rule.append({"type": "short_year"})
        elif token == "full_date":
            rule.append({"type": "full_date"})
        elif token == "symbol":
            rule.append({"type": "symbol"})
        elif token == "common_number":
            rule.append({"type": "common_number"})
        elif token == "number":
            rule.append({"type": "number"})
        elif token.startswith("literal:"):
            value = token.split(":", 1)[1]
            rule.append({"type": "literal", "value": value})
        else:
            rule.append({"type": "literal", "value": token})
    return rule

def generate_passwords_from_rule(
    rule: List[Dict],
    strings: List[str],
    numbers: List[str],
    date_info_list: List[Dict],
    symbols: Optional[List[str]] = None,
    common_numbers: Optional[List[str]] = None,
    has_spaces: bool = False
) -> Set[str]:
    if symbols is None:
        symbols = []
    if common_numbers is None:
        common_numbers = []
    valid_strings = [s for s in strings if s]
    date_components_in_rule = [t["type"] for t in rule if t["type"] in ["day", "month", "year", "short_year", "full_date"]]
    has_date_components = len(date_components_in_rule) > 0

    def join_tokens(tokens: List[str]) -> str:
        return " ".join(tokens) if has_spaces else "".join(tokens)

    all_passwords: Set[str] = set()

    if has_date_components:
        for date_info in date_info_list:
            date_components = date_info.get('components', (None, None, None, None))
            date_numbers = date_info.get('numbers', [])
            day, month, year, short_year = date_components

            base_tokens: List[Optional[str]] = []
            for token_rule in rule:
                if token_rule["type"] == "literal":
                    base_tokens.append(token_rule["value"])
                else:
                    base_tokens.append(None)

            configs: List[Tuple[List[Optional[str]], Set[str]]] = [(base_tokens.copy(), set())]

            for i, token_rule in enumerate(rule):
                new_configs: List[Tuple[List[Optional[str]], Set[str]]] = []
                token_type = token_rule["type"]

                for config, used_strings in configs:
                    if token_type in ["string", "string_leet"]:
                        available_strings = [s for s in valid_strings if s.lower() not in used_strings] or (valid_strings[:1] if valid_strings else [])
                        for string in available_strings:
                            new_config = config.copy()
                            new_used_strings = used_strings.copy()
                            adjusted_string = apply_case_pattern(token_rule["case_pattern"], string)
                            if token_type == "string_leet":
                                variants = generate_leet_variants(adjusted_string)
                                for variant in variants:
                                    variant_config = new_config.copy()
                                    variant_config[i] = variant
                                    variant_used_strings = new_used_strings.copy()
                                    variant_used_strings.add(string.lower())
                                    new_configs.append((variant_config, variant_used_strings))
                            else:
                                new_config[i] = adjusted_string
                                new_used_strings.add(string.lower())
                                new_configs.append((new_config, new_used_strings))

                    elif token_type == "character":
                        available_strings = [s for s in valid_strings if s.lower() not in used_strings] or (valid_strings[:1] if valid_strings else [])
                        for string in available_strings:
                            if string:
                                new_config = config.copy()
                                new_used_strings = used_strings.copy()
                                new_config[i] = apply_case_pattern(token_rule["case_pattern"], string[0])
                                new_used_strings.add(string.lower())
                                new_configs.append((new_config, new_used_strings))

                    elif token_type == "day":
                        if day:
                            new_config = config.copy()
                            new_config[i] = day
                            new_configs.append((new_config, used_strings))
                    elif token_type == "month":
                        if month:
                            new_config = config.copy()
                            new_config[i] = month
                            new_configs.append((new_config, used_strings))
                    elif token_type == "year":
                        if year:
                            new_config = config.copy()
                            new_config[i] = year
                            new_configs.append((new_config, used_strings))
                    elif token_type == "short_year":
                        if short_year:
                            new_config = config.copy()
                            new_config[i] = short_year
                            new_configs.append((new_config, used_strings))
                    elif token_type == "full_date":
                        for date_num in date_numbers:
                            new_config = config.copy()
                            new_config[i] = date_num
                            new_configs.append((new_config, used_strings))
                    elif token_type == "symbol":
                        for symbol in symbols:
                            new_config = config.copy()
                            new_config[i] = symbol
                            new_configs.append((new_config, used_strings))
                    elif token_type == "common_number":
                        for num in common_numbers:
                            new_config = config.copy()
                            new_config[i] = num
                            new_configs.append((new_config, used_strings))
                    elif token_type == "number":
                        for num in numbers:
                            new_config = config.copy()
                            new_config[i] = num
                            new_configs.append((new_config, used_strings))
                    elif token_type == "literal":
                        new_configs.append((config, used_strings))

                if not new_configs and token_type != "literal":
                    new_configs.append((config, used_strings))
                configs = new_configs

            for config, _ in configs:
                filled_tokens = [t if t is not None else "" for t in config]
                password = join_tokens(filled_tokens)
                if password:
                    all_passwords.add(password)

    else:
        base_tokens: List[Optional[str]] = []
        for token_rule in rule:
            if token_rule["type"] == "literal":
                base_tokens.append(token_rule["value"])
            else:
                base_tokens.append(None)

        configs: List[Tuple[List[Optional[str]], Set[str]]] = [(base_tokens.copy(), set())]

        for i, token_rule in enumerate(rule):
            new_configs: List[Tuple[List[Optional[str]], Set[str]]] = []
            token_type = token_rule["type"]

            for config, used_strings in configs:
                if token_type in ["string", "string_leet"]:
                    available_strings = [s for s in valid_strings if s.lower() not in used_strings] or (valid_strings[:1] if valid_strings else [])
                    for string in available_strings:
                        new_config = config.copy()
                        new_used_strings = used_strings.copy()
                        adjusted_string = apply_case_pattern(token_rule["case_pattern"], string)
                        if token_type == "string_leet":
                            variants = generate_leet_variants(adjusted_string)
                            for variant in variants:
                                variant_config = new_config.copy()
                                variant_config[i] = variant
                                variant_used_strings = new_used_strings.copy()
                                variant_used_strings.add(string.lower())
                                new_configs.append((variant_config, variant_used_strings))
                        else:
                            new_config[i] = adjusted_string
                            new_used_strings.add(string.lower())
                            new_configs.append((new_config, new_used_strings))

                elif token_type == "character":
                    available_strings = [s for s in valid_strings if s.lower() not in used_strings] or (valid_strings[:1] if valid_strings else [])
                    for string in available_strings:
                        if string:
                            new_config = config.copy()
                            new_used_strings = used_strings.copy()
                            new_config[i] = apply_case_pattern(token_rule["case_pattern"], string[0])
                            new_used_strings.add(string.lower())
                            new_configs.append((new_config, new_used_strings))
                elif token_type == "symbol":
                    for symbol in (symbols or []):
                        new_config = config.copy()
                        new_config[i] = symbol
                        new_configs.append((new_config, used_strings))
                elif token_type == "common_number":
                    for num in (common_numbers or []):
                        new_config = config.copy()
                        new_config[i] = num
                        new_configs.append((new_config, used_strings))
                elif token_type == "number":
                    for num in numbers:
                        new_config = config.copy()
                        new_config[i] = num
                        new_configs.append((new_config, used_strings))
                elif token_type == "literal":
                    new_configs.append((config, used_strings))

            if not new_configs and token_type != "literal":
                new_configs.append((config, used_strings))
            configs = new_configs

        for config, _ in configs:
            filled_tokens = [t if t is not None else "" for t in config]
            password = "".join(filled_tokens)
            if password:
                all_passwords.add(password)

    return all_passwords

# =============================================================================
# Generation and session logic
# =============================================================================

DEFAULT_SYMBOLS = ["@", "#", "$", "%", "!", "&", "*", "-", "_"]
DEFAULT_COMMON_NUMBERS = [
    "1","2","3","4","5","6","7","8","9","0",
    "123","1234","12345","123456",
    "321","4321","54321",
    "123321","12344321","1234554321",
    "2020","2021","2022","2023","2024","2025","2026"
]

def read_rules() -> List[str]:
    if not os.path.exists(RULES_PATH):
        print(color(f"rules.txt not found at: {RULES_PATH}", C.BRIGHT_RED))
        sys.exit(1)
    with open(RULES_PATH, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def create_session(data: Dict) -> Dict:
    sessions = load_sessions()
    session = {
        "session_id": data.get("session_id", generate_session_id()),
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "strings": data.get("strings", []),
        "dates": data.get("dates", []),
        "numbers": data.get("numbers", []),
        "min_length": data.get("min_length", 8),
        "max_length": data.get("max_length"),
        "must_include_uppercase": data.get("must_include_uppercase", False),
        "must_include_symbol": data.get("must_include_symbol", False),
        "current_rule_index": 0,
        "current_rule_password_count": 0,
        "is_completed": False,
        "last_run_files": [],
        "total_generated": 0
    }
    sessions.append(session)
    save_sessions(sessions)
    return session

def update_session(session_id: str, **updates) -> Dict:
    sessions = load_sessions()
    found = None
    for s in sessions:
        if s["session_id"] == session_id:
            for k, v in updates.items():
                s[k] = v
            s["updated_at"] = now_iso()
            found = s
            break
    if found is None:
        raise FileNotFoundError("Session not found")
    save_sessions(sessions)
    return found

def load_session_by_id(session_id: str) -> Dict:
    sessions = load_sessions()
    for s in sessions:
        if s["session_id"] == session_id:
            return s
    raise FileNotFoundError("Session not found")

def list_sessions_print() -> List[Dict]:
    sessions = load_sessions()
    sessions_sorted = sorted(sessions, key=lambda x: x.get("updated_at",""), reverse=True)
    if not sessions_sorted:
        print(color("No sessions available.", C.BRIGHT_YELLOW))
        return []
    print(color("\nAvailable sessions:", C.BRIGHT_WHITE, C.BOLD))
    header = "Idx | session_id   | created_at                | strings                       | dates                | generated | status"
    print(color(header, C.BRIGHT_GREEN))
    print(color("-"*len(header), C.BRIGHT_GREEN))
    for idx, s in enumerate(sessions_sorted, start=1):
        strings_preview = " ".join(s.get("strings", []))[:27]
        dates_preview = " ".join(s.get("dates", []))[:20] or "-"
        generated = s.get("total_generated", 0)
        status = "completed" if s.get("is_completed") else "in-progress"
        line = f"{idx:<3} | {s['session_id']:<12} | {s['created_at']:<24} | {strings_preview:<28} | {dates_preview:<20} | {generated:>9} | {status}"
        print(color(line, C.BRIGHT_WHITE))
    print()
    return sessions_sorted

def filter_valid_passwords(passwords: Set[str], min_len: Optional[int], max_len: Optional[int],
                           must_upper: bool, must_symbol: bool) -> List[str]:
    def ok(p: str) -> bool:
        if min_len and len(p) < min_len:
            return False
        if max_len and len(p) > max_len:
            return False
        if must_upper and not any(c.isupper() for c in p):
            return False
        if must_symbol and not any(not c.isalnum() for c in p):
            return False
        return True
    return [p for p in passwords if ok(p)]

def generate_to_file(
    session: Dict,
    rules: List[str],
    password_limit: int,
    custom_output_name: Optional[str] = None
) -> Tuple[int, str, List[str], Dict]:
    session_id = session["session_id"]
    current_rule_index = session.get("current_rule_index", 0)
    current_rule_password_count = session.get("current_rule_password_count", 0)
    total_rules = len(rules)

    if current_rule_index >= total_rules:
        return 0, "", [], {"is_completed": True}

    symbol_list = DEFAULT_SYMBOLS
    common_nums = DEFAULT_COMMON_NUMBERS

    strings = session["strings"]
    dates = session["dates"]
    numbers = session["numbers"]
    min_length = session.get("min_length", 8)
    max_length = session.get("max_length")
    must_include_uppercase = session.get("must_include_uppercase", False)
    must_include_symbol = session.get("must_include_symbol", False)

    date_info_list = [{
        'components': parse_date(d),
        'numbers': generate_numbers_from_date(d)
    } for d in dates]

    existing_runs = []
    pattern = re.compile(rf"(\d+)_passwords_{re.escape(session_id)}_run(\d+)\.txt")
    for fname in os.listdir(OUTPUT_DIR):
        m = pattern.match(fname)
        if m:
            try:
                existing_runs.append(int(m.group(2)))
            except Exception:
                pass
    next_run_index = max(existing_runs) + 1 if existing_runs else 1
    temp_path = os.path.join(OUTPUT_DIR, f"temp_{session_id}_run{next_run_index}.txt")

    total_written = 0
    preview_passwords: List[str] = []
    rule_index_updated = current_rule_index
    new_current_rule_password_count = current_rule_password_count

    with open(temp_path, "w", encoding="utf-8") as outfile:
        while total_written < password_limit and rule_index_updated < total_rules:
            rule_str = rules[rule_index_updated]
            rule = parse_rule(rule_str)
            has_spaces = " + " in rule_str and "literal: " in rule_str

            all_passwords = generate_passwords_from_rule(
                rule, strings, numbers, date_info_list,
                symbols=symbol_list,
                common_numbers=common_nums,
                has_spaces=has_spaces
            )

            valid_passwords = filter_valid_passwords(
                all_passwords, min_length, max_length,
                must_include_uppercase, must_include_symbol
            )

            if rule_index_updated == current_rule_index:
                valid_passwords = valid_passwords[current_rule_password_count:]

            for pwd in valid_passwords:
                if total_written >= password_limit:
                    break
                outfile.write(pwd + "\n")
                if len(preview_passwords) < 100:
                    preview_passwords.append(pwd)
                total_written += 1
                new_current_rule_password_count += 1
                progress = color(f"{total_written}/{password_limit}", C.BRIGHT_GREEN)
                print(f"\r{progress}", end="", flush=True)

            if new_current_rule_password_count >= len(valid_passwords):
                rule_index_updated += 1
                new_current_rule_password_count = 0
            else:
                break

    if custom_output_name and custom_output_name.strip():
        final_filename = custom_output_name.strip()
        if not os.path.splitext(final_filename)[1]:
            final_filename += ".txt"
    else:
        final_filename = f"{total_written}_passwords_{session_id}_run{next_run_index}.txt"

    final_path = os.path.join(OUTPUT_DIR, final_filename)
    os.replace(temp_path, final_path)
    print()
    print(color(f"Finished. Generated {total_written} passwords.", C.BRIGHT_GREEN, C.BOLD))
    print(color(f"Output: {final_path}", C.BRIGHT_WHITE))

    is_completed_flag = rule_index_updated >= total_rules
    updates = {
        "current_rule_index": rule_index_updated,
        "current_rule_password_count": new_current_rule_password_count,
        "is_completed": is_completed_flag,
        "total_generated": session.get("total_generated", 0) + total_written
    }
    list_files = session.get("last_run_files", [])
    list_files.append(final_filename)
    updates["last_run_files"] = list_files

    return total_written, final_filename, preview_passwords, updates

# =============================================================================
# CLI flows
# =============================================================================

def cli_new() -> None:
    print()
    print(color("Enter personal strings (e.g., first name, surname, nickname, pet name), separated by space:", C.BRIGHT_GREEN))
    # strings are mandatory
    while True:
        strings_line = input(color("> ", C.BRIGHT_CYAN)).strip()
        strings = [s for s in strings_line.split() if s]
        if strings:
            break
        print(color("Strings are required. Please enter at least one value.", C.BRIGHT_RED))

    print()
    print(color("Enter one or more dates in D/M/YYYY format, separated by space (e.g., 11/2/2003 1/1/2000), or press Enter to skip:", C.BRIGHT_GREEN))
    dates_line = input(color("> ", C.BRIGHT_CYAN)).strip()
    dates = [d for d in dates_line.split() if d]

    print()
    print(color("Enter any number(s) (e.g., favorite number, house number, phone number), separated by space, or press Enter to skip:", C.BRIGHT_GREEN))
    numbers_line = input(color("> ", C.BRIGHT_CYAN)).strip()
    numbers = [n for n in numbers_line.split() if n]

    while True:
        ml = prompt("\nEnter minimum password length [default: 8]", "8", show_default_hint=False)
        try:
            min_length = int(ml)
            break
        except ValueError:
            print(color("Please enter a valid integer.", C.BRIGHT_RED))

    mx = prompt("Enter maximum password length (press Enter to skip)", "", show_default_hint=False)
    max_length = None
    if mx.strip():
        try:
            max_length = int(mx.strip())
        except ValueError:
            print(color("Invalid value. Ignoring max length.", C.BRIGHT_YELLOW))
            max_length = None

    must_include_uppercase = yes_no_prompt("Must include at least one uppercase letter")
    must_include_symbol = yes_no_prompt("Must include at least one symbol")

    limit_str = prompt("\nHow many passwords do you want to generate [default: 1000000]", "1000000", show_default_hint=False)
    try:
        password_limit = int(limit_str)
    except ValueError:
        password_limit = 1000000

    out_name = prompt("Enter output file name (default: auto)", "", show_default_hint=False)
    save_session_flag = yes_no_prompt("\nSave session for resume", default_no=False)

    if save_session_flag:
        session = create_session({
            "strings": strings,
            "dates": dates,
            "numbers": numbers,
            "min_length": min_length,
            "max_length": max_length,
            "must_include_uppercase": must_include_uppercase,
            "must_include_symbol": must_include_symbol
        })
        print(color(f"\nSession created: {session['session_id']}", C.BRIGHT_BLUE))
    else:
        session = {
            "session_id": f"ephemeral_{generate_session_id()}",
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "strings": strings,
            "dates": dates,
            "numbers": numbers,
            "min_length": min_length,
            "max_length": max_length,
            "must_include_uppercase": must_include_uppercase,
            "must_include_symbol": must_include_symbol,
            "current_rule_index": 0,
            "current_rule_password_count": 0,
            "is_completed": False,
            "last_run_files": [],
            "total_generated": 0
        }

    print(color("\nLoading rules...", C.BRIGHT_WHITE))
    rules = read_rules()
    print(color(f"Total rules: {len(rules)}", C.BRIGHT_WHITE))

    _, final_name, preview, updates = generate_to_file(session, rules, password_limit, custom_output_name=out_name)

    if not session["session_id"].startswith("ephemeral_"):
        update_session(session["session_id"], **updates)

    if preview:
        print(color("\nPreview (first up to 100 lines):", C.BRIGHT_GREEN))
        for p in preview:
            print(color(p, C.BRIGHT_WHITE))

def cli_resume() -> None:
    sessions_sorted = list_sessions_print()
    if not sessions_sorted:
        return
    while True:
        choice = prompt("Select session index to resume (or 0 to cancel)", "", show_default_hint=False)
        if not choice:
            continue
        try:
            idx = int(choice)
        except ValueError:
            print(color("Please enter a valid number.", C.BRIGHT_RED))
            continue
        if idx == 0:
            return
        if 1 <= idx <= len(sessions_sorted):
            session = sessions_sorted[idx - 1]
            break
        else:
            print(color("Invalid index.", C.BRIGHT_RED))

    print(color("\nSession details:", C.BRIGHT_WHITE, C.BOLD))
    for k in ["session_id","created_at","updated_at","strings","dates","numbers",
              "min_length","max_length","must_include_uppercase","must_include_symbol",
              "current_rule_index","current_rule_password_count","is_completed","total_generated","last_run_files"]:
        print(color(f"- {k}: {session.get(k)}", C.BRIGHT_WHITE))

    if session.get("is_completed"):
        print(color("\nThis session is already completed (all rules processed).", C.BRIGHT_YELLOW))
        cont = yes_no_prompt("Generate again starting from scratch with same inputs")
        if not cont:
            return
        session = update_session(session["session_id"], current_rule_index=0, current_rule_password_count=0, is_completed=False)

    limit_str = prompt("\nHow many passwords to generate this run [default: 1000000]", "1000000", show_default_hint=False)
    try:
        password_limit = int(limit_str)
    except ValueError:
        password_limit = 1000000

    out_name = prompt("Enter output file name (default: auto)", "", show_default_hint=False)

    print(color("\nLoading rules...", C.BRIGHT_WHITE))
    rules = read_rules()
    print(color(f"Total rules: {len(rules)}", C.BRIGHT_WHITE))

    _, final_name, preview, updates = generate_to_file(session, rules, password_limit, custom_output_name=out_name)
    session = update_session(session["session_id"], **updates)

    if preview:
        print(color("\nPreview (first up to 100 lines):", C.BRIGHT_GREEN))
        for p in preview:
            print(color(p, C.BRIGHT_WHITE))

# =============================================================================
# Main
# =============================================================================

def main():
    banner()
    print(color("Choose mode:", C.BRIGHT_WHITE, C.BOLD))
    print(color("1) New generation", C.BRIGHT_GREEN))
    print(color("2) Resume existing session", C.BRIGHT_GREEN))
    mode = prompt("Enter choice [default: 1]", "1", show_default_hint=False)
    if mode == "1":
        cli_new()
    elif mode == "2":
        cli_resume()
    else:
        print(color("Unknown choice.", C.BRIGHT_RED))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(color("\nAborted by user.", C.BRIGHT_YELLOW))
