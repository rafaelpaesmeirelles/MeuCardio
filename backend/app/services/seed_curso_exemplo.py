"""Cadastra o curso de exemplo `MeuCardio Curso`.

Existe para o Rafael ver o cartão do Painel funcionando antes de haver parceiro
fechado. Duas escolhas deliberadas:

- Nasce **ativo e em destaque**, senão não haveria o que mostrar.
- Nasce **sem `stripe_account_id`**, e a rota de assinatura recusa a venda nesse
  estado. Um curso de demonstração que aceitasse cartão cobraria de verdade e
  criaria dívida com um parceiro que não existe.

Idempotente: rodar de novo não duplica nem sobrescreve o que já foi editado.
"""

from app.core.db import SessionLocal
from app.models.partner_course import PartnerCourse

SLUG = "meucardio-curso"


def semear() -> dict:
    db = SessionLocal()
    try:
        existente = db.query(PartnerCourse).filter(PartnerCourse.slug == SLUG).first()
        if existente:
            return {"criado": False, "slug": SLUG, "nota": "já existia, nada alterado"}

        curso = PartnerCourse(
            slug=SLUG,
            nome="MeuCardio Curso",
            parceiro="MeuCardio",
            descricao=(
                "Curso de exemplo, cadastrado para demonstrar a área de cursos "
                "parceiros. Preparação para o Título de Especialista em Cardiologia, "
                "com aulas ao vivo e gravadas no ambiente do parceiro e material de "
                "apoio disponível aqui dentro."
            ),
            # Frase e fonte andam juntas — a rota de cadastro recusa uma sem a
            # outra, e este exemplo respeita a mesma regra em vez de contorná-la.
            frase_destaque="Curso de exemplo para demonstração da área de cursos parceiros.",
            frase_destaque_fonte="MeuCardio (curso de demonstração, sem dado de terceiro)",
            link_aula_ao_vivo=None,
            link_aulas_gravadas=None,
            preco_parceiro_centavos=19000,   # R$ 190,00 ao parceiro
            margem_centavos=4000,            # R$ 40,00 de margem -> R$ 230,00 ao médico
            stripe_account_id=None,          # sem conta conectada: venda bloqueada
            ativo=True,
            destaque=True,
            trilhas_vinculadas=[],
            casos_vinculados=[],
        )
        db.add(curso)
        db.commit()
        db.refresh(curso)
        return {
            "criado": True,
            "slug": curso.slug,
            "preco_total_centavos": curso.preco_total_centavos,
            "venda_bloqueada": True,
            "motivo": "sem stripe_account_id — curso de demonstração não cobra",
        }
    finally:
        db.close()


if __name__ == "__main__":
    import json

    print(json.dumps(semear(), ensure_ascii=False, indent=2))
