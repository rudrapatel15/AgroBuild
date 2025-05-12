from django.core.management.base import BaseCommand
from agrobuild.models import Category

class Command(BaseCommand):
    help = 'Populates the database with initial categories'
    
    def handle(self, *args, **options):
        # Clear existing categories first
        Category.objects.all().delete()
        
        # ==================== PLANTS ====================
        plants = Category.objects.create(name='Plants', slug='plants', menu='plants')
        
       # Wellbeing Plants
        wellbeing = Category.objects.create(name='Wellbeing Plants', slug='wellbeing-plants', parent=plants, menu='plants')
        Category.objects.create(name='Positivity Plant', slug='positivity-plant', parent=wellbeing, menu='plants')
        Category.objects.create(name='Stress Buster Plant', slug='stress-buster-plant', parent=wellbeing, menu='plants')
        Category.objects.create(name='Mental Health Plant', slug='mental-health-plant', parent=wellbeing, menu='plants')
        Category.objects.create(name='Boosts Creativity Plant', slug='boosts-creativity-plant', parent=wellbeing, menu='plants')
        Category.objects.create(name='Self Care Plants', slug='self-care-plants', parent=wellbeing, menu='plants')
        Category.objects.create(name='Improves Mood Plant', slug='improves-mood-plant', parent=wellbeing, menu='plants')
        Category.objects.create(name='Aura Plant', slug='aura-plant', parent=wellbeing, menu='plants')
        # Shop by Type
        shop_by_type = Category.objects.create(name='Shop by Type', slug='shop-by-type', parent=plants, menu='plants')
        Category.objects.create(name='Air Purifying Plants', slug='air-purifying-plants', parent=shop_by_type, menu='plants')
        Category.objects.create(name='Indoor Plants', slug='indoor-plants', parent=shop_by_type, menu='plants')
        Category.objects.create(name='Low Maintenance Plants', slug='low-maintenance-plants', parent=shop_by_type, menu='plants')
        Category.objects.create(name='Hanging Plants', slug='hanging-plants', parent=shop_by_type, menu='plants')
        Category.objects.create(name='Colorful Plants', slug='colorful-plants', parent=shop_by_type, menu='plants')
        Category.objects.create(name='Vastu Plants', slug='vastu-plants', parent=shop_by_type, menu='plants')
        Category.objects.create(name='Fast Growing', slug='fast-growing-plants', parent=shop_by_type, menu='plants')
        
        # Shop by Face
        shop_by_face = Category.objects.create(name='Shop by Face', slug='shop-by-face', parent=plants, menu='plants')
        Category.objects.create(name='Office Plants', slug='office-plants', parent=shop_by_face, menu='plants')
        Category.objects.create(name='Dining Table Plants', slug='dining-table-plants', parent=shop_by_face, menu='plants')
        Category.objects.create(name='Living Room Plants', slug='living-room-plants', parent=shop_by_face, menu='plants')
        Category.objects.create(name='Bedroom Plants', slug='bedroom-plants', parent=shop_by_face, menu='plants')
        Category.objects.create(name='Balcony Plants', slug='balcony-plants', parent=shop_by_face, menu='plants')
        Category.objects.create(name='Study Room Plants', slug='study-room-plants', parent=shop_by_face, menu='plants')
        Category.objects.create(name='Window Plants', slug='window-plants', parent=shop_by_face, menu='plants')

        # ==================== SEEDS ====================
        seeds = Category.objects.create(name='Seeds', slug='seeds', menu='seeds')
        
        # Horticulture Crops
        horticulture = Category.objects.create(name='Horticulture Crops', slug='horticulture-crops', parent=seeds, menu='seeds')
        Category.objects.create(name='Vegetable Seeds', slug='vegetable-seeds', parent=horticulture, menu='seeds')
        Category.objects.create(name='Fruit Seeds', slug='fruit-seeds', parent=horticulture, menu='seeds')
        Category.objects.create(name='Flower Seeds', slug='flower-seeds', parent=horticulture, menu='seeds')
        Category.objects.create(name='Seeds Germinator', slug='seeds-germinator', parent=horticulture, menu='seeds')
        
        # Field Crops
        field_crops = Category.objects.create(name='Field Crops', slug='field-crops', parent=seeds, menu='seeds')
        Category.objects.create(name='Forages', slug='forages', parent=field_crops, menu='seeds')
        Category.objects.create(name='Maize/Corn', slug='maize-corn', parent=field_crops, menu='seeds')
        Category.objects.create(name='Paddy', slug='paddy', parent=field_crops, menu='seeds')
        Category.objects.create(name='Mustard', slug='mustard', parent=field_crops, menu='seeds')
        Category.objects.create(name='Jowar', slug='jowar', parent=field_crops, menu='seeds')
        Category.objects.create(name='Cotton', slug='cotton', parent=field_crops, menu='seeds')
        Category.objects.create(name='Fast Growing', slug='fast-growing-seeds', parent=field_crops, menu='seeds')
        
        # Popular Products
        popular_seeds = Category.objects.create(name='Popular Products', slug='popular-seeds', parent=seeds, menu='seeds')
        Category.objects.create(name='Tomato', slug='tomato-seeds', parent=popular_seeds, menu='seeds')
        Category.objects.create(name='Brinjal', slug='brinjal-seeds', parent=popular_seeds, menu='seeds')
        Category.objects.create(name='Cauliflower', slug='cauliflower-seeds', parent=popular_seeds, menu='seeds')
        Category.objects.create(name='Cucumber', slug='cucumber-seeds', parent=popular_seeds, menu='seeds')

        # ==================== CROP NUTRITION ====================
        crop_nutrition = Category.objects.create(name='Crop Nutrition', slug='crop-nutrition', menu='crop_nutrition')
        
        # Fertilizers
        fertilizers = Category.objects.create(name='Fertilizers', slug='fertilizers', parent=crop_nutrition, menu='crop_nutrition')
        Category.objects.create(name='BIO/Organic Fertilizers', slug='bio-organic-fertilizers', parent=fertilizers, menu='crop_nutrition')
        Category.objects.create(name='Chemical Fertilizers', slug='chemical-fertilizers', parent=fertilizers, menu='crop_nutrition')
        Category.objects.create(name='NPK Fertilizers', slug='npk-fertilizers', parent=fertilizers, menu='crop_nutrition')
        Category.objects.create(name='Liquid Fertilizers', slug='liquid-fertilizers', parent=fertilizers, menu='crop_nutrition')
        Category.objects.create(name='pH Balancers', slug='ph-balancers', parent=fertilizers, menu='crop_nutrition')
        Category.objects.create(name='Humic Acids', slug='humic-acids', parent=fertilizers, menu='crop_nutrition')
        
        # Growth Promotors
        growth_promotors = Category.objects.create(name='Growth Promotors', slug='growth-promotors', parent=crop_nutrition, menu='crop_nutrition')
        Category.objects.create(name='Plant Growth Promotors', slug='plant-growth-promotors', parent=growth_promotors, menu='crop_nutrition')
        Category.objects.create(name='Plant Enhancers', slug='plant-enhancers', parent=growth_promotors, menu='crop_nutrition')
        Category.objects.create(name='BIO Activators/Stimulants', slug='bio-activators-stimulants', parent=growth_promotors, menu='crop_nutrition')
        
        # Plant Growth Regulators
        growth_regulators = Category.objects.create(name='Plant Growth Regulators', slug='plant-growth-regulators', parent=crop_nutrition, menu='crop_nutrition')
        Category.objects.create(name='Fruit Enhancers', slug='fruit-enhancers', parent=growth_regulators, menu='crop_nutrition')
        Category.objects.create(name='Flower Boosters', slug='flower-boosters', parent=growth_regulators, menu='crop_nutrition')
        Category.objects.create(name='Yields Boosters', slug='yields-boosters', parent=growth_regulators, menu='crop_nutrition')

        # ==================== CROP PROTECTION ====================
        crop_protection = Category.objects.create(name='Crop Protection', slug='crop-protection', menu='crop_protection')
        
        # BIO/Organic Pesticides
        bio_pesticides = Category.objects.create(name='BIO/Organic Pesticides', slug='bio-organic-pesticides', parent=crop_protection, menu='crop_protection')
        Category.objects.create(name='BIO Insecticides', slug='bio-insecticides', parent=bio_pesticides, menu='crop_protection')
        Category.objects.create(name='BIO Fungicides', slug='bio-fungicides', parent=bio_pesticides, menu='crop_protection')
        Category.objects.create(name='BIO Viricides', slug='bio-viricides', parent=bio_pesticides, menu='crop_protection')
        Category.objects.create(name='BIO Nematicides', slug='bio-nematicides', parent=bio_pesticides, menu='crop_protection')
        Category.objects.create(name='BIO Miticides/Acaricides', slug='bio-miticides-acaricides', parent=bio_pesticides, menu='crop_protection')
        
        # Chemical Pesticides
        chemical_pesticides = Category.objects.create(name='Chemical Pesticides', slug='chemical-pesticides', parent=crop_protection, menu='crop_protection')
        Category.objects.create(name='Insecticides', slug='insecticides', parent=chemical_pesticides, menu='crop_protection')
        Category.objects.create(name='Fungicides', slug='fungicides', parent=chemical_pesticides, menu='crop_protection')
        Category.objects.create(name='Bactericides', slug='bactericides', parent=chemical_pesticides, menu='crop_protection')
        Category.objects.create(name='Herbicides', slug='herbicides', parent=chemical_pesticides, menu='crop_protection')
        Category.objects.create(name='Miticides/Acaricides', slug='miticides-acaricides', parent=chemical_pesticides, menu='crop_protection')
        
        # Traps And Lures
        traps_lures = Category.objects.create(name='Traps And Lures', slug='traps-and-lures', parent=crop_protection, menu='crop_protection')
        Category.objects.create(name='Sticky Traps', slug='sticky-traps', parent=traps_lures, menu='crop_protection')
        Category.objects.create(name='Pheromone Traps', slug='pheromone-traps', parent=traps_lures, menu='crop_protection')
        Category.objects.create(name='Pheromone Lures', slug='pheromone-lures', parent=traps_lures, menu='crop_protection')
        Category.objects.create(name='Solar Light Traps', slug='solar-light-traps', parent=traps_lures, menu='crop_protection')

        # ==================== AGRICULTURAL EQUIPMENT ====================
        equipment = Category.objects.create(name='Agricultural Equipment', slug='agricultural-equipment', menu='equipment')
        
        # Agricultural Tools
        agri_tools = Category.objects.create(name='Agricultural Tools', slug='agricultural-tools', parent=equipment, menu='equipment')
        Category.objects.create(name='Nursery Tools', slug='nursery-tools', parent=agri_tools, menu='equipment')
        Category.objects.create(name='Fruit Harvester/Plucker', slug='fruit-harvester-plucker', parent=agri_tools, menu='equipment')
        Category.objects.create(name='Garden Tools', slug='garden-tools', parent=agri_tools, menu='equipment')
        Category.objects.create(name='Seeder/Transplantner', slug='seeder-transplantner', parent=agri_tools, menu='equipment')
        Category.objects.create(name='Miticides/Acaricides', slug='equipment-miticides-acaricides', parent=agri_tools, menu='equipment')
        
        # Accessories
        accessories = Category.objects.create(name='Accessories', slug='accessories', parent=equipment, menu='equipment')
        Category.objects.create(name='Tripal/Tarpaulin', slug='tripal-tarpaulin', parent=accessories, menu='equipment')
        Category.objects.create(name='Shade Net', slug='shade-net', parent=accessories, menu='equipment')
        Category.objects.create(name='Crop Cover', slug='crop-cover', parent=accessories, menu='equipment')
        Category.objects.create(name='Safety Kit', slug='safety-kit', parent=accessories, menu='equipment')
        Category.objects.create(name='Mulch', slug='mulch', parent=accessories, menu='equipment')
        
        # Irrigation
        irrigation = Category.objects.create(name='Irrigation', slug='irrigation', parent=equipment, menu='equipment')
        Category.objects.create(name='Pipe', slug='irrigation-pipe', parent=irrigation, menu='equipment')
        Category.objects.create(name='Water Pump', slug='water-pump', parent=irrigation, menu='equipment')
        Category.objects.create(name='Sprinkler', slug='sprinkler', parent=irrigation, menu='equipment')
        Category.objects.create(name='Drip Kit', slug='drip-kit', parent=irrigation, menu='equipment')

        self.stdout.write(self.style.SUCCESS('Successfully populated all categories and subcategories'))