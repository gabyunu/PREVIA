// Copia de la propuesta del usuario; no es catálogo oficial. Solo H01-C.
export const PILOT_CATALOG = [
  {
    "id_referencia": "P01-01",
    "semestre_curricular": 1,
    "asignatura": "Cálculo I",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Ninguno",
    "prerrequisitos_ids": [],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "ninguno_explicito_propuesto",
    "revision_pendiente": false,
    "demostracion_elegibilidad_calculable": true
  },
  {
    "id_referencia": "P01-02",
    "semestre_curricular": 1,
    "asignatura": "Álgebra Lineal",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Ninguno",
    "prerrequisitos_ids": [],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "ninguno_explicito_propuesto",
    "revision_pendiente": false,
    "demostracion_elegibilidad_calculable": true
  },
  {
    "id_referencia": "P01-03",
    "semestre_curricular": 1,
    "asignatura": "Química I",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Ninguno",
    "prerrequisitos_ids": [],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "ninguno_explicito_propuesto",
    "revision_pendiente": false,
    "demostracion_elegibilidad_calculable": true
  },
  {
    "id_referencia": "P01-04",
    "semestre_curricular": 1,
    "asignatura": "Biología I",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Ninguno",
    "prerrequisitos_ids": [],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "ninguno_explicito_propuesto",
    "revision_pendiente": false,
    "demostracion_elegibilidad_calculable": true
  },
  {
    "id_referencia": "P01-05",
    "semestre_curricular": 1,
    "asignatura": "Inglés III",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Inglés II*",
    "prerrequisitos_ids": [],
    "prerrequisitos_fuera_de_malla": [
      "Inglés II"
    ],
    "estado_regla": "prerrequisitos_asignaturas_propuestos",
    "revision_pendiente": true,
    "demostracion_elegibilidad_calculable": false
  },
  {
    "id_referencia": "P02-01",
    "semestre_curricular": 2,
    "asignatura": "Cálculo II",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Cálculo I",
    "prerrequisitos_ids": [
      "P01-01"
    ],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "prerrequisitos_asignaturas_propuestos",
    "revision_pendiente": false,
    "demostracion_elegibilidad_calculable": true
  },
  {
    "id_referencia": "P02-02",
    "semestre_curricular": 2,
    "asignatura": "Ciencias de la Tierra",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Ninguno identificado",
    "prerrequisitos_ids": [],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "ninguno_identificado_sin_confirmar",
    "revision_pendiente": true,
    "demostracion_elegibilidad_calculable": false
  },
  {
    "id_referencia": "P02-03",
    "semestre_curricular": 2,
    "asignatura": "Física I",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Cálculo I",
    "prerrequisitos_ids": [
      "P01-01"
    ],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "prerrequisitos_asignaturas_propuestos",
    "revision_pendiente": false,
    "demostracion_elegibilidad_calculable": true
  },
  {
    "id_referencia": "P02-04",
    "semestre_curricular": 2,
    "asignatura": "Biología II",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Biología I",
    "prerrequisitos_ids": [
      "P01-04"
    ],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "prerrequisitos_asignaturas_propuestos",
    "revision_pendiente": false,
    "demostracion_elegibilidad_calculable": true
  },
  {
    "id_referencia": "P02-05",
    "semestre_curricular": 2,
    "asignatura": "Inglés IV",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Inglés III",
    "prerrequisitos_ids": [
      "P01-05"
    ],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "prerrequisitos_asignaturas_propuestos",
    "revision_pendiente": false,
    "demostracion_elegibilidad_calculable": true
  },
  {
    "id_referencia": "P03-01",
    "semestre_curricular": 3,
    "asignatura": "Ecuaciones Diferenciales",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Cálculo II",
    "prerrequisitos_ids": [
      "P02-01"
    ],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "prerrequisitos_asignaturas_propuestos",
    "revision_pendiente": false,
    "demostracion_elegibilidad_calculable": true
  },
  {
    "id_referencia": "P03-02",
    "semestre_curricular": 3,
    "asignatura": "Probabilidad y Estadística",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Cálculo II, Álgebra Lineal",
    "prerrequisitos_ids": [
      "P02-01",
      "P01-02"
    ],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "prerrequisitos_asignaturas_propuestos",
    "revision_pendiente": false,
    "demostracion_elegibilidad_calculable": true
  },
  {
    "id_referencia": "P03-03",
    "semestre_curricular": 3,
    "asignatura": "Física II",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Física I",
    "prerrequisitos_ids": [
      "P02-03"
    ],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "prerrequisitos_asignaturas_propuestos",
    "revision_pendiente": false,
    "demostracion_elegibilidad_calculable": true
  },
  {
    "id_referencia": "P03-04",
    "semestre_curricular": 3,
    "asignatura": "Química II",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Química I",
    "prerrequisitos_ids": [
      "P01-03"
    ],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "prerrequisitos_asignaturas_propuestos",
    "revision_pendiente": false,
    "demostracion_elegibilidad_calculable": true
  },
  {
    "id_referencia": "P03-05",
    "semestre_curricular": 3,
    "asignatura": "Introducción a las Ciencias e Ingenierías",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Ninguno identificado",
    "prerrequisitos_ids": [],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "ninguno_identificado_sin_confirmar",
    "revision_pendiente": true,
    "demostracion_elegibilidad_calculable": false
  },
  {
    "id_referencia": "P03-06",
    "semestre_curricular": 3,
    "asignatura": "Inglés V",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Inglés IV",
    "prerrequisitos_ids": [
      "P02-05"
    ],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "prerrequisitos_asignaturas_propuestos",
    "revision_pendiente": false,
    "demostracion_elegibilidad_calculable": true
  },
  {
    "id_referencia": "P04-01",
    "semestre_curricular": 4,
    "asignatura": "Cálculo III",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Cálculo II",
    "prerrequisitos_ids": [
      "P02-01"
    ],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "prerrequisitos_asignaturas_propuestos",
    "revision_pendiente": false,
    "demostracion_elegibilidad_calculable": true
  },
  {
    "id_referencia": "P04-02",
    "semestre_curricular": 4,
    "asignatura": "Matemáticas Discretas",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Cálculo I",
    "prerrequisitos_ids": [
      "P01-01"
    ],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "prerrequisitos_asignaturas_propuestos",
    "revision_pendiente": false,
    "demostracion_elegibilidad_calculable": true
  },
  {
    "id_referencia": "P04-03",
    "semestre_curricular": 4,
    "asignatura": "Electrónica",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Física I",
    "prerrequisitos_ids": [
      "P02-03"
    ],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "prerrequisitos_asignaturas_propuestos",
    "revision_pendiente": false,
    "demostracion_elegibilidad_calculable": true
  },
  {
    "id_referencia": "P04-04",
    "semestre_curricular": 4,
    "asignatura": "Introducción a la Programación",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Calculo I, Algebra Lineal",
    "prerrequisitos_ids": [
      "P01-01",
      "P01-02"
    ],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "prerrequisitos_asignaturas_propuestos",
    "revision_pendiente": false,
    "demostracion_elegibilidad_calculable": true
  },
  {
    "id_referencia": "P04-05",
    "semestre_curricular": 4,
    "asignatura": "Inglés VI",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Inglés V",
    "prerrequisitos_ids": [
      "P03-06"
    ],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "prerrequisitos_asignaturas_propuestos",
    "revision_pendiente": false,
    "demostracion_elegibilidad_calculable": true
  },
  {
    "id_referencia": "P05-01",
    "semestre_curricular": 5,
    "asignatura": "Métodos Numéricos",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Cálculo II",
    "prerrequisitos_ids": [
      "P02-01"
    ],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "prerrequisitos_asignaturas_propuestos",
    "revision_pendiente": false,
    "demostracion_elegibilidad_calculable": true
  },
  {
    "id_referencia": "P05-02",
    "semestre_curricular": 5,
    "asignatura": "Lógica Matemática y Computacional",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Matemáticas Discretas",
    "prerrequisitos_ids": [
      "P04-02"
    ],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "prerrequisitos_asignaturas_propuestos",
    "revision_pendiente": false,
    "demostracion_elegibilidad_calculable": true
  },
  {
    "id_referencia": "P05-03",
    "semestre_curricular": 5,
    "asignatura": "Álgebra Lineal y Multilineal",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Álgebra Lineal",
    "prerrequisitos_ids": [
      "P01-02"
    ],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "prerrequisitos_asignaturas_propuestos",
    "revision_pendiente": false,
    "demostracion_elegibilidad_calculable": true
  },
  {
    "id_referencia": "P05-04",
    "semestre_curricular": 5,
    "asignatura": "Programación Avanzada",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Introducción a la Programación",
    "prerrequisitos_ids": [
      "P04-04"
    ],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "prerrequisitos_asignaturas_propuestos",
    "revision_pendiente": false,
    "demostracion_elegibilidad_calculable": true
  },
  {
    "id_referencia": "P05-05",
    "semestre_curricular": 5,
    "asignatura": "Arquitectura de Computadores",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Electrónica",
    "prerrequisitos_ids": [
      "P04-03"
    ],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "prerrequisitos_asignaturas_propuestos",
    "revision_pendiente": false,
    "demostracion_elegibilidad_calculable": true
  },
  {
    "id_referencia": "P05-06",
    "semestre_curricular": 5,
    "asignatura": "Metodología de la Investigación Científica",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Ninguno identificado",
    "prerrequisitos_ids": [],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "ninguno_identificado_sin_confirmar",
    "revision_pendiente": true,
    "demostracion_elegibilidad_calculable": false
  },
  {
    "id_referencia": "P06-01",
    "semestre_curricular": 6,
    "asignatura": "Matemáticas Avanzadas para la Ciencia y la Ingeniería",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Cálculo III",
    "prerrequisitos_ids": [
      "P04-01"
    ],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "prerrequisitos_asignaturas_propuestos",
    "revision_pendiente": false,
    "demostracion_elegibilidad_calculable": true
  },
  {
    "id_referencia": "P06-02",
    "semestre_curricular": 6,
    "asignatura": "Análisis de Algoritmos",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Programación Avanzada, Matemáticas Discretas",
    "prerrequisitos_ids": [
      "P05-04",
      "P04-02"
    ],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "prerrequisitos_asignaturas_propuestos",
    "revision_pendiente": false,
    "demostracion_elegibilidad_calculable": true
  },
  {
    "id_referencia": "P06-03",
    "semestre_curricular": 6,
    "asignatura": "Redes",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Introducción a la programación",
    "prerrequisitos_ids": [
      "P04-04"
    ],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "prerrequisitos_asignaturas_propuestos",
    "revision_pendiente": false,
    "demostracion_elegibilidad_calculable": true
  },
  {
    "id_referencia": "P06-04",
    "semestre_curricular": 6,
    "asignatura": "Bases de Datos",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Introducción a la programación",
    "prerrequisitos_ids": [
      "P04-04"
    ],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "prerrequisitos_asignaturas_propuestos",
    "revision_pendiente": false,
    "demostracion_elegibilidad_calculable": true
  },
  {
    "id_referencia": "P06-05",
    "semestre_curricular": 6,
    "asignatura": "Sistemas Operativos",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Arquitectura de Computadores",
    "prerrequisitos_ids": [
      "P05-05"
    ],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "prerrequisitos_asignaturas_propuestos",
    "revision_pendiente": false,
    "demostracion_elegibilidad_calculable": true
  },
  {
    "id_referencia": "P06-06",
    "semestre_curricular": 6,
    "asignatura": "Ética Aplicada",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Ninguno identificado",
    "prerrequisitos_ids": [],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "ninguno_identificado_sin_confirmar",
    "revision_pendiente": true,
    "demostracion_elegibilidad_calculable": false
  },
  {
    "id_referencia": "P07-01",
    "semestre_curricular": 7,
    "asignatura": "Métodos de Optimización",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Programación avanzada",
    "prerrequisitos_ids": [
      "P05-04"
    ],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "prerrequisitos_asignaturas_propuestos",
    "revision_pendiente": false,
    "demostracion_elegibilidad_calculable": true
  },
  {
    "id_referencia": "P07-02",
    "semestre_curricular": 7,
    "asignatura": "Inteligencia Artificial",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Programación Avanzada",
    "prerrequisitos_ids": [
      "P05-04"
    ],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "prerrequisitos_asignaturas_propuestos",
    "revision_pendiente": false,
    "demostracion_elegibilidad_calculable": true
  },
  {
    "id_referencia": "P07-03",
    "semestre_curricular": 7,
    "asignatura": "Sistemas Distribuidos",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Redes",
    "prerrequisitos_ids": [
      "P06-03"
    ],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "prerrequisitos_asignaturas_propuestos",
    "revision_pendiente": false,
    "demostracion_elegibilidad_calculable": true
  },
  {
    "id_referencia": "P07-04",
    "semestre_curricular": 7,
    "asignatura": "Ingeniería de Software",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Programación Avanzada",
    "prerrequisitos_ids": [
      "P05-04"
    ],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "prerrequisitos_asignaturas_propuestos",
    "revision_pendiente": false,
    "demostracion_elegibilidad_calculable": true
  },
  {
    "id_referencia": "P07-05",
    "semestre_curricular": 7,
    "asignatura": "Asignatura de Itinerario I",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Depende del itinerario elegido",
    "prerrequisitos_ids": [],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "depende_del_itinerario_no_definido",
    "revision_pendiente": true,
    "demostracion_elegibilidad_calculable": false
  },
  {
    "id_referencia": "P07-06",
    "semestre_curricular": 7,
    "asignatura": "Innovación y Transferencia Tecnológica",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Ninguno identificado",
    "prerrequisitos_ids": [],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "ninguno_identificado_sin_confirmar",
    "revision_pendiente": true,
    "demostracion_elegibilidad_calculable": false
  },
  {
    "id_referencia": "P08-01",
    "semestre_curricular": 8,
    "asignatura": "Teoría de la Computación",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Análisis de algoritmos",
    "prerrequisitos_ids": [
      "P06-02"
    ],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "prerrequisitos_asignaturas_propuestos",
    "revision_pendiente": false,
    "demostracion_elegibilidad_calculable": true
  },
  {
    "id_referencia": "P08-02",
    "semestre_curricular": 8,
    "asignatura": "Asignatura de Itinerario II",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Depende del itinerario",
    "prerrequisitos_ids": [],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "depende_del_itinerario_no_definido",
    "revision_pendiente": true,
    "demostracion_elegibilidad_calculable": false
  },
  {
    "id_referencia": "P08-03",
    "semestre_curricular": 8,
    "asignatura": "Asignatura de Itinerario III",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Depende del itinerario",
    "prerrequisitos_ids": [],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "depende_del_itinerario_no_definido",
    "revision_pendiente": true,
    "demostracion_elegibilidad_calculable": false
  },
  {
    "id_referencia": "P08-04",
    "semestre_curricular": 8,
    "asignatura": "Asignatura de Itinerario IV",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Depende del itinerario",
    "prerrequisitos_ids": [],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "depende_del_itinerario_no_definido",
    "revision_pendiente": true,
    "demostracion_elegibilidad_calculable": false
  },
  {
    "id_referencia": "P08-05",
    "semestre_curricular": 8,
    "asignatura": "Asignatura de Itinerario V",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Depende del itinerario",
    "prerrequisitos_ids": [],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "depende_del_itinerario_no_definido",
    "revision_pendiente": true,
    "demostracion_elegibilidad_calculable": false
  },
  {
    "id_referencia": "P08-06",
    "semestre_curricular": 8,
    "asignatura": "Taller de Comunicación Científica",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Metodología de la Investigación Científica",
    "prerrequisitos_ids": [
      "P05-06"
    ],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "prerrequisitos_asignaturas_propuestos",
    "revision_pendiente": false,
    "demostracion_elegibilidad_calculable": true
  },
  {
    "id_referencia": "P09-01",
    "semestre_curricular": 9,
    "asignatura": "Proyecto de Titulación I",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Condiciones de titulación por verificar",
    "prerrequisitos_ids": [],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "requisito_no_definido",
    "revision_pendiente": true,
    "demostracion_elegibilidad_calculable": false
  },
  {
    "id_referencia": "P09-02",
    "semestre_curricular": 9,
    "asignatura": "Asignatura de Itinerario VI",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Depende del itinerario",
    "prerrequisitos_ids": [],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "depende_del_itinerario_no_definido",
    "revision_pendiente": true,
    "demostracion_elegibilidad_calculable": false
  },
  {
    "id_referencia": "P09-03",
    "semestre_curricular": 9,
    "asignatura": "Asignatura de Itinerario VII",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Depende del itinerario",
    "prerrequisitos_ids": [],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "depende_del_itinerario_no_definido",
    "revision_pendiente": true,
    "demostracion_elegibilidad_calculable": false
  },
  {
    "id_referencia": "P09-04",
    "semestre_curricular": 9,
    "asignatura": "Asignatura de Itinerario VIII",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Depende del itinerario",
    "prerrequisitos_ids": [],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "depende_del_itinerario_no_definido",
    "revision_pendiente": true,
    "demostracion_elegibilidad_calculable": false
  },
  {
    "id_referencia": "P09-05",
    "semestre_curricular": 9,
    "asignatura": "Asignatura de Itinerario IX",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Depende del itinerario",
    "prerrequisitos_ids": [],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "depende_del_itinerario_no_definido",
    "revision_pendiente": true,
    "demostracion_elegibilidad_calculable": false
  },
  {
    "id_referencia": "P10-01",
    "semestre_curricular": 10,
    "asignatura": "Proyecto de Titulación II",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Proyecto de Titulación I",
    "prerrequisitos_ids": [
      "P09-01"
    ],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "prerrequisitos_asignaturas_propuestos",
    "revision_pendiente": false,
    "demostracion_elegibilidad_calculable": true
  },
  {
    "id_referencia": "P10-02",
    "semestre_curricular": 10,
    "asignatura": "Redacción de Proyecto de Investigación",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Requisito por verificar",
    "prerrequisitos_ids": [],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "requisito_no_definido",
    "revision_pendiente": true,
    "demostracion_elegibilidad_calculable": false
  },
  {
    "id_referencia": "P10-03",
    "semestre_curricular": 10,
    "asignatura": "Integración Profesional y Social",
    "codigo_institucional": null,
    "prerrequisito_texto_original": "Requisitos institucionales de prácticas por verificar",
    "prerrequisitos_ids": [],
    "prerrequisitos_fuera_de_malla": [],
    "estado_regla": "requisito_no_definido",
    "revision_pendiente": true,
    "demostracion_elegibilidad_calculable": false
  }
] as const;
