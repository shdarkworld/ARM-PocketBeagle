# Modelo Autorregresivo para pronóstico de series de tiempo (Temperatura) utilizando una Pocket Beagle y un sensor LM35 con Python

El Pronóstico de la temperatura se obtiene a través del ajuste de los coeficientes del modelo Autorregresivo sobre las muestras de temperatura anterior.

$X(t+1) = \phi_0 + \phi_1 X(t-1) + \phi_2 X(t-2) + ... $

Los coeficientes $\phi_n$ se ajustan mediante un proceso iterativo de mínimos cuadrados a partir de las muestras de temperatura anteriores (lags).

> Se utiliza el criterio de Akaike (AIC) para determinar cómo se adaptan los datos al modelo **AR** a partir de los retrasos (lags).

## Clonar repositorio a la Pocket Beagle

Puede descargar el repositorio en Github o clonarlo directamente a la Pocket Beagle mediante *git clone* en la terminal.

		git clone https://github.com/shdarkworld/ARM-PocketBeagle

## Conexión sensor LM35 y Pocket Beagle

El Sensor de temperatura **LM35** entrega un voltaje que varía de forma lineal con la temperatura (en grados celsius) de **10mV/°C** en un rango de **0 a 150 °C** y puede operar con los **3.3V** proporcionados por la Pocket Beagle.

El pin **Vs+** se conecta directamente a los 3.3V de la Beagle, **GND** a su homólogo y **Vout** al pin 0 del ADC (**AIN0**).

```
	     USB  ^	
		  |	 -------------------          --------------
		  |	|		    |        |     LM35     |
	          ------|      		    |        | Vs+ Vout GND |
			|      Pocket	    |	      --------------
			|      Beagle	    |		|   |   |
			|		    |		|   |   |
			|	       3.3V |------------   |   |
			|	       AIN0 |----------------   |
			|	        GND |-------------------- 
			|		    |
			 ------------------- 

```
>**Nota:**
>**Debido a la salida del sensor y sus características, no es necesario un circuito de protección adicional.**

# Ejecución del Script
Utilice el argumento **bloques** para realizar una predicción sobre los datos contenidos en *data_temp.csv*.

		python3 AR_fcast.py bloques

El argumento **bloques** permite seleccionar el número de predicciones **h** a calcular, basadas en el modelo **AR** de $y(t)$ sobre los lags (retrasos) $x(t-h)$

La gráfica de la tendencia de la Temperatura a partir de las predicciones se almacena en *Graph_tend.png*
>Verifique que el número de predicciones no exceda el número de total de datos anteriores en *data_temp.csv*
___

Utilice el argumento **actual** para predecir la temperatura actual y compararla con la temperatura medida.
	
		python3 AR_fcast.py actual

Al utilizar el argumento **actual** se compara la última predicción con la temperatura actual a partir de las mediciones anteriores y actualiza los datos contenidos en *data_temp.csv* con el valor actual y los contenidos en *fcast_temp.csv* con la temperatura pronosticada. Así mismo muestra el error de la predicción.

La gráfica de la temperatura medida contra la pronosticada se almacena en *Graph_temp.png*.

>**Asegúrese de conectar un sensor de temperatura lineal como el LM35 al pin AIN0 de la Pocket Beagle**

---
En el caso de que se desee restaurar los valores por defecto de los datos en *data_temp.csv* y *fcast_temp.csv* utilice el argumento **reset**

		python3 AR_fcast.py reset

---
Utilice el argumento **ayuda** para obtener más información.

		python3 AR_fcast.py ayuda

---
Cualquier otro argumento (o ausencia de él) proporcionará un mensaje de error.


>### Disclaimer
>La ejecución del script está pensada para el pronóstico de la temperatura ambiente. No intente utilizarlo para otras aplicaciones, **podría dañar el dispositivo o el sensor**.
