from django.db import models
from ..person.models import Person

class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('PAID', 'Pagado'),
        ('SHIPPED', 'Enviado'),
        ('DELIVERED', 'Entregado'),
        ('CANCELLED', 'Cancelado'),
    ]

    id = models.AutoField(primary_key=True, db_column='id_order')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='PENDING'
    )
    creation_date = models.DateTimeField(auto_now_add=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='orders')

    class Meta:
        db_table = "Orders"
        ordering = ['-creation_date']

    def __str__(self):
        return f"Orden {self.id} - {self.person} ({self.status})"

class DetailOrder(models.Model):
    id = models.AutoField(primary_key=True, db_column='id_detail_order')
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='details'
    )
    product = models.ForeignKey(
        'product.Product', 
        on_delete=models.PROTECT, 
        related_name='order_details'
    )
    quantity = models.PositiveIntegerField(default=1)
    price_at_purchase = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Precio del producto al momento de la compra"
    )

    class Meta:
        db_table = "detail_order"
        verbose_name = "Detalle de Orden"
        verbose_name_plural = "Detalles de Órdenes"

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Orden {self.order.id})"

    @property
    def subtotal(self):
        return self.quantity * self.price_at_purchase
