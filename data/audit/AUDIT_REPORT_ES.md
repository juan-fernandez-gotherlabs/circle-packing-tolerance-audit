# Segunda auditoría estricta — circle packing n=26

Fecha de corte: **6 de agosto de 2026**.

## Veredicto

Con el criterio solicitado —misma tolerancia, artefacto público descargable y comprobación independiente— nuestros tres candidatos quedan en **puesto 1 del corpus público auditable localizado**:

| Régimen | Nuestro resultado recomputado | Mejor referencia externa comparable localizada | Diferencia | Posición auditable |
| --- | ---: | ---: | ---: | ---: |
| `1e-6` | `2.63599872089287514` | EurekAgent: `2.635998720859883` | `+3.2992e-11` | **1** |
| `1e-10` | `2.63598308647338795` | Packomania ASCII, reevaluado con `1e-10`: `2.635983084919` | `+1.55438795e-9` | **1** |
| `0` | `2.635983084917607783186569485443481730396676798274474857745771129860703849334…` | Station SOTA: `2.63598308491754727833633609179742052219808101654052734375` | `+6.0504850e-14` | **1** |

La palabra **auditable** es esencial. No se afirma que se haya enumerado todo resultado privado ni que exista una prueba de optimalidad global. Se afirma algo reproducible: ningún testigo público completo de los que se localizaron y descargaron supera al nuestro cuando se le aplica el mismo contrato.

## Regla de comparación

1. Mismo problema: 26 círculos de radios variables dentro del cuadrado unidad, maximizando la suma de radios.
2. La puntuación se vuelve a calcular como `sum(r_i)`; no se acepta únicamente el número declarado por el autor.
3. Para `tau=0`, cada decimal finito se interpreta como un racional exacto. Los `float64` de programas descargados se interpretan como sus valores IEEE-754 exactos.
4. Las paredes se comprueban linealmente. Los 325 pares se comprueban mediante distancias al cuadrado, sin raíz cuadrada en la decisión de validez.
5. Para `tau>0`, se exige `wall_gap >= -tau` y `distance >= r_i+r_j-tau`.
6. Una entrada sin coordenadas o programa reproducible no recibe puesto, aunque publique una cifra mayor.

El script comprobó **30 artefactos** —tres nuestros y 27 externos—, 429 desigualdades por artefacto y por régimen: **38.610 decisiones geométricas**. El JSON guarda todas las holguras, no solo la tabla final.

## Resultado por régimen

### Tolerancia `1e-6`

Nuestro CSV pasa la interpretación racional del contrato con:

- suma `2.63599872089287514`;
- margen mínimo de pared respecto al límite: `4.9985e-13`;
- margen mínimo de par respecto al límite: `4.9984625743987…e-13`.

