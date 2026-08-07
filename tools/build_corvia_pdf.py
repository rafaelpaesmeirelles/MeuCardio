from __future__ import annotations

from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, Color, white
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CAP = ROOT / "capturas_tela"
OUT = ROOT / "artifacts" / "Corvia_Apresentacao_Institucional.pdf"
OUT.parent.mkdir(parents=True, exist_ok=True)

W, H = 13.333 * inch, 7.5 * inch

NAVY = HexColor("#10293B")
NAVY2 = HexColor("#17384F")
TEAL = HexColor("#1A8E8A")
TEAL2 = HexColor("#0F6F6C")
MINT = HexColor("#DDF3EF")
BLUE = HexColor("#2D6F9F")
SKY = HexColor("#E8F2F7")
INK = HexColor("#17252F")
MUTED = HexColor("#657680")
LIGHT = HexColor("#F4F7F8")
LINE = HexColor("#D9E2E6")
WHITE = white
RED = HexColor("#B94B4B")
AMBER = HexColor("#B7791F")
GREEN = HexColor("#2F7A59")

TITLE = ParagraphStyle(
    "title", fontName="Helvetica-Bold", fontSize=28, leading=31,
    textColor=INK, alignment=TA_LEFT, spaceAfter=0,
)
TITLE_WHITE = ParagraphStyle(
    "title_white", fontName="Helvetica-Bold", fontSize=30, leading=33,
    textColor=WHITE, alignment=TA_LEFT,
)
SUBTITLE = ParagraphStyle(
    "subtitle", fontName="Helvetica", fontSize=13, leading=17,
    textColor=MUTED, alignment=TA_LEFT,
)
BODY = ParagraphStyle(
    "body", fontName="Helvetica", fontSize=10.5, leading=14,
    textColor=INK, alignment=TA_LEFT,
)
BODY_WHITE = ParagraphStyle(
    "body_white", fontName="Helvetica", fontSize=10.5, leading=14,
    textColor=HexColor("#DDE8EE"), alignment=TA_LEFT,
)
SMALL = ParagraphStyle(
    "small", fontName="Helvetica", fontSize=7.8, leading=10.2,
    textColor=MUTED, alignment=TA_LEFT,
)
SMALL_WHITE = ParagraphStyle(
    "smallw", fontName="Helvetica", fontSize=7.8, leading=10.2,
    textColor=HexColor("#BFD1DC"), alignment=TA_LEFT,
)
CARD_HEAD = ParagraphStyle(
    "cardh", fontName="Helvetica-Bold", fontSize=12.2, leading=14.5,
    textColor=INK, alignment=TA_LEFT,
)
CARD_BODY = ParagraphStyle(
    "cardb", fontName="Helvetica", fontSize=9.1, leading=12.3,
    textColor=MUTED, alignment=TA_LEFT,
)


def para(c: canvas.Canvas, text: str, x: float, y_top: float, w: float, h: float, style=BODY):
    p = Paragraph(text, style)
    _, ph = p.wrap(w, h)
    p.drawOn(c, x, y_top - ph)
    return ph


def rounded_card(c, x, y, w, h, fill=WHITE, stroke=LINE, radius=10, shadow=True):
    if shadow:
        c.saveState()
        try:
            c.setFillAlpha(0.10)
        except Exception:
            pass
        c.setFillColor(HexColor("#000000"))
        c.roundRect(x+3, y-3, w, h, radius, fill=1, stroke=0)
        c.restoreState()
    c.setFillColor(fill)
    c.setStrokeColor(stroke)
    c.setLineWidth(0.7)
    c.roundRect(x, y, w, h, radius, fill=1, stroke=1)


