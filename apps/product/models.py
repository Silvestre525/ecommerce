from django.core.exceptions import ValidationError
from django.db import models

from ..BaseModel.models import BaseModel
from ..category.models import Category
from ..color.models import Color
from ..order.models import Order
from ..size.models import Size
from ..suppliers.models import Suppliers


class Product(BaseModel):
    """
    Modelo de Producto mejorado con validaciones y constraints
    """

    id = models.AutoField(primary_key=True, db_column="id_product")
    name = models.CharField(
        "Nombre del producto",
        max_length=100,  # Aumentado para más flexibilidad
        null=True,  # Mantenemos null=True por ahora para evitar problemas de migración
        blank=False,
        help_text="Nombre del producto (máximo 100 caracteres)",
    )
    stock = models.IntegerField(
        "Stock disponible",
        help_text="Cantidad en stock (debe ser 0 o mayor)",
    )
    img = models.CharField(
        "URL de imagen",
        max_length=200,  # Aumentado de 100 a 200
        null=True,
        blank=True,
        help_text="URL de la imagen del producto",
    )

    # Relaciones
    categories = models.ManyToManyField(
        Category,
        related_name="products",
        blank=True,
        help_text="Categorías a las que pertenece el producto",
    )
    suppliers = models.ManyToManyField(
        Suppliers,
        related_name="products",
        blank=True,
        help_text="Proveedores del producto",
    )
    order = models.ManyToManyField(
        Order,
        related_name="products",
        blank=True,
        help_text="Órdenes que incluyen este producto",
    )
    color = models.ForeignKey(
        Color,
        on_delete=models.PROTECT,  # Más seguro que CASCADE
        default=1,
        help_text="Color del producto",
    )
    size = models.ForeignKey(
        Size,
        on_delete=models.PROTECT,  # Más seguro que CASCADE
        default=1,
        help_text="Tamaño del producto",
    )

    # Campos adicionales útiles
    is_active = models.BooleanField(
        "Producto activo",
        default=True,
        help_text="Indica si el producto está disponible para la venta",
    )

    class Meta:
        db_table = "Product"
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["name"]

        # Índices para mejorar performance
        indexes = [
            models.Index(fields=["name"], name="product_name_idx"),
            models.Index(fields=["stock"], name="product_stock_idx"),
            models.Index(fields=["is_active"], name="product_active_idx"),
            models.Index(fields=["color"], name="product_color_idx"),
            models.Index(fields=["size"], name="product_size_idx"),
            models.Index(fields=["creation_date"], name="product_created_idx"),
        ]

        # Constraints para integridad de datos (comentados temporalmente)
        # constraints = [
        #     models.CheckConstraint(
        #         check=models.Q(stock__gte=0), name="product_positive_stock"
        #     ),
        #     models.UniqueConstraint(
        #         fields=["name", "color", "size"],
        #         name="unique_product_variant",
        #         condition=models.Q(is_active=True),
        #     ),
        # ]

    def __str__(self):
        """Representación string del producto"""
        color_title = (
            getattr(self.color, "title", "Sin color") if self.color else "Sin color"
        )
        return f"{self.name} - {color_title} ({self.stock} en stock)"

    def clean(self):
        """Validaciones adicionales a nivel de modelo"""
        super().clean()

        if self.name:
            name_stripped = str(self.name).strip()
            self.name = name_stripped
            if len(name_stripped) < 2:
                raise ValidationError(
                    {"name": "El nombre debe tener al menos 2 caracteres."}
                )

        if self.stock is not None and self.stock < 0:
            raise ValidationError({"stock": "El stock no puede ser negativo."})

    def save(self, *args, **kwargs):
        """Override save para ejecutar validaciones"""
        self.full_clean()
        super().save(*args, **kwargs)

    # Propiedades útiles
    @property
    def is_available(self):
        """Indica si el producto está disponible para la venta"""
        return self.is_active and self.stock > 0

    @property
    def is_low_stock(self):
        """Indica si el producto tiene stock bajo (menos de 10 unidades)"""
        return self.stock < 10

    @property
    def stock_status(self):
        """Devuelve el estado del stock como string"""
        if not self.is_active:
            return "Inactivo"
        elif self.stock == 0:
            return "Sin stock"
        elif self.stock < 5:
            return "Stock crítico"
        elif self.stock < 10:
            return "Stock bajo"
        elif self.stock < 50:
            return "Stock normal"
        else:
            return "Stock alto"

    @property
    def categories_list(self):
        """Devuelve una lista de nombres de categorías"""
        return list(self.categories.values_list("name", flat=True))

    @property
    def suppliers_list(self):
        """Devuelve una lista de nombres de proveedores"""
        return list(self.suppliers.values_list("name", flat=True))

    # Métodos de instancia útiles
    def add_stock(self, quantity):
        """Añade stock al producto"""
        if quantity < 0:
            raise ValueError("La cantidad debe ser positiva")
        self.stock += quantity
        self.save()
        return self.stock

    def reduce_stock(self, quantity):
        """Reduce stock del producto"""
        if quantity < 0:
            raise ValueError("La cantidad debe ser positiva")
        if quantity > self.stock:
            raise ValueError("No hay suficiente stock disponible")
        self.stock -= quantity
        self.save()
        return self.stock

    def get_total_orders(self):
        """Devuelve el número total de órdenes que incluyen este producto"""
        return self.order.count()

    def deactivate(self):
        """Desactiva el producto"""
        self.is_active = False
        self.save()

    def activate(self):
        """Activa el producto"""
        self.is_active = True
        self.save()

    # Métodos de clase útiles
    @classmethod
    def get_available_products(cls):
        """Devuelve productos disponibles (activos y con stock)"""
        return cls.objects.filter(is_active=True, stock__gt=0)

    @classmethod
    def get_low_stock_products(cls, threshold=10):
        """Devuelve productos con stock bajo"""
        return cls.objects.filter(is_active=True, stock__lt=threshold, stock__gt=0)

    @classmethod
    def get_out_of_stock_products(cls):
        """Devuelve productos sin stock"""
        return cls.objects.filter(is_active=True, stock=0)
