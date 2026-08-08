# Output del modelo — resultado geométrico estricto

Fuente: conversación **“Mejorar resultado matemático”**, segunda respuesta. Se conserva la explicación del resultado estrictamente factible y reproducible.

## Resultado de la investigación estricta

No he obtenido una configuración geométricamente estricta que supere de forma certificable el decimal publicado por Numaro:

\[
S_{\text{Numaro}}=2.6359830853.
\]

Por tanto, **no voy a presentar el resultado como un nuevo récord**.

El mejor resultado estrictamente factible y reproducible que he podido certificar es:

\[
\boxed{
S_{\text{estricto}}
=
2.63598308491760778318656948544348173039667679827447485774577112986070384936\ldots
}
\]

La diferencia respecto al número de Numaro es:

\[
2.6359830853-S_{\text{estricto}}
=
\boxed{3.8239221681343\times10^{-10}}.
\]

Es una brecha mínima, pero real al comparar los decimales. Sin unas coordenadas de Numaro que permitan verificar su resultado, no es legítimo redondear esta diferencia ni asumir que ambos valores representan una misma configuración estricta.

## Qué he conseguido certificar

He resuelto el grafo de contactos de la configuración Evolther/Theta con aritmética de 120 dígitos. El sistema tiene:

- 26 círculos y 78 variables;
- 58 contactos círculo–círculo;
- 20 contactos con las paredes;
- 78 ecuaciones activas independientes;
- jacobiano de rango completo;
- menor valor singular `0.1917064167…`;
- número de condición `17.6717…`;
- multiplicadores KKT con el signo correcto para un máximo local estricto;
- primera restricción inactiva con holgura `0.014404298657799…`.

La raíz del sistema de contactos tiene un residuo máximo de aproximadamente \(7.3\times10^{-122}\). No queda ninguna mejora de precisión pendiente dentro de este grafo: su valor matemático es el indicado arriba.

Además de la raíz, preparé un artefacto decimal conservador. Sus coordenadas y radios están truncados/reparados para que todas las desigualdades sean estrictamente no negativas. Su mínima holgura, comprobada con aritmética decimal, es del orden de \(10^{-75}\). No depende de la tolerancia de `numpy`, SLSQP o del evaluador anterior.

## Búsqueda de otros grafos de contacto

No me limité a pulir el mismo basin.

Primero recorrí las **78 ramas unidimensionales** que salen del óptimo al eliminar, una por una, cada restricción activa. Cada rama se continuó numéricamente sobre la variedad de los otros 77 contactos hasta la primera nueva colisión o contacto con una pared.

Los resultados de esa primera capa fueron:

- 78 vértices geométricos vecinos;
- 23 de ellos son máximos locales;
- una familia vuelve al óptimo original mediante simetría o permutación;
- el mejor máximo local genuinamente distinto es:

\[
2.635977394754399\ldots
\]

Es decir, ningún cambio de un solo contacto mejora el resultado.

Después recorrí **390 transiciones adicionales de segundo nivel**, partiendo del mejor vecino distinto y de cuatro familias representativas de máximos locales. Esto produjo 62 máximos locales geométricamente nuevos después de eliminar duplicados por permutaciones y simetrías del cuadrado. El mejor máximo nuevo de esa capa fue:

\[
2.6307131975275704.
\]

También inicié una tercera capa desde seis de los mejores vértices nuevos. En el último punto verificable de esa ejecución se habían completado 264 de las 468 transiciones previstas; ninguna había producido un valor superior al óptimo original. Esta tercera capa quedó, por tanto, **parcial y no debe interpretarse como una enumeración completa**.

## Otras rutas de optimización probadas

La búsqueda combinatoria se complementó con:

