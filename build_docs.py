"""Make report and poster PDF using generated benchmark data. Requires reportlab."""
import csv
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, KeepTogether
from reportlab.pdfgen import canvas

BASE=Path(__file__).parent
rows=list(csv.DictReader((BASE/'benchmark_results.csv').open()))
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='ReportTitleCustom', parent=styles['Title'], fontName='Helvetica-Bold', fontSize=17, leading=20, spaceAfter=12, textColor=colors.HexColor('#15314C')))
styles.add(ParagraphStyle(name='ReportHCustom', parent=styles['Heading2'], fontSize=11.5, leading=14, spaceBefore=10, spaceAfter=5, textColor=colors.HexColor('#15314C')))
styles.add(ParagraphStyle(name='BodyCustom', parent=styles['BodyText'], fontSize=9.8, leading=14, spaceAfter=7))
styles.add(ParagraphStyle(name='SmallCustom', parent=styles['BodyText'], fontSize=8.6, leading=12, spaceAfter=6))
styles.add(ParagraphStyle(name='TinyCustom', parent=styles['BodyText'], fontSize=8, leading=10, spaceAfter=4))

def P(s, style='BodyCustom'):
    return Paragraph(s,styles[style])

def H(s):
    return P(s,'ReportHCustom')

def footer(c,doc):
    c.setFont('Helvetica',8)
    c.setFillColor(colors.grey)
    c.drawString(44, 27,'MATH 300 | Finding Shortest Paths, Old and New')
    c.drawRightString(570,27,f'Page {doc.page}')

