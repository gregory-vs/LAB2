from typing import TypedDict


class CatalogItem(TypedDict):
    title: str
    category: str
    points: int
    description: str
    image_url: str
    redeem_enabled: bool


class CollectionStats(TypedDict):
    today_collections: int
    pending_rewards: int


class RecentActivity(TypedDict):
    title: str
    date: str
    points: int


def get_collection_stats() -> CollectionStats:
    return {"today_collections": 12, "pending_rewards": 850}


def get_catalog_items() -> list[CatalogItem]:
    return [
        {
            "title": "Coffee Discount",
            "category": "Dining",
            "points": 50,
            "description": (
                "Get a 50% discount on any hot beverage at participating terminal coffee shops."
            ),
            "image_url": (
                "https://lh3.googleusercontent.com/aida-public/"
                "AB6AXuCYyS-QzdKv1GdunoSD5Cwc-mmhBDGrCmaZ45BzeJTKJgk5YFOBgDBcHLjZ-"
                "07MM1Vvt0hTveBCHAViAcmHxmcBb4ChwcXayASJgHuJe9RYaK7bBJobXqDCX3gLhf1FHtrEw"
                "LKcewey-WCYiBovjV8gScCf7KLPwzoy3E5gFwaEV1e4fKE-gXcuVU6-j56uY38_tbc9W84k"
                "viVz0Gnp5Cl5KChrOq4a1LFyXo7UWG1TUcenQQZyepoF69TEQM3prWBTH2_n4ImtNQM5"
            ),
            "redeem_enabled": True,
        },
        {
            "title": "VIP Lounge Access",
            "category": "Premium",
            "points": 500,
            "description": (
                "One-time entry pass to the Silver Wing Premium Lounge with buffet and showers."
            ),
            "image_url": (
                "https://lh3.googleusercontent.com/aida-public/"
                "AB6AXuDXAn5jnj-KV9SOcoHNIUGPJFP4ckjHXtCWK3Wp--QYzhHpOLJ_FYMU0KjOIz9K2fpe"
                "1e6vu-O4Y3RSnqdJwjmW2xnfxtU8pDIa2CE_NJAQd0lluHKH3WostCr-m5IkT20l9VvKlw3dX"
                "uW_0bgWAhNSROjBxHAFKKgaAReCdSo5UH_wYaL3QTiKV-Z9lXffNCirSR1KZlLc0Xvo9K4L_"
                "uJZMbgTKWWHkpqD0wkwCgjtbeUVpLZuLvUQYM74bEZSG9wRl6i_Q6yDhvDj"
            ),
            "redeem_enabled": True,
        },
        {
            "title": "Duty Free Voucher",
            "category": "Shopping",
            "points": 250,
            "description": (
                "$20 voucher applicable to any purchase over $100 at Terminal 3 Duty Free."
            ),
            "image_url": (
                "https://lh3.googleusercontent.com/aida-public/"
                "AB6AXuDlC2KDzqlVayIk-OoQC1kR3qbIAvjprDRW82kkrOaehLGe9cS83LGc0Nm5Mj6u9N6G"
                "TdpZTcHeBsQFrQMNbnjCy4u5Ix8BN_Tp69kcLP4hrq6vTLltGlPHqdsoKCy1RHkUw8JNKCEy"
                "7_93al08VxTKQC_t1VGGBnm-f9GNZFzKOk-b5TG0jJs3sUAz7pVwQkpdLhhQWUqNXxBst7HAU"
                "bUm93lQCqMUQ32xl3J2cMlFiyFYznZ8ItJbxfl3bmdIGC2vY5IDP8TpIq74"
            ),
            "redeem_enabled": True,
        },
        {
            "title": "Fast Track Lane",
            "category": "Utility",
            "points": 2500,
            "description": (
                "Skip the lines with a priority security lane pass for your next departure."
            ),
            "image_url": (
                "https://lh3.googleusercontent.com/aida-public/"
                "AB6AXuD7yGb7sozakuZLhs418kjlRcBPzt-IkIGuriYPyTGc4_5WYfBLOcYvDSGYNA6M7RFi"
                "dhh6fpE4RQ4hl9q3s8FJdOjCwjDFGtSCxRCfSXh_80i-lvMdI_EgtLuzNTJTjyCE7nAj18vO"
                "a-lDA-aEzcvqECC5kUyUaDG3nSlE_Qk-t4OYcYiXOaN5wCsMFeQOQUchEvXQt1S8H4y6sXhL"
                "lmKhnNaUEqeoa-4OMcAfrJXT4o8OWKXx7u-9ZswpxTGVXVKkQEhBuxJDquwn"
            ),
            "redeem_enabled": False,
        },
    ]


def get_recent_activities() -> list[RecentActivity]:
    return [
        {"title": "Coleção Terminal A", "date": "Hoje, 14:20", "points": 12},
        {"title": "Coleção Estacionamento P3", "date": "Ontem, 09:15", "points": 8},
        {"title": "Resgate: Vale-Café", "date": "12 Out, 16:45", "points": -30},
    ]
