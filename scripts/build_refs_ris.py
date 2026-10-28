# -*- coding: utf-8 -*-
"""Generate importable reference files (RIS + BibTeX) for the 18 task-book references.

Outputs:
  deliverables/任务书参考文献-v1.ris   -> Zotero: 文件 > 导入 > 从文件导入（或直接拖入窗口）
  deliverables/任务书参考文献-v1.bib   -> LaTeX / Zotero BibTeX 导入
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "deliverables"

# 结构化数据：与 thesis/task-book.md 第七节 GB/T 格式条目一一对应
REFS = [
    dict(key="jimenez2024swebench", ty="CONF", lang="en",
         title="SWE-bench: Can Language Models Resolve Real-World GitHub Issues?",
         authors=["Jimenez, Carlos E.", "Yang, John", "Wettig, Alexander", "Yao, Shunyu",
                  "Narasimhan, Karthik", "Press, Ofir"],
         venue="International Conference on Learning Representations (ICLR 2024)",
         venue_short="ICLR", year=2024, arxiv="2310.06770", pages=None, doi=None),
    dict(key="yang2024sweagent", ty="CONF", lang="en",
         title="SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering",
         authors=["Yang, John", "Jimenez, Carlos E.", "Wettig, Alexander", "Lieret, Kilian",
                  "Yao, Shunyu", "Narasimhan, Karthik", "Press, Ofir"],
         venue="Advances in Neural Information Processing Systems 37 (NeurIPS 2024)",
         venue_short="NeurIPS", year=2024, arxiv="2405.15793", pages=None, doi=None),
    dict(key="wang2025openhands", ty="CONF", lang="en",
         title="OpenHands: An Open Platform for AI Software Developers as Generalist Agents",
         authors=["Wang, Xingyao", "Li, Boxuan", "Song, Yufan", "Xu, Frank F.", "Tang, Xiangru",
                  "Zhuge, Mingchen", "Pan, Jiayi", "Song, Yueqi", "Li, Bowen", "Singh, Jaskirat"],
         venue="International Conference on Learning Representations (ICLR 2025)",
         venue_short="ICLR", year=2025, arxiv="2407.16741", pages=None, doi=None),
    dict(key="wang2024codeact", ty="CONF", lang="en",
         title="Executable Code Actions Elicit Better LLM Agents",
         authors=["Wang, Xingyao", "Chen, Yangyi", "Yuan, Lifan", "Zhang, Yizhe",
                  "Li, Yunzhu", "Peng, Hao", "Ji, Heng"],
         venue="International Conference on Machine Learning (ICML 2024)",
         venue_short="ICML", year=2024, arxiv="2402.01030", pages=None, doi=None),
    dict(key="hong2024metagpt", ty="CONF", lang="en",
         title="MetaGPT: Meta Programming for a Multi-Agent Collaborative Framework",
         authors=["Hong, Sirui", "Zhuge, Mingchen", "Chen, Jonathan", "Zheng, Xiawu",
                  "Cheng, Yuheng", "Zhang, Ceyao", "Wang, Jinlin", "Wang, Zili"],
         venue="International Conference on Learning Representations (ICLR 2024)",
         venue_short="ICLR", year=2024, arxiv="2308.00352", pages=None, doi=None),
    dict(key="qian2024chatdev", ty="CONF", lang="en",
         title="ChatDev: Communicative Agents for Software Development",
         authors=["Qian, Chen", "Liu, Wei", "Liu, Hongzhang", "Chen, Nuo", "Dang, Yufan",
                  "Li, Jiahao", "Yang, Cheng", "Chen, Weize", "Su, Yusheng", "Cong, Xin"],
         venue="Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics",
         venue_short="ACL", year=2024, pages=("15174", "15186"),
         doi="10.18653/v1/2024.acl-long.810", arxiv=None),
    dict(key="kagdi2007survey", ty="JOUR", lang="en",
         title="A Survey and Taxonomy of Approaches for Mining Software Repositories in the Context of Software Evolution",
         authors=["Kagdi, Huzefa", "Collard, Michael L.", "Maletic, Jonathan I."],
         venue="Journal of Software Maintenance and Evolution: Research and Practice",
         year=2007, volume="19", issue="2", pages=("77", "131"), doi="10.1002/smr.344"),
    dict(key="robbes2007change", ty="JOUR", lang="en",
         title="A Change-based Approach to Software Evolution",
         authors=["Robbes, Romain", "Lanza, Michele"],
         venue="Electronic Notes in Theoretical Computer Science",
         year=2007, volume="166", pages=("93", "109"), doi="10.1016/j.entcs.2006.06.015"),
    dict(key="falleri2014gumtree", ty="CONF", lang="en",
         title="Fine-grained and Accurate Source Code Differencing",
         authors=["Falleri, Jean-Rémy", "Morandat, Floréal", "Blanc, Xavier",
                  "Martinez, Matias", "Monperrus, Martin"],
         venue="Proceedings of the 29th ACM/IEEE International Conference on Automated Software Engineering (ASE 2014)",
         venue_short="ASE", year=2014, pages=("313", "324"), doi="10.1145/2642937.2642982"),
    dict(key="grund2021codeshovel", ty="CONF", lang="en",
         title="CodeShovel: Constructing Method-Level Source Code Histories",
         authors=["Grund, Florian", "Chowdhury, Shaiful Alam", "Bradley, Nick C.",
                  "Hall, Braxton", "Holmes, Reid"],
         venue="Proceedings of the 43rd International Conference on Software Engineering (ICSE 2021)",
         venue_short="ICSE", year=2021, pages=("1510", "1522"), doi="10.1109/ICSE43902.2021.00135"),
    dict(key="ko2004whyline", ty="CONF", lang="en",
         title="Designing the Whyline: A Debugging Interface for Asking Questions about Program Behavior",
         authors=["Ko, Andrew J.", "Myers, Brad A."],
         venue="Proceedings of the SIGCHI Conference on Human Factors in Computing Systems (CHI 2004)",
         venue_short="CHI", year=2004, pages=("151", "158"), doi="10.1145/985692.985712"),
    dict(key="cheney2009provenance", ty="JOUR", lang="en",
         title="Provenance in Databases: Why, How, and Where",
         authors=["Cheney, James", "Chiticariu, Laura", "Tan, Wang-Chiew"],
         venue="Foundations and Trends in Databases",
         year=2009, volume="1", issue="4", pages=("379", "474"), doi="10.1561/1900000006"),
    dict(key="pimentel2017noworkflow", ty="JOUR", lang="en",
         title="noWorkflow: A Tool for Collecting, Analyzing, and Managing Provenance from Python Scripts",
         authors=["Pimentel, João Felipe", "Murta, Leonardo", "Braganholo, Vanessa", "Freire, Juliana"],
         venue="Proceedings of the VLDB Endowment",
         year=2017, volume="10", issue="12", pages=("1841", "1844"), doi="10.14778/3137765.3137789"),
    dict(key="parnin2011resumption", ty="JOUR", lang="en",
         title="Resumption Strategies for Interrupted Programming Tasks",
         authors=["Parnin, Chris", "Rugaber, Spencer"],
         venue="Software Quality Journal",
         year=2011, volume="19", issue="1", pages=("5", "34"), doi="10.1007/s11219-010-9104-9"),
    dict(key="otel2026genai", ty="ELEC", lang="en",
         title="Generative AI Semantic Conventions",
         authors=["OpenTelemetry"],
         venue="OpenTelemetry Documentation",
         year=2026, url="https://opentelemetry.io/docs/specs/semconv/gen-ai/", access="2026-10-27"),
    dict(key="langfuse2026observability", ty="ELEC", lang="en",
         title="Observability Overview",
         authors=["Langfuse"],
         venue="Langfuse Documentation",
         year=2026, url="https://langfuse.com/docs/observability/overview", access="2026-10-27"),
    dict(key="zhang2026ragse", ty="JOUR", lang="zh",
         title="检索增强生成在软件工程中的应用综述",
         authors=["张犬俊", "谢杨", "房春荣", "虞圣呈", "赵源", "陈振宇"],
         venue="软件学报", year=2026, volume="37", issue="3", pages=("1316", "1339"),
         doi="10.13328/j.cnki.jos.007567"),
    dict(key="wang2026faultrepro", ty="JOUR", lang="zh",
         title="基于大语言模型的故障复现测试用例生成方法",
         authors=["汪莹", "字千成", "彭鑫", "娄一翎"],
         venue="软件学报", year=2026, volume="37", issue="4", pages=("1690", "1714"),
         doi="10.13328/j.cnki.jos.007474"),
]


def ris_text(refs):
    lines = []
    for r in refs:
        lines.append(f"TY  - {r['ty']}")
        lines.append(f"TI  - {r['title']}")
        for a in r["authors"]:
            lines.append(f"AU  - {a}")
        if r["ty"] == "JOUR":
            lines.append(f"JO  - {r['venue']}")
            lines.append(f"T2  - {r['venue']}")
        elif r["ty"] == "CONF":
            lines.append(f"T2  - {r['venue']}")
        else:
            lines.append(f"T2  - {r['venue']}")
        lines.append(f"PY  - {r['year']}")
        lines.append(f"DA  - {r['year']}")
        if r.get("volume"):
            lines.append(f"VL  - {r['volume']}")
        if r.get("issue"):
            lines.append(f"IS  - {r['issue']}")
        if r.get("pages"):
            sp, ep = r["pages"]
            lines.append(f"SP  - {sp}")
            lines.append(f"EP  - {ep}")
        if r.get("doi"):
            lines.append(f"DO  - {r['doi']}")
        if r.get("arxiv"):
            lines.append(f"UR  - https://arxiv.org/abs/{r['arxiv']}")
            lines.append(f"N1  - arXiv:{r['arxiv']}")
        if r.get("url"):
            lines.append(f"UR  - {r['url']}")
            lines.append(f"Y2  - {r['access']}")
        if r["lang"] == "zh":
            lines.append("LA  - zh-CN")
        lines.append("ER  - ")
        lines.append("")
    return "\n".join(lines)


def bib_text(refs):
    def esc(s):
        return s.replace("&", r"\&").replace("%", r"\%").replace("_", r"\_")

    out = []
    for r in refs:
        kind = "article" if r["ty"] == "JOUR" else ("misc" if r["ty"] == "ELEC" else "inproceedings")
        out.append(f"@{kind}{{{r['key']},")
        out.append(f"  title = {{{esc(r['title'])}}},")
        out.append("  author = {" + " and ".join(esc(a) for a in r["authors"]) + "},")
        if r["ty"] == "JOUR":
            out.append(f"  journal = {{{esc(r['venue'])}}},")
        elif r["ty"] == "CONF":
            out.append(f"  booktitle = {{{esc(r['venue'])}}},")
        else:
            out.append(f"  howpublished = {{{esc(r['venue'])}}},")
        out.append(f"  year = {{{r['year']}}},")
        if r.get("volume"):
            out.append(f"  volume = {{{r['volume']}}},")
        if r.get("issue"):
            out.append(f"  number = {{{r['issue']}}},")
        if r.get("pages"):
            out.append(f"  pages = {{{r['pages'][0]}--{r['pages'][1]}}},")
        if r.get("doi"):
            out.append(f"  doi = {{{r['doi']}}},")
        if r.get("arxiv"):
            out.append(f"  eprint = {{{r['arxiv']}}},")
            out.append("  archivePrefix = {arXiv},")
        if r.get("url"):
            out.append(f"  url = {{{r['url']}}},")
            out.append(f"  urldate = {{{r['access']}}},")
        out.append("}")
        out.append("")
    return "\n".join(out)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    ris = OUT / "任务书参考文献-v1.ris"
    bib = OUT / "任务书参考文献-v1.bib"
    ris.write_text(ris_text(REFS), encoding="utf-8")
    bib.write_text(bib_text(REFS), encoding="utf-8")
    print("refs:", len(REFS))
    print("ris:", ris, ris.stat().st_size, "bytes")
    print("bib:", bib, bib.stat().st_size, "bytes")
