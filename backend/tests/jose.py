"""Compatibilidade exclusiva da suíte para tokens históricos.

A aplicação de produção usa PyJWT diretamente. Este módulo permite que o teste
histórico ainda escrito como ``from jose import jwt`` gere o mesmo JWT HS256
sem reinstalar a dependência vulnerável ``python-jose``.
"""
import jwt as jwt

__all__ = ["jwt"]
