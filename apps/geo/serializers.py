from rest_framework import serializers

from .models import City, Country, Province


class CountrySerializer(serializers.ModelSerializer):
    provinces_count = serializers.SerializerMethodField()

    class Meta:
        model = Country
        fields = ["id", "name", "provinces_count"]

    def get_provinces_count(self, obj):
        return obj.provinces.count()


class ProvinceSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source="country.name", read_only=True)
    cities_count = serializers.SerializerMethodField()

    class Meta:
        model = Province
        fields = ["id", "name", "country", "country_name", "cities_count"]

    def get_cities_count(self, obj):
        return obj.cities.count()


class CitySerializer(serializers.ModelSerializer):
    province_name = serializers.CharField(source="province.name", read_only=True)
    country_name = serializers.CharField(source="province.country.name", read_only=True)
    full_location = serializers.SerializerMethodField()

    class Meta:
        model = City
        fields = [
            "id",
            "name",
            "province",
            "province_name",
            "country_name",
            "full_location",
        ]

    def get_full_location(self, obj):
        return f"{obj.name}, {obj.province.name}, {obj.province.country.name}"


class CountryDetailSerializer(serializers.ModelSerializer):
    provinces = ProvinceSerializer(many=True, read_only=True)

    class Meta:
        model = Country
        fields = ["id", "name", "provinces"]


class ProvinceDetailSerializer(serializers.ModelSerializer):
    country = CountrySerializer(read_only=True)
    cities = CitySerializer(many=True, read_only=True)

    class Meta:
        model = Province
        fields = ["id", "name", "country", "cities"]


class CityDetailSerializer(serializers.ModelSerializer):
    province = ProvinceDetailSerializer(read_only=True)

    class Meta:
        model = City
        fields = ["id", "name", "province"]