pdf=SimpleDocTemplate(str(BASE/'Project_2_Report.pdf'), pagesize=(612,792), rightMargin=44,leftMargin=44,topMargin=39,bottomMargin=42, title='Project 2: Finding Shortest Paths, Old and New')
story=[]
story += [P('Finding Shortest Paths, Old and New','ReportTitleCustom'),P('<b>MATH 300 - Mathematical Computing | Project 2 | November 20, 2026</b>','SmallCustom'),P('<b>Author(s):</b> [INSERT ACTUAL GROUP MEMBERS] &nbsp;&nbsp; <b>Repository:</b> [INSERT GITHUB LINK]','SmallCustom')]
story += [H('Abstract'),P('We implemented two methods for directed single-source shortest paths with nonnegative edge weights: heap-based Dijkstra and an educational adaptation of the bounded multi-source shortest path (BMSSP) method from Duan et al. (2025). We validated computed distances against hand-solvable graphs and systematically compared both outputs on randomized graphs. Median timings on sparse graphs of 50 to 1,600 vertices showed the adapted BMSSP implementation was approximately 4.9–5.9 times slower than heap-based Dijkstra in our Python experiments. This result concerns our simplified implementation, not the theoretical method described in the paper.')]
story += [H('1. Question and mathematical background'),P('Given a directed weighted graph G=(V,E), a source vertex s, and nonnegative edge weights w(u,v), the single-source shortest path problem is to compute d(v), the smallest possible total edge weight of any route from s to vertex v. Unreachable vertices have distance infinity. For example, with edges 0→1 (weight 4), 0→2 (1), 2→1 (2), 1→3 (1), and 2→3 (5), the distances from 0 are (0,3,1,4).')]
story += [P('Dijkstra selects the currently nearest unsettled vertex from a priority queue and relaxes its outgoing edges. The standard binary-heap implementation typically takes O((m+n) log n) time. In contrast, Duan et al. [2] prove O(m log<super>2/3</super> n) time using a recursive bounded multi-source scheme and a specialized data structure, under the assumptions of their model. The central idea is to avoid sorting all tentative distances globally by reducing the frontier to strategically chosen pivots.')]
story += [H('2. Implementation'),P('All code was written in Python. A graph is a dictionary keyed by vertex labels, with lists of (destination, weight) pairs. The seeded generator produces m distinct directed edges and randomly sampled positive real-valued weights. To keep timing graphs reachable from node 0, it first creates a directed spanning structure from lower-numbered to higher-numbered vertices and then adds random edges.')]
story += [P('For Dijkstra, the built-in heapq module holds (tentative distance, vertex) pairs. Outdated heap entries are discarded. For the second method, the code follows the high-level pseudocode of FindPivots (Algorithm 1), BaseCase (Algorithm 2), and recursive BMSSP (Algorithm 3) from [2]. FindPivots performs bounded rounds of edge relaxation, BaseCase runs a limited heap search, and BMSSP recursively groups work according to distance boundaries. The specialized Lemma 3.3 data structure is replaced with a sorted dictionary for Pull, Insert and BatchPrepend; a predecessor-based forest replaces the paper’s tie-order construction. The constant-degree transformation is also omitted.')]
story += [P('<b>Interpretation:</b> the second implementation is an educational approximation of the published BMSSP procedure; it is not an exact, formally verified reproduction and should not be claimed to retain the paper’s runtime guarantee.')]
story += [PageBreak(),H('3. Verification and experimental setup'),P('We checked the hand-worked four-vertex graph, a disconnected graph, and a singleton graph; verified that invalid negative-weight edges are rejected; and ran the same input graphs through both algorithms. Randomized unit tests included 60 graphs (15 seeds each at n=5, 10, 20, 40). A supplementary stress check ran 540 additional graph configurations across sizes 5–200, three edge densities and 30 seeds. All generated comparisons tested matched shortest-path distances within floating-point tolerance.')]
story += [P('For runtime evaluation, we generated sparse directed graphs with m=3n edges at n=50, 100, 200, 400, 800, and 1,600. Five seeds were tested for each size. The two implementations each ran on the same graph, and the median wall-clock runtime in milliseconds was recorded using time.perf_counter. Timings reflect a single execution environment and will vary with hardware, load and Python version; no theoretical complexity was inferred from these measurements.')]
story += [H('4. Measured results')]
headers=['Vertices','Edges','Dijkstra (ms)','BMSSP adapted (ms)','Ratio']
data=[headers]+[[r['vertices'],r['edges'],r['dijkstra_ms'],r['bmssp_ms'],f"{r['ratio']}x"] for r in rows]
t=Table(data,colWidths=[70,65,118,151,74],rowHeights=23)
t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#173A56')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTNAME',(0,1),(-1,-1),'Helvetica'),('FONTSIZE',(0,0),(-1,-1),8.5),('GRID',(0,0),(-1,-1),.35,colors.HexColor('#B9C4CE')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#EEF4F8')]),('ALIGN',(0,0),(-1,-1),'CENTER'),('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
story += [t, Spacer(1,10),P('<b>Table 1.</b> Five-seed median measured runtime. Ratio = BMSSP adaptation time divided by Dijkstra time.','SmallCustom')]
story += [Image(str(BASE/'figures/runtime.png'),width=490,height=219),P('<b>Figure 1.</b> Median wall-clock time for increasing sparse graph sizes. Horizontal axis: vertices; vertical axis: time in milliseconds.','SmallCustom')]
story += [PageBreak(),H('5. Discussion and limitations'),P('All tested graphs returned matching distances, providing useful empirical checks of the core mathematical task. Dijkstra was consistently faster on the measured graph sizes. In the largest test, with 1,600 vertices and 4,800 edges, Dijkstra took '+rows[-1]['dijkstra_ms']+' ms versus '+rows[-1]['bmssp_ms']+' ms for our BMSSP adaptation. Across graph sizes, the adaptation took roughly '+str(min(float(r['ratio']) for r in rows))+'–'+str(max(float(r['ratio']) for r in rows))+' times as long.')]
story += [P('A result that is faster in asymptotic analysis need not be faster at practical sizes. This implementation intentionally substitutes full sorting of frontier entries for the paper’s special sublinear-overhead blocks, performs recursive bookkeeping in Python, and does not apply the constant-degree reduction. These choices introduce overhead and remove the conditions supporting the authors’ advertised asymptotic bound. A more faithful data-structure implementation and much larger sparse inputs would be necessary for a meaningful experimental evaluation of the paper’s optimality claim. Our measured result must not be interpreted as evidence against the original proof.')]
story += [Image(str(BASE/'figures/ratio.png'),width=480,height=204),P('<b>Figure 2.</b> Ratio of median BMSSP-adaptation runtime to Dijkstra runtime; values above 1 mean Dijkstra is faster.','SmallCustom')]
story += [H('6. Conclusion'),P('The two implementations agreed on all tested shortest distances. For our chosen graph sizes and simplified Python code, Dijkstra was faster; the experiment illustrates the distinction between elegant asymptotic bounds and the overhead of a practical implementation. The code and seeded tests in the accompanying GitHub repository make this result reproducible.')]
story += [PageBreak(),H('References'),P('[1] E. W. Dijkstra, “A note on two problems in connexion with graphs,” <i>Numerische Mathematik</i> 1, pp. 269–271, 1959. https://doi.org/10.1007/BF01386390','SmallCustom'),P('[2] R. Duan, J. Mao, X. Mao, X. Shu, and L. Yin, “Breaking the Sorting Barrier for Directed Single-Source Shortest Paths,” arXiv:2504.17033v2, 2025. https://arxiv.org/abs/2504.17033','SmallCustom'),P('[3] Python Software Foundation, “heapq — Heap queue algorithm,” Python 3 documentation. https://docs.python.org/3/library/heapq.html','SmallCustom')]
story += [H('AI-use statement'),P('Generative AI (OpenAI ChatGPT) assisted with design, Python implementation, debugging, tests, figures, quantitative analysis and drafting of this report and poster. The reported data come from executing the included code. Human author(s) should review, reproduce and understand all work before submission. This statement should be revised if the final project differs.')]
story += [H('Author-contributions statement - COMPLETE BEFORE SUBMITTING'),P('<b>[Member 1 name]:</b> [Specify work on code / testing / experiments / report / poster, approximate percent in each area, and leadership.]'),P('<b>[Member 2 name]:</b> [Specify actual contributions, approximate percentages, and leadership.]'),P('<b>[Member 3 if applicable]:</b> [Specify actual contributions.]'),P('The author names and contribution percentages cannot be inferred from these materials. Fill in accurately so the report and Git history reflect actual group work.')]
story += [H('Reproducibility and scope'),P('Run <font face="Courier">python -m unittest -v</font> and <font face="Courier">python benchmark.py</font> in the repository. The latter regenerates the CSV and two figures. Python 3.10+ is required; matplotlib is required only for plots. The original paper’s specialized data structure and graph transformation are not implemented.')]
pdf.build(story, onFirstPage=footer, onLaterPages=footer)