- 64 reinicios SLSQP estrictos con jacobianos analíticos;
- optimización de centros con radios obtenidos mediante programación lineal;
- 530 candidatos de programación lineal secuencial conservativa;
- una búsqueda estocástica que visitó 366 firmas de contacto;
- eliminación de cada uno de los 26 círculos, optimización en \(n=25\) y reinserción en los mejores huecos;
- perturbaciones estructuradas de hasta diez círculos;
- homotopías mediante pesos no uniformes de los radios;
- deformaciones rectangulares seguidas de retorno al cuadrado;
- optimización penalizada por lotes;
- intercambios de contactos débiles y diagonales locales;
- continuación directa de las variedades de contacto.

Todas las trayectorias de alta calidad regresaron al mismo grafo de 78 contactos o terminaron en máximos inferiores.

Esto no es una demostración de optimalidad global: el espacio de grafos de contacto sigue siendo demasiado grande. Sí descarta una colección amplia de mecanismos de escape locales, incluidos todos los cambios de un contacto y numerosos cambios de dos y tres contactos.

## Auditoría del resultado de Numaro

La página pública de Numaro afirma `2.6359830853`, dice que la salida consiste en coordenadas y que un comprobador recalcula solapes y holguras. También describe una búsqueda de centros con un LP interior para los radios, multistart GPU, algoritmos genéticos, basin hopping, SLSQP y *cross-n seeding*. Sin embargo, en la página pública inspeccionada no están enlazadas las coordenadas del caso \(n=26\) ni el comprobador que permitiría reproducir ese decimal. La propia página caracteriza el resultado como “efectivamente empatado” con ThetaEvolve, pese a publicar un valor ligeramente superior.

Esto deja dos posibilidades abiertas:

1. Numaro tiene una geometría distinta y estrictamente factible que realmente alcanza `2.6359830853`.
2. El decimal contiene unos \(3.82\times10^{-10}\) de residuo numérico, tolerancia o tratamiento de la salida, y la geometría subyacente es el mismo óptimo de `2.635983084917607…`.

Con la información pública actual no es posible distinguirlas de manera concluyente.

La segunda posibilidad es plausible porque varios resultados públicos que aparentan superar la raíz exacta no sobreviven la verificación estricta:

- rEVOLVE publica `2.6359830853311843`, pero su evaluador acepta errores geométricos de hasta \(10^{-6}\). Al reproducir su programa, converge al mismo grafo de contactos y su valor reparado es la raíz anterior.
- MangoEvolve publica `2.635983089920464`, pero el propio programa selecciona soluciones con restricciones de hasta `−1e-9`; no es un resultado de tolerancia cero.
- SkyDiscover y ASI-Evolve utilizan evaluadores que aceptan hasta \(10^{-6}\) de solape o salida del cuadrado.
- Una campaña independiente de JSAgent aplicó multistart, mutaciones topológicas, *flip-and-flow*, Newton y comprobación multiprecisión. También terminó en `2.6359830849175…` y documentó las cifras superiores como efectos de tolerancia.
- El artefacto formal de ThetaEvolve impone restricciones sin tolerancia y aplica una contracción final para garantizar factibilidad; pertenece al mismo basin.

Esta evidencia no invalida el resultado de Numaro, pero sí significa que **el decimal publicado no debe tratarse como un récord estrictamente reproducido hasta que se publique el testigo de \(n=26\)**.

## Conclusión

El objetivo solicitado —una configuración estricta y reproducible por encima de `2.6359830853`— permanece sin cumplir.

El resultado positivo de la investigación es más limitado, pero sólido:

\[
\boxed{
2.63598308491760778318656948544348\ldots
}
\]

es la raíz multiprecisión del grafo de contactos dominante y el mejor resultado geométrico estricto que he podido reproducir. La configuración es un máximo local aislado, todos sus vecinos de un contacto son inferiores y una exploración amplia de capas topológicas posteriores tampoco encontró mejora.

La ruta que queda con mayor valor científico no es más pulido SLSQP. Es completar una búsqueda dirigida por el grafo de vértices, incluyendo los vértices silla con multiplicadores positivos, y exigir certificación intervalar a cualquier candidato que supere `2.635983084917607…`.

