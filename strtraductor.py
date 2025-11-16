import re 

def conseguirtodaspromedioaltura(cadena, sort_list):
    alturas=[]
    divicion=0
    for i in range(len(sort_list)): 
        if cadena[i]=="div" or cadena[i]=="-": 
            continue
        else: 
            x,y,w,h = sort_list[i][1]
            alturas.append(h)
            divicion += 1
            
    promedio=sum(alturas)/divicion
    
    return promedio   

def conseguirtodaslasfracciones(cadena, sort_list, centros):
    # Lista para almacenar los índices de las fracciones encontradas
    fracciones = []
    # Lista para almacenar las cadenas de fracciones
    cadenadefracciones = []

    # Encontrar los índices de las divisiones en la cadena
    indices_division = [indice for indice, elemento in enumerate(cadena) if elemento == "div"] 
    # Para almacenar los indices de las diviciones de las fracciones encontradas
    diviones12=[]

    # Iterar sobre cada índice de división encontrado
    for divicion in indices_division:

        # Obtener las coordenadas de la división actual
        x_div, y_div, w_div, _ = sort_list[divicion][1]
        ancho = x_div + w_div
        centro_div = centros[divicion]
        
        # Calcular la altura de un dígito
        altura_digito = conseguirtodaspromedioaltura(cadena, sort_list)*0.9
        
        D_adiviciones=[]
        
        for indice2 in indices_division:
            _,yi=centros[indice2]
            if abs(yi-y_div)>altura_digito:
                D_adiviciones.append(indice2)

        # Listas para almacenar los índices de los numeradores y denominadores de la fracción actual
        numerador = []
        denominador = []

        # Iterar sobre cada dígito en la cadena
        for digito in range(len(sort_list)): 

            # Saltar la división actual
            if digito == divicion:
                continue

            x1, y1 = centros[digito]

            # Verificar si el dígito está dentro del rango de la división actual
            if x_div < x1 < ancho:
                if y1 < centro_div[1]:
                    # Si el dígito está por encima del centro de la división, es parte del numerador
                    numerador.append(digito)
                else:
                    # Si el dígito está por debajo del centro de la división, es parte del denominador
                    denominador.append(digito)
                
        digitostotal = numerador + denominador
        
        digitosquitar = []
        
        for diviciones in D_adiviciones: 
            for digito in digitostotal: 
                
                centrodiv = centros[diviciones]
                centrodig = centros[digito]
                
                if centros[divicion][1] < centrodiv[1]: 
                    if centrodig[1]>centrodiv[1]: 
                        digitosquitar.append(digito)
                else: 
                    if centrodig[1]<centrodiv[1]:
                        digitosquitar.append(digito)
        
        digitosquitar.extend(D_adiviciones)
        
        # Quitar digitosquitar de Numerador y denominador
        for i in digitosquitar: 
            if i in numerador:
                numerador.remove(i) 
            if i in denominador: 
                denominador.remove(i) 

        # Ordenar los índices del numerador y del denominador según su posición horizontal
        numerador.sort(key=lambda i: centros[i][0])
        denominador.sort(key=lambda i: centros[i][0])

        # Construir la lista de índices que representa la fracción actual
        fraccion = numerador + [divicion] + denominador
        diviones12.append(divicion)
        fracciones.append(fraccion)

        # Construir la cadena de la fracción actual
        numerador_str = ''.join(cadena[i] for i in numerador) if numerador else '0'
        denominador_str = ''.join(cadena[i] for i in denominador) if denominador else '1'
        cadenafraccion = f"¿¿{numerador_str}?/¿{denominador_str}??"
        cadenadefracciones.append(cadenafraccion)

    # Eliminamos las fracciones que sean intersección de dos fracciones distintas
    
    for fraccion, cadenafraccion in zip(fracciones[:], cadenadefracciones[:]):  # Itera sobre copias de las listas
        
        fraccionesqueintersecta = []
        
        for j in fraccion: 
            for fraccion2 in fracciones: 
                if fraccion2 == fraccion:
                    continue
                if j in fraccion2: 
                    if fraccion2 not in fraccionesqueintersecta: 
                        fraccionesqueintersecta.append(fraccion2)
                            
        if len(fraccionesqueintersecta) > 1:
            fracciones.remove(fraccion)
            cadenadefracciones.remove(cadenafraccion)
        if len(fraccionesqueintersecta) == 1 and  len(fracciones)==2:
            _, _, w, _ = sort_list[diviones12[0]][1]
            _, _, w1, _ = sort_list[diviones12[1]][1]
            if w>w1:
                fracciones.pop(0)
                cadenadefracciones.pop(0)
            else: 
                fracciones.pop(1)
                cadenadefracciones.pop(1)
                
    return fracciones, cadenadefracciones

def divatex(cadena, sort_list, centros):
    
    # Imprimir la cadena de entrada
    print(f"Cadena: {cadena}")
    print(f"Iniciando proceso de división de la cadena...")

    indicesfracciones = []  # Lista para almacenar los índices de fracciones encontradas

    # Verificar si hay divisiones en la cadena
    if "div" in cadena:
        print("Se encontró al menos una división en la cadena.")
        
        fracciones = []  # Lista para almacenar las fracciones encontradas
        indices_division = [indice for indice, elemento in enumerate(cadena) if elemento == "div"]  # Obtener los índices de las divisiones
        
        indices_num_dem = indices_division  # Lista de índices de numerador y denominador

        # Iterar sobre cada índice de división encontrado
        for indice in indices_division:
            print(f"Procesando división en el índice {indice}.")

            # Obtener las coordenadas de la división actual
            x, y, w, h = sort_list[indice][1]
            
            numerador = ""  # Inicializar el numerador
            denominador = ""  # Inicializar el denominador
            
            centro_div = centros[indice]  # Coordenadas del centro de la división
            
            nume = []  # Lista de índices del numerador
            deno = []  # Lista de índices del denominador
            
            # Iterar sobre cada dígito en la cadena
            for j in range(len(cadena)):
                if cadena[j] == "div":
                    continue
                
                x1, y1 = centros[j]
                
                # Verificar si el dígito está dentro del rango de la división actual
                if x < x1 < x+w:
                    if y1 < centro_div[1]:  # Si está por encima del centro de la división
                        numerador += cadena[j]
                        if j not in indices_num_dem:
                            indices_num_dem.append(j)
                            nume.append(j)
                    else:  # Si está por debajo del centro de la división
                        denominador += cadena[j]
                        if j not in indices_num_dem:
                            indices_num_dem.append(j)
                            deno.append(j)
            
            nuevalista = []  # Lista para almacenar los índices de la fracción actual
            nuevalista.extend(nume)
            nuevalista.append(indice)
            nuevalista.extend(deno)
            
            if nuevalista not in indicesfracciones:
                indicesfracciones.append(nuevalista)

            # Imprimir los elementos encontrados
            print("Elementos encontrados para la fracción:")
            print(f"Numerador: {numerador}")
            print(f"Denominador: {denominador}")
            
            # Construir la fracción con el numerador y el denominador seleccionados
            if numerador and denominador:  # Verificar que ambos no estén vacíos
                fraccion = f"¿¿{numerador}?/¿{denominador}??"
                
                if fraccion not in fracciones:  # Verificar si la fracción ya existe en la lista
                    fracciones.append(fraccion)
                    
        # Imprimir las fracciones encontradas
        print("Fracciones encontradas:")
        print(fracciones)

        # Crear la cadena final con "R" en las posiciones correspondientes
        cadena_final = ""
        
        for i in range(len(cadena)):
            if i in indices_num_dem:
                cadena_final += "R"
            else:
                cadena_final += cadena[i]
                
        cadena_final = re.sub(r"R+", "R", cadena_final)  # Reemplazar "RR" con "R"
        
        print("Cadena final antes de reemplazar las fracciones:")
        print(cadena_final)
        
        indice_fraccion = 0  # Inicializar el índice de la fracción
        
        # Iterar sobre cada caracter en la cadena final
        aux = 0
        for i, caracter in enumerate(cadena_final):
            if caracter == "R":
                # Reemplazar la "R" con la fracción correspondiente
                cadena_final = cadena_final[:i+aux] + fracciones[indice_fraccion] + cadena_final[i+1+aux:]
                aux += len(fracciones[indice_fraccion]) - 1  # Actualizar el desplazamiento
                indice_fraccion += 1  # Mover al siguiente índice de fracciones
        
        # Imprimir la cadena final después de reemplazar las fracciones
        print("Cadena final después de reemplazar las fracciones:")
        print(cadena_final)
        
        # Retornar la cadena final y los índices de las fracciones encontradas
        return cadena_final, indicesfracciones
    else:
        # Si no hay divisiones en la cadena, retornar la cadena original y una lista vacía de índices de fracciones
        print("No se encontraron divisiones en la cadena.")
        print("Cadena final:")
        print(cadena)
        return cadena, indicesfracciones
    
