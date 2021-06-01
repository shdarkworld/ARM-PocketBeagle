# Modelo Autorregresivo para pronóstico de series de tiempo (Temperatura) utilizando una Pocket Beagle y un sensor LM35 con Python
# por bloques y sobre muestra actual

import Adafruit_BBIO.ADC as ADC
import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy import linalg

def err_arg():
    print("Error")
    print("Número incorrecto de argumentos y/o argumento incorrecto")
    print("Utilice <<bloques>> para realizar una predicción sobre los datos contenidos en <<data_temp.csv>>")
    print("Utilice <<actual>> para predecir la temperatura actual y compararla con la temperatura medida")
    print("Utilice <<ayuda>> para obtener más información")
    return

def ayuda():
    print("Utilice <<bloques>> para realizar una predicción sobre los datos contenidos en <<data_temp.csv>>")
    print("<<bloques>> permite seleccionar el número de predicciones -h- a calcular basadas en AR de y(t) sobre los lags x(t-h)")
    print()
    print("Utilice <<actual>> para predecir la temperatura actual y compararla con la temperatura medida")
    print("<<actual>> compara la última predicción con la temperatura actual a partir de las mediciones anteriores y actualiza <<data_temp.csv>> con el valor actual")
    print("Asegúrese de conectar un sensor de temperatura lineal como el LM35 al pin AIN0 de la Beagle")
    print()
    print("Utilice <<reset>> para restablecer los valores por defecto contenidos en <<data_temp.csv>> y <<fcast_temp.csv>>")
    return

def finalizado():
    print("Ejecutado con éxito")
    return

if len(sys.argv) != 2:
    # Verifica si el número de argumentos es correto
    err_arg()

print("Ejecutando...")
ts = np.loadtxt('data_temp.csv', delimiter = ',', unpack = True)
l = len(ts)
P = len(ts)-1

# Máximo número de retrasos (lags) p
p = int(np.round(np.sqrt(P)/2))

# Criterio de Akaike (AIC)
# determina cómo se adaptan los datos al modelo (Ar)
# a partir de los retrasos (lags) mediante el algoritmo AIC
AIC = np.zeros((p,1))

for i in range(p):
    z = np.zeros((l-i-1, i+2))

    # dividiendo el vector de datos en retrasos (lags)
    for j in range(i+2):
        z[:,j] = ts[j:len(ts)-i-1+j]

    y = z[:,0]
    ly = len(y)

    x = z[:,1:len(z)-1]

    phi = linalg.lstsq((x.T @ x),(x.T @ y)) # solución

    yfit = x @ phi[0] # sal adaptada (pred)
    e = yfit - y      # error

    sig = (e.T @ e)/ly # valor de la función de prob
    AIC[i] = np.log(sig)+2*(i+1)/l

Aans = np.where(min(AIC)) # elige el mejor número de lags
p = int(Aans[0])          # n lags

y = ts[p+1: ]   # variable dependiente a partir de los lags
xl = np.zeros((len(ts)-1, p+1)) 

for i in range(p+1):        # lags
    xl[:,i] = ts[p-i:len(ts)-i-1]

############################################################
# Forecast (Predicción)

# Por bloque de datos
# La predicción se basa en AR de y(t) sobre los lags x(t-h)
# Grafica la tendencia de la temperatura a partir de la cantidad de 
# predicciones deseada

if sys.argv[1] == "bloques":
    h = int(input("Ingrese el número de predicciones a obtener:  "))
    while(h >= l): # Revisar si el no. de predicciones no excede la cantidad de datos
        print("Verifique que el número de predicciones no exceda el número de total de datos anteriores")
        print("Total datos anteriores:  ", l)
        h = int(input("Ingrese el número de predicciones a obtener:  "))
    F = np.zeros((h,1))     # vector de predicciones
    for i in range(h):
        xh = xl[0:len(x)-i+1]
        yh = np.array(y[i: ])
        phih = linalg.lstsq((xh.T @ xh),(xh.T @ yh.T))
        F[i] = np.array(y[(len(y)-p-1):len(y)]).T @ phih[0]

    print("Temperatura pronosticada:  ", F, "°C")
    
    # Graficar tendencia
    plt.plot(F, '-r')
    plt.title('Tendencia temperatura pronosticada')
    plt.xlabel('N. Predicciones')
    plt.ylabel('Temperatura °C')
    plt.ylim([0, 30])
    plt.show()
    plt.savefig('Graph_tend.png')
    
    finalizado()

# A partir de la penúltima medición
# compara la última predicción con el valor medido
# y actualiza el vector de datos con la última medición
# Mide la temperatura a través del ADC0 de la Beagle 
# mediante un sensor de temperatura lineal como el LM35
# Grafica las últimas 10 muestras de la temperatura actual
# contra la pronosticada

elif sys.argv[1] == "actual":
    h = 1
    F = np.zeros((h,1))
    y = np.array(y)
    phi = linalg.lstsq((xl.T @ xl), (xl.T @ y.T))
    Y = np.zeros((len(y) + h, 1))

    for i in range(len(y)):
        Y[i,0] = y[i]

    for i in range(h):
        F[i] = np.array(Y[(len(Y)-p-1-h+i):len(Y)-h+i,0]).T @ phi[0]
        Y[len(y)+i] = F[i]

    fcast = Y[len(Y)-h: len(Y)]
    print("Temperatura pronosticada:  ", fcast, "°C")

    ADC.setup()
    val = ADC.read("AIN0")
    temp = val*180          # Temp = ADC*1.8V/10mV/°C
    print("Temperatura actual:  ", temp, "°C")

    err = np.abs((temp - fcast[-1])/temp * 100)
    print("El error de la predicción es de  :", err, "%")

    # Actualizar csv de datos
    data = np.zeros((1,len(ts)+h))
    data[0,0:len(data)-1-h] = ts
    data[0, -1] = temp
    np.savetxt('data_temp.csv', data, fmt='%s', delimiter=',')
    
    # Actualizar csv de predicciones
    tf = np.loadtxt('fcast_temp.csv', delimiter = ',', unpack = True)
    pred = np.zeros((1,len(tf)+h))
    pred[0,0:len(pred)-1-h] = tf
    pred[0, -1] = fcast[-1]
    np.savetxt('fcast_temp.csv', pred, fmt='%s', delimiter=',')
    
    # Graficar Temperatura real vs pronosticada
    n_data = 10
    plt.plot(data[0,-n_data: ], '-b', label="Temperatura real")
    plt.plot(pred[0,-n_data: ], '-r', label="Temperatura pronosticada")
    plt.title('Temperatura real vs Temperatura pronosticada')
    plt.xlabel('Últimas 10 muestras')
    plt.ylabel('Temperatura °C')
    plt.legend(loc='lower left')
    plt.ylim([0, 30])
    plt.show()
    plt.savefig('Graph_temp.png')
    
    
    finalizado()

elif sys.argv[1] == "reset":
    data = np.zeros((1,10))
    data[0,:] = [25.0,24.0,23.0,25.0,24.0,23.0,25.0,24.0,23.0,25.0]
    np.savetxt('data_temp.csv', data, fmt='%s', delimiter=',')
    fcast = data
    np.savetxt('fcast_temp.csv', fcast, fmt='%s', delimiter=',')
    print("Datos restablecidos a valores por defecto")
    finalizado()
    
elif sys.argv[1] == "ayuda":
    ayuda()

else:
    err_arg()