def image_fit(c, path: Path, x, y, w, h, crop=False, border=True, bg=WHITE):
    if not path.exists():
        c.setFillColor(LIGHT); c.rect(x, y, w, h, fill=1, stroke=0)
        para(c, f"Captura indisponível: {path.name}", x+12, y+h/2+10, w-24, 40, SMALL)
        return
    with Image.open(path) as im:
        iw, ih = im.size
    scale = max(w/iw, h/ih) if crop else min(w/iw, h/ih)
    dw, dh = iw*scale, ih*scale
    dx, dy = x+(w-dw)/2, y+(h-dh)/2
    c.setFillColor(bg); c.rect(x, y, w, h, fill=1, stroke=0)
    c.saveState()
    p = c.beginPath(); p.rect(x, y, w, h); c.clipPath(p, stroke=0, fill=0)
    c.drawImage(ImageReader(str(path)), dx, dy, dw, dh, preserveAspectRatio=True, mask='auto')
    c.restoreState()
    if border:
        c.setStrokeColor(LINE); c.setLineWidth(0.8); c.rect(x, y, w, h, fill=0, stroke=1)


def pill(c, text, x, y, fill=MINT, color=TEAL2, w=None):
    if w is None:
        w = max(62, 7.2*len(text)+18)
    h = 20
    c.setFillColor(fill); c.roundRect(x, y, w, h, h/2, fill=1, stroke=0)
    c.setFillColor(color); c.setFont("Helvetica-Bold", 8.2)
    c.drawCentredString(x+w/2, y+6.2, text)
    return w


def footer(c, page_no, dark=False):
    color = HexColor("#AFC2CD") if dark else HexColor("#8A99A1")
    c.setFont("Helvetica", 7.2); c.setFillColor(color)
    c.drawString(0.62*inch, 0.28*inch, "Corvia - apoio à decisão clínica em Cardiologia")
    c.drawRightString(W-0.62*inch, 0.28*inch, f"{page_no:02d}")


def section_header(c, kicker, title, subtitle=None, dark=False):
    if dark:
        c.setFillColor(WHITE); tc = WHITE
        sub = BODY_WHITE
    else:
        tc = INK; sub = SUBTITLE
    c.setFillColor(TEAL if not dark else HexColor("#66D5CA"))
    c.setFont("Helvetica-Bold", 8.2); c.drawString(0.62*inch, H-0.55*inch, kicker.upper())
    style = TITLE_WHITE if dark else TITLE
    para(c, title, 0.62*inch, H-0.76*inch, 7.0*inch, 0.7*inch, style)
    if subtitle:
        para(c, subtitle, 0.62*inch, H-1.43*inch, 8.7*inch, 0.52*inch, sub)


def draw_feature_card(c, x, y, w, h, num, title, body, accent=TEAL):
    rounded_card(c, x, y, w, h, fill=WHITE, stroke=LINE, radius=10, shadow=False)
    c.setFillColor(accent); c.circle(x+24, y+h-25, 12, fill=1, stroke=0)
    c.setFillColor(WHITE); c.setFont("Helvetica-Bold", 8.5); c.drawCentredString(x+24, y+h-28, str(num))
    para(c, title, x+46, y+h-14, w-58, 30, CARD_HEAD)
    para(c, body, x+18, y+h-54, w-36, h-64, CARD_BODY)


def arrow(c, x1, y1, x2, y2, color=TEAL):
    c.setStrokeColor(color); c.setFillColor(color); c.setLineWidth(1.6)
    c.line(x1, y1, x2, y2)
    import math
    ang = math.atan2(y2-y1, x2-x1)
    ah = 7
    pts = []
    for a in (ang+2.55, ang-2.55):
        pts.append((x2+ah*math.cos(a), y2+ah*math.sin(a)))
    p=c.beginPath(); p.moveTo(x2,y2); p.lineTo(*pts[0]); p.lineTo(*pts[1]); p.close()
    c.drawPath(p, fill=1, stroke=0)


def decision_node(c, x, y, w, h, title, sub, fill=WHITE, stroke=LINE, title_color=INK):
    rounded_card(c, x, y, w, h, fill=fill, stroke=stroke, radius=9, shadow=False)
    st = ParagraphStyle("n", parent=CARD_HEAD, fontSize=10.2, leading=12.1, textColor=title_color)
    para(c, title, x+10, y+h-10, w-20, 30, st)
    para(c, sub, x+10, y+h-39, w-20, h-45, ParagraphStyle("ns", parent=CARD_BODY, fontSize=7.8, leading=10.2))