def divatexnumdem(cadena, sort_list, centros, indices, indicesdediv):  
    
    print("____________________________________")
    print(f"Inicio de divatexnumdem:")
    print(f"Cadena: {cadena}")
    print(f"Indices de la cadena: {indices}")
    print(f"Indices de las divisiones: {indicesdediv}")
    print("____________________________________")
        
    if "div" in cadena:
        # Si hay "div" en la cadena, proceder
        print("La cadena contiene 'div'.")
            
        # Reemplazar "div" por "/"
        cadena = cadena.replace("div", "/")
        cadena = cadena.replace("div", "/")
        
        # Crear un diccionario para mapear los números con las letras respectivas
        asignaciones = {}
            
        if len(cadena) == len(indices):
            # Asignar cada número con su respectiva letra en el diccionario
            for i in range(len(cadena)):
                asignaciones[indices[i]] = cadena[i]

            # Imprimir el diccionario de asignaciones
            print("Asignaciones:")
            for numero, letra in asignaciones.items():
                print(f"{letra}: {numero}")
        else:
            print("La longitud de la cadena y la lista de índices no coinciden.")

        # Inicializar la lista de fracciones
        fracciones = []

        # Obtener los índices de división
        indices_division = indicesdediv
        indices_num_dem = indices_division

        for indice in indices_division:
            # Procesar cada división

            x, _, w, _ = sort_list[indice][1] 
            numerador = ""
            denominador = ""

            centro_div = centros[indice] 

            # Iterar sobre los índices de la cadena
            for j in indices:
                if j == indice:
                    continue

                x1, y1 = centros[j]

                # Verificar si el índice está dentro del rango de la división actual
                if x < x1 < x+w:
                    if y1 < centro_div[1]:
                        numerador += asignaciones[j]
                        if j not in indices_num_dem:
                            indices_num_dem.append(j)
                    else:
                        denominador += asignaciones[j]
                        if j not in indices_num_dem:
                            indices_num_dem.append(j)

            # Construir la fracción con el numerador y el denominador seleccionados
            fraccion = f"¿¿{numerador}?/¿{denominador}??"

            if fraccion not in fracciones:
                fracciones.append(fraccion)

        print("Fracciones encontradas:")
        print(fracciones)

        # Crear la cadena final con "R" en las posiciones correspondientes
        cadena_final = ""
        indice_fraccion = 0

        for i in indices:
            if i in indices_num_dem:
                cadena_final += "R"
            else:
                cadena_final += asignaciones[i]

        cadena_final = re.sub(r"R+", "R", cadena_final)

        print("Cadena final antes de reemplazar las fracciones:")
        print(cadena_final)

        indice_fraccion = 0  # Inicializar el índice de la fracción

        # Reemplazar las "R" con las fracciones correspondientes
        aux = 0
        for i, caracter in enumerate(cadena_final):
            if caracter == "R":
                cadena_final = cadena_final[:i+aux] + fracciones[indice_fraccion] + cadena_final[i+1+aux:]
                aux += len(fracciones[indice_fraccion]) - 1  # Actualizar el desplazamiento
                indice_fraccion += 1  # Mover al siguiente índice de fracciones

        print("Cadena final después de reemplazar las fracciones:")
        print(cadena_final)

        return cadena_final
    else:
        # Si no hay "div" en la cadena, retornar la cadena original
        print("No se encontraron 'div' en la cadena.")
        print("Cadena final:")
        print(cadena)
        return cadena

def trascadena(indice, cadena, sort_list, centros):
    print("-----------------------------------------INICIO DE TRANSCADENA---------------------------------------------------")
    print(f"Cadena que entra en trascadena: {cadena}")
    
    num = ""  # Inicializar el numerador
    dem = ""  # Inicializar el denominador

    # Listas para almacenar los índices de las divisiones en el numerador y el denominador
    indicesDeDivicionNum = []
    indicesDeDivicionDem = []

    # Listas para almacenar los índices de las divisiones en el numerador y el denominador
    indicesdedivnum = []
    indicesdedivdem = []

    # Obtener las coordenadas de la división que queremos dividir en numerador y denominador
    x, _, w, _ = sort_list[indice][1]
    ancho = x + w
    centro_div = centros[indice]

    # Iterar sobre todas las imágenes de los dígitos
    for i in range(len(sort_list)):
        
        # No procesar la misma división
        if i != indice:
            
            x1, y1 = centros[i]

            # Verificar si el dígito está dentro del rango de la división actual
            if x < x1 < ancho:
                
                if y1 < centro_div[1]:  # Si está arriba del centro de la división
                    num += cadena[i]  # Agregar al numerador

                    if cadena[i] == "div":  # Si es una división
                        indicesdedivnum.append(i)  # Agregar el índice a la lista

                    if i not in indicesDeDivicionNum:  # Si el índice no está en la lista de divisiones del numerador
                        indicesDeDivicionNum.append(i)  # Agregar el índice
                    
                else:  # Si está abajo del centro de la división
                    dem += cadena[i]  # Agregar al denominador

                    if cadena[i] == "div":  # Si es una división
                        indicesdedivdem.append(i)  # Agregar el índice a la lista

                    if i not in indicesDeDivicionDem:  # Si el índice no está en la lista de divisiones del denominador
                        indicesDeDivicionDem.append(i)  # Agregar el índice

    # Imprimir los resultados de trascadena
    print("--------------------------------------")
    print("Salida de trascadena:")
    print(f"Numerator: {num}")
    print(f"Denominator: {dem}")
    print(f"Numerador Indices: {indicesDeDivicionNum}")
    print(f"Denominador Indices: {indicesDeDivicionDem}")
    print("--------------------------------------")   
    print("-----------------------------------------FINAL DE TRANSCADENA---------------------------------------------------")
    return num, dem, indicesDeDivicionNum, indicesDeDivicionDem, indicesdedivnum, indicesdedivdem
    
