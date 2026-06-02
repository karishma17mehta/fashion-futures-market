"""
Rewrites the top 50 market questions with sharp, verifiable, gut-feel questions.
Run: python -m scripts.rewrite_markets --execute
"""
import sys
import argparse
from pathlib import Path

_BACKEND = Path(__file__).resolve().parent.parent
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from db.session import SessionLocal
from db.models import Market

REWRITES = {
    # market_id: (new_question, new_resolution_criteria)
    "70e77ce6-0a8c-4f45-93cc-1d6cbcaab99a": (
        "Will the quarter-zip become a mainstream luxury item by end of 2026?",
        "Resolves YES if a luxury brand (Loro Piana, Brunello Cucinelli, Bottega Veneta or equivalent) launches a quarter-zip as a hero piece, OR if 'quarter zip' trends in Google Trends fashion category above 60/100 in any week before Jan 1 2027.",
    ),
    "cebbd541-8399-4195-abdc-fa1f027d7356": (
        "Will 'summer nails' remain a top trending search on Pinterest through August 2026?",
        "Resolves YES if 'summer nails' or 'summer nails 2026' stays in Pinterest's top 20 growing searches in any week during July or August 2026.",
    ),
    "ecbac69f-5ade-449a-abfe-7faef995795c": (
        "Will 'intentional wardrobe' become mainstream fashion language by end of 2026?",
        "Resolves YES if the phrase 'intentional wardrobe' or 'edited wardrobe' appears in a campaign or editorial by Zara, H&M, Net-a-Porter, or equivalent mass/mid-market brand.",
    ),
    "264a36b8-a652-46af-8a3c-2fa2a79ddcd9": (
        "Will thrift flipping go mainstream — covered by Vogue, NYT, or GQ in 2026?",
        "Resolves YES if a feature story on fashion resale as income or thrift arbitrage is published by Vogue, NYT Style, GQ, or BoF before Jan 1 2027.",
    ),
    "a862e757-8ffb-4564-bcd2-aa56480a5272": (
        "Will Y2K and 90s archival pieces dominate resale platforms by Q3 2026?",
        "Resolves YES if Depop, Vestiaire Collective, or Vinted publicly reports 90s/Y2K as a top search or sales category in any Q2 or Q3 2026 report.",
    ),
    "d13146a7-7e26-4e68-b603-c498713fe074": (
        "Will sheer layering be everywhere this summer — on the street, in stores, on social?",
        "Resolves YES if sheer layering appears in homepage features of 3+ major retailers (Zara, ASOS, Net-a-Porter, Mango, H&M) by September 1 2026.",
    ),
    "f2a8e3e5-4925-42ef-8bb1-68a7c15eaa8d": (
        "Will Matthieu Blazy make Chanel the hottest luxury brand of 2026?",
        "Resolves YES if Chanel ranks in Lyst's Top 5 Hottest Brands in any quarterly index published in 2026.",
    ),
    "da8879fa-7f73-493b-bf23-d0b62d241558": (
        "Will capsule wardrobe culture peak in 2026 — everyone talks about 'buying less, better'?",
        "Resolves YES if 'capsule wardrobe' trends above 70/100 on Google Trends in any week in 2026, OR appears as a named trend in Vogue or BoF.",
    ),
    "09e4375b-5caa-4431-ac28-d472ea327e42": (
        "Will cerulean blue be the colour of summer 2026?",
        "Resolves YES if cerulean or a named blue shade is declared a key colour by Zara, H&M, or ASOS in their summer 2026 campaign, or appears in Pantone's 2026 fashion colour report.",
    ),
    "58000a2e-029c-45ac-ba57-4c14a9240ed9": (
        "Will 'buy less, wear more' become the dominant fashion message of 2026?",
        "Resolves YES if intentional or mindful wardrobe messaging appears in campaigns from 5+ brands across different market levels (luxury, mid, fast fashion) before Jan 1 2027.",
    ),
    "02a7b40c-e421-43e1-aa2b-2f29657c4334": (
        "Will slow fashion finally go mainstream — picked up by trend forecasters in 2026?",
        "Resolves YES if 'slow fashion' or 'restorative fashion' is named a macro trend by WGSN, Trendalytics, Vogue Business, or BoF before Jan 1 2027.",
    ),
    "dbc0c773-0cc6-48f6-ab37-63e54d7abd36": (
        "Will the Travis Scott Shy Pink Jordan 1 hold a 2x resale premium for 3 months?",
        "Resolves YES if the Travis Scott x Air Jordan 1 Low 'Shy Pink' sells for 2x+ retail price on StockX or GOAT for any 30-day window within 90 days of release.",
    ),
    "3cda774e-69aa-4b23-829b-4c2a3686127c": (
        "Will barrel/balloon leg trousers be the trouser silhouette of 2026?",
        "Resolves YES if barrel or balloon leg trousers trend above 60/100 on Google Trends fashion in any week before Sept 1 2026, OR are featured on homepage of 3+ major retailers.",
    ),
    "361291e5-c351-4ac3-a5d5-dc03aa8816b4": (
        "Will surrealist fashion be a major runway theme for SS27?",
        "Resolves YES if trompe l'oeil, dreamlike proportions, or surrealist design is a named theme in 5+ SS27 runway reviews from Vogue Runway, BoF, or equivalent.",
    ),
    "50994f1d-2625-4e0a-a932-11a8e754bbc6": (
        "Will the fashion resale market top $30B in the US in 2026?",
        "Resolves YES if any industry report (ThredUp Resale Report, Statista, McKinsey) publishes US fashion resale market size above $30B for 2026.",
    ),
    "9c9bb113-67d3-4cf9-871a-3212e9e93a26": (
        "Will dopamine dressing come back — but make it expensive this time?",
        "Resolves YES if quality-fabric bright colour dressing (not fast fashion) is named a trend in 3+ major SS27 runway reviews by Vogue, BoF, or WWD.",
    ),
    "1538e064-3a64-4a84-8a54-97848cdd5471": (
        "Will the Swatch x Audemars Piguet collab sell out and flip above retail?",
        "Resolves YES if the MoonsWatch or equivalent Swatch x AP collab piece sells for 1.5x+ retail on secondary markets (eBay, Chrono24) for any 14-day period in 2026.",
    ),
    "9e9a0223-e5d0-4de3-9aeb-0390572552c0": (
        "Will 'offline luxury' — no screens, no drops, no hype — become a real trend in 2026?",
        "Resolves YES if 'offline luxury', 'digital detox fashion', or 'anti-digital luxury' is named a trend by WGSN, Vogue Business, or BoF before Jan 1 2027.",
    ),
    "9ade7d94-edf2-451d-a574-f521cd394fc6": (
        "Will office dressing become a dominant aesthetic on TikTok and Instagram in 2026?",
        "Resolves YES if office or 'corporate' styling hashtags maintain top-20 status in weekly growing fashion hashtags on TikTok or Instagram through Q3 2026.",
    ),
    "0604c574-2af9-44f1-91a9-9861493a297e": (
        "Will Saint Laurent be the most talked-about luxury brand of 2026?",
        "Resolves YES if Saint Laurent ranks top-3 in any Lyst Hottest Brands index, or top-3 in social share of voice among luxury houses (per Brandwatch or similar) in 2026.",
    ),
    "d474c977-6eed-4a73-bee6-8c5e2f35a636": (
        "Will lace be everywhere in SS26/AW26 — runways, high street, and social?",
        "Resolves YES if lace is a featured fabric in 5+ SS26 or AW26 runway collections per Vogue Runway, OR appears on homepages of 3+ major retailers simultaneously.",
    ),
    "04642e17-09ff-4cc2-84ea-755e609a3036": (
        "Will kitten heels and metallics define the going-out look of 2026?",
        "Resolves YES if kitten heels or metallic fabric is named a key trend in Vogue, Harpers Bazaar, or BoF for SS26 or AW26 season.",
    ),
    "37f824d4-35e8-4714-8b5b-84b2ed3dfe0c": (
        "Will the French tip nail stay in the top 3 nail trends all summer 2026?",
        "Resolves YES if French tip or French manicure ranks in Pinterest's top 3 nail trends in any monthly report during June, July, or August 2026.",
    ),
    "5aaaea73-bf73-4af4-89eb-0040b0e6555d": (
        "Will mismatched, chaotic, or avant-garde nails replace clean-girl nails in 2026?",
        "Resolves YES if abstract, mismatched, or maximalist nail content ranks in TikTok or Pinterest's top 10 beauty content in any week of Q3 2026.",
    ),
    "f889f18d-9234-4a29-a885-331bb3a41e1e": (
        "Will graduation dressing become a major fashion moment in May–June 2026?",
        "Resolves YES if 'graduation outfit' trends above 70/100 on Google Trends in May or June 2026, OR 5+ major brands launch graduation-specific campaigns.",
    ),
    "34ae4f57-2949-480c-893e-339f0cad6748": (
        "Will Loewe become a top resale brand — searched as much as it's worn?",
        "Resolves YES if Loewe ranks top-5 in most-searched brands on Depop, Vestiaire Collective, or The RealReal in any month of Q3 or Q4 2026.",
    ),
    "5042c18f-2493-444b-a22e-d6e4ed983172": (
        "Will anti-theft, practical design features become a selling point in mainstream fashion?",
        "Resolves YES if hidden zips, RFID pockets, or anti-theft features are mentioned as a design highlight in 3+ major brand launches or editorial features before Jan 1 2027.",
    ),
    "1cd8ac0c-5d0a-413f-a518-b19d0c25fe64": (
        "Will the Isabel Marant x Havaianas flip sell out and hold resale value this summer?",
        "Resolves YES if the collaboration sells out within 72 hours of release AND lists for 1.5x+ retail on eBay or Depop within 30 days.",
    ),
    "9bbdef51-8536-4ae2-8a38-dcf9aa8c9679": (
        "Will Coach have a major Gen Z moment in 2026 — the new 'it' accessible luxury brand?",
        "Resolves YES if Coach ranks top-5 in most-searched accessible luxury brands on Depop or The RealReal, OR is named a breakout brand by Lyst or BoF in 2026.",
    ),
    "5aa3ffaf-f718-402b-9f9e-e24f6946f2c2": (
        "Will Valentino's popularity surge last all year or fade by summer?",
        "Resolves YES if Valentino maintains 2x+ search volume versus its pre-surge baseline (Jan 2025) on Google Trends through Q3 2026.",
    ),
    "6b16ffac-b926-480b-b9a3-4abc7dce49fe": (
        "Will 80s power dressing — big shoulders, bold colour, maximum drama — come back in 2026?",
        "Resolves YES if power dressing, 80s silhouettes, or structured shoulders are named a key trend in Vogue, BoF, or WWD for AW26.",
    ),
    "f6fc3204-77ae-4648-ac3a-2e123da37544": (
        "Will fashion get silly on purpose — humour and novelty as the anti-doom aesthetic?",
        "Resolves YES if novelty, humour-forward, or anti-serious fashion is named a macro theme in 5+ brand AW26 lookbooks or 2+ major editorial trend reports.",
    ),
    "d14a165d-a374-4140-a326-6969729db11d": (
        "Will statement belts — chain, western, oversized — be the accessory of 2026?",
        "Resolves YES if statement belts trend in top-10 accessory searches on Depop, Vestiaire Collective, or Pinterest in any month between May and September 2026.",
    ),
    "dff8926c-52ec-4782-9c18-fa8a4b8b7d21": (
        "Will thrift-flipping become a documented income stream — not just a hobby — in 2026?",
        "Resolves YES if a mainstream outlet (Vogue, GQ, NYT Style, The Cut) publishes a feature on fashion resale as a primary or supplemental income source before Jan 1 2027.",
    ),
    "a4c1024d-8ff3-4567-987f-a8879e9c3156": (
        "Will sporty-romantic dressing — tennis skirts, ballet flats, track jackets — define 2026?",
        "Resolves YES if 'romanticised sportswear' or 'elevated athleisure' is named a trend by Vogue, BoF, or WGSN, OR sports-inspired pieces dominate 3+ major retailer summer campaigns.",
    ),
    "ec8f478b-22eb-4b7c-b500-5a2e04df5974": (
        "Will crochet be a staple summer item in 2026 — not just festival, but everyday?",
        "Resolves YES if crochet maintains top-10 in summer fashion searches on Pinterest or Google Trends for any 4-week window between June and August 2026.",
    ),
    "d2fad4d2-40a4-4ded-b135-d77c45aaa8e2": (
        "Will gold — jewellery, fabric, accessories — be the dominant finish of 2026?",
        "Resolves YES if gold tones, lamé, or gold accessories feature on homepages of 5+ major fast-fashion retailers (Zara, H&M, ASOS, Mango, Topshop) simultaneously before Sept 2026.",
    ),
    "d04a7239-db45-47de-8f55-f56a8c98a8a6": (
        "Will gender-fluid minimalism break into the mainstream mid-market in 2026?",
        "Resolves YES if gender-neutral or gender-fluid collections are launched by 5+ mid-market brands (COS, Arket, & Other Stories, Uniqlo, M&S equivalent) before Jan 1 2027.",
    ),
    "71515bb6-9ff1-444e-b548-b58b0e3acf1f": (
        "Will graphic narrative prints — movie posters, murals, illustrations — take over fashion in 2026?",
        "Resolves YES if large-scale graphic or illustrative prints feature in 3+ SS27 runway collections or in high-street drop campaigns before end of 2026.",
    ),
    "7079d371-a6b1-4aa8-acac-c340e195eb08": (
        "Will brooches and statement pins become the accessory trend of 2026?",
        "Resolves YES if 'brooch' or 'statement pin' ranks in top-20 accessory searches on Pinterest in any week of Q2 or Q3 2026.",
    ),
    "dd61c4f7-55c3-41a4-9e22-3ce158893741": (
        "Will braids and structured half-up hairstyles dominate summer 2026 content?",
        "Resolves YES if braided or half-up hairstyle content ranks top-5 in Pinterest's hair category in any month between June and September 2026.",
    ),
    "0f8f0bdc-b573-4638-a540-3a2ed3aeb3bb": (
        "Will romantic, feminine dressing be the defining aesthetic of AW26?",
        "Resolves YES if 'romantic', 'feminine', or 'soft dressing' is named a top-5 macro trend by Vogue, BoF, or Harper's Bazaar for AW26.",
    ),
    "dd3444fe-704a-47a1-be56-403563354a22": (
        "Will a major brand drop a Tomodachi Life or Nintendo-inspired fashion collab in 2026?",
        "Resolves YES if a fashion brand (any tier) officially collaborates with Nintendo or directly references Tomodachi Life / Nintendo aesthetics in a commercial collection before Jan 1 2027.",
    ),
    "2bece603-a283-467f-80e1-c4e9a45326fe": (
        "Will the satchel bag make a full comeback as the It-bag of 2026?",
        "Resolves YES if satchel bags appear in top-10 bag searches on Depop or Vestiaire Collective, OR are featured as a key accessory in 2+ major editorial trend stories in 2026.",
    ),
    "591fb820-42f8-4596-8e6a-26b121aa6a30": (
        "Will white and off-white dominate every brand's summer 2026 campaign?",
        "Resolves YES if white or off-white is the dominant colour in homepage campaigns of 3+ major retailers (Zara, H&M, Mango, ASOS, Net-a-Porter) simultaneously in summer 2026.",
    ),
    "b429c6a6-2501-4f2a-a51b-6d99e60280d0": (
        "Will icy/frosted blue be named a key colour trend for 2026 by a major forecaster?",
        "Resolves YES if cool blue, ice blue, or frosted blue is named a key colour in the Pantone Fashion Colour Report, WGSN, or equivalent for any 2026 season.",
    ),
    "cb8aa1e8-8cd0-4115-a862-671a51eaa61f": (
        "Will month-specific nail content (June nails, July nails) become a permanent content format?",
        "Resolves YES if month-specific nail content maintains 200%+ YoY growth on Pinterest in any consecutive 3-month period through summer 2026.",
    ),
    "0d3eb12c-27c5-413e-81b5-70060e834ae1": (
        "Will anime-inspired monochrome looks cross over from Pinterest into runway and editorial?",
        "Resolves YES if anime aesthetic or manga-inspired fashion is referenced in 2+ SS27 runway collections or editorial spreads in Vogue, i-D, or Dazed.",
    ),
    "0a6e6684-0d0b-4982-9938-5f9c01ce29c0": (
        "Will vintage golf wear become a mainstream fashion trend — not just for golfers?",
        "Resolves YES if heritage or vintage golf-inspired clothing is named a trend by a major fashion publication (Vogue, BoF, GQ) or appears in high-street campaigns before Sept 2026.",
    ),
    "031de191-dad7-4301-b04d-0ea8eaabcd5e": (
        "Will luxury outdoor — expensive gear that looks good off the mountain — break through in 2026?",
        "Resolves YES if 3+ luxury brands (Loro Piana, Brunello Cucinelli, Arc'teryx Veilance, or equivalent) launch dedicated outdoor-elevated collections before Jan 1 2027.",
    ),
}


def run(execute: bool = False):
    db = SessionLocal()
    updated = 0
    not_found = 0

    try:
        for market_id, (question, criteria) in REWRITES.items():
            market = db.query(Market).filter(Market.id == market_id).first()
            if not market:
                print(f"  NOT FOUND: {market_id[:8]}")
                not_found += 1
                continue

            print(f"  {'UPDATING' if execute else 'PREVIEW'}: {market_id[:8]}")
            print(f"    OLD: {market.question[:80]}")
            print(f"    NEW: {question}")
            print()

            if execute:
                market.question = question
                market.resolution_criteria = criteria
                updated += 1

        if execute:
            db.commit()
            print(f"\n✓ Updated {updated} markets. {not_found} not found.")
        else:
            print(f"\nDRY RUN — would update {len(REWRITES)} markets. Pass --execute to apply.")

    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    run(execute=args.execute)
