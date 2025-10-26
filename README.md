# Aplicativo de Tabla de Amortización en Python

Este proyecto consiste en el desarrollo de un **simulador de crédito** que genera la **tabla de amortización completa** según los parámetros definidos por el usuario.  
Permite probar distintos escenarios de tasa de interés (efectiva o nominal), tipo de cobro (anticipada o vencida), plazos variables y la posibilidad de incluir abonos programados o adicionales.

---

## Uso del Programa

1. Abre la terminal en la carpeta del proyecto.  
2. Ejecuta el archivo principal:  
   ```bash
   python amortizacion.py  
3. Ingresa los valores solicitados:  
- Monto del crédito: valor total del préstamo.  
- Tasa de interés: nominal o efectiva (por ejemplo, 2% mensual).  
- Plazo: número de meses.  
- Frecuencia de pago: mensual, trimestral, semestral o anual.  
- Tipo de tasa: anticipada o vencida.  
4. El programa calculará:   
- La cuota fija.  
- Los intereses y amortización por período.  
- El saldo restante del crédito.  
4. Al finalizar:  
- Generará una tabla detallada en pantalla.  
- Exportará los resultados a CSV y Excel (.xlsx).  
- Mostrará una gráfica con el comportamiento del crédito.  