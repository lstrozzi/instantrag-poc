"""
instantrag_qwen_demo.py — streamed tool-call interrupt/resume demo (qwen-3.5-35b)

Mimics how the Thalabus toolset intercepts InstantRAG tags (see
config/instantrag.txt) during token-stream collection:

  1. The completion is streamed (reasoning arrives in the delta field
     "reasoning_content", the answer in "content").
  2. The stream is watched for an empty self-closed tool tag such as
     <MUL x1="2" x2="4"/>. As soon as it completes, inference is stopped,
     the tokens after the closed tag are discarded (one tool call at a
     time), and the tool is executed.
  3. The result is NOT written back into the thinking. It is published in a
     dedicated message wrapped in <RESULTS> with a server-assigned id, like
     <RESULTS><MUL id="mul-1">8</MUL></RESULTS>, sent with role user right
     before the assistant continuation — the only supported slot, since the
     LiteLLM gateway accepts exactly one system message (at the beginning)
     and Thalabus' own Qwen provider likewise uses a user-role secondary
     system message. The <RESULTS> wrapper is the trust boundary: only
     numbers visible inside it are server-computed. Inference resumes from
     the interrupted partial assistant message (thinking header + thinking
     collected so far), with the intercepted call tag rewritten into a pure
     reference to the published result: the collected
     `I must obtain <MUL x1="2" x2="4"/>` is fed back as
     `I must obtain <MUL id="mul-1"/>`, so the model continues thinking
     right after the closing `/>`. It therefore never needs an operand or a
     result inside its own generation channel, and cannot forge one there,
     since results only ever appear in the RESULTS message.

Phases
------
    -1   stop at the first tool call: reasoning shows the tags used and the
         run halts before any injection (Example A of the prompt)
    -2   intercept both calls and publish both results in the RESULTS
         message, resuming between them; the final answer is not
         requested (Example B state: results available, none quoted yet)
    -3   additionally request the final answer: it must be derived from the
         id-referenced RESULTS values (Example C)

Usage (from the repository root, .venv active)
----------------------------------------------
    python src/instantrag_qwen_demo.py -1
    python src/instantrag_qwen_demo.py -2
    python src/instantrag_qwen_demo.py -3
"""

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

import requests

# running as a plain script leaves no package context, so add src/ explicitly
sys.path.insert(0, str(Path(__file__).resolve().parent))
from llm_request import resolve_api_key

USER_QUESTION_DEFAULT = "Please calculate 10+(2*4)"
NO_RESULT = object()
# merged into every request payload; the capture script uses it to vary the
# request body and bypass a response cache keyed on the body
PAYLOAD_EXTRAS = {}

# matches <ADD x1=".." x2=".."/> style empty, self-closed tool tags
OPEN_TOOL_RE = re.compile(r'<(ADD|MUL)((?:\s+\w+="[^"]*")*)\s*/>')
ATTR_RE = re.compile(r'(\w+)="([^"]*)"')


# ---------------------------------------------------------------------------
# Config helpers
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent


def _settings_path_default() -> Path:
    return ROOT / "config" / "llm_config.json"


def _system_prompt_path_default() -> Path:
    return ROOT / "config" / "instantrag.txt"


def load_model(settings_path):
    """Load the single-model llm_config.json into the shape run_turn expects."""
    with open(settings_path, encoding="utf-8-sig") as f:
        config = json.load(f)
    base_url = config.get("base_url", "").rstrip("/")
    if not base_url:
        raise ValueError(f"'base_url' is missing or empty in {settings_path}")
    config["endpoint"] = base_url + config.get("endpoint", "/chat/completions")
    # token is resolved from the environment, falling back to the .env file
    config["token"] = resolve_api_key(config)
    return config


def load_system_prompt(prompt_path):
    result = prompt_path.read_text(encoding="utf-8")
    return result


# ---------------------------------------------------------------------------
# Tool tag handling
# ---------------------------------------------------------------------------

def _fmt(value):
    if isinstance(value, float) and value.is_integer():
        result = str(int(value))
    else:
        result = str(value)
    return result


def parse_number(token, dep_value):
    value = token.strip()
    if re.fullmatch(r"\s*<\s*DEP\s*>\s*", value):
        result = dep_value if dep_value is not NO_RESULT else None
    else:
        try:
            result = float(value)
        except ValueError:
            result = None
    return result


