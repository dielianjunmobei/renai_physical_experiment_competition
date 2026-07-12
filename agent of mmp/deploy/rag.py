import os
import re

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_PARENT_DIR = os.path.dirname(_BASE_DIR)

_KNOWLEDGE_FILES = [
    os.path.join(_PARENT_DIR, "KNOWLEDGE_BASE.md"),
    os.path.join(_PARENT_DIR, "RESOURCE_KNOWLEDGE.md"),
    os.path.join(_PARENT_DIR, "REASONING_RULES.md"),
    os.path.join(_PARENT_DIR, "EXAMPLES.md"),
]

CHAPTER_KEYWORDS = {
    "第1章": ["解析函数", "C-R", "柯西-黎曼", "调和函数", "初等函数", "复变函数", "可导", "解析性", "共轭调和", "指数函数", "三角函数", "对数函数", "多值", "实解析", "复解析", "全纯", "holomorphic", "C^∞"],
    "第2章": ["柯西定理", "积分公式", "复积分", "高阶导数", "Morera", "路径无关", "闭路积分", "原函数"],
    "第3章": ["泰勒级数", "洛朗级数", "幂级数", "收敛半径", "收敛圆", "孤立奇点", "展开"],
    "第4章": ["留数", "Res", "奇点分类", "极点", "本性奇点", "可去奇点", "实积分", "Jordan引理", "围道"],
    "第5章": ["傅里叶变换", "频谱", "δ函数", "卷积", "Parseval", "频域", "时域"],
    "第6章": ["拉普拉斯变换", "反演", "像函数", "传递函数", "ODE求解", "初值定理", "终值定理"],
    "第7章": ["定解问题", "波动方程", "热传导", "拉普拉斯方程", "达朗贝尔", "特征线", "双曲", "抛物", "椭圆", "初始条件", "边界条件"],
    "第8章": ["分离变量", "分离变数", "驻波", "本征值", "叠加原理", "弦振动", "热传导方程"],
    "第9章": ["S-L", "Sturm-Liouville", "本征函数", "正交性", "广义傅里叶", "级数解法", "Frobenius"],
    "第10章": ["勒让德", "球函数", "球谐函数", "Legendre", "连带勒让德", "Rodrigue"],
    "第11章": ["贝塞尔", "柱函数", "Bessel", "诺依曼", "汉克尔", "圆膜", "递推"],
    "第12章": ["格林函数", "Green", "点源", "电像法", "本征函数展开", "δ函数"],
    "第13章": ["积分变换法", "热核", "扩散", "傅里叶变换解PDE", "拉普拉斯变换解PDE"],
    "第14章": ["保角变换", "保角映射", "共形映射", "分式线性", "上半平面", "单位圆"],
    "第15章": ["孤立子", "soliton", "KdV", "混沌", "非线性", "Lorenz"],
}


def _load_and_chunk():
    chunks = []
    for fpath in _KNOWLEDGE_FILES:
        if not os.path.exists(fpath):
            continue
        with open(fpath, "r", encoding="utf-8") as f:
            text = f.read()
        sections = re.split(r'\n(?=##+ )', text)
        for sec in sections:
            sec = sec.strip()
            if len(sec) < 20:
                continue
            header = sec.split('\n')[0].lstrip('#').strip()
            chunks.append({"header": header, "content": sec, "source": os.path.basename(fpath)})
    return chunks


_CHUNKS = None


def _get_chunks():
    global _CHUNKS
    if _CHUNKS is None:
        _CHUNKS = _load_and_chunk()
    return _CHUNKS


def detect_chapters(question: str) -> list:
    question_lower = question.lower()
    scores = {}
    for chapter, keywords in CHAPTER_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw.lower() in question_lower)
        if score > 0:
            scores[chapter] = score
    ranked = sorted(scores.items(), key=lambda x: -x[1])
    return [ch for ch, _ in ranked[:3]]


