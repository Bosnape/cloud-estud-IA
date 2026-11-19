# syntax=docker/dockerfile:1
# La variante C no tiene instrucciones propias.
# Se construye con Dockerfile.b. La diferencia está en el workflow:
# caché de GitHub Actions, type=gha, scope=estudia-sesion4-variante-c, mode=max.
#
# No ejecutes `docker build -f variante-c.Dockerfile`: este archivo solo deja
# la variante visible en el árbol. No se llama Dockerfile.c porque el
# analizador de Sonar trata el sufijo .c como código C y rompe el job.