def reoganizarindices(cadena, subcadenas):
    lista_nueva = []  # Lista para almacenar la cadena reorganizada
    indicesusados = []  # Lista para almacenar los índices de subcadenas ya utilizados

    # Iterar sobre cada dígito en la cadena original
    for digito in cadena:
        encontrado = False
        # Buscar en cada subcadena si el dígito está presente
        for indice, lista in enumerate(subcadenas):
            if digito in lista:
                encontrado = True
                # Si se encuentra el dígito, y el índice de la subcadena no ha sido usado, agregar la subcadena completa a la lista nueva
                if indice not in indicesusados:
                    indicesusados.append(indice)  # Marcar el índice como usado
                    lista_nueva.extend(lista)  # Agregar la subcadena completa a la lista nueva
                break
        # Si el dígito no se encuentra en ninguna subcadena, agregarlo directamente a la lista nueva
        if not encontrado:
            lista_nueva.append(digito)
    
    # Retornar la lista nueva reorganizada
    return lista_nueva

def validacion_de_casos(sort_list, indice, indicesdediv):
    print("________________________________________INICIO VALIDACION______________________________________")
    
    # Inicializamos la variable `validacion` a True. Esta variable se usará para determinar si la validación es exitosa o no.
    validacion = True
    
    print("Inicio de eliminación de divisiones de divarribanoabajo que están cubiertas por las divisiones de divabajonoarriba")
    print(f"INDICE ACTUAL, {indice}")

    # Obtenemos las coordenadas y dimensiones de la división actual del `sort_list` utilizando el índice actual.
    x, _, w, _ = sort_list[indice][1]
    print(f"División actual -> Índice: {indice}, Coordenadas: x={x}, w={w}")
        
    # Calculamos el ancho total de la división.
    ancho = x + w
    print(f"Ancho calculado de la división actual: {ancho}")
        
    # Aumentamos el ancho en un 20% para la validación.
    w *= 1.2
    print(f"Ancho incrementado en 20%: {w}")

    # Iteramos nuevamente sobre cada índice en `indicesdediv` para comparar cada división con todas las demás.
    for indice2 in indicesdediv:
        if indice2 == indice:
            continue
        # Obtenemos las coordenadas y dimensiones de la segunda división del `sort_list` utilizando el índice actual.
        x1, _, w1, _ = sort_list[indice2][1]
        print(f"Comparando con división -> Índice: {indice2}, Coordenadas: x1={x1}, w1={w1}")
            
        # Calculamos el ancho total de la segunda división.
        ancho1 = x1 + w1
        print(f"Ancho calculado de la segunda división: {ancho1}")

        # Si el ancho de la segunda división es mayor que el ancho incrementado de la primera división,
        # se establece `validacion` a False y se sale del bucle.
        if w1 > w:
            validacion = False
            print(f"División {indice2} cubre a división {indice}. Validación fallida.")
            break
    
    print("________________________________________FINAL VALIDACION______________________________________")
    # Devolvemos el valor de `validacion` que indica si todas las divisiones cumplen con la condición.
    return validacion

def divicionenlinea(indicediv, cadena, sort_list, centros):
    print("-----------------------------------------INICIO DIVICIONENLINEA------------------------------------------------------------")
    print(f"Entrada -> indicediv: {indicediv}, cadena: {cadena}")
    
    promedio = conseguirtodaspromedioaltura(cadena, sort_list)
    promedio *= 1.1
    print(f"Promedio de alturas calculado: {promedio}")
        
    # Encuentra los índices de las divisiones en la cadena
    indices_division = [indice for indice, elemento in enumerate(cadena) if elemento == "div"]
    print(f"Indices de divisiones en la cadena: {indices_division}")

    centro_div = centros[indicediv]
    print(f"Centro de la división actual: {centro_div}")
    
    contadorArriba = []  # Lista para divisiones encima de la división actual
    contadorAbajo = []  # Lista para divisiones debajo de la división actual

    # Verificamos cuántas divisiones hay encima y debajo de la división actual
    for indice2 in indices_division:
        if indice2 == indicediv:
            continue

        _, y1 = centros[indice2]
        print(f"Comparando con división -> Índice: {indice2}, Centro: {centros[indice2]}")

        if y1 > centro_div[1] + promedio:
            if indice2 not in contadorAbajo: 
                contadorAbajo.append(indice2)
                print(f"  -> Añadido a contadorAbajo: {contadorAbajo}")
        if y1 < centro_div[1] - promedio:
            if indice2 not in contadorArriba: 
                contadorArriba.append(indice2)
                print(f"  -> Añadido a contadorArriba: {contadorArriba}")
        else:
            continue

    print(f"Divisiones arriba de la actual: {contadorArriba}")
    print(f"Divisiones abajo de la actual: {contadorAbajo}")


    # Verificamos alineación de múltiples divisiones arriba
    alineadoarriba = True
    if len(contadorArriba) > 1:
        _, h2 = centros[contadorArriba[0]]
        _, y2 = centro_div
        distancia = abs(h2 - y2) / 2.5

        for inde2 in contadorArriba[1:]:
            _, c2 = centros[inde2]
            if not (h2 - distancia < c2 < h2 + distancia):
                alineadoarriba = False
                print(f"Divisiones múltiples arriba no alineadas (indice: {inde2}), estableciendo estaenlinea en False")
                break

    # Verificamos alineación de múltiples divisiones abajo
    alineadoabajo = True
    if len(contadorAbajo) > 1:
        _, h2 = centros[contadorAbajo[0]]
        _, y2 = centro_div
        distancia = abs(h2 - y2) / 2.5

        for inde2 in contadorAbajo[1:]:
            _, c2 = centros[inde2]
            if not (h2 - distancia < c2 < h2 + distancia):
                alineadoabajo = False
                print(f"Divisiones múltiples abajo no alineadas (indice: {inde2}), estableciendo estaenlinea en False")
                break
            
    # Inicializamos las variables de resultado
    estaenlinea = False
    caso2 = False
    caso3 = False

    # Verificamos los casos de alineación
    if len(contadorArriba) == 0 and len(contadorAbajo) == 0:
        estaenlinea = False
        caso2 = False
        caso3 = False
    elif len(contadorArriba) == 0 and len(contadorAbajo) == 1:
        caso2 = True
    elif len(contadorArriba) == 1 and len(contadorAbajo) == 0:
        caso3 = True
    elif len(contadorArriba) == 1 and len(contadorAbajo) == 1:
        estaenlinea = True   
    ##
    elif len(contadorArriba) > 1 and len(contadorAbajo) == 0 and alineadoarriba == True:
        caso3 = True
    elif len(contadorArriba) > 1 and len(contadorAbajo) == 1 and alineadoarriba == True: 
        estaenlinea = True
    ##   
    elif len(contadorArriba) == 1 and len(contadorAbajo) > 1 and alineadoabajo == True:
        estaenlinea = True
    elif len(contadorArriba) == 0 and len(contadorAbajo) > 1 and alineadoabajo == True: 
        caso2 = True
    ## 
    elif len(contadorArriba) > 1 and len(contadorAbajo) > 1 and alineadoarriba == True and alineadoabajo == True:
        estaenlinea = True 
    ######________________######
    else:
        estaenlinea = False
        caso2 = False
        caso3 = False 
        

    print(f"Estado antes de verificar divisiones -> estaenlinea: {estaenlinea}, caso2: {caso2}, caso3: {caso3}")
    if caso2: 
        validacion = validacion_de_casos(sort_list, indicediv,contadorAbajo)
        if validacion == False: 
            caso2 = False
        else: 
            caso2 = True
    if caso3: 
        validacion = validacion_de_casos(sort_list, indicediv,contadorArriba)
        if validacion == False: 
            caso3 = False
        else: 
            caso3 = True
    print(f"Estado FINAL de verificar divisiones -> estaenlinea: {estaenlinea}, caso2: {caso2}, caso3: {caso3}")
    print("-----------------------------------------FINAL DIVICIONENLINEA------------------------------------------------------------")
        
    return estaenlinea, caso2, caso3

