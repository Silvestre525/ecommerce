import logging

logger = logging.getLogger(__name__)

class ProductService:
    """
    Servicio para manejar la lógica de negocio relacionada con los Productos.
    """

    @staticmethod
    def get_stock_statistics(queryset):
        """
        Calcula las estadísticas de stock para un queryset de productos.
        """
        total_stock = sum(product.stock for product in queryset)
        low_stock_count = len([p for p in queryset if p.is_low_stock])
        
        return {
            "total_products": queryset.count(),
            "total_stock": total_stock,
            "low_stock_products": low_stock_count,
        }

    @staticmethod
    def toggle_status(product, user=None):
        """
        Activa o desactiva un producto y registra el cambio.
        Devuelve un mensaje de éxito.
        """
        if product.is_active:
            product.deactivate()
            message = f"Producto '{product.name}' desactivado"
        else:
            product.activate()
            message = f"Producto '{product.name}' activado"
            
        username = user.username if user and hasattr(user, 'username') else "Sistema"
        logger.info(f"{message} por {username}")
        
        return message

    @staticmethod
    def update_stock(product, action, quantity, user=None):
        """
        Añade o reduce el stock de un producto validando la operación.
        Lanza ValueError si la operación no es válida.
        Devuelve (message, previous_stock, current_stock).
        """
        if quantity <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")
            
        if action == "add":
            new_stock = product.add_stock(quantity)
            message = f"Se añadieron {quantity} unidades"
        elif action == "reduce":
            new_stock = product.reduce_stock(quantity)
            message = f"Se redujeron {quantity} unidades"
        else:
            raise ValueError("Acción debe ser 'add' o 'reduce'")
            
        username = user.username if user and hasattr(user, 'username') else "Sistema"
        logger.info(f"Stock actualizado para {product.name}: {message} por {username}")
        
        previous_stock = new_stock - quantity if action == "add" else new_stock + quantity
        
        return message, previous_stock, new_stock
