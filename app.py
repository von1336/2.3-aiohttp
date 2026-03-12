from aiohttp import web
from datetime import datetime
import uuid
import json

ads = {}
AD_FIELDS = ("title", "description", "owner")


def ad_to_dict(ad_id, ad):
    return {
        "id": ad_id,
        "title": ad["title"],
        "description": ad["description"],
        "created_at": ad["created_at"],
        "owner": ad["owner"],
    }


async def create_ad(request):
    try:
        data = await request.json()
    except Exception:
        data = {}
    if not all(k in data for k in AD_FIELDS):
        return web.json_response(
            {"error": "Missing fields: title, description, owner"}, status=400
        )
    ad_id = str(uuid.uuid4())
    ads[ad_id] = {
        "title": data["title"],
        "description": data["description"],
        "owner": data["owner"],
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    return web.json_response(ad_to_dict(ad_id, ads[ad_id]), status=201)


async def get_ad(request):
    ad_id = request.match_info["ad_id"]
    if ad_id not in ads:
        return web.json_response({"error": "Not found"}, status=404)
    return web.json_response(ad_to_dict(ad_id, ads[ad_id]))


async def update_ad(request):
    ad_id = request.match_info["ad_id"]
    if ad_id not in ads:
        return web.json_response({"error": "Not found"}, status=404)
    try:
        data = await request.json()
    except Exception:
        data = {}
    for key in ("title", "description", "owner"):
        if key in data:
            ads[ad_id][key] = data[key]
    return web.json_response(ad_to_dict(ad_id, ads[ad_id]))


async def delete_ad(request):
    ad_id = request.match_info["ad_id"]
    if ad_id not in ads:
        return web.json_response({"error": "Not found"}, status=404)
    del ads[ad_id]
    return web.Response(status=204)


async def list_ads(request):
    return web.json_response([ad_to_dict(i, a) for i, a in ads.items()])


def create_app():
    app = web.Application()
    app.router.add_post("/advertisement", create_ad)
    app.router.add_get("/advertisement", list_ads)
    app.router.add_get("/advertisement/{ad_id}", get_ad)
    app.router.add_patch("/advertisement/{ad_id}", update_ad)
    app.router.add_delete("/advertisement/{ad_id}", delete_ad)
    return app


if __name__ == "__main__":
    app = create_app()
    web.run_app(app, host="0.0.0.0", port=5000)
