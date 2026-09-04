# ai-tell-free-web

웹 화면을 AI에게 시켰을 때 나오는 "AI가 뽑은 티"를 없애는 규칙 묶음이다.
실제 서비스 화면을 여러 번 갈아엎으며 확정한 것을 정리했다.

## 무슨 문제를 푸나

지시 없이 화면을 뽑으면 언제나 같은 모양이 나온다.

- 크림색 바탕에 흰 카드, 진한 테두리
- 카드마다 왼쪽에 굵은 색 세로바
- 브랜드색으로 칠한 제목
- 이모지가 박힌 알록달록한 알약 배지
- 글자 크기가 두 단계뿐이라 납작한 화면
- "어디서 나갔나", "누가 벌어주나" 같은 물음꼴 카드 제목
- 긴 줄표와 "혁신적인", "지금 바로 시작하세요"

여기 규칙 9개와 뼈대 9종, 문구 표, 검사 도구가 그 기본값을 끊는다.

## Claude Code에서 쓰기

폴더째 스킬 자리에 넣으면 끝이다.

```bash
git clone https://github.com/wnstjd878/ai-tell-free-web.git ~/.claude/skills/ai-tell-free-web
```

Windows면 `C:\Users\<이름>\.claude\skills\ai-tell-free-web` 이다.
넣고 나면 화면·목업·랜딩·대시보드를 만들 때 Claude가 알아서 이 규칙을 읽는다.
직접 부르려면 `/ai-tell-free-web` 이라고 치면 된다.

갱신은 `git pull` 이다.

## Claude Code를 안 쓴다면

그냥 문서 묶음이다. `SKILL.md` 를 먼저 읽고 순서대로 따라가면 된다.
Cursor나 다른 도구를 쓴다면 `references/VISUAL-RULES.md` 상단의 요약 9줄을
프롬프트에 그대로 붙이는 것만으로도 대부분 걸러진다.

## 무엇이 들어 있나

| 파일 | 내용 |
|---|---|
| `SKILL.md` | 순서. 톤 정하기 → 뼈대 고르기 → 9규칙대로 그리기 → 점검 |
| `references/DESIGN-COPY.md` | 톤 후보 9종, 금지 폰트·레이아웃·어휘의 원본 |
| `references/SKELETONS.md` | 뼈대 9종 고르는 표와 갈리는 6가지 축 |
| `references/SKELETONS.html` | **브라우저로 여는 살아 있는 견본.** 9종이 같은 내용으로 나란히 렌더링된다 |
| `references/VISUAL-RULES.md` | AI 기본값을 끊는 시각 규칙 9개 + 자가 점검 7개 |
| `references/WRITING.md` | 화면에 나가는 한국어. 고칠 것 9줄과 적용 범위 |
| `references/CARD-TITLES.md` | 카드·표·그래프 제목 짓는 법. 물음꼴 짝 표 10줄 |
| `tools/screen_copy.py` | 소스에서 화면 문구만 훑어 기호·상투어·물음꼴 제목을 잡는다 |

## 먼저 볼 것 하나

`references/SKELETONS.html` 을 브라우저로 연다. 같은 내용이 9가지 판으로 그려져 있다.
글로 설명을 읽는 것보다 이걸 한 번 보는 게 빠르다.

## 한국어 문장 자체의 AI 티

번역투, 이중 피동, "A가 아니라 B" 대구 반복 같은 **문장 층위**는 여기서 다루지 않는다.
이미 잘 정리된 것이 있어서 그걸 가리킨다.

- [im-not-ai](https://github.com/epoko77-ai/im-not-ai) (MIT) — 10개 분류 70개 패턴
- [yoonmoon](https://github.com/amondnet/yoonmoon) (MIT) — 진단과 윤문이 분리돼 있어 검사에 맞다

이 묶음은 **화면**을 담당하고 저쪽이 **문장**을 담당한다.

## 스택

Next.js 15 + Supabase + Vercel 기준으로 쓰던 것이지만, 시각 규칙과 문구 규칙은
스택과 무관하다. `tools/screen_copy.py` 만 `.tsx .ts .jsx .js` 를 훑는다.

## 라이선스

MIT.
