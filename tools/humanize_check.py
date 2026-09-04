#!/usr/bin/env python3
"""
== 운영 맥락 ==
용도: 사람이 읽는 한국어 글(칼럼·보고서·알림 본문·상세페이지 문안·.md)을 훑어 AI 티가 나는
      자리를 줄 번호와 함께 잡는다. 고치지는 않는다. 고치는 규칙은 references/HUMANIZE-KO.md 에
      있고, 그 문서는 blader/humanizer (MIT, 위키백과 "AI 글의 신호" 35패턴) 를 한국어에 맞게
      옮긴 것이다. 패턴 번호는 그 문서와 같다.
      소스 코드 안의 화면 문구는 여기서 안 본다. 그건 screen_copy.py 가 한다.
사용: python3 humanize_check.py <파일 또는 폴더>...      .md .txt 를 훑는다
      python3 humanize_check.py - < 글.txt                 표준입력
      python3 humanize_check.py <파일> --strict            볼 것도 실패로
종료코드: 0 깨끗 / 2 볼 것만 있음 / 3 고칠 것 있음 / 1 실행 오류

무엇을 보나: 본문 산문.
무엇을 안 보나: 코드 울타리(```) 안, 머리 정보(---), 인용 줄(>), 링크 주소, HTML 태그, 표 줄(|).
              humanizer 가 "인용·제목·고유명사 안의 낱말은 고치지 않는다" 고 못박은 것과 같다.
의도적 미구현: 문장 길이 통계·번역투·연결어미 뒤 쉼표 같은 한국어 문법 층. 그건 im-not-ai
              (github.com/epoko77-ai/im-not-ai) 의 규칙과 metrics.py 가 이미 하고, 여기서 다시
              만들면 원본 갱신과 어긋난다. 이 도구는 humanizer 35패턴 중 기계로 볼 수 있는 것만.
"""
import os
import re
import sys

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            pass

EXTS = (".md", ".txt", ".markdown")
SKIP_DIRS = {"node_modules", ".git", ".next", "venv", "dist", "build"}

# ── 고칠 것: 예외가 거의 없는 것 ──────────────────────────────────────
HARD = [
    (re.compile(r"[—–]|(?<=\S) -- (?=\S)"), "줄표",
     "쉼표·괄호·마침표로 풀거나 문장을 나눈다 (14)"),
    (re.compile("[\U0001F300-\U0001FAFF\U0001F000-\U0001F0FF✅❌❗❓✨⚠⛔⭐]"),
     "그림글자", "뺀다 (18)"),
    (re.compile(r"도움이\s*(?:되셨|되길|됐으면|되었으면|되기를)|물론입니다|궁금한\s*점이\s*있|언제든지?\s*(?:말씀|문의|물어)|"
                r"더\s*필요하(?:시면|신)|다음은\s+\S+(?:에\s*대한|의)\s+\S+입니다|알려\s*드리겠습니다[.!]?\s*$"),
     "대화창 잔여", "챗봇 인사·제안·맺음말. 뺀다 (20)"),
    (re.compile(r"좋은\s*질문|훌륭한\s*질문|정확히\s*보셨|맞습니다!|탁월한\s*지적"),
     "아첨", "칭찬·동의 먼저 하지 말고 바로 답 (22)"),
]

