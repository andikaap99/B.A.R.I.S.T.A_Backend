from fastapi import APIRouter

router = APIRouter(prefix="/api/menu", tags=["menu"])

MENUS = [
    "Chocolate Croissant",
    "Ginger Scone",
    "Cranberry Scone",
    "Latte",
    "Columbian Medium Roast Rg",
    "Latte Rg",
    "Dark chocolate Lg",
    "Sustainably Grown Organic Lg",
    "Sustainably Grown Organic Rg",
    "Earl Grey Rg",
    "Morning Sunrise Chai Rg",
    "Peppermint Rg",
]


@router.get("")
def get_all_menu():
    return {"count": len(MENUS), "data": MENUS}