def qr_code(c, url, x, y, size):
    widget = qr.QrCodeWidget(url)
    bounds = widget.getBounds(); bw=bounds[2]-bounds[0]; bh=bounds[3]-bounds[1]
    d = Drawing(size, size, transform=[size/bw,0,0,size/bh,0,0]); d.add(widget)
    renderPDF.draw(d, c, x, y)


c = canvas.Canvas(str(OUT), pagesize=(W,H))
c.setTitle("Corvia - Apresentação Institucional")
c.setAuthor("Corvia")

# 1. Capa
c.setFillColor(NAVY); c.rect(0,0,W,H,fill=1,stroke=0)
c.setFillColor(TEAL); c.rect(0, H-0.11*inch, W, 0.11*inch, fill=1, stroke=0)
pill(c, "PLATAFORMA CLÍNICA", 0.68*inch, H-1.16*inch, fill=HexColor("#20495F"), color=HexColor("#75E2D7"), w=118)
para(c, "Corvia", 0.68*inch, H-1.55*inch, 4.4*inch, 0.7*inch, ParagraphStyle("brand", parent=TITLE_WHITE, fontSize=40, leading=42))
para(c, "Apoio à decisão clínica em Cardiologia", 0.68*inch, H-2.25*inch, 4.55*inch, 0.8*inch, ParagraphStyle("hero", parent=BODY_WHITE, fontSize=18, leading=23, textColor=WHITE))
para(c, "Evidência, estratificação de risco, protocolos, prescrição e documentação clínica em um único ambiente.", 0.68*inch, H-3.15*inch, 4.45*inch, 1.0*inch, ParagraphStyle("herob", parent=BODY_WHITE, fontSize=11.5, leading=16))
# screenshot hero
rounded_card(c, 5.45*inch, 0.82*inch, 7.20*inch, 5.78*inch, fill=HexColor("#EAF0F3"), stroke=HexColor("#31566A"), radius=12, shadow=True)
image_fit(c, CAP/"01-dashboard-home.png", 5.58*inch, 0.95*inch, 6.94*inch, 5.52*inch, crop=False, border=False, bg=HexColor("#EAF0F3"))
para(c, "Capturas reais do ambiente de produção · dados fictícios nas telas de demonstração", 0.68*inch, 0.76*inch, 4.4*inch, 0.35*inch, SMALL_WHITE)
footer(c,1,dark=True); c.showPage()

# 2. Visão geral
c.setFillColor(LIGHT); c.rect(0,0,W,H,fill=1,stroke=0)
section_header(c,"Visão geral","Um único ambiente, da evidência à prática","A Corvia organiza conhecimento clínico e ferramentas de trabalho em uma experiência contínua.")
# screenshot left
rounded_card(c, 0.62*inch, 1.08*inch, 6.05*inch, 4.78*inch, fill=WHITE, stroke=LINE, radius=10)
image_fit(c, CAP/"01-dashboard-home.png", 0.75*inch, 1.21*inch, 5.79*inch, 4.52*inch, crop=False, border=False)
# cards right
x=6.95*inch; cw=2.72*inch; gap=0.25*inch; ch=1.82*inch
draw_feature_card(c,x,4.02*inch,cw,ch,1,"Evidência","Biblioteca científica com documentos clínicos, referências e árvores de decisão.",TEAL)
draw_feature_card(c,x+cw+gap,4.02*inch,cw,ch,2,"Risco","Calculadoras clínicas com interpretação, referência e limitações visíveis.",BLUE)
draw_feature_card(c,x,1.88*inch,cw,ch,3,"Ação","Modo Emergência e fluxos rápidos orientados ao ponto de decisão.",RED)
draw_feature_card(c,x+cw+gap,1.88*inch,cw,ch,4,"Documentação","Receituário, documentos, assinatura digital, exportação e comunicação.",GREEN)
footer(c,2); c.showPage()

