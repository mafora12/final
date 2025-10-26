#!/usr/bin/env python3
"""
Simulador de Crédito - Tabla de Amortización (Método Francés)
Versión interactiva tipo Bancolombia
Exporta CSV y XLSX organizados y con tabla visual de pagos.
"""

# ----------------------------------
# Importación de librerías necesarias
# ----------------------------------
# Estas librerías permiten manejar fechas, matemáticas, gráficos y archivos Excel/CSV
from datetime import date, timedelta
import math
import csv
import pandas as pd
import matplotlib.pyplot as plt
from openpyxl import Workbook
from openpyxl.drawing.image import Image
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter  # 🔧 ayuda a ajustar columnas de Excel sin errores

# ----------------------------------
# Funciones de conversión de tasas
# ----------------------------------
# Estas funciones sirven para transformar las tasas de interés
# (por ejemplo, de nominal a efectiva, o de anticipada a vencida).
# Se usan porque los bancos y los créditos pueden presentar tasas de distintas formas.

def nominal_to_effective_annual(nominal_rate, comp_per_year):
    # Convierte una tasa nominal anual a una efectiva anual
    return (1 + nominal_rate / comp_per_year) ** comp_per_year - 1

def effective_annual_to_period_rate(eff_annual, payments_per_year):
    # Convierte una tasa efectiva anual a una tasa por período (por ejemplo, mensual)
    return (1 + eff_annual) ** (1 / payments_per_year) - 1

def anticipada_to_vencida(rate_anticipada):
    # Convierte una tasa anticipada (pagada al inicio) a vencida (pagada al final)
    return rate_anticipada / (1 - rate_anticipada)

def parse_rate(rate_value, rate_type, rate_kind, nominal_comp_per_year, payments_per_year):
    # Esta función principal interpreta los datos que el usuario introduce
    # y obtiene la tasa correcta según el tipo y la clase (nominal/efectiva, vencida/anticipada)
    if rate_type == "nominal":
        ear = nominal_to_effective_annual(rate_value, nominal_comp_per_year)
        i = effective_annual_to_period_rate(ear, payments_per_year)
    else:
        i = effective_annual_to_period_rate(rate_value, payments_per_year)

    if rate_kind == "anticipada":
        i = anticipada_to_vencida(i)
    return i

# ----------------------------------
# Cálculo de tabla método francés
# ----------------------------------
# El método francés se usa para calcular préstamos donde las cuotas son fijas,
# pero cambian las proporciones de interés y abono a capital.

def cuota_frances(principal, tasa, n_periodos):
    # Calcula el valor fijo de la cuota mensual
    if tasa == 0:
        return principal / n_periodos
    return principal * (tasa * (1 + tasa) ** n_periodos) / ((1 + tasa) ** n_periodos - 1)

def generar_tabla(principal, tasa, n_periodos, frecuencia, abonos, reducir):
    # Genera una tabla completa con cada período, intereses, abonos y saldo restante
    saldo = principal
    cuota = cuota_frances(principal, tasa, n_periodos)
    tabla = []
    fecha = date.today()  # Fecha inicial: hoy

    for periodo in range(1, n_periodos + 1):
        interes = saldo * tasa
        abono_capital = cuota - interes
        abono_extra = abonos.get(periodo, 0)
        saldo -= (abono_capital + abono_extra)

        if saldo < 0:
            saldo = 0  # Evita que aparezcan saldos negativos al final

        # Se guarda la información del período en un diccionario
        tabla.append({
            "Periodo": periodo,
            "Fecha": fecha.strftime("%d/%m/%Y"),
            "Cuota ($)": round(cuota, 2),
            "Interés ($)": round(interes, 2),
            "Abono a Capital ($)": round(abono_capital, 2),
            "Abono Extra ($)": round(abono_extra, 2),
            "Saldo Restante ($)": round(saldo, 2)
        })

        # Si hay un abono extra y el usuario elige reducir el plazo, recalcula la cuota
        if abono_extra > 0 and reducir == "plazo":
            n_restante = n_periodos - periodo
            cuota = cuota_frances(saldo, tasa, n_restante)

        fecha += timedelta(days=30)  # Avanza 1 mes (aproximado)

        if saldo <= 1e-6:  # Si ya se terminó de pagar
            break

    return tabla

# ----------------------------------
# Exportar CSV y XLSX ordenados
# ----------------------------------
# Esta parte guarda la tabla en dos formatos:
# - CSV (texto)
# - XLSX (Excel) con formato bonito y gráfico de barras