poster_path=BASE/'Final_Project_Poster.pdf'
c=canvas.Canvas(str(poster_path),pagesize=(36*inch,18*inch))
W,H=36*inch,18*inch
navy=colors.HexColor('#173A56'); pale=colors.HexColor('#F0F5FA')
c.setFillColor(pale);c.rect(0,0,W,H,fill=1,stroke=0)
c.setFillColor(navy);c.rect(0,H-210,W,210,fill=1,stroke=0)
c.setFillColor(colors.white);c.setFont('Helvetica-Bold',64);c.drawString(75,H-112,'FINDING SHORTEST PATHS, OLD AND NEW')
c.setFont('Helvetica',30);c.drawString(78,H-170,'MATH 300  |  Fall 2026  |  [INSERT GROUP MEMBERS]')

def txt(x,y,lines,size=23,leading=33,color=navy):
 c.setFillColor(color);c.setFont('Helvetica',size)
 for line in lines:
  c.drawString(x,y,line);y-=leading

def head(x,y,s):
 c.setFillColor(navy);c.setFont('Helvetica-Bold',37);c.drawString(x,y,s)
head(85,H-285,'THE QUESTION')
txt(85,H-330,['How do we find the lowest-weight routes from one', 'starting vertex to every other vertex?','Graphs have directed edges and nonnegative weights.'])
head(85,H-505,'TWO ALGORITHMS')
txt(85,H-550,['Dijkstra: settles nearest vertex with a binary heap.', 'BMSSP: bounded searches, pivots and recursion.', 'Our BMSSP uses a sorted frontier, not the paper\'s', 'specialized structure. Therefore the published speed', 'bound does not apply to our adaptation.'])
head(85,H-810,'VALIDATION')
txt(85,H-855,['Known graph: (0, 3, 1, 4) from source 0.', 'Random tests: all compared distances matched.', '540 extra stress comparisons also passed.', 'Disconnected vertices have infinite distance.'])
head(1380,H-285,'MEASURED RUNTIME')
c.drawImage(str(BASE/'figures/runtime.png'),1350,H-780,width=1120,height=510,mask='auto')
head(1380,H-855,'TAKEAWAYS')
txt(1380,H-902,['Sparse graphs, m = 3n; five random seeds per size.', 'Dijkstra was 4.9-5.9x faster in our Python tests.', 'Theoretical improvement does not guarantee practical', 'speedup with a simplified implementation.'],size=22)
c.setFillColor(navy);c.rect(0,0,W,133,stroke=0,fill=1)
c.setFillColor(colors.white);c.setFont('Helvetica',17)
c.drawString(65,90,'References: Dijkstra (1959); Duan et al. (2025), arXiv:2504.17033; Python heapq documentation.')
c.drawString(65,58,'AI-assisted code, experiments, figures and drafting. [INSERT GITHUB LINK]  |  Confirm required poster dimensions with instructor.')
c.showPage();c.save()
print('Created report and poster')