# 3. Biblioteca
c.setFillColor(WHITE); c.rect(0,0,W,H,fill=1,stroke=0)
section_header(c,"Conhecimento clínico","Biblioteca científica com árvores de decisão","Conteúdo navegável para transformar recomendações e documentos extensos em rotas visuais de raciocínio.")
rounded_card(c, 0.62*inch, 0.78*inch, 8.12*inch, 5.45*inch, fill=LIGHT, stroke=LINE, radius=10)
image_fit(c, CAP/"02-biblioteca-documento-arvore-decisao.png", 0.76*inch, 0.92*inch, 7.84*inch, 5.17*inch, crop=False, border=False, bg=LIGHT)
# side copy
pill(c,"ÁRVORES DE DECISÃO",9.08*inch,5.42*inch,fill=MINT,color=TEAL2,w=135)
para(c,"Visualizar o método, não apenas o resultado",9.08*inch,5.15*inch,3.55*inch,0.7*inch,ParagraphStyle("sideh",parent=CARD_HEAD,fontSize=17,leading=20))
para(c,"A proposta é expor o caminho clínico: critérios de entrada, bifurcações, exames, limiares e condutas. Isso facilita revisão, ensino e aplicação à beira do leito.",9.08*inch,4.28*inch,3.55*inch,1.25*inch,BODY)
for yy,txt in [(3.35,"• Fonte científica visível"),(2.92,"• Fluxos em linguagem clínica"),(2.49,"• Limitações documentadas"),(2.06,"• Integração com calculadoras")]:
    para(c,txt,9.08*inch,yy*inch,3.55*inch,0.35*inch,BODY)
footer(c,3); c.showPage()

# 4. Calculadoras
c.setFillColor(LIGHT); c.rect(0,0,W,H,fill=1,stroke=0)
section_header(c,"Estratificação","Calculadoras com resultado, interpretação e referência","O número aparece junto do contexto clínico necessário para não transformar escore em decisão automática.")
rounded_card(c,0.62*inch,0.85*inch,7.95*inch,5.35*inch,fill=WHITE,stroke=LINE,radius=10)
image_fit(c,CAP/"03b-calculadora-com-resultado.png",0.76*inch,0.99*inch,7.67*inch,5.07*inch,crop=False,border=False)
# callouts
x=8.92*inch
for i,(head,body,col) in enumerate([
    ("Dados estruturados","Entradas clínicas explícitas e reproduzíveis.",TEAL),
    ("Resultado interpretado","Escore e mensagem clínica no mesmo contexto.",BLUE),
    ("Referência e limites","A fonte e as limitações permanecem visíveis.",AMBER),
]):
    yy=4.72*inch-i*1.42*inch
    rounded_card(c,x,yy,3.73*inch,1.12*inch,fill=WHITE,stroke=LINE,radius=9,shadow=False)
    c.setFillColor(col); c.roundRect(x+12,yy+15,5,50,2.5,fill=1,stroke=0)
    para(c,head,x+28,yy+0.88*inch,3.2*inch,0.3*inch,CARD_HEAD)
    para(c,body,x+28,yy+0.51*inch,3.2*inch,0.43*inch,CARD_BODY)
footer(c,4); c.showPage()

# 5. Pré-operatório
c.setFillColor(WHITE); c.rect(0,0,W,H,fill=1,stroke=0)
section_header(c,"Perioperatório","Avaliação Cardiológica Pré-Operatória integrada","Diferentes metodologias podem ser combinadas em uma leitura única, sem esconder quando um método não deve ser reproduzido localmente.")
rounded_card(c,0.62*inch,0.82*inch,8.42*inch,5.42*inch,fill=LIGHT,stroke=LINE,radius=10)
image_fit(c,CAP/"04-avaliacao-preoperatoria-completa.png",0.75*inch,0.95*inch,8.16*inch,5.16*inch,crop=False,border=False,bg=LIGHT)
x=9.34*inch
pill(c,"RISCO CIRÚRGICO",x,5.52*inch,fill=SKY,color=BLUE,w=110)
para(c,"Múltiplos métodos, uma leitura clínica",x,5.18*inch,3.35*inch,0.7*inch,ParagraphStyle("preh",parent=CARD_HEAD,fontSize=16.5,leading=19))
para(c,"A captura demonstra cálculo real de <b>RCRI, Gupta MICA, DASI e VSG-CRI</b>, com resultado integrado.",x,4.26*inch,3.35*inch,0.72*inch,BODY)
para(c,"<b>GSCRI e ACS-NSQIP</b> aparecem com tratamento transparente: o sistema não inventa coeficientes nem embute ferramenta externa quando isso não é apropriado.",x,3.38*inch,3.35*inch,0.95*inch,BODY)
rounded_card(c,x,1.52*inch,3.35*inch,1.25*inch,fill=MINT,stroke=HexColor("#B7DDD6"),radius=9,shadow=False)
para(c,"Princípio de produto",x+14,2.53*inch,3.05*inch,0.3*inch,ParagraphStyle("pp",parent=CARD_HEAD,fontSize=10.5,textColor=TEAL2))
para(c,"O score informa. A árvore de decisão mostra o que fazer com ele.",x+14,2.17*inch,3.05*inch,0.52*inch,CARD_BODY)
footer(c,5); c.showPage()