El artefacto público fijado de EurekAgent declara `2.635998720859883`; su evaluador usa tolerancia `1e-6`. La ejecución del evaluador oficial en `float64` lo acepta, por lo que es la referencia justa para este régimen. Nuestro valor es mayor en aproximadamente `3.2992e-11`. Véanse el [resultado descargable de EurekAgent](https://github.com/THU-Team-Eureka/EurekAgent/blob/38585790ff56e7993aec322e0179ded8b101d82c/results/circle_packing/result.jsonl) y su [evaluador fijado](https://github.com/THU-Team-Eureka/EurekAgent/blob/38585790ff56e7993aec322e0179ded8b101d82c/examples/circle_packing/hidden_eval_dir/evaluate.py).

Hay una sutileza verificable: si los decimales publicados por EurekAgent se tratan como racionales exactos, un par rebasa el límite `1e-6` en `6.18e-17`; en la aritmética `float64` definida por su evaluador sí pasa. Esto no afecta al primer puesto: nuestro candidato queda por encima y además conserva margen racional positivo.

GEPA/optimize_anything también usa `atol=1e-6`, pero solo publica `2.63598+` y no un testigo final congelado; por eso no puede ocupar un puesto verificable. El código público permite confirmar la tolerancia en [`examples/circle_packing/utils.py`](https://github.com/gepa-ai/gepa/blob/main/examples/circle_packing/utils.py).

### Tolerancia `1e-10`

Nuestro CSV pasa con:

- suma `2.63598308647338795`;
- peor holgura geométrica sin tolerancia cercana a `-9.95001563e-11`;
- reserva frente a `-1e-10` de aproximadamente `4.99844e-13`.

La mejor referencia externa del corpus que también pasa este contrato es el ASCII de Packomania, reevaluado a partir de sus radios publicados: `2.635983084919`. Sus coordenadas tienen un solape de aproximadamente `1.04164e-12`, admisible bajo `1e-10`. Nuestro margen sobre ese testigo es `1.55438795e-9`.

AlphaZ-CORAL genera `2.635983084917610311…` y pasa `1e-10`, pero falla tolerancia cero por `6.1161e-15`; queda por debajo de nuestro candidato `1e-10`. El [programa completo está publicado](https://github.com/Kurorz2004/alphaz-coral/blob/main/task1/result/best_program.py).

No se encontró una clasificación pública dedicada exactamente a `1e-10`. Por ello, el puesto indicado es una clasificación reconstruida: todos los testigos descargados se vuelven a evaluar con `tau=1e-10`.

### Tolerancia cero

La clasificación estricta superior queda así:

| Puesto | Artefacto que pasa `tau=0` | Suma recomputada |
| ---: | --- | ---: |
| **1** | Nuestro `strict_high_precision.csv` | `2.635983084917607783186569485443481730396676798274474857745771129860703849334…` |
| 2 | Station SOTA | `2.63598308491754727833633609179742052219808101654052734375` |
| 3 | EinsteinArena GaussAgent3615 | `2.63598308491660695` |
| 3 | EinsteinArena PerelmanAgent5442 | `2.63598308491660695` |
| 5 | EinsteinArena TopologyAgent7556 | `2.63598308491497804` |

Nuestro testigo verifica las 429 desigualdades con aritmética racional exacta. La holgura mínima de pared es `1.0000000000000015957e-75` y la separación lineal mínima entre pares es aproximadamente `2.0000000000000015957e-75`.

El segundo puesto reproducible es el [`station_sota.py` de Station](https://github.com/dualverse-ai/station/blob/main/example/research_circle_n26/station_sota.py). Interpretando exactamente sus `float64`, no hay violación: la suma es inferior a la nuestra en `6.0504850e-14`.

Se descargaron las **17 soluciones** de la [clasificación actual de EinsteinArena](https://einsteinarena.com/problems/circle-packing). Sus cuatro primeras cifras visibles no pasan `tau=0`:

| Entrada visible | Suma descargada | Motivo de exclusión estricta |
| --- | ---: | --- |
| JSAgent | `2.63598309526084391` | solape `9.98000e-10` |
| PRIDE-agent | `2.63598309467298385` | solape `9.98020e-10` |
| alpha_omega_agents | `2.63598309281158470` | solape `9.99999e-10` |
| CHRONOS | `2.63598308911027738` | solape `9.99355e-10` |

La primera entrada de EinsteinArena que sí pasa exactamente es GaussAgent3615 —empatada con PerelmanAgent5442— y queda `1.000833…e-12` por debajo de nuestro certificado.

## Packomania y la cifra redondeada

La [tabla vigente de Packomania](https://www.packomania.com/csqv/csqv.html), actualizada el 4 de agosto de 2026, muestra para `n=26` el valor `2.635983084918`, 78 contactos y no lo marca como óptimo demostrado. Nuestro certificado redondea al mismo valor con 12 decimales.

Sin embargo, el [ASCII descargable de `csqv26`](https://www.packomania.com/csqv/txt/csqv26.txt) solo conserva 12 decimales. Tratando esos números publicados como exactos:

- suma de radios recomputada: `2.635983084919`;
- holgura mínima de pared: `0`;
- separación mínima entre pares: `-1.041635179149…e-12`;
- resultado con `tau=0`: **falla**;
- resultado con `tau=1e-10`: **pasa**.

Por tanto, la fila redondeada de Packomania sirve como referencia histórica, pero su archivo ASCII no es un competidor estricto de precisión completa. No es legítimo declarar que `2.635983084918` es mayor que nuestro decimal completo; ambos redondean a esa misma fila y el testigo publicado no permite resolver más cifras de manera estricta.

## Otras comprobaciones y exclusiones justificadas

- **Tencent Hyra:** el [JSON completo](https://github.com/Tencent-Hunyuan/Hyra-results/blob/main/AI4Science/packing_records/records/cirRsqu_n26.json) suma `2.63598309510684482`, pero sale de la pared en `7.38e-10` y solapa aproximadamente `9.80e-10`; no es exacto.
- **ThetaEvolve:** se reevaluaron las coordenadas fijas de [`Results/CirclePacking/data.json`](https://github.com/ypwang61/ThetaEvolve/blob/main/Results/CirclePacking/data.json). Su testigo formal pasa `tau=0` con `2.63598307738811934`, por debajo del nuestro.
- **MangoEvolve:** su propio [`strict_scores_results.json`](https://github.com/PaliC/mangoEvolve/blob/main/analysis/strict_scores_results.json) da como mejor puntuación estricta publicada `2.6359830849174837`, inferior a Station y a nuestro certificado.
- **Jason Liang:** su [`csqv26.pck`](https://github.com/jasonzliang/circle-packing-sota/blob/main/sota/ours/pck/csqv26.pck) pasa exactamente, con suma `2.635983084893`.
- **LearningEvolve:** el resumen publica `2.635983084917901`, pero el [verificador del repositorio](https://github.com/vicruz99/learning_evolve/blob/main/src/envs/circle_packing.py) admite `1e-12` y no congela las coordenadas finales en el resumen. No puede entrar en `tau=0`; aun si se acepta para `1e-10`, queda muy por debajo de nuestro resultado.
- **Scalable AI Class / SkyDiscover:** el resultado `2.635983084917693` fue puntuado por un [evaluador con `1e-6`](https://github.com/mert-cemri/scalable_ai_class/blob/main/benchmarks/math/circle_packing/evaluator.py); no entra en la tabla exacta.
- **Numaro:** publica `2.6359830853` y afirma verificar coordenadas, pero la [página pública](https://numaro.tech/research/circle-packing-unit-square-2026/) no enlaza el testigo `n=26`. La cifra queda como **afirmación no auditable**, no como puesto estricto.

## Alcance exacto de la conclusión

La formulación defendible es:

> A fecha de 6 de agosto de 2026, nuestros tres artefactos ocupan el primer puesto entre los resultados públicos completos localizados y reevaluados bajo su misma tolerancia. En tolerancia cero, nuestro certificado es el mejor testigo público descargable que esta auditoría pudo verificar exactamente.

No debe sustituirse por “óptimo global demostrado” ni por “récord mundial absoluto”, porque no existe una enumeración completa de todos los empaquetamientos posibles y todavía hay cifras públicas sin testigo descargable.

## Reproducción

Ejecutar:

```bash
PYTHONDONTWRITEBYTECODE=1 python verify_strict_leaderboard.py
```

Archivos producidos:

- `strict_leaderboard_audit.json`: comprobaciones y clasificaciones completas.
- `verify_strict_leaderboard.py`: auditor independiente reproducible.

