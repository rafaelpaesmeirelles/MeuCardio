from pathlib import Path

p = Path(__file__).with_name('build_corvia_pdf.py')
s = p.read_text(encoding='utf-8')

s = s.replace(
    'section_header(c,"Metodologia visual","Do dado bruto à decisão: o raciocínio fica explícito","Estrutura visual proposta para cada metodologia validada de risco, facilitando comparação e entendimento.")',
    'section_header(c,"Metodologia visual","Do dado bruto à decisão","O raciocínio fica explícito em cada metodologia validada de risco, facilitando comparação e entendimento.")',
)

s = s.replace(
    'section_header(c,"Operação conectada","Agenda, integrações e acesso responsivo","A plataforma reúne a rotina clínica sem separar conhecimento, paciente e ferramentas de produtividade.")',
    'section_header(c,"Operação conectada","Agenda, integrações e acesso móvel","Interface responsiva e rotina conectada sem separar conhecimento, paciente e ferramentas de produtividade.")',
)

old = 'image_fit(c,CAP/"04-avaliacao-preoperatoria-completa.png",0.75*inch,0.95*inch,8.16*inch,5.16*inch,crop=False,border=False,bg=LIGHT)'
new = '''# A captura pré-operatória é uma página vertical longa. Exibir a visão completa\n# junto de um recorte central ampliado melhora a leitura sem esconder o contexto.\nimage_fit(c,CAP/"04-avaliacao-preoperatoria-completa.png",0.75*inch,0.95*inch,1.48*inch,5.16*inch,crop=False,border=False,bg=LIGHT)\nimage_fit(c,CAP/"04-avaliacao-preoperatoria-completa.png",2.34*inch,0.95*inch,6.57*inch,5.16*inch,crop=True,border=False,bg=LIGHT)'''
if old not in s:
    raise SystemExit('Trecho da captura pré-operatória não encontrado')
s = s.replace(old, new)

p.write_text(s, encoding='utf-8')
print('Layout patch applied')