# 6. Árvore de decisão perioperatória (visão de produto, não prescrição)
c.setFillColor(LIGHT); c.rect(0,0,W,H,fill=1,stroke=0)
section_header(c,"Metodologia visual","Do dado bruto à decisão: o raciocínio fica explícito","Estrutura visual proposta para cada metodologia validada de risco, facilitando comparação e entendimento.")
# row 1
nodes=[
    (0.65,4.35,2.15,1.18,"1. Contexto","Paciente, cirurgia, urgência e condições clínicas ativas.",WHITE,LINE),
    (3.16,4.35,2.15,1.18,"2. Risco","Aplicar o método validado adequado ao cenário.",WHITE,LINE),
    (5.67,4.35,2.15,1.18,"3. Capacidade","Integrar desempenho funcional quando pertinente.",WHITE,LINE),
    (8.18,4.35,2.15,1.18,"4. Investigação","Exames somente quando o resultado puder mudar manejo.",WHITE,LINE),
    (10.69,4.35,1.98,1.18,"5. Plano","Prosseguir, otimizar ou reavaliar.",MINT,HexColor("#B7DDD6")),
]
for n in nodes:
    decision_node(c,n[0]*inch,n[1]*inch,n[2]*inch,n[3]*inch,n[4],n[5],n[6],n[7])
for i in range(len(nodes)-1):
    x1=(nodes[i][0]+nodes[i][2])*inch+3; y1=(nodes[i][1]+nodes[i][3]/2)*inch
    x2=nodes[i+1][0]*inch-4; y2=(nodes[i+1][1]+nodes[i+1][3]/2)*inch
    arrow(c,x1,y1,x2,y2)
# bottom score cards
para(c,"Exemplos de metodologias que podem ocupar o bloco 2",0.65*inch,3.62*inch,7.5*inch,0.3*inch,ParagraphStyle("ex",parent=CARD_HEAD,fontSize=12.4))
for i,(tag,desc,col) in enumerate([
    ("RCRI","6 variáveis binárias; leitura por classes de risco.",TEAL),
    ("Gupta MICA","Estimativa percentual individualizada de IAM/PCR.",BLUE),
    ("DASI","Capacidade funcional estimada por atividades relatadas.",GREEN),
    ("VSG-CRI","Metodologia complementar disponível no módulo.",AMBER),
]):
    xx=(0.65+i*3.05)*inch
    rounded_card(c,xx,1.52*inch,2.78*inch,1.55*inch,fill=WHITE,stroke=LINE,radius=9,shadow=False)
    c.setFillColor(col); c.circle(xx+18,2.78*inch,6,fill=1,stroke=0)
    para(c,tag,xx+32,2.92*inch,2.2*inch,0.35*inch,CARD_HEAD)
    para(c,desc,xx+16,2.45*inch,2.45*inch,0.65*inch,CARD_BODY)
para(c,"A árvore acima representa a experiência de uso do produto; a conduta clínica específica de cada método deve seguir a diretriz e a população em que ele foi validado.",0.65*inch,1.04*inch,11.9*inch,0.42*inch,SMALL)
footer(c,6); c.showPage()

