#!/usr/bin/env python3
"""
== 운영 맥락 ==
용도: 소스 안에서 화면에 나가는 한국어 문구를 훑어 AI 티가 나는 기호와 상투어를 잡는다.
      규칙 원본은 im-not-ai (MIT, github.com/epoko77-ai/im-not-ai) 와 같은 묶음의 WRITING.md.
      여기서는 그중 **화면 문구에서 실제로 반복해서 걸리는 것만** 기계로 본다.
      사람이 읽는 생성물 파일(리포트·콘텐츠)이 아니라 소스 코드 안의 화면 문구만 본다.
사용: python3 screen_copy.py <프로젝트폴더>
      python3 screen_copy.py <프로젝트폴더> --strict      어휘 경고도 실패로
종료코드: 0 깨끗 / 2 볼 것만 있음(경고) / 3 고칠 것 있음 / 1 실행 오류

무엇을 보나: 사용자에게 보이는 한국어 문자열과 화면 글자.
무엇을 안 보나: 코드 주석, 변수·함수 이름, 서버 기록(console), 개발자에게 던지는 오류
              (throw new Error), git 메시지, 파일 경로. 그 자리는 기술용어를 그대로
              쓰는 게 맞다(WRITING.md 비적용 범위).
빼는 법: 줄 끝에 copy-ok, 파일 통째로는 머리 주석에 "문구검사: 제외".
        모델에게 넘기는 지시문 파일이 그렇다. 사람이 보는 화면이 아니라 규칙이 다르다.
의도적 미구현: 문장 리듬·길이 균일성 같은 통계 판정. 그건 사람이 읽고 판단할 일이고,
              기계로 하면 오탐이 쏟아진다. 필요하면 im-not-ai 의 metrics.py 를 쓴다.
다루는 확장자: .tsx .ts .jsx .js
"""
import os
import re
import sys

# 윈도우 기본 콘솔은 cp949 라서 긴 줄표 같은 글자를 찍다가 죽는다. 출력 통로를 UTF-8 로 돌린다.
for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            pass

# ── 무조건 고칠 것 (기호) ────────────────────────────────────────────
HARD = [
    ("—", "긴 줄표(em dash). 쉼표나 괄호로 풀거나 문장을 나눈다 (im-not-ai J-3)"),
    ("–", "짧은 줄표(en dash). 쉼표나 괄호로 (im-not-ai J-3)"),
    ("━", "강조선. 빼거나 여백으로"),
    ("═", "강조선. 빼거나 여백으로"),
    ("···", "말줄임은 … 또는 마침표 세 개로"),
]
# 줄 맨 앞의 머리표만 잡는다. 문장 안의 가운뎃점(주문·배송)은 한국어 표준 부호라 통과.
BULLET_HEAD = re.compile(r"^\s*[•·]\s+")
# 글자 앞에 붙은 장식 화살표만 잡는다("▶ 영상"). 홀로 선 것은 재생 아이콘이라 그대로 둔다.
ARROW_LABEL = re.compile(r"▶\s*[가-힣A-Za-z0-9{]")

# ── 고치는 게 나은 것 (어휘) ────────────────────────────────────────
# 기술 표준 용어로 쓰이면 맞을 수 있어 경고로만 본다(WRITING.md 예외 규칙).
SOFT = {
    "혁신적": "무엇이 어떻게 달라지는지 구체로",
    "획기적": "무엇이 어떻게 달라지는지 구체로",
    "차별화된": "무엇이 다른지 그대로",
    "진정한": "빼도 뜻이 통한다",
    "손쉽게": "몇 번 만에 되는지로",
    "간편하게": "몇 번 만에 되는지로",
    "솔루션": "무엇을 해 주는지로 (업계 표준 용어면 그대로 둬도 된다)",
    "여정": "영어 journey 직역",
    "경험을 선사": "무엇을 하게 되는지로",
    "결론적으로": "바로 결론만 쓴다 (im-not-ai D-1)",
    "정리하자면": "바로 결론만 쓴다 (im-not-ai D-1)",
    "한마디로": "바로 결론만 쓴다 (im-not-ai D-1)",
    "지금 바로 시작": "무엇을 하는 단추인지로",
    "더 알아보기": "무엇을 보여 주는지로",
    "주목할 만": "왜 그런지 사실로 (im-not-ai D-2)",
}

# 카드 제목 자리에 물음·말투가 들어간 것("어디서 나갔나", "누가 벌어주나")을 잡는다.
# 제목은 두 어절 명사구가 기준(CARD-TITLES.md).
# 제목 자리로 보는 것: card-title / admin-card-header / fold-t 클래스와 h2~h4. 본문 문장은 안 본다.
# 대화창 제목처럼 물음이 맞는 자리는 줄 끝 copy-ok.
HEADING_SLOT = re.compile(r'(?:className="(?:card-title|admin-card-header|fold-t)[^"]*"|<h[234]\b)[^>]*>\s*([^<{]*)')
HEADING_QUESTION = re.compile(r"(?:[가-힣]+(?:나|는가|인가|까)|\?)\s*[)）]?\s*$")

# 그림글자만 잡는다. 닫기·체크 같은 기호 문자는 아이콘으로 쓰이니 건드리지 않는다.
# 빼면 단추가 빈 칸이 된다.
EMOJI = re.compile("[\U0001F300-\U0001FAFF\U0001F000-\U0001F0FF]|[✅❌❗❓✨❤⚠⛔⭐⁉]")
HANGUL = re.compile(r"[가-힣]")
SKIP_DIRS = {"node_modules", ".next", ".git", "e2e", "scripts", "migrations", "test-results", "venv"}
EXTS = (".tsx", ".ts", ".jsx", ".js")

