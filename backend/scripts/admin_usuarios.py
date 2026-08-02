"""CLI administrativa para operações que hoje só existem via API HTTP:
criar usuário, ativar o CorvIA Mail com senha própria e decidir a fila de
autocadastro pendente. Fala com o backend real (produção ou local) por HTTP —
não toca o banco diretamente — então basta rede até a API e uma conta admin
já existente.

Uso (rodar onde houver rede até a API, ex.: `docker exec <container-backend>
python scripts/admin_usuarios.py ...`):

    export CORVIA_ADMIN_EMAIL=admin@corvia.med.br
    export CORVIA_ADMIN_PASSWORD='...'

    python scripts/admin_usuarios.py criar-usuario \
        --base-url https://corvia.med.br \
        --nome "Natalia Canevari Valenti" \
        --email natalia@corvia.med.br \
        --senha 'GustaAntonio21@@' \
        --crm "CRBM 14026/SP" \
        --role admin \
        --ativar-email

    python scripts/admin_usuarios.py listar-pendentes --base-url https://corvia.med.br

    python scripts/admin_usuarios.py decidir-pendente --base-url https://corvia.med.br \
        --user-id 42 --aprovar --role medico
"""

import argparse
import os
import sys

import httpx


def _token(base_url: str, email: str, senha: str) -> str:
    resp = httpx.post(
        f"{base_url}/api/auth/login",
        data={"username": email, "password": senha},
        timeout=30,
    )
    if resp.status_code != 200:
        raise SystemExit(f"Login falhou para {email}: {resp.status_code} {resp.text}")
    return resp.json()["access_token"]


def _admin_token(args) -> str:
    email = args.admin_email or os.environ.get("CORVIA_ADMIN_EMAIL")
    senha = args.admin_password or os.environ.get("CORVIA_ADMIN_PASSWORD")
    if not email or not senha:
        raise SystemExit(
            "Informe --admin-email/--admin-password ou as variáveis de ambiente "
            "CORVIA_ADMIN_EMAIL/CORVIA_ADMIN_PASSWORD."
        )
    return _token(args.base_url, email, senha)


def criar_usuario(args) -> None:
    admin_token = _admin_token(args)
    headers = {"Authorization": f"Bearer {admin_token}"}

    resp = httpx.post(
        f"{args.base_url}/api/admin/users",
        json={
            "email": args.email,
            "full_name": args.nome,
            "crm": args.crm,
            "role": args.role,
            "password": args.senha,
        },
        headers=headers,
        timeout=30,
    )
    if resp.status_code != 201:
        raise SystemExit(f"Criação do usuário falhou: {resp.status_code} {resp.text}")
    criado = resp.json()
    print(f"Usuário criado: id={criado['id']} email={criado['email']} role={criado['role']}")

    if args.ativar_email:
        user_token = _token(args.base_url, args.email, args.senha)
        resp = httpx.post(
            f"{args.base_url}/api/email/conta",
            json={"senha": args.senha, "aceite_lgpd": True},
            headers={"Authorization": f"Bearer {user_token}"},
            timeout=30,
        )
        if resp.status_code != 201:
            raise SystemExit(f"Ativação do CorvIA Mail falhou: {resp.status_code} {resp.text}")
        conta = resp.json()
        print(f"CorvIA Mail ativado: {conta.get('email_address', conta)}")


def listar_pendentes(args) -> None:
    admin_token = _admin_token(args)
    resp = httpx.get(
        f"{args.base_url}/api/admin/users",
        params={"status": "pendente"},
        headers={"Authorization": f"Bearer {admin_token}"},
        timeout=30,
    )
    if resp.status_code != 200:
        raise SystemExit(f"Falha ao listar pendentes: {resp.status_code} {resp.text}")
    pendentes = resp.json()
    if not pendentes:
        print("Nenhuma solicitação pendente.")
        return
    for u in pendentes:
        print(
            f"id={u['id']} nome={u['full_name']!r} email={u['email']} "
            f"conselho={u.get('council_name')} {u.get('council_number')}/{u.get('council_state')}"
        )


def decidir_pendente(args) -> None:
    admin_token = _admin_token(args)
    resp = httpx.post(
        f"{args.base_url}/api/admin/users/{args.user_id}/decidir",
        json={"aprovar": args.aprovar, "role": args.role, "nota": args.nota},
        headers={"Authorization": f"Bearer {admin_token}"},
        timeout=30,
    )
    if resp.status_code != 200:
        raise SystemExit(f"Decisão falhou: {resp.status_code} {resp.text}")
    print(resp.json())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--base-url", required=True, help="Ex.: https://corvia.med.br")
    parser.add_argument("--admin-email", default=None)
    parser.add_argument("--admin-password", default=None)
    sub = parser.add_subparsers(dest="comando", required=True)

    p_criar = sub.add_parser("criar-usuario", help="Cria usuário e, opcionalmente, ativa o CorvIA Mail")
    p_criar.add_argument("--nome", required=True)
    p_criar.add_argument("--email", required=True)
    p_criar.add_argument("--senha", required=True)
    p_criar.add_argument("--crm", default=None, help='Ex.: "CRBM 14026/SP" — texto livre')
    p_criar.add_argument("--role", default="admin", choices=["admin", "medico", "residente", "leitor"])
    p_criar.add_argument("--ativar-email", action="store_true", help="Também ativa o CorvIA Mail com a mesma senha")
    p_criar.set_defaults(func=criar_usuario)

    p_listar = sub.add_parser("listar-pendentes", help="Lista solicitações de autocadastro aguardando decisão")
    p_listar.set_defaults(func=listar_pendentes)

    p_decidir = sub.add_parser("decidir-pendente", help="Aprova ou rejeita uma solicitação pendente")
    p_decidir.add_argument("--user-id", type=int, required=True)
    p_decidir.add_argument("--aprovar", action="store_true")
    p_decidir.add_argument("--rejeitar", dest="aprovar", action="store_false")
    p_decidir.add_argument("--role", default="medico", choices=["admin", "medico", "residente", "leitor"])
    p_decidir.add_argument("--nota", default=None)
    p_decidir.set_defaults(func=decidir_pendente)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
