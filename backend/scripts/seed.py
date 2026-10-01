import sys
from pathlib import Path

# Ensure backend root is on sys.path
backend_root = Path(__file__).resolve().parent.parent
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))

from app.database.session import SessionLocal
from app.models.disposal_guideline import DisposalGuideline
from app.models.waste_category import WasteCategory

SEED_DATA = [
    {
        "name": "Plastic",
        "slug": "plastic",
        "description": "Rigid and flexible plastics, beverage bottles, jugs, and recyclable containers.",
        "guideline": {
            "title": "Plastic Disposal & Recycling",
            "instructions": "Separate recyclable plastic from contaminated waste. Rinse containers when appropriate to remove residue and place in the designated recycling stream.",
            "do_not": "Do not include plastic contaminated with hazardous chemicals, medical waste, or non-recyclable multi-material films.",
        },
    },
    {
        "name": "Paper",
        "slug": "paper",
        "description": "Clean paper products, office paper, newspapers, magazines, and mail.",
        "guideline": {
            "title": "Paper Sorting & Handling",
            "instructions": "Keep paper clean and reasonably dry. Separate clean paper sheets from wet or food-contaminated waste.",
            "do_not": "Do not mix with grease-soaked paper, soiled napkins, or wax-lined paper.",
        },
    },
    {
        "name": "Cardboard",
        "slug": "cardboard",
        "description": "Corrugated boxes, shipping cartons, and paperboard food packaging.",
        "guideline": {
            "title": "Cardboard Preparation",
            "instructions": "Flatten cardboard boxes where possible to conserve bin volume. Keep cardboard clean and dry prior to recycling.",
            "do_not": "Do not recycle wax-coated, oil-stained, or food-greased cardboard (e.g. greasy pizza box bottoms).",
        },
    },
    {
        "name": "Glass",
        "slug": "glass",
        "description": "Glass beverage bottles, food jars, and container glass.",
        "guideline": {
            "title": "Glass Handling & Segregation",
            "instructions": "Handle carefully to avoid breakage. Rinse containers lightly and separate container glass from general household waste.",
            "do_not": "Do not mix window panes, mirrors, light bulbs, drinking tumblers, or ceramics with container glass.",
        },
    },
    {
        "name": "Metal",
        "slug": "metal",
        "description": "Aluminium beverage cans, tin and steel food cans, and clean metal lids.",
        "guideline": {
            "title": "Metal Recovery Guidelines",
            "instructions": "Empty all liquids and rinse food cans. Separate clean metal items for designated curbside or depot recycling.",
            "do_not": "Do not puncture pressurized aerosol cans or attempt to recycle cans with hazardous residues.",
        },
    },
    {
        "name": "Organic",
        "slug": "organic",
        "description": "Biodegradable food scraps, fruit and vegetable peels, coffee grounds, and yard clippings.",
        "guideline": {
            "title": "Organic Waste & Composting",
            "instructions": "Place suitable biodegradable food scraps and organic plant matter into the organic waste or composting stream.",
            "do_not": "Do not include plastic packaging, produce stickers, synthetic tea bags, or non-compostable liners.",
        },
    },
    {
        "name": "E-Waste",
        "slug": "e-waste",
        "description": "Discarded electronic devices, batteries, cables, chargers, and circuit boards.",
        "guideline": {
            "title": "Safe E-Waste Management",
            "instructions": "Deliver discarded electronics, circuit boards, and batteries to an authorized municipal e-waste collection center or drop-off facility.",
            "do_not": "Do not place electronic waste or rechargeable batteries in normal household garbage due to fire and chemical risks.",
        },
    },
    {
        "name": "Other",
        "slug": "other",
        "description": "Miscellaneous materials, composites, and residual non-recyclable solid waste.",
        "guideline": {
            "title": "General Residual Disposal",
            "instructions": "Use appropriate disposal based on the item's material composition. Place non-hazardous, non-recyclable items into the residual landfill waste stream.",
            "do_not": "Do not discard hazardous chemicals, paints, medical sharps, or toxic substances in general trash.",
        },
    },
]


def seed_database() -> None:
    """Idempotently seeds initial waste categories and disposal guidelines."""
    session = SessionLocal()
    categories_added = 0
    guidelines_added = 0

    try:
        for item in SEED_DATA:
            category = (
                session.query(WasteCategory)
                .filter(WasteCategory.slug == item["slug"])
                .first()
            )

            if not category:
                category = WasteCategory(
                    name=item["name"],
                    slug=item["slug"],
                    description=item["description"],
                    is_active=True,
                )
                session.add(category)
                session.flush()
                categories_added += 1
                print(f"[SEED] Added category: {category.name} ({category.slug})")
            else:
                print(f"[SKIP] Category already exists: {category.name} ({category.slug})")

            # Check for existing guideline for this category
            guideline_data = item["guideline"]
            existing_guideline = (
                session.query(DisposalGuideline)
                .filter(
                    DisposalGuideline.category_id == category.id,
                    DisposalGuideline.title == guideline_data["title"],
                )
                .first()
            )

            if not existing_guideline:
                guideline = DisposalGuideline(
                    category_id=category.id,
                    title=guideline_data["title"],
                    instructions=guideline_data["instructions"],
                    do_not=guideline_data.get("do_not"),
                )
                session.add(guideline)
                guidelines_added += 1
                print(f"  [SEED] Added guideline for: {category.name}")
            else:
                print(f"  [SKIP] Guideline already exists for: {category.name}")

        session.commit()
        print("\nSeed completed successfully!")
        print(f"Categories added: {categories_added}, Guidelines added: {guidelines_added}")

    except Exception as e:
        session.rollback()
        print(f"Error during seeding: {e}", file=sys.stderr)
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_database()
