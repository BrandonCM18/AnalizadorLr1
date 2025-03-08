import os

# ==========================
# CARGA DE ARCHIVOS .if Y .lr
# ==========================
def cargar_tokens(inf_file_path):
    if not os.path.exists(inf_file_path):
        raise FileNotFoundError(f"Error: No se encontro el archivo {inf_file_path}")

    tokens = {}
    with open(inf_file_path, "r", encoding="utf-8") as inf_file:
        for line in inf_file:
            print(f"Linea leida: {line}")  # Esto imprimirá cada línea leída
            parts = line.strip().split("\t")
            if len(parts) == 2:
                token, token_id = parts
                tokens[token] = int(token_id)
    
    if "$" not in tokens:
        raise ValueError("Error: El token '$' (fin de entrada) no esta definido en el archivo .inf")
    
    return tokens

def cargar_gramatica(lr_file_path):
    """Carga el archivo .lr para extraer reglas y la tabla LR(1)."""
    if not os.path.exists(lr_file_path):
        raise FileNotFoundError(f"Error: No se encontro el archivo {lr_file_path}")

    with open(lr_file_path, "r", encoding="utf-8") as lr_file:
        lr_content = lr_file.readlines()
    
    if len(lr_content) < 2:
        raise ValueError("Error: El archivo .lr esta vacio o corrupto")

    num_rules = int(lr_content[0].strip())  # Numero de reglas
    rules = []

    # Extraer reglas de produccion
    for line in lr_content[1:num_rules + 1]:
        parts = line.strip().split("\t")
        if len(parts) == 3:
            left_id = int(parts[0])  # ID del lado izquierdo
            right_length = int(parts[1])  # Longitud del lado derecho
            non_terminal = parts[2]  # Nombre del no terminal
            rules.append((left_id, right_length, non_terminal))

    # Extraer dimensiones de la tabla LR(1)
    num_rows, num_cols = map(int, lr_content[num_rules + 1].strip().split())

    # Extraer la tabla LR(1)
    lr_table = []
    for line in lr_content[num_rules + 2:num_rules + 2 + num_rows]:
        lr_table.append(list(map(int, line.strip().split())))

    return rules, lr_table

# ==========================
# CLASES PARA EL ANALISIS LR(1)
# ==========================
class AnalizadorLexico:
    def __init__(self, tokens):
        self.tokens = tokens

    def analizar(self, entrada):
        """Convierte la entrada en una lista de tokens segun la tabla de tokens."""
        resultado = []
        palabras = entrada.split()
        for palabra in palabras:
            if palabra in self.tokens:
                resultado.append((palabra, self.tokens[palabra]))
            else:
                raise ValueError(f"Error lexico: token no reconocido '{palabra}'")
        resultado.append(('$', self.tokens['$']))  # Agregar fin de entrada
        return resultado

class AnalizadorLR:
    def __init__(self, lr_table, rules):
        self.lr_table = lr_table
        self.rules = rules

    def analizar(self, tokens):
        """Realiza el analisis sintactico usando la tabla LR."""
        pila = [0]  # Pila de estados
        index = 0
        entrada = [t[1] for t in tokens]  # Convertir tokens a sus IDs

        while True:
            estado_actual = pila[-1]
            token_actual = entrada[index]
            accion = self.lr_table[estado_actual][token_actual]

            if accion > 0:  # Desplazamiento
                pila.append(token_actual)
                pila.append(accion)  # Nuevo estado
                index += 1
            elif accion < 0:  # Reduccion
                regla = self.rules[-accion - 1]
                _, longitud, _ = regla
                for _ in range(2 * longitud):  # Sacar elementos de la pila
                    pila.pop()
                nuevo_estado = pila[-1]
                pila.append(regla[0])  # Agregar no terminal
                pila.append(self.lr_table[nuevo_estado][regla[0]])  # Nuevo estado
            elif accion == 0:  # Error sintactico
                raise ValueError("Error sintactico: Secuencia no valida")
            else:  # Aceptacion (-1)
                print("Analisis sintactico exitoso")
                return True

# ==========================
# EJECUCION DEL PROGRAMA
# ==========================
if __name__ == "__main__":
    # Rutas correctas a los archivos
    lr_file_path = "/Users/brandoncm18/Library/CloudStorage/OneDrive-UniversidaddeGuadalajara/SeminarioTraductores2/AnalizadorLr1/compilador.lr"
    inf_file_path = "/Users/brandoncm18/Library/CloudStorage/OneDrive-UniversidaddeGuadalajara/SeminarioTraductores2/AnalizadorLr1/compilador.inf"

    # Cargar tokens y gramatica
    try:
        tokens = cargar_tokens(inf_file_path)
        rules, lr_table = cargar_gramatica(lr_file_path)
    except Exception as e:
        print(f"Error durante la carga: {e}")
        exit(1)  # Terminar el programa si hay error

    # Instanciar analizadores
    lexico = AnalizadorLexico(tokens)
    lr = AnalizadorLR(lr_table, rules)

    # Prueba con una cadena de entrada
    entrada = "programa { entero identificador ; }"
    tokens_entrada = lexico.analizar(entrada)
    print("Tokens generados:", tokens_entrada)

    # Ejecutar analisis sintactico
    lr.analizar(tokens_entrada)