def retrieve(question: str, top_k: int = 5) -> str:
    chunks = _get_chunks()
    if not chunks:
        return ""

    question_lower = question.lower()
    matched_chapters = detect_chapters(question)

    scored = []
    for chunk in chunks:
        score = 0
        header_lower = chunk["header"].lower()
        content_lower = chunk["content"].lower()

        for ch in matched_chapters:
            if ch in chunk["header"] or ch in chunk["content"][:200]:
                score += 10

        words = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+', question_lower)
        for w in words:
            if len(w) < 2:
                continue
            if w in header_lower:
                score += 5
            count = content_lower.count(w)
            score += min(count, 3)

        if score > 0:
            scored.append((score, chunk))

    scored.sort(key=lambda x: -x[0])
    top = scored[:top_k]

    if not top:
        return ""

    result_parts = []
    for _, chunk in top:
        content = chunk["content"]
        if len(content) > 800:
            content = content[:800] + "\n..."
        result_parts.append(f"### {chunk['header']}\n{content}")

    return "\n\n---\n\n".join(result_parts)


TOPIC_TO_VIZ = {
    "第1章": {
        "static": ["z_squared_mapping", "harmonic_z2", "complex_exp", "complex_sine", "cr_geometry", "conformal_angle"],
        "anim": ["anim_cr_grad", "anim_mapping", "anim_sine", "anim_log_branches"],
    },
    "第2章": {
        "static": ["cauchy_path", "cauchy_integral_formula"],
        "anim": ["anim_path_def", "anim_cauchy_formula"],
    },
    "第3章": {
        "static": ["taylor_convergence", "laurent_annulus"],
        "anim": ["anim_taylor", "anim_laurent"],
    },
    "第4章": {
        "static": ["residue_contour"],
        "anim": ["anim_residue"],
    },
    "第5章": {
        "static": ["fourier_spectrum"],
        "anim": ["anim_fourier_sq", "anim_fourier_dual"],
    },
    "第6章": {
        "static": ["laplace_poles"],
        "anim": ["anim_laplace"],
    },
    "第7章": {
        "static": ["pde_classification", "dalembert_formula"],
        "anim": ["anim_dalembert", "anim_pde_types"],
    },
    "第8章": {
        "static": ["separation_modes", "heat_evolution"],
        "anim": ["anim_separation", "anim_heat"],
    },
    "第9章": {
        "static": ["sl_eigenfunctions", "sl_orthogonality"],
        "anim": ["anim_sl_overlay", "anim_sl_ortho"],
    },
    "第10章": {
        "static": ["legendre_polynomials", "spherical_harmonics"],
        "anim": ["anim_legendre", "anim_spherical"],
    },
    "第11章": {
        "static": ["bessel_functions", "bessel_zeros"],
        "anim": ["anim_bessel", "anim_drum"],
    },
    "第12章": {
        "static": ["green_function_1d", "green_superposition"],
        "anim": ["anim_green"],
    },
    "第13章": {
        "static": ["heat_kernel_diffusion"],
        "anim": ["anim_kernel", "anim_fourier_pde"],
    },
    "第14章": {
        "static": ["conformal_examples"],
        "anim": ["anim_conformal"],
    },
    "第15章": {
        "static": ["kdv_soliton"],
        "anim": ["anim_kdv", "anim_lorenz"],
    },
}


def get_viz_recommendations(question: str) -> dict:
    chapters = detect_chapters(question)
    recs = {"static": [], "anim": []}
    for ch in chapters:
        if ch in TOPIC_TO_VIZ:
            recs["static"].extend(TOPIC_TO_VIZ[ch]["static"][:2])
            recs["anim"].extend(TOPIC_TO_VIZ[ch]["anim"][:1])
    recs["static"] = list(dict.fromkeys(recs["static"]))[:3]
    recs["anim"] = list(dict.fromkeys(recs["anim"]))[:2]
    return recs