# 7. Emergência
c.setFillColor(NAVY); c.rect(0,0,W,H,fill=1,stroke=0)
section_header(c,"Modo Emergência","Protocolos rápidos com fluxograma aberto","Filtros reduzem o caminho até o protocolo; a árvore concentra a sequência de reconhecimento, decisão e escalada.",dark=True)
rounded_card(c,0.62*inch,0.85*inch,8.65*inch,5.30*inch,fill=HexColor("#EAF0F3"),stroke=HexColor("#31566A"),radius=10)
image_fit(c,CAP/"05b-modo-emergencia-protocolo-aberto.png",0.76*inch,0.99*inch,8.37*inch,5.02*inch,crop=False,border=False,bg=HexColor("#EAF0F3"))
x=9.62*inch
pill(c,"ACESSO RÁPIDO",x,5.43*inch,fill=HexColor("#20495F"),color=HexColor("#75E2D7"),w=105)
para(c,"Menos navegação. Mais contexto no ponto crítico.",x,5.12*inch,2.95*inch,0.85*inch,ParagraphStyle("eh",parent=TITLE_WHITE,fontSize=18,leading=21))
para(c,"A captura mostra um protocolo real de Afogamento com árvore de decisão. O mesmo padrão visual pode ser aplicado a diferentes síndromes e cenários especiais.",x,3.92*inch,2.95*inch,1.05*inch,BODY_WHITE)
para(c,"• filtros por tema/sistema<br/>• protocolo e fluxograma no mesmo ambiente<br/>• referências e limitações preservadas",x,2.65*inch,2.95*inch,1.0*inch,BODY_WHITE)
footer(c,7,dark=True); c.showPage()

# 8. Documentos / receituário
c.setFillColor(WHITE); c.rect(0,0,W,H,fill=1,stroke=0)
section_header(c,"Fluxo assistencial","Da avaliação ao documento clínico","A documentação acompanha o raciocínio: gerar, revisar, assinar, baixar e comunicar.")
rounded_card(c,0.62*inch,1.02*inch,7.14*inch,5.07*inch,fill=LIGHT,stroke=LINE,radius=10)
image_fit(c,CAP/"08-receituario.png",0.76*inch,1.16*inch,6.86*inch,4.79*inch,crop=False,border=False,bg=LIGHT)
# right workflow
x=8.15*inch
steps=[("1","Gerar","Documento estruturado a partir do fluxo clínico."),("2","Revisar","Conteúdo permanece sob controle do médico."),("3","Assinar","Integração com provedores de assinatura digital."),("4","Entregar","PDF, impressão e envio eletrônico."),]
for i,(num,head,body) in enumerate(steps):
    yy=(5.48-i*1.11)*inch
    c.setFillColor(TEAL); c.circle(x+13,yy-1,11,fill=1,stroke=0)
    c.setFillColor(WHITE); c.setFont("Helvetica-Bold",8); c.drawCentredString(x+13,yy-4,num)
    para(c,head,x+34,yy+10,3.8*inch,0.26*inch,CARD_HEAD)
    para(c,body,x+34,yy-17,3.8*inch,0.38*inch,CARD_BODY)
    if i<3: c.setStrokeColor(LINE); c.setLineWidth(1); c.line(x+13,yy-14,x+13,yy-0.83*inch)
rounded_card(c,x,0.86*inch,4.34*inch,0.82*inch,fill=SKY,stroke=HexColor("#C8DEE9"),radius=9,shadow=False)
para(c,"CorvIA Mail e histórico de documentos completam a etapa de comunicação e acompanhamento.",x+14,1.51*inch,4.0*inch,0.52*inch,CARD_BODY)
footer(c,8); c.showPage()