def removerduplicados(original_list):
    seen = set()
    result_list = []
    for number in original_list:
        if number not in seen:
            seen.add(number)
            result_list.append(number)
    return result_list

def Organizarcadena(cadena, sort_list, centros):
    # Se imprimen líneas divisorias y el inicio del proceso de organización de la cadena
    print("////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////")
    print("_____________________________________________INICIO ORGANIZAR CADENA________________________________________________________________")
    
    # Se crean índices iniciales basados en la longitud de sort_list
    indicesiniciales = [i for i in range(len(sort_list))]
    print("Cadena de entrada:", cadena)

    # Verifica si hay divisiones en la cadena
    if "div" in cadena:
        # Encuentra los índices de todas las divisiones en la cadena
        indices_division = [indice for indice, elemento in enumerate(cadena) if elemento == "div"]
        # Ordena los índices de las divisiones en base a su posición horizontal (x) en centros
        indices_division = sorted(indices_division, key=lambda indice: centros[indice][0])
        print("Índices de división:", indices_division)

        # Obtiene las fracciones predefinidas y sus cadenas correspondientes
        fraccionespredefinas, cadenaspredefinidas = conseguirtodaslasfracciones(cadena, sort_list, centros)
        print("Fracciones predefinidas:", fraccionespredefinas)
        print("Cadenas predefinidas:", cadenaspredefinidas)

        # Inicializa listas para diferentes tipos de fracciones
        divdiv = []
        
        divabajonoarriba = []
        divarribanoabajo = []
            
        # Clasifica las divisiones en diferentes categorías basadas en su alineación
        for i in indices_division:
            caso1, caso2, caso3 = divicionenlinea(i, cadena, sort_list, centros)
            if caso1:
                if i not in divdiv:
                    divdiv.append(i)
            if caso2:
                if i not in divabajonoarriba:
                    divabajonoarriba.append(i)
            if caso3:
                if i not in divarribanoabajo:
                    divarribanoabajo.append(i)
        
        print(f"antes de aplicar DIVARRIBAABAJO, divarribanoabajo{divarribanoabajo}, divabajonoarriba{divabajonoarriba}")
        
        if len(divdiv)==0 and len(divabajonoarriba) == 0 and len(divarribanoabajo) == 0:
            # Si no hay fracciones anidadas, procesa la cadena directamente
            cadena_final, indi = divatex(cadena, sort_list, centros)
            nuevalistaindices = reoganizarindices(indicesiniciales, indi)
            print("Cadena Final:", cadena_final)
            print("Nuevos índices:", nuevalistaindices)
            return cadena_final, nuevalistaindices
                        
        # Imprime las listas de fracciones clasificadas
        print(f"Fracciones anidadas: {divdiv}")
        print(f"Fracciones Con divicion arriba pero no abajo: {divarribanoabajo}")
        print(f"Fracciones Con divicion abjo pero no arriba: {divabajonoarriba}")

        indicesquitar=[]
        
        fraccionesconfracciones = []
        cadenafraccionesconfracciones = []
        
        indicesdefraccionesaquitar=[]
        # Procesa las fracciones anidadas si existen
        if len(divdiv) > 0:
            print("_________________________________________FRACCIONES ANIDADAS______________________________________________________")
            # Para cada división anidada, procesa su numerador y denominador
            for div in divdiv:
                num, dem, indicesDeDivicionNum, indicesDeDivicionDem, indicesdedivnum, indicesdedivdem = trascadena(div, cadena, sort_list, centros)
                print(f"Numerador (div {div}):", num)
                print(f"Denominador (div {div}):", dem)
                print(f"Índices de división del numerador (div {div}):", indicesDeDivicionNum)
                print(f"Índices de división del denominador (div {div}):", indicesDeDivicionDem)

                # Combina los índices del numerador, la división central y el denominador
                indifracciones = indicesDeDivicionNum + [div] + indicesDeDivicionDem
                print(F"INDIFRACCIONES: {indifracciones}")
                print(f"Fracciones predefinidas:", fraccionespredefinas)
                indifraccionesreoganizados = reoganizarindices(indifracciones, fraccionespredefinas)
                print(f"Índices de fracciones reorganizados (div {div}):", indifraccionesreoganizados)
                fraccionesconfracciones.append(indifraccionesreoganizados)

                # Genera las fracciones del numerador y denominador
                numerador = divatexnumdem(num, sort_list, centros, indicesDeDivicionNum, indicesdedivnum)
                denominador = divatexnumdem(dem, sort_list, centros, indicesDeDivicionDem, indicesdedivdem)
                fraccion = f"¿¿{numerador}?/¿{denominador}??"
                print(f"Fracción generada (div {div}):", fraccion)
                cadenafraccionesconfracciones.append(fraccion)

                # Determina los índices a quitar después de procesar la fracción
                indicesdefraccionesaquitar = indicesquitar + indicesdedivnum + indicesdedivdem
                indicesquitar = indicesquitar + indifraccionesreoganizados
        
        if len(divarribanoabajo) > 0:
            print("_________________________________________FRACCIONES ANIDADAS______________________________________________________")
            # Para cada división anidada, procesa su numerador y denominador
            for div in divarribanoabajo:
                num, dem, indicesDeDivicionNum, indicesDeDivicionDem, indicesdedivnum, indicesdedivdem = trascadena(div, cadena, sort_list, centros)
                print(f"Numerador (div {div}):", num)
                print(f"Denominador (div {div}):", dem)
                print(f"Índices de división del numerador (div {div}):", indicesDeDivicionNum)
                print(f"Índices de división del denominador (div {div}): No hay",)

                # Combina los índices del numerador, la división central y el denominador
                indifracciones = indicesDeDivicionNum + [div] + indicesDeDivicionDem
                print(F"INDIFRACCIONES: {indifracciones}")
                print(f"Fracciones predefinidas:", fraccionespredefinas)
                indifraccionesreoganizados = reoganizarindices(indifracciones, fraccionespredefinas)
                print(f"Índices de fracciones reorganizados (div {div}):", indifraccionesreoganizados)
                fraccionesconfracciones.append(indifraccionesreoganizados)

                # Genera las fracciones del numerador y denominador
                numerador = divatexnumdem(num, sort_list, centros, indicesDeDivicionNum, indicesdedivnum)
                denominador = dem
                fraccion = f"¿¿{numerador}?/¿{denominador}??"
                print(f"Fracción generada (div {div}):", fraccion)
                cadenafraccionesconfracciones.append(fraccion)

                # Determina los índices a quitar después de procesar la fracción
                indicesdefraccionesaquitar = indicesquitar + indicesdedivnum 
                indicesquitar = indicesquitar + indifraccionesreoganizados
                
        if len(divabajonoarriba) > 0:
            print("_________________________________________FRACCIONES ANIDADAS______________________________________________________")
            # Para cada división anidada, procesa su numerador y denominador
            for div in divabajonoarriba:
                num, dem, indicesDeDivicionNum, indicesDeDivicionDem, indicesdedivnum, indicesdedivdem = trascadena(div, cadena, sort_list, centros)
                print(f"Numerador (div {div}):", num)
                print(f"Denominador (div {div}):", dem)
                print(f"Índices de división del numerador (div {div}): No hay")
                print(f"Índices de división del denominador (div {div}): {indicesdedivdem}",)

                # Combina los índices del numerador, la división central y el denominador
                indifracciones = indicesDeDivicionNum + [div] + indicesDeDivicionDem
                print(F"INDIFRACCIONES: {indifracciones}")
                print(f"Fracciones predefinidas:", fraccionespredefinas)
                indifraccionesreoganizados = reoganizarindices(indifracciones, fraccionespredefinas)
                print(f"Índices de fracciones reorganizados (div {div}):", indifraccionesreoganizados)
                fraccionesconfracciones.append(indifraccionesreoganizados)

                # Genera las fracciones del numerador y denominador
                numerador = num
                denominador = divatexnumdem(dem, sort_list, centros, indicesDeDivicionDem, indicesdedivdem)
                fraccion = f"¿¿{numerador}?/¿{denominador}??"
                print(f"Fracción generada (div {div}):", fraccion)
                cadenafraccionesconfracciones.append(fraccion)

                # Determina los índices a quitar después de procesar la fracción
                indicesdefraccionesaquitar = indicesquitar + indicesdedivdem
                indicesquitar = indicesquitar + indifraccionesreoganizados
        # Encuentra y elimina fracciones predefinidas que ya han sido procesadas
        fracciones_a_eliminar = []
        fraccionescadena_a_eliminar = []
                
        for indiceaquitar in indicesdefraccionesaquitar:
            for fraccion in fraccionespredefinas:
                if indiceaquitar in fraccion:
                    if fraccion not in fracciones_a_eliminar:
                        fracciones_a_eliminar.append(fraccion)
                        fraccionescadena_a_eliminar.append(cadenaspredefinidas[fraccionespredefinas.index(fraccion)])
                                
        print(f"Fracciones a eliminar (div {div}):", fracciones_a_eliminar)
        print(f"Cadenas a eliminar (div {div}):", fraccionescadena_a_eliminar)
                
        for fraccion, cadena1 in zip(fracciones_a_eliminar, fraccionescadena_a_eliminar):
            fraccionespredefinas.remove(fraccion)
            cadenaspredefinidas.remove(cadena1)
            
        print(f"Fracciones predefinidas después de la eliminación (div {div}):", fraccionespredefinas)
        print(f"Cadenas predefinidas después de la eliminación (div {div}):", cadenaspredefinidas)

        # Combina las listas de fracciones procesadas y no procesadas
        print(f"FRACCIONES CON FRACCIONES: {fraccionesconfracciones}")
        listatotal = fraccionesconfracciones + fraccionespredefinas
        listacadenastotal = cadenafraccionesconfracciones + cadenaspredefinidas
        print("Lista total de fracciones:", listatotal)
        print("Lista total de cadenas:", listacadenastotal)

        fracciones_sorted = []
        cadenafracciones_sorted = []

        # Ordena las fracciones de acuerdo a los índices de división
        for i in indices_division:
            for j in range(len(listatotal)):
                if i in listatotal[j]:
                    if listatotal[j] not in fracciones_sorted:
                        fracciones_sorted.append(listatotal[j])
                        cadenafracciones_sorted.append(listacadenastotal[j])
                        
        print("Fracciones ordenadas:", fracciones_sorted)
        print("Cadenas de fracciones ordenadas:", cadenafracciones_sorted)

        # Crea la lista de índices a quitar y actualiza la cadena reemplazando esos índices con 'R'
        indicesquitar = [elemento for sublista in listatotal for elemento in sublista]
        print(f"INDICES A QUITAR: {indicesquitar}")
        cadena_final = list(cadena)
        print(f"CADENA: {cadena_final}")
        for indice in indicesquitar:
            cadena_final[indice] = "R"
            print(f"proceso cadena: {cadena_final}")
        
        
        print("Cadena final antes de reemplazar 'R':", cadena_final)
        

        # Junta la cadena final, reemplazando múltiples 'R' consecutivos por un solo 'R'
        cadena_final = "".join(cadena_final)
        cadena_final = re.sub(r"R+", "R", cadena_final)
        print("Cadena final después de reemplazar 'R':", cadena_final)

        # Reemplaza 'R' con las fracciones generadas en cadenafracciones_sorted
        aux = 0
        indice_fraccion = 0
        for i, caracter in enumerate(cadena_final):
            if caracter == "R":
                if indice_fraccion < len(cadenafracciones_sorted):
                    cadena_final = cadena_final[:i + aux] + cadenafracciones_sorted[indice_fraccion] + cadena_final[i + 1 + aux:]
                    aux += len(cadenafracciones_sorted[indice_fraccion]) - 1
                    
                    indice_fraccion += 1
        print("Cadena final completa:", cadena_final)
                
        # Crea la lista de índices final combinando los índices de las fracciones ordenadas
        lista_indices_final = []
        for fraccion in fracciones_sorted:
            lista_indices_final.extend(fraccion)
            
        lista_indices_final=removerduplicados(lista_indices_final)
                    
        return cadena_final, lista_indices_final
    
    else:
        # Si no hay divisiones en la cadena, retorna la cadena y los índices iniciales
        print("La cadena no contiene divisiones.")
        print(f"Cadena Final: {cadena}")
        return cadena, indicesiniciales
    
