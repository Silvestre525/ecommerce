from .models import Country, Province, City

class GeoService:
    """
    Servicio para manejar la lógica de negocio de Geografía
    """
    @staticmethod
    def get_public_countries():
        return Country.objects.values("id", "name").order_by("name")

    @staticmethod
    def get_provinces_by_country(country_id):
        if not country_id:
            raise ValueError("Parámetro 'country_id' es requerido")
        try:
            country = Country.objects.get(id=country_id)
            provinces = Province.objects.filter(country=country).values("id", "name").order_by("name")
            return country, provinces
        except Country.DoesNotExist:
            raise KeyError("País no encontrado")

    @staticmethod
    def get_cities_by_province(province_id):
        if not province_id:
            raise ValueError("Parámetro 'province_id' es requerido")
        try:
            province = Province.objects.select_related("country").get(id=province_id)
            cities = City.objects.filter(province=province).values("id", "name").order_by("name")
            return province, cities
        except Province.DoesNotExist:
            raise KeyError("Provincia no encontrada")

    @staticmethod
    def get_cities_by_country(country_id):
        if not country_id:
            raise ValueError("Parámetro 'country_id' es requerido")
        try:
            country = Country.objects.get(id=country_id)
            cities = City.objects.select_related("province").filter(province__country=country).values("id", "name", "province__name").order_by("name")
            return country, cities
        except Country.DoesNotExist:
            raise KeyError("País no encontrado")