# 주석 줄. 블록 주석 본문은 거의 " * " 로 시작하고, 화면 코드에는 {/* ... */} 도 흔하다.
COMMENT_LINE = re.compile(r"^\s*(//|\{?/\*|\*/|\*(?!/))")
# 코드 뒤에 붙은 주석은 잘라 낸다. 주소(https://) 안의 // 는 건드리지 않는다.
TRAILING_COMMENT = re.compile(r"(?<![:\w])//.*$")
# 줄 안에 닫힌 블록 주석도 주석이다: } catch { /* 실패는 조용히 */ }
INLINE_BLOCK = re.compile(r"/\*.*?\*/", re.S)
# 개발자에게 던지는 오류는 화면 문구가 아니다. 그 자리는 정확한 용어를 그대로 쓴다.
DEV_ONLY = re.compile(r"throw\s+new\s+Error|console\.|new Error\(")
# 일부러 남기는 자리는 줄 끝에 표시한다.
ALLOW_MARK = re.compile(r"(copy-ok|문구검사-예외)")
# 파일 통째로 빼려면 머리 주석에 이 표시를 둔다.
FILE_SKIP = re.compile(r"(screen-copy:\s*off|문구검사:\s*제외)")


def screen_text(line: str) -> str:
    """이 줄에서 사람이 보는 부분만 남긴다. 아니면 빈 문자열."""
    if COMMENT_LINE.search(line) or ALLOW_MARK.search(line):
        return ""
    if DEV_ONLY.search(line):
        return ""
    body = INLINE_BLOCK.sub(" ", line)
    body = TRAILING_COMMENT.sub("", body)
    return body if HANGUL.search(body) else ""


def files(roots):
    for root in roots:
        if os.path.isfile(root):
            yield root
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
            for f in filenames:
                if f.endswith(EXTS):
                    yield os.path.join(dirpath, f)


def check(path):
    """(고칠 것, 볼 것) 을 돌려준다. 한국어가 있는 줄만 본다."""
    try:
        raw = open(path, encoding="utf-8").read()
    except (OSError, UnicodeDecodeError):
        return [], []

    head = "\n".join(raw.splitlines()[:40])
    if FILE_SKIP.search(head):
        return [], []

    errors, warns = [], []
    in_block = False  # 여러 줄 주석 안인가. 본문 줄에 * 가 없는 주석도 있다.
    for no, raw_line in enumerate(raw.splitlines(), 1):
        stripped = INLINE_BLOCK.sub(" ", raw_line)  # 한 줄에서 닫힌 것은 먼저 지운다
        if in_block:
            if "*/" in stripped:
                in_block = False
                stripped = stripped.split("*/", 1)[1]
            else:
                continue
        elif "/*" in stripped:
            # 여는 것만 있으면 다음 줄부터 주석이다
            in_block = True
            stripped = stripped.split("/*", 1)[0]

        line = screen_text(stripped)
        if not line:
            continue
        for sym, fix in HARD:
            if sym in line:
                errors.append((no, sym, fix, line.strip()[:90]))
        if BULLET_HEAD.search(line):
            errors.append((no, "머리표", "줄바꿈이나 번호로", line.strip()[:90]))
        if ARROW_LABEL.search(line):
            errors.append((no, "화살표 장식", "글자 앞의 화살표는 뺀다 (홀로 쓰는 아이콘은 그대로)",
                           line.strip()[:90]))
        m = EMOJI.search(line)
        if m:
            warns.append((no, m.group(), "그림글자는 빼는 게 기본", line.strip()[:90]))
        for h in HEADING_SLOT.finditer(line):
            title = h.group(1).strip()
            if title and HEADING_QUESTION.search(title):
                warns.append((no, "제목이 물음", "카드 제목은 두 어절 명사구로 (CARD-TITLES.md 짝 표: 어디서 나갔나→이탈 지점)",
                              line.strip()[:90]))
        for word, fix in SOFT.items():
            if word in line:
                warns.append((no, word, fix, line.strip()[:90]))
    return errors, warns


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    strict = "--strict" in sys.argv

    # 인자가 폴더 하나면 프로젝트 뿌리로 보고 그 안의 화면 폴더를 찾는다.
    if len(args) == 1 and os.path.isdir(args[0]):
        base = args[0]
        roots = [os.path.join(base, d) for d in ("app", "components", "lib", "src")]
    else:
        roots = args or ["app", "components", "lib"]
    roots = [r for r in roots if os.path.exists(r)]
    if not roots:
        return 0

    n_err = n_warn = 0
    for path in sorted(files(roots)):
        errors, warns = check(path)
        if not errors and not warns:
            continue
        print("\n" + path)
        for no, sym, fix, line in errors:
            n_err += 1
            print("  고칠 것  " + str(no) + "행  " + sym + " → " + fix)
            print("           " + line)
        for no, sym, fix, line in warns:
            n_warn += 1
            print("  볼 것    " + str(no) + "행  " + sym + " → " + fix)
            print("           " + line)

    if n_err or n_warn:
        print("\n  고칠 것 " + str(n_err) + " · 볼 것 " + str(n_warn) +
              "   (규칙: WRITING.md · im-not-ai)")
    if n_err or (strict and n_warn):
        return 3
    return 2 if n_warn else 0


if __name__ == "__main__":
    sys.exit(main())