import re

def depurar_trigonometria(cadena):
    i = 0
    resultado = ""
    
    # Patrones para cada función trigonométrica
    patrones = {
        'cos': {
            'inicio': ['c'],
            'segundo': ['0', 'o'],
            'tercero': ['5', '2', 's'],
            'requiere_parentesis': []  # No hay casos que requieran paréntesis especial
        },
        'tan': {
            'inicio': ['+', 't'],
            'segundo': ['4', 'a'],
            'tercero': ['n', 'x', '4', 'a'],
            'requiere_parentesis': ['+4x']  # Solo estos requieren '('
        },
        'sin': {
            'inicio': ['5', '2', 's'],
            'segundo': ['1', '(', '/',')'],
            'tercero': ['n', 'x','a'],
            'requiere_parentesis': ['51x','21x','s)n','s(n']  # Solo estos requieren '('
        }
    }
    
    while i < len(cadena):
        encontrado = False
        
        # --- Manejo de 'cos' CON LA MISMA LÓGICA QUE sin y tan ---
        if i + 3 <= len(cadena):
            if cadena[i] in patrones['cos']['inicio']:
                if (cadena[i+1] in patrones['cos']['segundo'] and 
                    cadena[i+2] in patrones['cos']['tercero']):
                    
                    patron_actual = cadena[i:i+3]
                    
                    # Como no hay casos que requieran paréntesis, siempre se reemplaza
                    resultado += 'cos'
                    i += 3
                    encontrado = True
        
        if encontrado:
            continue
        
        # --- Manejo de 'tan' (MANTENIDO EXACTAMENTE IGUAL) ---
        if i + 3 <= len(cadena):
            if cadena[i] in patrones['tan']['inicio']:
                if (cadena[i+1] in patrones['tan']['segundo'] and 
                    cadena[i+2] in patrones['tan']['tercero']):
                    
                    patron_actual = cadena[i:i+3]
                    
                    if patron_actual in patrones['tan']['requiere_parentesis']:
                        if i + 3 < len(cadena) and cadena[i+3] == '(':
                            resultado += 'tan('
                            i += 4
                        else:
                            resultado += patron_actual
                            i += 3
                    else:
                        resultado += 'tan'
                        i += 3
                    encontrado = True
        if encontrado:
            continue
        
        # --- Manejo de 'sin' (MANTENIDO EXACTAMENTE IGUAL) ---
        if i + 3 <= len(cadena):
            if cadena[i] in patrones['sin']['inicio']:
                if (cadena[i+1] in patrones['sin']['segundo'] and 
                    cadena[i+2] in patrones['sin']['tercero']):
                    
                    patron_actual = cadena[i:i+3]
                    
                    if patron_actual in patrones['sin']['requiere_parentesis']:
                        if i + 3 < len(cadena) and cadena[i+3] == '(':
                            resultado += 'sin('
                            i += 4
                        else:
                            resultado += patron_actual
                            i += 3
                    else:
                        resultado += 'sin'
                        i += 3
                    encontrado = True
        if encontrado:
            continue
        
        # --- Si no es un patrón especial, copiar el carácter original ---
        resultado += cadena[i]
        i += 1
    
    return resultado

