# ai-tell-free-web

웹 화면과 한국어 글에서 "AI가 뽑은 티"를 없애는 규칙 묶음이다.
실제 서비스 화면과 칼럼을 여러 번 갈아엎으며 확정한 것을 정리했다.

## 무슨 문제를 푸나

지시 없이 화면을 뽑으면 언제나 같은 모양이 나온다.

- 크림색 바탕에 흰 카드, 진한 테두리
- 카드마다 왼쪽에 굵은 색 세로바
- 브랜드색으로 칠한 제목
- 이모지가 박힌 알록달록한 알약 배지
- 글자 크기가 두 단계뿐이라 납작한 화면
- "어디서 나갔나", "누가 벌어주나" 같은 물음꼴 카드 제목
- 긴 줄표와 "혁신적인", "지금 바로 시작하세요"

글도 마찬가지다. "단순한 도구가 아니라 사고방식의 변화", "핵심은", "전문가들은",
"도움이 되셨길 바랍니다", 그리고 억지로 셋을 맞춘 나열이 어디서나 나온다.

여기 시각 규칙 9개와 뼈대 9종, 화면 문구 표, 글 고치는 35패턴, 검사 도구 2개가 그 기본값을 끊는다.

## Claude Code에서 쓰기

폴더째 스킬 자리에 넣으면 끝이다.

```bash
git clone https://github.com/wnstjd878/ai-tell-free-web.git ~/.claude/skills/ai-tell-free-web
```

Windows면 `C:\Users\<이름>\.claude\skills\ai-tell-free-web` 이다.
넣고 나면 화면·목업·랜딩·대시보드를 만들 때, 그리고 "이 글 AI 티 없애줘"라고 할 때 Claude가 알아서 이 규칙을 읽는다.
직접 부르려면 `/ai-tell-free-web` 이라고 치면 된다.

갱신은 `git pull` 이다.

## Claude Code를 안 쓴다면

그냥 문서 묶음이다. `SKILL.md` 를 먼저 읽고 순서대로 따라가면 된다.
Cursor나 다른 도구를 쓴다면 `references/VISUAL-RULES.md` 상단의 요약 9줄을
프롬프트에 그대로 붙이는 것만으로도 대부분 걸러진다. 글은 `references/HUMANIZE-KO.md` 를 통째로 지시문에 넣는다.

검사 도구 둘은 파이썬 3 만 있으면 어디서나 돈다. 외부 패키지가 없다.

## 무엇이 들어 있나

| 파일 | 내용 |
|---|---|
| `SKILL.md` | 순서. 톤 정하기 → 뼈대 고르기 → 9규칙대로 그리기 → 점검. 글은 맨 아래 절 |
| `references/DESIGN-COPY.md` | 톤 후보 9종, 금지 폰트·레이아웃·어휘의 원본 |
| `references/SKELETONS.md` | 뼈대 9종 고르는 표와 갈리는 6가지 축 |
| `references/SKELETONS.html` | **브라우저로 여는 살아 있는 견본.** 9종이 같은 내용으로 나란히 렌더링된다 |
| `references/VISUAL-RULES.md` | AI 기본값을 끊는 시각 규칙 9개 + 자가 점검 7개 |
| `references/WRITING.md` | 화면에 나가는 한국어. 고칠 것 표와 적용 범위 |
| `references/CARD-TITLES.md` | 카드·표·그래프 제목 짓는 법. 물음꼴 짝 표 10줄 |
| `references/HUMANIZE-KO.md` | 글을 사람이 쓴 것처럼 고치는 절차와 35패턴. 한국어 전·후 예문 |
| `tools/screen_copy.py` | 소스에서 화면 문구만 훑어 기호·상투어·물음꼴 제목·대화창 잔여·반박 틀을 잡는다 |
| `tools/humanize_check.py` | 글 파일(.md .txt)이나 표준입력을 훑어 35패턴 중 기계로 잡히는 것을 줄 번호와 함께 준다 |

## 먼저 볼 것 하나

`references/SKELETONS.html` 을 브라우저로 연다. 같은 내용이 9가지 판으로 그려져 있다.
글로 설명을 읽는 것보다 이걸 한 번 보는 게 빠르다.

## 글 고치기

`references/HUMANIZE-KO.md` 는 [blader/humanizer](https://github.com/blader/humanizer) (MIT) 의
절차와 35패턴을 한국어에 맞게 옮긴 것이다. 원본은 위키백과의
[Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) 에서 왔다.
패턴 번호를 원본과 같게 두어 서로 대조할 수 있다.

원본과 다른 점은 셋이다.

1. 예문을 전부 한국어 사업·마케팅 글로 바꿨다. 영어에만 있는 패턴(제목 대문자, 붙임표 낱말 짝)은
   한국어에서 같은 자리를 차지하는 버릇(콜론 부제, 한자어 명사화)으로 바꿨다.
2. 한국어 문법 층은 새로 쓰지 않았다. 번역투, 이중 피동, "A가 아니라 B" 대구, 연결어미 뒤 쉼표는
   [im-not-ai](https://github.com/epoko77-ai/im-not-ai) (MIT, 70패턴) 가 이미 정리했으니 겹치는
   자리마다 그쪽 번호를 적어 두었다. 변경률 가드(30% 경고, 50% 중단)도 그쪽에서 가져왔다.
3. 기계 검사 도구를 붙였다. `tools/humanize_check.py` 가 35패턴 중 낱말이나 틀로 잡히는 것을
   줄 번호와 패턴 번호로 준다. 고치지는 않는다. 고치는 건 규칙을 읽은 모델이 한다.

```bash
python3 tools/humanize_check.py 칼럼.md
python3 tools/humanize_check.py - < 알림문안.txt
```

진단만 따로 하려면 [yoonmoon](https://github.com/amondnet/yoonmoon) (MIT) 도 있다. 진단과 윤문이
분리돼 있어 검사 용도에 맞다.

## 스택

Next.js 15 + Supabase + Vercel 기준으로 쓰던 것이지만, 시각 규칙과 문구 규칙은
스택과 무관하다. `tools/screen_copy.py` 만 `.tsx .ts .jsx .js` 를 훑는다.

## 라이선스

MIT. `references/HUMANIZE-KO.md` 는 blader/humanizer (MIT) 를 바탕으로 했다.
