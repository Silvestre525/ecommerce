# 🛒 Guía de Lógica de Negocio - Ecommerce API

## 1. Flujo de Pedidos (Orders)
El carrito de compras vive en el **LocalStorage** del frontend. Al finalizar la compra, se envía la lista de IDs y cantidades al backend.

### Creación de Orden
- **Seguridad**: El frontend **NUNCA** envía el precio total. El backend lo calcula usando los precios actuales de la DB.
- **Stock**: Si un producto no tiene stock suficiente, la orden **falla por completo** (Transacción Atómica).
- **Historial**: Al crear la orden, se guarda el `price_at_purchase` en la tabla `detail_order`. Si cambias el precio del producto después, la orden vieja no se ve afectada.

## 2. Modelos y Relaciones
- **Product**: Cada fila es un SKU único (ej: Remera Roja Talle L). 
- **DetailOrder**: Tabla intermedia que une Orden y Producto con su cantidad.
- **Status**: Las órdenes nacen como `PENDING`.

## 3. Endpoints Clave para el Frontend

### Catálogo
`GET /api/product/` -> Lista de productos con stock, precio, talle y color.
`GET /api/category/` -> Categorías disponibles.

### Proceso de Compra
`POST /api/order/`
**Body:**
```json
{
  "items": [
    {"product": 1, "quantity": 2},
    {"product": 3, "quantity": 1}
  ]
}
```

## 4. Roles y Permisos
- **Público**: Solo `GET` a productos y categorías.
- **Visitante**: Puede crear órdenes y ver **solo sus propias órdenes**.
- **Administrador**: Puede gestionar stock, cambiar precios y ver todas las órdenes de todos los usuarios.

## 5. Recomendaciones para el Frontend
- **Validación previa**: Antes de enviar la orden, verifica que los productos tengan stock en el estado local.
- **Sincronización**: Al cargar el carrito del LocalStorage, haz un `GET` de esos productos específicos para asegurar que los precios y stock sigan vigentes.

## 🚀 Flujo de Trabajo Recomendado (Frontend)

Para integrar esta API de manera eficiente, sigue estos flujos de usuario:

### 1. Autenticación y Perfil
1. **Registro**: `POST /api/register/` (si el usuario es nuevo).
2. **Login**: `POST /api/login/` -> Guardar el `token` en una Cookie segura o LocalStorage.
3. **Validación**: `GET /api/profile/` (usando el Token) para obtener los datos de la "Persona" y confirmar que el perfil está completo.

### 2. Navegación del Catálogo
1. **Categorías**: `GET /api/category/` para llenar los filtros o el menú de navegación.
2. **Productos**: 
   - Público: `GET /api/product/public_catalog/` (Landing page rápida).
   - Logueado: `GET /api/product/` (Permite filtros avanzados por talla, color, etc.).
3. **Detalle**: `GET /api/product/{id}/` al hacer clic en una prenda para ver stock por variante.

### 3. Proceso de Carrito y Compra (Checkout)
1. **Persistencia**: El carrito se gestiona **exclusivamente en el Frontend** (LocalStorage).
2. **Verificación**: Antes de abrir el Checkout, se recomienda hacer un `GET /api/product/{id}/` de los items del carrito para refrescar precios y stock.
3. **Creación de Orden**: `POST /api/order/` enviando solo la lista de `items` (IDs y cantidades).
4. **Resultado**: El backend responde con el `total` calculado y el ID de la orden.

### 4. Post-Venta
1. **Historial**: `GET /api/order/` para listar los pedidos del usuario.
2. **Detalle de Pedido**: `GET /api/order/{id}/` para mostrar el desglose, cantidades y precios históricos.