# ── 볼 것: 문맥 따라 맞을 수 있어 경고로만 ────────────────────────────
SOFT = [
    (re.compile(r"전환점|분수령|새로운\s*장을|이정표|획을\s*긋|패러다임|중대한\s*변화|자리매김"),
     "부풀린 의미", "평범한 사실을 큰 변화로 포장. 사실만 남긴다 (1)"),
    (re.compile(r"(?:언론|매체|방송)에\s*(?:소개|보도|출연)|팔로워\s*\d|수많은\s*매체"),
     "이름 나열", "매체·숫자 나열로 중요성 증명. 쓸모 있는 맥락만 (2)"),
    (re.compile(r"(?:보여\s*주며|상징하며|반영하며|강조하며|입증하며|드러내며|기여하며)"),
     "-며 덧붙임", "사실 뒤에 해석을 매달아 깊어 보이게 함. 근거 있는 것만 (3)"),
    (re.compile(r"혁신적|획기적|압도적|최고의|최상의|완벽한|손꼽히는|자랑하는|아름다운\s*자연|숨은\s*보석|필수\s*코스"),
     "홍보 어투", "광고 문장. 무엇이 어떻게 다른지 사실로 (4)"),
    (re.compile(r"전문가들은|업계에서는|많은\s*이들이|연구에\s*따르면|알려져\s*있다|평가받고\s*있다|여겨진다"),
     "출처 모호", "누가 말했는지 없으면 주장을 빼거나 실제 출처를 (5)"),
    (re.compile(r"그럼에도\s*불구하고|여러\s*과제가\s*남|향후\s*전망|앞으로의\s*과제|지속적인\s*성장"),
     "과제와 전망 공식", "뻔한 과제·전망 단락. 사실과 실제 계획만 (6)"),
    (re.compile(r"자리매김|역할을\s*하고\s*있|(?:을|를)\s*자랑하|(?:을|를)\s*갖추고\s*있|기능을\s*제공"),
     "'이다·있다' 회피", "'~로 자리매김' 대신 '~이다', '~을 갖추고 있다' 대신 '~이 있다' (8)"),
    (re.compile(r"되어진|되어\s*진다|에\s*의해\s*(?:이루어|만들어|진행|제공)"),
     "이중 피동·행위자 숨김", "누가 하는지 주어로. im-not-ai A-8·A-9 (13)"),
    (re.compile(r"(?:에서|부터)\s+\S+(?:까지|에\s*이르기까지)"),
     "X에서 Y까지", "실제 범위가 아니면 항목을 그냥 나열 (12)"),
    (re.compile(r"^\s*#{1,6}\s+[^:\n]{2,}:\s*\S", re.M),
     "콜론 부제 제목", "제목은 명사구 하나로. im-not-ai C-10 (17)"),
    (re.compile(r"[“”‘’]"),
     "굽은 따옴표", "곧은 따옴표로. 다른 신호와 겹칠 때만 의미 있음 (19)"),
    (re.compile(r"정확한\s*(?:정보|자료)(?:는|가)\s*(?:없|부족)|알려진\s*바(?:에|로)|(?:으로|로)\s*추정된다|"
                r"(?:인|한)\s*것으로\s*보인다|자세한\s*내용은\s*확인되지"),
     "지식 한계·추측", "모르면 모른다고 쓰거나 문장을 뺀다. 추측을 사실처럼 쓰지 않는다 (21)"),
    (re.compile(r"하기\s*위해서는|에\s*있어서|라고\s*할\s*수\s*있다|하는\s*것이\s*중요합니다|할\s*필요가\s*있다|"
                r"라는\s*점에서|주목할\s*점은|다는\s*것이다"),
     "군더더기", "'~하려면', '~에서', 바로 단언으로 (23)"),
    (re.compile(r"밝은\s*미래|기대(?:된다|됩니다|해\s*본다)|앞으로도|나아갈\s*것|계속될\s*것|주목된다|귀추가"),
     "뻔한 긍정 결말", "마지막 사실이나 실제 계획으로 끝낸다 (25)"),
    (re.compile(r"핵심은|본질은|진짜\s*문제는|결국\s*중요한\s*것은|근본적으로|본질적으로|중요한\s*건"),
     "숨은 진실인 척", "평범한 말을 깊은 통찰처럼 포장. 그 문장을 바로 쓴다 (27)"),
    (re.compile(r"살펴보(?:겠습니다|자|겠다)|알아보(?:겠습니다|자)|짚어보(?:겠습니다|자)|이제\s*\S+\s*해\s*보자|"
                r"지금부터|다음과\s*같(?:다|습니다)|하나\s*짚고\s*넘어가"),
     "예고", "다음 내용을 예고하지 말고 바로 내용부터 (28)"),
    (re.compile(r"기존에는|이전\s*방식은|예전에는|과거에는|종전"),
     "이전 판 이야기", "지금 어떻게 동작하는지만. 변경 이력은 변경 기록에 (30)"),
    (re.compile(r"(?:의|는)\s*(?:언어|화폐|건축|거울)(?:다|이다)|함정이\s*된다|도구가\s*아니라\s*거울"),
     "격언 공식", "그럴듯한 한 줄 대신 구체 주장 (32)"),
    (re.compile(r"(?:^|[.!?]\s+)(?:솔직히|사실은|까놓고|진심으로\s*말하면|고백하자면)", re.M),
     "가짜 솔직", "솔직한 척 멈칫하지 말고 바로 답 (33)"),
    (re.compile(r"오해하지\s*마|오해는\s*마|라는\s*(?:말|뜻)은\s*아니|분명히\s*하자면|하자는\s*(?:게|것이)\s*아니라|"
                r"(?:을|를)\s*부정하는\s*(?:게|것은)\s*아니"),
     "없는 반박에 답함", "글에 없는 반론을 막지 않는다. 진짜 주장만 남긴다 (34)"),
    (re.compile(r"(?:흔히|보통|대개)\s+\S+(?:고르|선택|쓰|하)[^.]*?지만|쉬운\s*방법은[^.]*?지만|유혹|"
                r"라고\s*생각할\s*수\s*있지만|얼핏\s*\S+\s*같지만|당연해\s*보이지만"),
     "가짜 대안", "아무도 안 고를 선택지를 세워 물리치는 틀. 실제 제약만 (35)"),
    (re.compile(r"결론적으로|정리하자면|요약하면|한마디로|종합하면"),
     "결산 상투구", "바로 결론만. im-not-ai D-1"),
]

