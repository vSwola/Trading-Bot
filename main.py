import ccxt
import colored
import time

exchange = ccxt.kraken({
    'apiKey': 'TU_API_KEY',
    'secret': 'TU_API_SECRET',
    'enableRateLimit': True,
})

def obtener_entrada(mensaje):
    return input(colored.stylize(mensaje + ": ", colored.fg("green")))

# Obtener datos históricos del mercado
def obtener_datos_historicos(symbol, timeframe, limit):
    data = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    return data

# Análisis de tendencias
def analizar_tendencias(data):
    close_prices = [item[4] for item in data]
    last_price = close_prices[-1]
    previous_price = close_prices[-2]

    if last_price > previous_price:
        return 'comprar'
    elif last_price < previous_price:
        return 'vender'
    else:
        return 'esperar'

def comprar(cantidad, precio):
    symbol = 'BTC/USD'  
    order = exchange.create_limit_buy_order(symbol, cantidad, precio)
    print("Orden de compra realizada:")
    print(order)

def vender(cantidad, precio):
    symbol = 'BTC/USD'  
    order = exchange.create_limit_sell_order(symbol, cantidad, precio)
    print("Orden de venta realizada:")
    print(order)

# Gestión del riesgo
def gestionar_riesgo(precio_compra):

    stop_loss_percentage = 0.95  
    take_profit_percentage = 1.05  
    stop_loss = precio_compra * stop_loss_percentage
    take_profit = precio_compra * take_profit_percentage

    posiciones_abiertas = exchange.fetch_open_orders(symbol)
    for posicion in posiciones_abiertas:
        if posicion['side'] == 'buy':

            order_id = posicion['id']
            cantidad_compra = posicion['amount']
            precio_compra_actual = posicion['price']
            
        
            if precio_compra_actual > precio_compra:
                nuevo_stop_loss = precio_compra_actual * stop_loss_percentage
                exchange.edit_order(id=order_id, stop_loss=nuevo_stop_loss)
                print("Stop-loss actualizado para la posición de compra", order_id)

         
            if precio_compra_actual > precio_compra:
                nuevo_take_profit = precio_compra_actual * take_profit_percentage
                exchange.edit_order(id=order_id, take_profit=nuevo_take_profit)
                print("Take-profit actualizado para la posición de compra", order_id)


saldo_disponible = float(obtener_entrada("Ingresa el saldo disponible"))
symbol = obtener_entrada("Ingresa el símbolo de la criptomoneda que deseas operar")
timeframe = '1d' 
limit = 100  
monto_maximo_compra = float(obtener_entrada("Ingresa el monto máximo de compra"))

data = obtener_datos_historicos(symbol, timeframe, limit)
tendencia = analizar_tendencias(data)
print("Tendencia detectada:", tendencia)

if tendencia == 'comprar':
    precio_compra = exchange.fetch_ticker(symbol)['bid']
    cantidad_compra = min(monto_maximo_compra / precio_compra, saldo_disponible / precio_compra)
    comprar(cantidad_compra, precio_compra)
    gestionar_riesgo(precio_compra)

elif tendencia == 'vender':
    cantidad_venta = 0.001  
    precio_venta = exchange.fetch_ticker(symbol)['ask']
    vender(cantidad_venta, precio_venta)

def determinar_cantidad_venta(saldo_disponible, cantidad_posicion):
   
    if saldo_disponible >= cantidad_posicion:
        return cantidad_posicion
    else:
        porcentaje_venta = 0.8 
        cantidad_venta = saldo_disponible * porcentaje_venta
        return cantidad_venta

if tendencia == 'vender':
    cantidad_posicion = obtener_cantidad_posicion(symbol) 
    cantidad_venta = determinar_cantidad_venta(saldo_disponible, cantidad_posicion)
    precio_venta = exchange.fetch_ticker(symbol)['ask']
    vender(cantidad_venta, precio_venta)

else:
    print("No se realizó ninguna acción.")
