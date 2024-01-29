
# Simulación de Incendios Forestales

Este repositorio contiene un programa en Python para simular la propagación de incendios forestales. El programa calcula diversas métricas como la tasa de propagación del fuego, la intensidad del fuego y la extensión del área afectada, entre otras. Originalmente desarrollado en MATLAB, este código ha sido convertido a Python para una mayor accesibilidad y facilidad de uso.

## Requisitos

- Python 3.8.18
- Jupyter Notebook
- Bibliotecas de Python: pandas, math, numpy

## Instalación

No se requiere una instalación especial para ejecutar este programa, siempre y cuando se disponga de un entorno Python con las bibliotecas mencionadas. 

## Ejecución

Para ejecutar el programa, abra el Jupyter Notebook que contiene el código y ejecutelo celda por celda. Asegurese de que todas las funciones auxiliares y los datos necesarios estén disponibles en el Notebook o importados adecuadamente.

Puede modificar la parte de #Inputs para probar algunas cosas.

### Ejemplo de Uso

El siguiente ejemplo muestra cómo podría configurar y ejecutar una simulación básica:

```python
# Configuración de parámetros iniciales
ftype = "C1"  # Tipo de combustible
lat, long = 51.621244, -115.608378  # Coordenadas geográficas
elev = 2138.0  # Elevación
ps, saz = 0, 0  # Pendiente y azimut de la pendiente

# Ejecución de la simulación
ros, wsv, raz, isi = rate_of_spread(ftype, wdfh, a, b, c, ps, saz, FuelConst2, bui0, q)

# Continúa con el resto de las funciones y cálculos como se muestra en el código
```

