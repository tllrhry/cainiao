"""Update company info with correct seed data."""

import sys
sys.path.insert(0, "D:\\cainiao\\backend")

from app.database import SessionLocal
from app.models.company import CompanyInfo

db = SessionLocal()

# Updated seed data - user's actual company info
seeds = [
    ("company_name", "菜鸟设计", "text"),
    ("company_subtitle", "深耕郑州 · 立足河南 · 辐射全国", "text"),
    ("about_us",
     "菜鸟设计深耕郑州，立足河南，辐射全国，郑州菜鸟广告设计是一家专注高端创意设计、纯设计不施工的专业广告设计机构。\n\n"
     "专注文化建设核心领域，主打展厅展馆、文化墙、主题公园、导视系统、文化连廊五大业务板块。服务覆盖政企单位、院校校园、医疗机构、城市社区等各类机构。\n\n"
     "我们拥有资深设计团队60余人，深耕行业多年，坚持原创定制、方案落地、高性价比、报价透明的服务准则。拒绝模板套稿，配备一对一专属设计师全程跟进，从前期策划、方案创意到效果图、施工图输出，提供一站式全流程专业设计交付。\n\n"
     "以匠心做设计，以专业赢口碑，我们致力于打造全国值得信赖的全案设计服务商，为每一位客户量身定制专属高品质设计作品。",
     "text"),
    ("core_values_title", "核心优势", "text"),
    ("core_value_1_title", "纯设计不施工", "text"),
    ("core_value_1_desc", "专注高端创意设计，拒绝模板套稿，坚持原创定制方案", "text"),
    ("core_value_1_icon", "Medal", "text"),
    ("core_value_2_title", "资深团队", "text"),
    ("core_value_2_desc", "60余人设计团队深耕行业多年，一对一专属设计师全程跟进", "text"),
    ("core_value_2_icon", "UserFilled", "text"),
    ("core_value_3_title", "一站式交付", "text"),
    ("core_value_3_desc", "从策划到效果图、施工图输出，全流程专业设计交付", "text"),
    ("core_value_3_icon", "DocumentChecked", "text"),
    ("core_value_4_title", "报价透明", "text"),
    ("core_value_4_desc", "高性价比，报价透明，致力于成为全国信赖的全案设计服务商", "text"),
    ("core_value_4_icon", "PriceTag", "text"),
    ("contact_address", "郑州市郑东新区商务外环路18号", "text"),
    ("contact_phone", "0371-8888-6666", "text"),
    ("contact_email", "hello@cainiao.design", "text"),
]

count = 0
for k, v, t in seeds:
    existing = db.query(CompanyInfo).filter(CompanyInfo.key == k).first()
    if existing:
        existing.value = v
        existing.type = t
    else:
        db.add(CompanyInfo(key=k, value=v, type=t))
    count += 1

db.commit()
db.close()
print(f"OK: {count} records updated")