def exportar_archivos(tabla):
    # --- CSV limpio ---
    csv_name = "tabla_amortizacion.csv"
    with open(csv_name, "w", newline="", encoding="utf-8-sig") as f:
        escritor = csv.DictWriter(f, fieldnames=tabla[0].keys())
        escritor.writeheader()
        escritor.writerows(tabla)
    print(f"\n✅ Archivo CSV generado: {csv_name}")

    # --- Crear DataFrame para XLSX ---
    df = pd.DataFrame(tabla)
    xlsx_name = "tabla_amortizacion.xlsx"

    # Crear gráfico tipo “barras Bancolombia” para visualizar cuotas
    plt.figure(figsize=(8, 4))
    plt.bar(df["Periodo"], df["Cuota ($)"], color="#009FE3", label="Cuota total")
    plt.bar(df["Periodo"], df["Interés ($)"], color="#F4B400", label="Interés")
    plt.bar(df["Periodo"], df["Abono a Capital ($)"], color="#34A853", label="Abono capital")
    plt.title("Distribución de Pagos - Simulación de Crédito")
    plt.xlabel("Periodo")
    plt.ylabel("Valor ($)")
    plt.legend()
    plt.tight_layout()
    grafico = "grafico_pagos.png"
    plt.savefig(grafico, dpi=150)
    plt.close()

    # Crear archivo XLSX con formato visual agradable
    wb = Workbook()
    ws = wb.active
    ws.title = "Tabla de Amortización"

    # Agregar título principal
    ws["A1"] = "Tabla de Amortización - Simulación de Crédito"
    ws["A1"].font = Font(size=14, bold=True)
    ws.merge_cells("A1:G1")
    ws["A1"].alignment = Alignment(horizontal="center")

    # Agregar tabla de datos desde el DataFrame
    for r in dataframe_to_rows(df, index=False, header=True):
        ws.append(r)

    # 🔧 Ajustar anchos de columnas (versión segura para evitar errores con celdas combinadas)
    for i, col in enumerate(ws.columns, start=1):
        max_length = 0
        column = get_column_letter(i)
        for cell in col:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            except:
                pass
        ws.column_dimensions[column].width = max_length + 2

    # Insertar gráfico en el archivo Excel
    img = Image(grafico)
    img.width = 600
    img.height = 300
    ws.add_image(img, f"A{len(df) + 4}")

    wb.save(xlsx_name)
    print(f"✅ Archivo XLSX generado: {xlsx_name}")

# ----------------------------------
# Programa principal (interactivo)
# ----------------------------------
# Aquí es donde el usuario introduce los datos paso a paso.
# Cada input tiene un comentario para entender qué se está pidiendo.

def main():
    print("=== SIMULADOR DE CRÉDITO - TABLA DE AMORTIZACIÓN ===\n")

    # 💵 Monto total del préstamo
    principal = float(input("Monto del crédito ($): "))

    # 📈 Porcentaje de la tasa de interés
    tasa_valor = float(input("Tasa de interés (%): ")) / 100

    # 💬 Tipo de tasa (cómo se expresa)
    tipo_tasa = input("Tipo de tasa (nominal/efectiva): ").strip().lower()

    # 🕓 Clase de tasa (cuándo se cobra)
    clase_tasa = input("Clase de tasa (vencida/anticipada): ").strip().lower()

    # 🔁 Cada cuánto se capitalizan los intereses (por ejemplo, 12 = mensual)
    capitalizacion = int(input("Capitalizaciones por año (ej. 12 para mensual): "))

    # 📅 Cada cuánto se paga (por ejemplo, 12 mensual, 4 trimestral)
    frecuencia = int(input("Pagos por año (12 mensual, 4 trimestral, etc.): "))

    # ⏳ Tiempo total del crédito
    plazo = int(input("Plazo total en meses: "))

    # Calcula la tasa por período según los datos anteriores
    tasa_periodo = parse_rate(tasa_valor, tipo_tasa, clase_tasa, capitalizacion, frecuencia)
    print(f"\nTasa por periodo: {tasa_periodo*100:.4f}%")

    # 💸 Abonos extra (pagos adicionales al capital)
    abonos = {}
    print("\n¿Deseas ingresar abonos extra? (s/n)")
    if input().strip().lower() == "s":
        while True:
            p = int(input("Periodo del abono: "))
            monto = float(input("Monto del abono ($): "))
            abonos[p] = monto
            if input("¿Otro abono? (s/n): ").strip().lower() != "s":
                break

    # 🔧 Elección: reducir el plazo del crédito o el valor de la cuota
    reducir = input("\nTras abono extra, ¿reducir 'plazo' o 'cuota'?: ").strip().lower()

    # Genera la tabla completa con todos los cálculos
    tabla = generar_tabla(principal, tasa_periodo, plazo, frecuencia, abonos, reducir)

    # 📊 Muestra la tabla por consola
    print("\n=== TABLA DE AMORTIZACIÓN ===")
    for fila in tabla:
        print(fila)

    # 📂 Exporta los resultados a CSV y Excel
    exportar_archivos(tabla)

    # 💰 Muestra el saldo final del crédito (debería ser 0)
    saldo_final = tabla[-1]["Saldo Restante ($)"]
    print(f"\nSaldo final: ${saldo_final:.2f}")

# ----------------------------------
# Punto de inicio del programa
# ----------------------------------
# Si el archivo se ejecuta directamente, se llama a main()
if __name__ == "__main__":
    main()