def exec_tool(name, attrs, dep_value):
    result = None
    numbers = []
    for key in sorted(attrs, key=lambda k: int(k[1:]) if re.fullmatch(r"x\d+", k) else -1):
        if not re.fullmatch(r"x\d+", key):
            continue
        number = parse_number(attrs[key], dep_value)
        if number is None:
            return None
        numbers.append(number)
    if numbers:
        if name == "ADD":
            total = 0.0
            for number in numbers:
                total += number
            result = total
        else:
            product = 1.0
            for number in numbers:
                product *= number
            result = product
    return result


def first_empty_tag(text):
    # only tags carrying x-arguments are proposed calls; id-only self-closed
    # tags like <ADD id="add-1"/> are references to already-published results
    result = None
    for match in OPEN_TOOL_RE.finditer(text):
        attrs = dict(ATTR_RE.findall(match.group(2)))
        if any(re.fullmatch(r"x\d+", key) for key in attrs):
            result = {
                "name": match.group(1),
                "attrs": attrs,
                "start": match.start(),
                "end": match.end(),
                "raw": match.group(0),
            }
            break
    return result


def result_tag(name, tag_id, value):
    tag = "<" + name + ' id="' + tag_id + '">' + _fmt(value) + "<" + "/" + name + ">"
    return tag


def reference_tag(name, tag_id):
    # self-closed, id-only form: a reference to a published result, never a call
    tag = "<" + name + ' id="' + tag_id + '"' + "/>"
    return tag


def results_message(entries):
    content = "<RESULTS>" + " ".join(entries) + "<" + "/RESULTS>"
    # user role: the gateway allows exactly one system message (index 0);
    # provider_qwen.py uses the same convention (QWEN_SECONDARY_SYSTEM_ROLE)
    message = {"role": "user", "content": content}
    return message


# a closed tool tag with a body in model output is a forged result
CLOSED_TOOL_RE = re.compile(r'<(ADD|MUL)((?:\s+\w+="[^"]*")*)\s*>([^<]+)' + "<" + "/" + r"\1>")


def forged_tags(text, published):
    # a closed tag is legitimate only as an exact echo of a published result:
    # same id, no call arguments, body identical to what the server computed
    found = []
    for match in CLOSED_TOOL_RE.finditer(text):
        name = match.group(1)
        attrs = dict(ATTR_RE.findall(match.group(2)))
        body = match.group(3).strip()
        tag_id = attrs.get("id")
        is_call = any(re.fullmatch(r"x\d+", key) for key in attrs)
        echo = tag_id in published and not is_call and published[tag_id] == (name, body)
        if not echo:
            found.append(match.group(0))
    return found


# ---------------------------------------------------------------------------
# Interruptible streaming
# ---------------------------------------------------------------------------

