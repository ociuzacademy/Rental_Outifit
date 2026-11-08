import os
from django.core.files import File
from rentelapp.models import Outfits, OutfitSize, Categories

def run():

    # Get or create category
    category, _ = Categories.objects.get_or_create(
        name="Wedding Collection",
        defaults={'requires_size': True}
    )

    base_path = r"D:\st_marys\rentel\rentel\rentel\outfits"

    outfits_data = [
        {
            "name": "Elegant Bridal White Saree",
            "price": 2500,
            "description": "Beautiful lace bridal saree with floral bouquet styling.",
            "image": "o1.avif",
            "sizes": {
                "S": 2,
                "M": 3,
                "L": 2,
                "XL": 1
            }
        },
        {
            "name": "Royal Wedding Ball Gown",
            "price": 4500,
            "description": "Heavy designer wedding gown with premium embroidery.",
            "image": "w1.jpeg",
            "sizes": {
                "S": 1,
                "M": 2,
                "L": 2,
                "XL": 1
            }
        },
        {
            "name": "Princess Style White Gown",
            "price": 4000,
            "description": "Elegant princess gown perfect for receptions and bridal shoots.",
            "image": "w-gown.jpeg",
            "sizes": {
                "S": 2,
                "M": 2,
                "L": 3,
                "XL": 1
            }
        }
    ]

    for data in outfits_data:
        image_path = os.path.join(base_path, data["image"])

        with open(image_path, 'rb') as img_file:
            outfit = Outfits.objects.create(
                category=category,
                name=data["name"],
                price=data["price"],
                description=data["description"],
                image=File(img_file, name=data["image"])
            )

        # Add sizes
        for size, qty in data["sizes"].items():
            OutfitSize.objects.create(
                outfit=outfit,
                size=size,
                quantity=qty
            )

        print(f"✅ Added: {outfit.name}")