# 9. Operação conectada
c.setFillColor(LIGHT); c.rect(0,0,W,H,fill=1,stroke=0)
section_header(c,"Operação conectada","Agenda, integrações e acesso responsivo","A plataforma reúne a rotina clínica sem separar conhecimento, paciente e ferramentas de produtividade.")
# three screenshot cards
cards=[
    (0.62,1.02,4.06,4.96,"07-agenda-integrada.png","Agenda Integrada","Compromissos e organização da rotina em um ambiente único."),
    (4.88,1.02,4.06,4.96,"10-minha-conta.png","Minha Conta","Perfil profissional e pontos de integração da experiência."),
    (9.14,1.02,3.57,4.96,"12-mobile-responsivo.png","Mobile","Interface responsiva para acesso em diferentes contextos de uso."),
]
for xx,yy,ww,hh,img,head,body in cards:
    rounded_card(c,xx*inch,yy*inch,ww*inch,hh*inch,fill=WHITE,stroke=LINE,radius=10)
    ih=3.47*inch if img!="12-mobile-responsivo.png" else 3.60*inch
    image_fit(c,CAP/img,(xx+0.13)*inch,(yy+1.18)*inch,(ww-0.26)*inch,ih,crop=False,border=False,bg=WHITE)
    para(c,head,(xx+0.18)*inch,(yy+0.98)*inch,(ww-0.36)*inch,0.3*inch,CARD_HEAD)
    para(c,body,(xx+0.18)*inch,(yy+0.60)*inch,(ww-0.36)*inch,0.44*inch,CARD_BODY)
footer(c,9); c.showPage()

# 10. Governança / encerramento
c.setFillColor(NAVY); c.rect(0,0,W,H,fill=1,stroke=0)
c.setFillColor(TEAL); c.rect(0,H-0.11*inch,W,0.11*inch,fill=1,stroke=0)
para(c,"Corvia",0.72*inch,H-0.72*inch,4*inch,0.6*inch,ParagraphStyle("brand2",parent=TITLE_WHITE,fontSize=28,leading=30))
para(c,"Tecnologia clínica com uma regra simples: quando a evidência não sustenta o número, o sistema não deve inventá-lo.",0.72*inch,H-1.42*inch,7.55*inch,1.05*inch,ParagraphStyle("close",parent=TITLE_WHITE,fontSize=22,leading=27))
# principles
principles=[
    ("Fonte real","Referências verificáveis e conteúdo científico rastreável."),
    ("Limite explícito","Incerteza ou coeficiente não confirmado permanece sinalizado."),
    ("Humano no circuito","A ferramenta apoia; a decisão clínica permanece médica."),
    ("Método visual","Escores e diretrizes ganham árvores de decisão para tornar o raciocínio auditável."),
]
for i,(head,body) in enumerate(principles):
    xx=(0.72+(i%2)*3.86)*inch; yy=(3.00-(i//2)*1.28)*inch
    rounded_card(c,xx,yy,3.52*inch,1.03*inch,fill=HexColor("#17384F"),stroke=HexColor("#31566A"),radius=9,shadow=False)
    c.setFillColor(HexColor("#66D5CA")); c.circle(xx+18,yy+0.72*inch,5,fill=1,stroke=0)
    para(c,head,xx+32,yy+0.89*inch,2.92*inch,0.28*inch,ParagraphStyle("ph",parent=CARD_HEAD,textColor=WHITE,fontSize=10.5))
    para(c,body,xx+16,yy+0.55*inch,3.12*inch,0.46*inch,ParagraphStyle("pb",parent=CARD_BODY,textColor=HexColor("#BFD1DC"),fontSize=8.2,leading=10.5))
# CTA/QR
rounded_card(c,8.72*inch,1.10*inch,3.86*inch,4.30*inch,fill=WHITE,stroke=HexColor("#31566A"),radius=12)
para(c,"Conheça a Corvia",9.05*inch,4.93*inch,3.2*inch,0.4*inch,ParagraphStyle("ctah",parent=CARD_HEAD,fontSize=17,leading=19))
para(c,"Plataforma de apoio à decisão clínica em Cardiologia.",9.05*inch,4.43*inch,3.05*inch,0.6*inch,BODY)
qr_code(c,"https://corvia.med.br",9.42*inch,2.05*inch,1.75*inch)
c.setFillColor(TEAL2); c.setFont("Helvetica-Bold",11); c.drawCentredString(10.30*inch,1.65*inch,"corvia.med.br")
para(c,"Capturas reais do ambiente de produção, registradas em 07/08/2026. Nenhuma captura contém dado real de paciente.",0.72*inch,0.78*inch,7.35*inch,0.45*inch,SMALL_WHITE)
footer(c,10,dark=True); c.showPage()

c.save()
print(OUT)