def cadenasinintegrales(cadena):
    print("------------------------------INICIO DE CADENASININTEGRALES----------------------------------------")
    print(f"Entrada - Cadena: {cadena}")
    
    # Inicializar la cadena de salida
    cadena_sin_integrales = cadena
    
    # Inicializar la variable de control para saber si estamos dentro de una integral
    dentro_de_integral = ""
    diferenciales = []
    derivadasparciales = []
    
    for digito in cadena: 
        if digito == "∫":
            dentro_de_integral+=digito
            
    if "dx" in cadena_sin_integrales:
        diferenciales.append("dx")
        cadena_sin_integrales = cadena_sin_integrales.replace("dx", "")
    if "dy" in cadena_sin_integrales: 
        diferenciales.append("dy")
        cadena_sin_integrales = cadena_sin_integrales.replace("dy", "")
    if "dz" in cadena_sin_integrales:
        diferenciales.append("dz")
        cadena_sin_integrales = cadena_sin_integrales.replace("dz", "")
    if "((d)/(dx))" in cadena_sin_integrales:
        derivadasparciales.append("∂x")
        cadena_sin_integrales = cadena_sin_integrales.replace("((d)/(dx))", "")
    if "((d)/(dy))" in cadena_sin_integrales:
        derivadasparciales.append("∂y")
        cadena_sin_integrales = cadena_sin_integrales.replace("((d)/(dy))", "")
    if "((d)/(dz))" in cadena_sin_integrales:
        derivadasparciales.append("∂z")
        cadena_sin_integrales = cadena_sin_integrales.replace("((d)/(dz))", "")
        
    ordendepresion = derivadasparciales
    diferenciales = diferenciales
    cantidaddeintegrales = dentro_de_integral 

    return cadena_sin_integrales

def modificar_indices(cadena, indices):
    print("------------------------------INICIO DE MODIFICAR INDICES----------------------------------------")
    print(f"Entrada - Cadena: {cadena}")
    print(f"Entrada - Indices: {indices}")

    # Crear una nueva lista de índices para almacenar los índices modificados
    indices_modificados = []
    # Copiar la lista de índices original para no modificarla directamente
    indices_copy = indices.copy()
    
    # Iterar sobre la cadena con sus índices
    for idx, char in enumerate(cadena):
        if char == '¿':
            # Si el carácter es '¿', añadir 666 a la lista de índices modificados
            indices_modificados.append(666)
            print(f"Carácter '¿' encontrado en el índice {idx}, añadiendo 666 a indices_modificados")
        elif char == '?':
            # Si el carácter es '?', añadir 999 a la lista de índices modificados
            indices_modificados.append(999)
            print(f"Carácter '?' encontrado en el índice {idx}, añadiendo 999 a indices_modificados")
        else:
            # Añadir el índice correspondiente de la lista original
            if indices_copy:  # Verificar si todavía hay elementos en indices_copy
                indice_a_añadir = indices_copy.pop(0)
                indices_modificados.append(indice_a_añadir)
                print(f"Carácter '{char}' encontrado en el índice {idx}, añadiendo {indice_a_añadir} a indices_modificados")

    print(f"Salida - indices_modificados: {indices_modificados}")
    print("------------------------------FINAL DE MODIFICAR INDICES----------------------------------------")
    return indices_modificados

def DeterminarExponencial(indice, i, indices, cadena, sort_list, centros,permanecearriba): 
    print("------------------------------INICIO DE DETERMINAR EXPONENCIAL----------------------------------------")
    print(f"Entrada - indice: {indice}, i: {i}, indices: {indices}, cadena: {cadena}")
    
    Arriba = False
    Abajo = False
    Lado = False
    final = False
    
    # Verificar si el índice actual no es el último
    if i < len(indices) - 1: 
        # Verificar condiciones especiales para el siguiente índice
        if indices[i+1] == 666 or indices[i+1] == 999 or cadena[i+1] == "/":
            if permanecearriba == True:
                print(f"Esta arriba y la condición especial encontrada en el índice {i+1}, devolviendo False, True, False")
                Arriba = False
                Abajo = True
                Lado = False
                return Arriba, Abajo, Lado, final
            else: 
                print(f"Esta Abajo y la condición especial encontrada en el índice {i+1}, devolviendo False, False, True")
                Arriba = False
                Abajo = False
                Lado = True
                return Arriba, Abajo, Lado, final
        # Obtener las coordenadas y altura del elemento actual
        _, y, _, h = sort_list[indice][1]
        altura = y + h
        centroexponente = centros[indices[i+1]]
        
        print(f"Comparando elemento actual con índice {indice}: y={y}, h={h}, altura={altura}")
        print(f"Centro del exponente con índice {indices[i+1]}: centroexponente={centroexponente}")

        # Determinar la posición relativa del centro del exponente
        if centroexponente[1] < y: 
            Arriba = True
            print(f"El siguiente elemento '{cadena[i+1]}' está arriba del elemento actual '{cadena[i]}'")
        elif y <= centroexponente[1] <= altura: 
            Lado = True
            print(f"El siguiente elemento '{cadena[i+1]}' está al lado del elemento actual '{cadena[i]}'")
        else:
            Abajo = True
            print(f"El siguiente elemento '{cadena[i+1]}' está abajo del elemento actual '{cadena[i]}'")

        print(f"El término que sigue es: '{cadena[i+1]}'")
    else:
        Arriba = False
        Abajo = False
        Lado = False
        final = True
        return Arriba, Abajo, Lado, final
    
    print(f"Salida - Arriba: {Arriba}, Abajo: {Abajo}, Lado: {Lado}, final: {final}")
    print("------------------------------FINAL DE DETERMINAR EXPONENCIAL----------------------------------------")
    return Arriba, Abajo, Lado, final
    
