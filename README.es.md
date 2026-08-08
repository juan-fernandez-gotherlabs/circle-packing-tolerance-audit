# Circle packing n=26: auditoría por tolerancia y certificado exacto

Este repositorio publica tres resultados distintos sin mezclarlos:

| Contrato | Puntuación recomputada | Interpretación |
| --- | ---: | --- |
| tolerancia `1e-6` | `2.63599872089287514` | resultado del benchmark público |
| tolerancia `1e-10` | `2.63598308647338795` | resultado del evaluador interno |
| tolerancia `0` | `2.635983084917607783186569485443481730396676798274474857745771129860703849334…` | certificado decimal finito comprobado como racional exacto |

Los dos primeros aprovechan la tolerancia y fallan al exigir tolerancia cero.
El tercero es geométricamente factible, pero no demuestra optimalidad global ni
se presenta como un nuevo récord numérico frente a la fila redondeada de
Packomania.

La reproducción completa del artefacto se ejecuta con:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --requirement requirements.lock
./verify_all.sh
```

El módulo temporal `contact_flip.py` y las semillas `.npz` del entorno de
ChatGPT no aparecían entre los adjuntos finales. Se sustituyeron por una
implementación autocontenida que reconstruye el grafo desde el certificado y
regenera las semillas. Los logs históricos se conservan aparte para no
confundirlos con la nueva reproducción.

Se incluyen en `results/search_reproduction/` la raíz reconstruida, las 78
semillas `.npz` de primera capa, sus trazas y el resumen. Los archivos usan una
marca temporal ZIP fija para que una regeneración limpia sea idéntica byte a
byte.

Una comprobación posterior de los logs corrige dos cifras del texto original:
la segunda capa contiene 312 transiciones, por lo que 390 es el acumulado
`78+312`, y el archivo de la tercera capa contiene finalmente las 468
transiciones previstas, aunque la explicación se redactó cuando llevaba 264.

Consulta el [README principal](README.md), la definición de
[exactitud](docs/EXACTNESS.md) y las [limitaciones](docs/LIMITATIONS.md).