# 문서 단위로 세는 것. 한 번은 사람도 쓴다. 쌓이면 틀이다.
AI_WORDS = ["다양한", "효과적", "최적화", "강화", "촉진", "심층", "핵심적", "중요한 역할", "활용하", "한층",
            "혁신", "시너지", "통찰", "가치를", "지속 가능", "역동적", "풍부한", "폭넓은", "체계적", "전략적"]
NOT_X_BUT_Y = re.compile(r"(?:이|가|은|는)\s*아니라\s+[가-힣]|뿐만\s*아니라|단순한\s+\S+(?:이|가)?\s*아니")
# "매출, 비용, 고객 수를" 처럼 짧은 명사 셋이 한 조사로 묶인 꼴만. 절이 쉼표로 이어진 것은 안 잡는다.
TRIPLE = re.compile(r"(?<![가-힣])[가-힣]{1,8}(?:와|과|,)\s*[가-힣]{1,8}(?:,|와|과)\s*(?:그리고\s+)?[가-힣]{1,8}(?:\s[가-힣]{1,4})?(?:을|를|이|가|은|는|까지|도|로|으로)(?![가-힣])")
BOLD = re.compile(r"\*\*[^*\n]+\*\*")
# "- **이름:** 설명" 과 "- **이름**: 설명" 둘 다. 콜론이 굵게 안에 있든 밖에 있든.
BOLD_LABEL_ITEM = re.compile(r"^\s*(?:[-*]|\d+\.)\s+\*\*[^*]+?(?:[:：]\*\*|\*\*\s*[:：])")
LIST_MARK = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
# 큰따옴표 안은 남의 말이다. 인용 안의 낱말은 고치지 않는다(humanizer "Secondhand text").
QUOTED = re.compile(r"\"[^\"\n]{1,120}\"|“[^”\n]{1,120}”")
HEADING = re.compile(r"^\s*#{1,6}\s+(.+?)\s*$")
FENCE = re.compile(r"^\s*```")
QUOTE = re.compile(r"^\s*>")
TABLE = re.compile(r"^\s*\|")
LINK_TARGET = re.compile(r"\]\([^)]*\)")
INLINE_CODE = re.compile(r"`[^`]*`")
HTML_TAG = re.compile(r"<[^>]+>")
SENT_SPLIT = re.compile(r"(?<=[.!?…])\s+")
HANGUL = re.compile(r"[가-힣]")