def exponentes(cadena, indices, sort_list, centros): 
    print("------------------------------INICIO DE EXPONENTES----------------------------------------")
    print(f"Entrada - Cadena: {cadena}")
    print(f"Entrada - Indices: {indices}")
    
    cadena_exponencial = ""
    indices_exponenciales = []
    permanecearriba = False
    conteoarriba = 0
    
    for i, indice in enumerate(indices): 
        print(f"Procesando índice {i} con valor {indice} y carácter '{cadena[i]}'")
        if cadena[i] == "/" or indice == 666 or indice == 999 or cadena[i] == "q" or cadena[i] == "*" or cadena[i] == "-" or cadena[i] == "+" or cadena[i] == ".":
            cadena_exponencial += cadena[i]
            indices_exponenciales.append(indice)
            print(f"Carácter especial '{cadena[i]}' encontrado, añadiéndolo directamente a cadena_exponencial y a indices_exponenciales")
        else:
            if not permanecearriba:
                arriba, abajo, lado, final = DeterminarExponencial(indice, i, indices, cadena, sort_list, centros, permanecearriba)
                print(f"Resultado de DeterminarExponencial: arriba={arriba}, abajo={abajo}, lado={lado}")
                
                if final: 
                    if cadena[i] == "(" or cadena[i] == ")":
                        cadena_exponencial += ")"
                        indices_exponenciales.append(999)
                        print("Es paréntesis")
                    else:
                        cadena_exponencial += cadena[i]
                        indices_exponenciales.extend([indice])
                        print("No es paréntesis")
                elif arriba: 
                    if i+2 < len(cadena):
                        if cadena[i+2] == "q":
                            print(f"condicion especial de raiz en las siguiente siguientes dos posiciones: indice={i+2}, letra={cadena[i+2]}") 
                            cadena_exponencial += cadena[i]
                            indices_exponenciales.extend([indice])
                        else:
                            conteoarriba += 1
                            permanecearriba = True
                            cadena_exponencial += cadena[i] + "**("
                            indices_exponenciales.extend([indice, 22, 22, 666])
                            print(f"Añadiendo exponente arriba: '{cadena[i]}**(' a cadena_exponencial")
                    else:
                        conteoarriba += 1
                        permanecearriba = True
                        cadena_exponencial += cadena[i] + "**("
                        indices_exponenciales.extend([indice, 22, 22, 666])
                        print(f"Añadiendo exponente arriba: '{cadena[i]}**(' a cadena_exponencial")
                elif abajo: 
                    if cadena[i+1] == "q":
                        print(f"Condicion especial de abajo en la que la siguiente es una q")
                        cadena_exponencial += cadena[i]
                        indices_exponenciales.extend([indice])
                    else: 
                        cadena_exponencial += cadena[i] + ")"
                        indices_exponenciales.extend([indice, 999])
                        permanecearriba = False
                        conteoarriba = 0
                        print(f"Añadiendo exponente abajo: '{cadena[i]})' a cadena_exponencial")
                elif lado: 
                    cadena_exponencial += cadena[i]
                    indices_exponenciales.append(indice)
                    print(f"Añadiendo carácter al lado: '{cadena[i]}' a cadena_exponencial")
            else: 
                arriba, abajo, lado, final = DeterminarExponencial(indice, i, indices, cadena, sort_list, centros, permanecearriba)
                print(f"Resultado de DeterminarExponencial: arriba={arriba}, abajo={abajo}, lado={lado}")
                
                if final: 
                    if cadena[i] == "(" or cadena[i] == ")":
                        cadena_exponencial += ")"
                        indices_exponenciales.append(999)
                        print("Es paréntesis")
                    else:
                        cadena_exponencial += cadena[i] + ")"
                        indices_exponenciales.extend([indice, 999])
                        print("No es paréntesis")
                elif arriba: 
                    cadena_exponencial += cadena[i] + ")**("
                    indices_exponenciales.extend([indice, 999, 22, 22, 666])
                    print(f"Añadiendo exponente arriba: '{cadena[i]}^(' a cadena_exponencial")
                elif abajo: 
                    if cadena[i+1] == "q":
                        cadena_exponencial += cadena[i]
                    else: 
                        cadena_exponencial += cadena[i] + ")"
                        indices_exponenciales.extend([indice, 999])
                        permanecearriba = False
                        print(f"Añadiendo exponente abajo: '{cadena[i]})' a cadena_exponencial")
                elif lado: 
                    cadena_exponencial += cadena[i]
                    indices_exponenciales.append(indice)
                    print(f"Añadiendo carácter al lado: '{cadena[i]}' a cadena_exponencial")
                
    print(f"Salida - Cadena exponencial resultante: {cadena_exponencial}")
    print(f"Salida - Indices exponenciales resultantes: {indices_exponenciales}")
    print("------------------------------FINAL DE EXPONENTES----------------------------------------")
    
    return cadena_exponencial, indices_exponenciales

def raices(cadenafinaltrigonometrica,indices, sort_list, centros):
    
    cadenarepuesto = list(cadenafinaltrigonometrica)
    indicesrepuesto = indices[:]
    
    posiciones = []

    for i,caracter in enumerate(cadenafinaltrigonometrica): 
        if caracter == "q":
            
            #agregamos la posicion siguiente de la q para insertar el parentesis luego
            posiciones.append(i+1)
            
            digitos_de_raiz = []
            
            #tomamos el indice del digito 
            indice = indices[i] 
            
            #tomamos las dimensiones del digito escrito en la pantalla 
            x_r, y_r, w_r, h_r = sort_list[indice][1]
            ancho = x_r + w_r
            alto = y_r + h_r
            
            # recorremos todos las dimensiones de los digitos 
            for j in indices: 
                #obviamos los casos de los "parentesis"
                if j == 666 or j == 999:
                    continue
                else:
                    # Si el el centro esta contenido entre las dimensiones del digito lo introducimos en la lista 
                    x,y = centros[j]
                    if (x_r < x < ancho) and (y_r < y < alto):
                        digitos_de_raiz.append(j)
            
            digito_derecha = -1  # Por si no hay ningún dígito a la derecha
            max_x = -float('inf')
            for digito in digitos_de_raiz:
                x, y = centros[digito]
                if x > max_x:
                    max_x = x
                    digito_derecha = digito
            
            if digito_derecha != -1:  # Si encontramos un dígito a la derecha
                # Buscar la posición en indicesrepuesto
                posicion_derecha = indicesrepuesto.index(digito_derecha)
                
                # Agregamos la posicion del ultimo digito de la raiz 
                posiciones.append(posicion_derecha + 1)

    
    contadorpares = 1
    contadorpaso = 0
    for posicion in posiciones: 
        
        # Verificamos que que vayamos a insertar un parentesis abierto o cerrado
        if contadorpares % 2 == 0: 
            cadenarepuesto.insert(posicion+contadorpaso, "?")  # Inserta el carácter "¿"
            indicesrepuesto.insert(posicion+contadorpaso, 999)
            
            contadorpaso += 1
            contadorpares += 1
        else: 
            cadenarepuesto.insert(posicion+contadorpaso, "¿")  # Inserta el carácter "¿"
            indicesrepuesto.insert(posicion+contadorpaso, 666)
            
            contadorpaso += 1
            contadorpares += 1
    
    cadenarepuesto = ''.join(cadenarepuesto)
    
    return cadenarepuesto, indicesrepuesto     
        