def run_turn(model_cfg, messages, max_tokens, temperature, stop_at_tool, dep_value=None):
    endpoint = model_cfg["endpoint"].rstrip("/")
    url = endpoint if endpoint.endswith("/chat/completions") else endpoint + "/chat/completions"
    payload = {
        "model": model_cfg["model"],
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": True,
        "stream_options": {"include_usage": True},
        "chat_template_kwargs": {"enable_thinking": True},
    }
    payload.update(PAYLOAD_EXTRAS)
    headers = {"Content-Type": "application/json", "Accept": "text/event-stream"}
    token = model_cfg.get("token")
    if token:
        headers["Authorization"] = "Bearer " + token

    reasoning = ""
    content = ""
    # untouched copies of each channel as received: the interrupt path trims
    # `reasoning`/`content` at the intercepted tag, so the full output the model
    # actually produced is kept here for the report
    reasoning_all = ""
    content_all = ""
    finish_reason = None
    usage = {}
    interrupt = None
    discarded = ""

    request = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    with urllib.request.urlopen(request, timeout=300) as resp:
        for raw_line in resp:
            line = raw_line.decode("utf-8").strip()
            if not line.startswith("data:"):
                continue
            data_str = line[5:].strip()
            if data_str == "[DONE]":
                break
            chunk = json.loads(data_str)
            usage = chunk.get("usage") or usage
            choices = chunk.get("choices") or []
            if not choices:
                continue
            delta = choices[0].get("delta") or {}
            finish_reason = choices[0].get("finish_reason") or finish_reason
            delta_reasoning = delta.get("reasoning") or delta.get("reasoning_content") or ""
            delta_content = delta.get("content") or ""
            content += delta_content
            if interrupt is not None:
                discarded += delta_reasoning + delta_content
                continue
            reasoning += delta_reasoning
            reasoning_all += delta_reasoning
            content_all += delta_content
            if stop_at_tool:
                tool = first_empty_tag(reasoning)
                leak = False
                if tool is not None:
                    discarded += reasoning[tool["end"]:]
                    reasoning = reasoning[:tool["end"]]
                else:
                    tool = first_empty_tag(content)
                    leak = True
                    if tool is not None:
                        discarded += content[tool["start"]:]
                        content = content[:tool["start"]]
                if tool is not None:
                    dep = dep_value if dep_value is not None else NO_RESULT
                    value = exec_tool(tool["name"], tool["attrs"], dep)
                    interrupt = {"tool": tool, "value": value, "leak": leak}
                    # closing the connection stops the inference engine
                    break

    result = {
        "reasoning": reasoning,
        "content": content,
        "reasoning_all": reasoning_all,
        "content_all": content_all,
        "finish_reason": finish_reason,
        "usage": usage,
        "interrupt": interrupt,
        "discarded": discarded,
    }
    return result


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def print_streamed_turn(label, turn):
    print("-" * 78)
    print(label)
    print("-" * 78)
    print()
    print("[REASONING COLLECTED BEFORE STOP]")
    print(turn["reasoning"] if turn["reasoning"] else "(none)")
    print()
    print("[ANSWER / OUTPUT COLLECTED]")
    # show the whole answer channel as received (up to the stop), including the
    # intercepted tag: on a leak turn["content"] is trimmed at the tag and would
    # otherwise hide the very evidence the channel note refers to
    answer_shown = turn.get("content_all") or turn["content"]
    print(answer_shown.strip() if answer_shown.strip() else "(none yet)")
    print()
    if turn["interrupt"] is not None:
        tool = turn["interrupt"]["tool"]
        value = turn["interrupt"]["value"]
        print("[INTERCEPTED TOOL CALL]")
        print(f"  tag executed    : {tool['raw']}")
        print(f"  result          : {_fmt(value) if value is not None else '(unresolved: <DEP> without a known value)'}")
        if turn["interrupt"].get("leak"):
            print("  channel note    : call tag appeared in the ANSWER channel (protocol leak) — intercepted anyway")
        print("  stream stopped  : tokens after the closed tag discarded")
        print("  thinking as collected (the call tag is still the model's own empty call here):")
        print("  " + json.dumps("<|im_start|>" + turn["reasoning"], ensure_ascii=False))
        print("  it is continued with that tag rewritten to an id reference — see [resume] below")
    elif turn["content"]:
        print("[NO TOOL CALL] the model answered directly")
    print(f"  finish_reason   : {turn['finish_reason']}")
    if turn["usage"]:
        print(f"  usage           : {json.dumps(turn['usage'])}")
    print()


# ---------------------------------------------------------------------------
# Phases
# ---------------------------------------------------------------------------

PHASE_LABELS = {
    1: "Example A — stream stops at the first tool call, nothing injected yet",
    2: "Example B state — both results published in the RESULTS message, final answer not requested",
    3: "Example C — results referenced by id and used for the final answer",
}


def partial_assistant_message(partial_thinking):
    message = {"role": "assistant", "content": "<|im_start|>" + partial_thinking}
    return message


def assign_id(counters, name):
    key = name.lower()
    counters[key] = counters.get(key, 0) + 1
    tag_id = key + "-" + str(counters[key])
    return tag_id


def resume_prefix(turn, tag_id):
    # the interrupted thinking is continued from the point of the stop, with
    # the call tag replaced by a reference to the result published for it, so
    # the model resumes its reasoning after the closing "/>" and sees neither
    # the operands nor the value in its own channel
    interrupt = turn["interrupt"]
    tool = interrupt["tool"]
    thinking = turn["reasoning"]
    ref = reference_tag(tool["name"], tag_id)
    if interrupt.get("leak"):
        # the tag had leaked into the answer channel, so the thinking does not
        # contain it: append the reference to what was collected
        result = thinking + ref
    else:
        result = thinking[:tool["start"]] + ref
    return result