def prose_lines(text):
    """(줄 번호, 산문) 만 돌려준다. 코드·머리 정보·인용·표·링크 주소는 지운다."""
    lines = text.splitlines()
    out = []
    in_fence = False
    in_front = False
    for no, raw in enumerate(lines, 1):
        if no == 1 and raw.strip() == "---":
            in_front = True
            continue
        if in_front:
            if raw.strip() == "---":
                in_front = False
            continue
        if FENCE.match(raw):
            in_fence = not in_fence
            continue
        if in_fence or QUOTE.match(raw) or TABLE.match(raw):
            continue
        body = LINK_TARGET.sub("]", raw)
        body = INLINE_CODE.sub(" ", body)
        body = HTML_TAG.sub(" ", body)
        out.append((no, body))
    return out


def sentences(lines):
    """줄 목록을 문장 목록 [(줄 번호, 문장)] 으로."""
    out = []
    for no, body in lines:
        if HEADING.match(body):
            continue
        for s in SENT_SPLIT.split(LIST_MARK.sub("", body.strip())):
            s = s.strip()
            if s and HANGUL.search(s):
                out.append((no, s))
    return out


def check_text(text):
    errors, warns = [], []
    lines = prose_lines(text)
    if not lines:
        return errors, warns

    for no, body in lines:
        if not HANGUL.search(body) and not BOLD.search(body):
            continue
        clean = QUOTED.sub(" ", body)  # 남의 말(인용) 안은 안 본다
        for rx, label, fix in HARD:
            if rx.search(clean):
                errors.append((no, label, fix, body.strip()[:90]))
        for rx, label, fix in SOFT:
            target = body if label == "굽은 따옴표" else clean
            if rx.search(target):
                warns.append((no, label, fix, body.strip()[:90]))

    # 15. 굵은 글씨 과다: 한 문단(줄)에 세 군데 이상
    for no, body in lines:
        if len(BOLD.findall(body)) >= 3:
            warns.append((no, "굵은 글씨 과다", "이유 없는 굵게는 푼다 (15)", body.strip()[:90]))

    # 16. 굵은 소제목 목록: "- **이름:** 설명" 꼴이 세 줄 연속
    run = []
    for no, body in lines + [(0, "")]:
        if BOLD_LABEL_ITEM.match(body):
            run.append(no)
        else:
            if len(run) >= 3:
                warns.append((run[0], "굵은 소제목 목록", "항목마다 굵은 이름+콜론. 산문으로 풀거나 이름만 (16)",
                              str(len(run)) + "줄 연속"))
            run = []

    # 29. 소제목을 바로 아래 한 줄이 되풀이
    for i, (no, body) in enumerate(lines):
        h = HEADING.match(body)
        if not h:
            continue
        title = re.sub(r"[^가-힣A-Za-z0-9]", "", h.group(1))
        for no2, nxt in lines[i + 1:i + 3]:
            if not nxt.strip():
                continue
            first = re.sub(r"[^가-힣A-Za-z0-9]", "", nxt.strip()[:40])
            if title and len(title) >= 4 and (title in first or first[:len(title)] == title):
                warns.append((no2, "소제목 되풀이", "제목이 이미 말한 것을 첫 문장이 또 말함. 첫 문장을 뺀다 (29)",
                              nxt.strip()[:90]))
            break

    sents = sentences(lines)

    # 9. "A가 아니라 B" 틀이 문서에 두 번 넘게
    hits = [(no, s) for no, s in sents if NOT_X_BUT_Y.search(s)]
    if len(hits) >= 2:
        for no, s in hits:
            warns.append((no, "A가 아니라 B 반복", "문서당 한 번만. 나머지는 직접 단언으로 (9, im-not-ai C-8)", s[:90]))

    # 10. 세 개 묶음이 문서에 세 번 넘게
    hits = [(no, s) for no, s in sents if TRIPLE.search(s)]
    if len(hits) >= 3:
        for no, s in hits:
            warns.append((no, "세 개 묶음", "뜻에 맞는 개수로. 셋으로 맞추려 억지로 채운 항목을 뺀다 (10)", s[:90]))

    # 11. 같은 첫 어절로 시작하는 문장이 세 번 연속
    prev, streak, start = None, 0, 0
    for no, s in sents + [(0, "")]:
        head = s.split(" ", 1)[0] if s else None
        if head and head == prev:
            streak += 1
        else:
            if streak >= 3:
                warns.append((start, "첫 어절 반복", "'" + str(prev) + "'로 시작하는 문장 " + str(streak) +
                              "개 연속. 합치거나 주어를 바꾼다 (11)", ""))
            prev, streak, start = head, 1, no

    # 31. 짧은 조각 문장이 세 개 넘게 연속
    streak, start = 0, 0
    for no, s in sents + [(0, "")]:
        if s and len(s) <= 12:
            if streak == 0:
                start = no
            streak += 1
        else:
            if streak >= 3:
                warns.append((start, "조각 문장 연속", "짧은 문장 " + str(streak) + "개 연속. 하나면 강조, 줄지으면 연출 (31)", ""))
            streak = 0

    # 7. AI 단어가 한 문단에 세 종류 넘게
    for no, body in lines:
        found = sorted({w for w in AI_WORDS if w in body})
        if len(found) >= 3:
            warns.append((no, "AI 단어 몰림", "·".join(found) + ". 흔한 말로 (7)", body.strip()[:90]))

    # 24. 완곡이 문서에 네 번 넘게
    hedge = re.compile(r"어느\s*정도|다소|경우에\s*따라|일\s*수도\s*있|가능성이\s*있을\s*수|아마도|어쩌면")
    hits = [(no, s) for no, s in sents if hedge.search(s)]
    if len(hits) >= 4:
        for no, s in hits:
            warns.append((no, "완곡 과다", "확신 없는 말이 " + str(len(hits)) + "곳. 근거 있는 곳만 남긴다 (24)", s[:90]))

    errors.sort()
    warns.sort()
    return errors, warns