def depurar_parentesis(cadena,indices):
    # Convertimos la cadena en una lista para poder modificarla
    cadena_lista = list(cadena)
    print("Cadena original:", cadena)
    
    # Lista para rastrear los índices de los símbolos ya procesados
    simbolosprocesados = []
    
    # Recorremos cada carácter en la cadena
    for i, simbolo in enumerate(cadena_lista):
        print(f"Procesando símbolo '{simbolo}' en posición {i}")
        
        # Si ya hemos procesado este índice, lo saltamos
        if i in simbolosprocesados:
            print(f"Índice {i} ya procesado, se omite.")
            continue
        
        # Si encontramos un paréntesis de apertura o cierre
        if (simbolo == "(" or simbolo == ")") and indices[i] != 666 and indices[i] != 999:

            
            # Si el elemento anterior es una barra '/', lo saltamos (parece ser un caso especial en la lógica)
            if i > 0 and indices[i] == 666: 
                print(f"Símbolo '{simbolo}' en posición {i} precedido por '/', se omite.")
                continue
            
            # Verificamos que hay un siguiente carácter en la cadena
            if i + 1 < len(cadena_lista):
                siguiente = cadena_lista[i + 1]
                print(f"Siguiente carácter en posición {i+1}: '{siguiente}'")
                
                # Si el siguiente carácter no es un paréntesis ni una barra, procesamos el interior
                if siguiente != "(" and siguiente != ")" and siguiente != "/":
                    
                    # Buscamos el siguiente paréntesis para encontrar el cierre correspondiente
                    j = i + 1
                    while j < len(cadena_lista) and cadena_lista[j] != "(" and cadena_lista[j] != ")":
                        j += 1
                    
                    # Si encontramos un paréntesis de cierre en la cadena
                    if j < len(cadena_lista):
                        print(f"Paréntesis correspondiente encontrado en posición {j}: '{cadena_lista[j]}'")
                        
                        # Marcamos estos índices como procesados para evitar modificaciones posteriores
                        simbolosprocesados.append(i)
                        simbolosprocesados.append(j)
                        
                        # Corregimos la dirección de los paréntesis si es necesario
                        if simbolo == "(" and cadena_lista[j] == ")":
                            print("Paréntesis correctamente emparejados, no se realiza cambio.")
                        elif simbolo == "(" and cadena_lista[j] == "(":
                            cadena_lista[j] = ")"  # Si ambos son '(', cambiamos el segundo a ')'
                            print(f"Corrigiendo: cambiando '(' en posición {j} a ')'")
                        elif simbolo == ")" and cadena_lista[j] == ")":
                            cadena_lista[i] = "("  # Si ambos son ')', cambiamos el primero a '('
                            print(f"Corrigiendo: cambiando ')' en posición {i} a '('")
                        elif simbolo == ")" and cadena_lista[j] == "(":
                            cadena_lista[i] = "("  # Convertimos el primer ')' en '('
                            cadena_lista[j] = ")"  # Convertimos el segundo '(' en ')'
                            print(f"Corrigiendo: cambiando ')' en posición {i} a '(' y '(' en posición {j} a ')'")
    
    # Reconstruimos la cadena corregida a partir de la lista modificada
    cadena_corregida = "".join(cadena_lista)
    print("Cadena corregida:", cadena_corregida)
    return cadena_corregida

def roots(cadena, indices, sort_list, centros): 
    print("------------------------------INICIO DE ROOTS----------------------------------------")
    print(cadena)
    print(indices)

    # Asegurar que la cadena sea una lista
    if isinstance(cadena, str):
        cadena = list(cadena)

    i = 0
    while i < len(cadena):  
        print(f"Paso {i}: {''.join(cadena)}")  # Mostrar cadena en cada iteración
        
        if cadena[i] == "q":  
            print(f"Encontrado 'q' en posición {i}")

            # Buscar el índice del paréntesis de cierre más cercano
            indicedelparentesis = next((i + j for j in range(len(cadena) - i) if cadena[i + j] == "?"), None)

            if indicedelparentesis is None:
                print(f"No se encontró un paréntesis de cierre para 'q' en posición {i}, continuando...\n")
                i += 1
                continue  # Si no hay paréntesis de cierre, pasamos al siguiente símbolo

            # Obtener la posición y altura del símbolo actual
            _, y, _, h = sort_list[indices[i]][1]  
            altura_q = y + h  # Altura del símbolo "q"
            
            # Obtener centro del número anterior
            if i > 0:
                centroexponente = centros[indices[i - 1]]  # Centro del número anterior
            else:
                print(f"Error: No hay número antes de 'q' en posición {i}")
                i += 1
                continue  # Pasamos al siguiente símbolo si no hay número antes

            print(f"Altura de 'q': {altura_q}, Centro del número anterior: {centroexponente[1]}")

            # Verificar si el número anterior está por encima del radical
            if centroexponente[1] < y*0.85:  
                numero = cadena[i - 1]  # Tomar el número anterior como exponente
                print(f"Detectado número '{numero}' como exponente en posición {i-1}")

                # **PASO 1:** Reemplazar "q" por "r" PRIMERO
                cadena[i] = "r"
                print(f"Reemplazando 'q' por 'r' en la posición {i}...")
                print(f"Cadena después de reemplazo: {''.join(cadena)}")
                casos = [1,2,3,4,5,6,7,8,9,0,"x","y","z","(",")"]
                # **PASO 2:** Eliminar el número de su posición original
                del cadena[i - 1]  
                print(f"Eliminado '{numero}' de posición {i-1}: {''.join(cadena)}")

                # **PASO 3:** Ajustar índice del paréntesis de cierre
                indicedelparentesis -= 1  

                # **PASO 4:** Insertar la coma y el número en la posición del paréntesis de cierre
                cadena.insert(indicedelparentesis, ",")  
                cadena.insert(indicedelparentesis + 1, numero)  
                print(f"Insertados ',' y '{numero}' en posición {indicedelparentesis}: {''.join(cadena)}")

                print(f"Convertido: raíz detectada con exponente '{numero}' → {''.join(cadena)}\n")

                # **Importante:** No aumentar `i` aquí porque la lista se ha modificado
                continue  
            else:
                pass
        i += 1  # Mover al siguiente elemento si no hubo modificación

    # Convertir la lista nuevamente a cadena antes de retornarla
    resultado = ''.join(cadena)

    print("------------------------------FIN DE ROOTS----------------------------------------\n")
    return resultado, indices