def run_phase(model_cfg, system_prompt, question, phase, max_tokens, temperature):
    base_messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question},
    ]
    counters = {}
    result_entries = []
    published = {}
    pending_prefix = None

    print("=" * 78)
    print(f"phase -{phase}: {PHASE_LABELS[phase]}")
    print("=" * 78)
    print()

    stage = 0
    turn = None
    dep_value = None
    retries = 0
    correction = None
    while stage < 6:
        stage += 1
        stop_at_tool = True
        if phase == 3 and len(result_entries) >= 2:
            stop_at_tool = False
        messages = list(base_messages)
        if result_entries:
            messages.append(results_message(result_entries))
        if correction is not None:
            messages.append({"role": "user", "content": correction})
            pending_prefix = None
        if pending_prefix is not None:
            messages.append(partial_assistant_message(pending_prefix))
        turn = run_turn(model_cfg, messages, max_tokens, temperature, stop_at_tool=stop_at_tool, dep_value=dep_value)
        label = "stage 1 — stream watched, interrupted at the first empty tool call"
        if stage > 1 and stop_at_tool:
            label = f"stage {stage} — resumed with {len(result_entries)} published result(s)"
        if not stop_at_tool:
            label = f"stage {stage} — final request: answer asked, no tool-watch stop"
        if correction is not None:
            label += " (after correction prompt)"
            correction = None
        print_streamed_turn(label.upper(), turn)
        if stage > 1:
            forged = forged_tags(turn["reasoning"], published)
            print(f"[guard] forged tool results in model output : {forged if forged else 'none'}")
            print()
        if stage == 1:
            tags = re.findall(r"<(ADD|MUL)\b", turn["reasoning"])
            print(f"[a] operation tags in reasoning : {sorted(set(tags)) if tags else 'none'}")
            print(f"[b] answer while results pending: {turn['content'].strip()!r}")
            print()
        if turn["interrupt"] is None:
            content = turn["content"].strip()
            digits = re.search(r"\d", content) is not None
            if not digits and retries < 1 and phase >= 2 and (len(result_entries) >= 1 or stage == 1):
                retries += 1
                correction = "Continue the calculation: emit the remaining empty tool-call tag (with literal or published x-values), or give the final answer using only numbers published inside <RESULTS>."
                continue
            quoted = dep_value is not None and _fmt(dep_value) in content
            print(f"[c] collected answer              : {content!r}")
            print(f"    last server-calculated value  : {_fmt(dep_value) if dep_value is not None else 'n/a'} — quoted in answer: {quoted}")
            print(f"    published results             : {result_entries}")
            return turn
        value = turn["interrupt"]["value"]
        if value is None:
            print("[halt] intercepted call has an unresolved <DEP>: the server has no value for it")
            return turn
        tag_id = assign_id(counters, turn["interrupt"]["tool"]["name"])
        entry = result_tag(turn["interrupt"]["tool"]["name"], tag_id, value)
        result_entries.append(entry)
        published[tag_id] = (turn["interrupt"]["tool"]["name"], _fmt(value))
        dep_value = value
        pending_prefix = resume_prefix(turn, tag_id)
        print(f"[inject] result published in a user-role RESULTS message: {entry}")
        print("[resume] assistant continuation sent as a partial message: the interrupted thinking")
        print("         with the intercepted call tag replaced by the reference to its published result")
        print("         " + json.dumps(partial_assistant_message(pending_prefix)["content"], ensure_ascii=False))
        print()
        if phase == 1:
            break
        if phase == 2 and len(result_entries) >= 2:
            break

    print(f"[c] phase -{phase} stops here: results published to the model: {result_entries}")
    print("    the final answer was deliberately not requested — quoting a number now would be premature.")
    return turn


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def parse_arguments():
    parser = argparse.ArgumentParser(description="InstantRAG interrupt/resume demo against qwen-3.5-35b")
    parser.add_argument("phase", metavar="[-1|-2|-3]", choices=["-1", "-2", "-3"], help="phase to run (see module docstring)")
    parser.add_argument("--model", default=None, help="model to use (default: the model in llm_config.json)")
    parser.add_argument("--settings", type=Path, default=_settings_path_default(), help="path to llm_config.json")
    parser.add_argument("--system-prompt", type=Path, default=_system_prompt_path_default(), help="path to the system prompt file")
    parser.add_argument("--question", default=USER_QUESTION_DEFAULT, help="the user question to ask")
    parser.add_argument("--max-tokens", type=int, default=2048, help="max tokens for the completion")
    parser.add_argument("--temperature", type=float, default=0.1, help="sampling temperature")
    return parser.parse_args()


def main():
    exit_code = 0
    try:
        arguments = parse_arguments()
        model_cfg = load_model(arguments.settings)
        if arguments.model:
            model_cfg["model"] = arguments.model
        system_prompt = load_system_prompt(arguments.system_prompt)
        print(f"model    : {model_cfg['model']}")
        print(f"endpoint : {model_cfg['endpoint']}")
        print(f"system   : {arguments.system_prompt} ({len(system_prompt)} chars)")
        print(f"question : {arguments.question}")
        print()
        final_turn = run_phase(
            model_cfg=model_cfg,
            system_prompt=system_prompt,
            question=arguments.question,
            phase=int(arguments.phase[1:]),
            max_tokens=arguments.max_tokens,
            temperature=arguments.temperature,
        )
        if final_turn["content"].strip():
            exit_code = 0
    except Exception as error:
        print(f"ERROR: {error}", file=sys.stderr)
        exit_code = 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