def files(paths):
    for p in paths:
        if os.path.isfile(p):
            yield p
            continue
        for dirpath, dirnames, filenames in os.walk(p):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
            for f in filenames:
                if f.endswith(EXTS):
                    yield os.path.join(dirpath, f)


def report(name, errors, warns):
    if not errors and not warns:
        return
    print("\n" + name)
    for no, label, fix, line in errors:
        print("  고칠 것  " + str(no) + "행  " + label + " → " + fix)
        if line:
            print("           " + line)
    for no, label, fix, line in warns:
        print("  볼 것    " + str(no) + "행  " + label + " → " + fix)
        if line:
            print("           " + line)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    strict = "--strict" in sys.argv
    if not args:
        print(__doc__)
        return 1

    n_err = n_warn = 0
    if args == ["-"]:
        errors, warns = check_text(sys.stdin.read())
        report("(표준입력)", errors, warns)
        n_err, n_warn = len(errors), len(warns)
    else:
        for path in sorted(files(args)):
            try:
                text = open(path, encoding="utf-8").read()
            except (OSError, UnicodeDecodeError):
                continue
            errors, warns = check_text(text)
            report(path, errors, warns)
            n_err += len(errors)
            n_warn += len(warns)

    if n_err or n_warn:
        print("\n  고칠 것 " + str(n_err) + " · 볼 것 " + str(n_warn) +
              "   (규칙: HUMANIZE-KO.md, 번호는 humanizer 패턴)")
    if n_err or (strict and n_warn):
        return 3
    return 2 if n_warn else 0


if __name__ == "__main__":
    sys.exit(main())
