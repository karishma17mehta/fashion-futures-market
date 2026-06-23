"""
Manual seed data for Fashion Futures Market.
All descriptions and theses are original analysis written by this platform.
Statistical data points (percentages, search volumes, market sizes) are facts
and are not subject to copyright.
Run from backend/ directory: python -m data.seeds.manual_seed
"""
import sys, uuid
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "backend"))

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=False)

from db.session import SessionLocal
from db.models import Trend, Market, TrendStatus, MarketStatus

TRENDS = [
    # ── RESALE ECONOMY & INTENTIONAL CONSUMPTION ─────────────────────────────
    {
        "name": "Modern Uniforms",
        "description": "Economic pressure and decision fatigue are pushing consumers toward capsule wardrobes and deliberate outfit repetition. Neutral palettes, quality tailoring, and enduring basics are replacing trend-driven hauls. The global capsule wardrobe market was valued at $1.3B in 2023 and is projected to reach $2.6B by 2030 — a doubling that signals structural behavioral shift rather than a passing style moment.",
        "ai_score": 9.1,
        "ai_thesis": "Modern Uniforms is the clearest expression of post-microtrend fatigue. The capsule wardrobe market is on track to double by 2030, and social search data confirms the shift: quality-descriptor queries are replacing trend-keyword searches across major platforms. Brands like COS, The Row, and Jil Sander are structurally positioned as beneficiaries. The signal is amplified by the fact that 57% of Americans now factor clothing resale into household financial planning — meaning consumers are selecting pieces partly on their future resale value, which rewards quality over novelty.",
        "source": "trend_intelligence",
        "signal_velocity": 8.7,
        "resolution_question": "Will 'capsule wardrobe' searches on Pinterest grow by more than 20% YoY by end of Q3 2026, confirming the Modern Uniforms trend entering mainstream demand?",
    },
    {
        "name": "Neo Nostalgia",
        "description": "Multi-era blending has replaced single-decade revival as the dominant nostalgia mode. Consumers are layering '70s coats with '90s knits and early-2000s accessories rather than recreating one era wholesale. Bandage dresses, JNCO-style jorts, and medieval-inspired silhouettes are simultaneously trending as top resale search terms — an unusual concurrent spike across three distinct decades.",
        "ai_score": 8.8,
        "ai_thesis": "Neo Nostalgia is historically durable — periods of cultural instability consistently drive fashion backward, and this cycle is notable for layering multiple eras simultaneously rather than reviving one at a time. Search analytics show JNCO jorts, bandage dresses, and medieval silhouettes spiking together in 2026, suggesting consumers are building hybrid-era identities rather than following a single trend directive. Pinterest's 'reaction pictures' at +400% YoY and 'aesthetic' holding at 98–100 normalized volume confirm appetite for layered, reference-rich visual expression. Brands enabling cross-decade styling through curated archive drops will capture outsized engagement.",
        "source": "trend_intelligence",
        "signal_velocity": 9.2,
        "resolution_question": "Will archival '90s and Y2K clothing searches on major resale platforms rank in the top 10 categories by Q3 2026, validating Neo Nostalgia as the dominant resale driver?",
    },
    {
        "name": "Everyday Ceremony",
        "description": "A behavioral shift toward treating ordinary moments as occasions — dressing up for daily life rather than reserving elevated styling for events. Tailored coats, kitten heels, draped skirts, metallic fabrics, and statement jewelry are the key items driving this movement. Social search data shows 'outfit inspo' at 99 normalized volume with +90% YoY growth, directly corroborating the elevated-everyday aesthetic direction.",
        "ai_score": 8.6,
        "ai_thesis": "Everyday Ceremony marks a structural reversal of athleisure's decade-long dominance. Search analytics confirm it: 'outfit inspo' has surged +90% YoY and floral content spiked to peak normalized volume in spring 2026, indicating the romantic, intentional aesthetic is fully embedded in consumer inspiration behavior. Miu Miu's kitten heel became one of the most-searched shoe styles of the past year; brands that position their products as occasion-worthy for daily life rather than reserved for events will benefit most from this shift.",
        "source": "trend_intelligence",
        "signal_velocity": 7.9,
        "resolution_question": "Will kitten heels and metallic fabrics appear as top-trending items in at least 3 major trend forecasting reports by end of 2026, confirming Everyday Ceremony's mainstream arrival?",
    },
    {
        "name": "Romanticized Sports",
        "description": "Athletic wear is being restyled through a high-fashion lens — vintage tracksuits, reworked jerseys, elevated bike shorts, and ski layers worn as fashion statements rather than performance gear. The 2026 World Cup, alongside several sports-themed films and TV series, is amplifying sportswear's cultural visibility. Resale platforms are recording vintage athletic pieces regularly exceeding their original retail prices.",
        "ai_score": 8.3,
        "ai_thesis": "Romanticized Sports benefits from a convergence of major cultural catalysts: the 2026 World Cup providing peak sportswear visibility, while the boundary between athletic and fashion media continues to dissolve. Prada Linea Rossa has validated luxury sport aesthetics from the top; independent labels are translating it for street-level consumption. Social search data shows 'braided hairstyles' at 99 normalized volume — a styling trend directly adjacent to sport-adjacent aesthetics. Resale velocity of vintage athletic pieces is the most reliable leading indicator for where this trend is heading.",
        "source": "trend_intelligence",
        "signal_velocity": 8.1,
        "resolution_question": "Will 'romanticized sports' or 'elevated athleisure' appear as named trend categories in Vogue, BoF, or similar editorial publications by Q4 2026?",
    },
    {
        "name": "The Intentional Wardrobe",
        "description": "A macro consumer shift away from accumulation toward curation — building wardrobes around pieces that earn repeated wear rather than chasing new arrivals. Consumers are repeating silhouettes, refining core staples, and measuring wardrobe value by longevity and resale potential. The capsule wardrobe market doubling by 2030 ($1.3B to $2.6B) is the quantitative anchor for this behavioral direction.",
        "ai_score": 9.0,
        "ai_thesis": "The Intentional Wardrobe is the most significant behavioral shift in fashion consumption in a decade. If it sustains, it represents a structural headwind for fast fashion and a structural tailwind for quality-positioned brands and resale platforms. The quantitative evidence is strong: the capsule wardrobe market is doubling, 57% of Americans factor resale into financial planning, and social search data consistently shows quality-descriptor queries outpacing trend keywords. Platforms and brands that speak the language of conviction and longevity rather than novelty will be the decade's winners.",
        "source": "trend_intelligence",
        "signal_velocity": 9.5,
        "resolution_question": "Will 'intentional wardrobe' messaging appear in the brand positioning of 5+ fashion brands' 2026 campaigns, signaling the concept's adoption as an industry-wide strategy?",
    },
    {
        "name": "Resale as Financial Planning",
        "description": "Clothing resale has crossed from sustainability behavior into household financial strategy. Survey data shows 57% of Americans now consider resale as part of their financial planning, using it to budget, save, and supplement income. Separately, 77% of Americans own fashion items they no longer wear — representing a massive pool of untapped inventory that the resale economy is only beginning to convert.",
        "ai_score": 8.9,
        "ai_thesis": "When the majority of Americans view their wardrobe as a financial asset rather than a sunk cost, market dynamics change fundamentally. Fashion churn increases, quality decisions are made with resale value in mind, and platforms that reduce listing friction win disproportionately. This shift amplifies adjacent trends: Neo Nostalgia pieces have measurable resale premiums, intentional wardrobe curation naturally selects for resale-worthy quality, and the 77% unused-wardrobe statistic represents an enormous supply pipeline waiting to be unlocked.",
        "source": "trend_intelligence",
        "signal_velocity": 9.3,
        "resolution_question": "Will resale platform GMV in the US exceed $30B in 2026, and will 'wardrobe as financial asset' framing appear in mainstream financial media (WSJ, Bloomberg) by Q3 2026?",
    },
    {
        "name": "Thrift Arbitrage Culture",
        "description": "Growing consumer fluency in brand quality, production history, and condition grading is creating a sophisticated thrift arbitrage culture — where knowledge of what to look for at thrift stores translates directly into resale income. With no-fee resale platforms lowering barriers and 57% of Americans using resale for financial planning, thrift-to-resale pipelines are becoming a mainstream income supplement rather than a niche hobby.",
        "ai_score": 8.3,
        "ai_thesis": "Thrift arbitrage is fashion's version of the gig economy — accessible, knowledge-dependent, and growing rapidly as the tools to execute it (no-fee platforms, AI listing assistance, pricing data) become widely available. The most sophisticated participants are building brand knowledge that rivals professional buyers. This behavior will increasingly surface in mainstream media as a skills story and lifestyle feature rather than merely a sustainability narrative, reaching audiences well beyond the existing resale community.",
        "source": "trend_intelligence",
        "signal_velocity": 7.7,
        "resolution_question": "Will a mainstream media outlet (Vogue, GQ, NYT Style) publish a feature on thrift arbitrage or 'fashion resale as income stream' by end of 2026?",
    },

    # ── SURREALISM & ESCAPIST AESTHETICS ─────────────────────────────────────
    {
        "name": "Surrealist Fashion Movement",
        "description": "Color, whimsy, and eccentricity are moving from runway niche into mainstream consumer aesthetics as a response to cultural uncertainty. Key wardrobing signals include extreme ruching and draped details, graphic narrative prints on utility silhouettes, thigh-high denim boots, exaggerated blazers, paper bag trousers, and asymmetrical hemlines. Men's surrealism is expressing through portrait-style knits, color-blocked wide-leg trousers, and sculptural accessories.",
        "ai_score": 8.9,
        "ai_thesis": "Surrealism as a macro-movement has documented historical precedent — it emerged after WWI as cultural escapism and is re-emerging now amid a similar climate of instability. Runway signals (narrative print utility garments, ruched asymmetry, sculptural accessories) are gaining editorial momentum after appearing in FW 2024. Social search analytics corroborate it: floral content peaked at 100 normalized volume, 'aesthetic' has held at 98–100 persistently, and 'doodles' rose +70% YoY — all consistent with appetite for expressive, escapist visual language.",
        "source": "trend_intelligence",
        "signal_velocity": 8.3,
        "resolution_question": "Will surrealist design elements (trompe l'oeil prints, dreamlike proportions, eccentrically placed hardware) appear in 5+ luxury brand SS27 runway collections?",
    },
    {
        "name": "Conversational Print Utility",
        "description": "Narrative-print utility garments — workwear silhouettes carrying large-scale graphic imagery — are emerging as a distinct fashion category at the intersection of gorpcore functionality and surrealist expression. Movie-poster prints on trousers, hand-painted imagery on jackets, and oversized illustrative graphics on utility-cut clothing are the primary expressions. Social search data shows 'doodles' +70% YoY and 'painting ideas' at 99 normalized volume, confirming appetite for expressive graphic content.",
        "ai_score": 8.1,
        "ai_thesis": "Conversational print utility sits at the collision of two durable trends: the ongoing workwear/gorpcore utility movement and the surrealist desire to turn clothing into narrative objects. Several high-profile runway moments in 2024 generated significant resale demand for graphic-print utility pieces, validating consumer appetite beyond editorial admiration. The broader creative-expression signals in social search (painting, doodles, drawing) suggest the graphic appetite is audience-wide, not just fashion-insider.",
        "source": "trend_intelligence",
        "signal_velocity": 7.5,
        "resolution_question": "Will graphic narrative prints (large-scale illustrative imagery, pop-culture graphics) on utility silhouettes appear in 3+ SS27 runway collections or major high-street drops by mid-2026?",
    },
    {
        "name": "Dopamine Dressing 2.0",
        "description": "The original dopamine dressing wave (2021–2023) mainstreamed bright color as a mood-lifting consumer behavior. The 2026 iteration is more sophisticated: expressive color is now paired with intentional silhouette and quality materials rather than volume and fast-fashion price points. The surrealist fashion macro-movement and a documented shift toward yellow and optimistic hues are both feeding into this elevated second generation of color dressing.",
        "ai_score": 7.9,
        "ai_thesis": "Dopamine Dressing 2.0 is distinguished from its predecessor by a craftsmanship requirement — consumers want color that is also quality. Brands modeling this successfully are using exceptional construction to justify bold color statements. Social search data shows 'painting ideas' at 99 normalized volume and 'aesthetic' at sustained 98–100, confirming color expressiveness remains in high demand. In periods of cultural uncertainty, optimistic colors historically outperform — the surrealism movement's documented driver of 'escapism' points in the same direction.",
        "source": "trend_intelligence",
        "signal_velocity": 6.8,
        "resolution_question": "Will quality-material expressive color dressing appear as a named trend in 3+ major SS27 runway reviews, distinguishing itself from the prior fast-fashion dopamine dressing wave?",
    },
    {
        "name": "Shades of Yellow Fashion",
        "description": "Yellow, mustard, butter cream, and ochre tones are gaining consistent runway and social visibility. AI-powered color forecasting flagged shades of yellow as a dominant direction for 2025 extending into 2026, and runway data supports it: yellow-mustard appears prominently across menswear collections in color-blocked trousers and knits. Social search confirms the broader optimistic-color appetite, with 'painting ideas' holding at 99 normalized volume year-round.",
        "ai_score": 7.5,
        "ai_thesis": "Color forecasting runs on a 12–18 month runway-to-retail pipeline, meaning AI-flagged yellow predictions from 2025 are now in retail execution. The broader surrealist fashion movement's emphasis on optimistic, escapist color directly supports yellow's continued relevance. Yellow is the most visually legible 'joy' signal in fashion — historically, in periods of cultural uncertainty, optimistic colors see amplified consumer uptake. The social search signal for color expressiveness (painting, doodles, drawing) is strong across the board.",
        "source": "trend_intelligence",
        "signal_velocity": 7.1,
        "resolution_question": "Will yellow/mustard/butter tones appear as a featured color in 5+ major brand SS26 or FW26 campaigns by end of 2026?",
    },

    # ── BRAND MOMENTUM SIGNALS ────────────────────────────────────────────────
    {
        "name": "Matthieu Blazy Era at Chanel",
        "description": "Matthieu Blazy's appointment as Chanel's creative director generated a +15% popularity spike in the 24 hours following his runway debut — outperforming the average creative director debut by approximately 7% in measured post and press volume. Blazy previously drove Bottega Veneta's ascent; his move to Chanel is the most-watched brand transition of 2026. Social listening data shows Chanel brand awareness accelerating from already elevated baseline levels.",
        "ai_score": 9.2,
        "ai_thesis": "Creative director transitions at luxury houses are among the highest-signal events in fashion — each major appointment in recent years produced multi-year brand momentum shifts. Blazy's debut showed +15% popularity within 24 hours and +7% more coverage than the average debut. For scale reference: one of the tracked luxury houses saw brand awareness grow 258% over 2025, partly driven by directional clarity at the top. A Blazy-led Chanel has the combination of heritage depth and a proven aesthetic builder — the dominant long-position in luxury fashion heading into 2026.",
        "source": "social_data",
        "signal_velocity": 9.0,
        "resolution_question": "Will Chanel rank in Lyst's Top 5 hottest brands index for both Q2 and Q3 2026, reflecting sustained momentum from Matthieu Blazy's creative direction?",
    },
    {
        "name": "Saint Laurent Brand Resurgence",
        "description": "Saint Laurent's brand awareness grew 258% over the course of 2025 — the largest single-year awareness increase among tracked luxury houses in the measured period. This growth outpaced comparable houses in raw awareness scale. The brand sits at the intersection of rock-and-roll heritage and modern minimalism, positioning it favorably against both the surrealist macro-movement and the ongoing multi-era nostalgia cycle.",
        "ai_score": 8.7,
        "ai_thesis": "A 258% annual brand awareness increase is a significant outlier at the luxury level, where organic growth typically moves in single digits. The brand's alignment with both Neo Nostalgia (YSL's archival rock-and-roll DNA) and the surrealist macro-movement (YSL's iconic surrealist history via Elsa Schiaparelli adjacency and its own archive) gives it rare dual positioning. Resale market signals — specifically vintage YSL commanding premiums over retail — are the leading indicator for whether this awareness converts to sustained commercial heat.",
        "source": "social_data",
        "signal_velocity": 8.8,
        "resolution_question": "Will Saint Laurent maintain top-3 brand awareness growth among tracked luxury houses through Q4 2026, sustaining its exceptional 2025 momentum?",
    },
    {
        "name": "Valentino Popularity Surge",
        "description": "Valentino's measured popularity is approximately 7x higher versus its baseline from a few months prior — an unusually abrupt acceleration compared to Saint Laurent's gradual awareness growth. Sudden spikes of this magnitude typically indicate a specific catalyst: creative direction signaling, a high-profile campaign, or a viral cultural moment. The brand's aesthetic territory overlaps with Everyday Ceremony and Romanticized Sports, two of the strongest 2026 consumer trend directions.",
        "ai_score": 8.4,
        "ai_thesis": "A 7x popularity spike in a compressed timeframe is algorithmically significant: social platforms amplify rising momentum, meaning Valentino's discovery rate is compounding rapidly across Instagram, Pinterest, and TikTok simultaneously. Historically, such spikes either convert into a durable new brand era or plateau within 6 months depending on product release cadence and editorial consistency. Resale velocity on major platforms is the most reliable proxy for whether this spike reflects genuine consumer desire or momentary viral exposure.",
        "source": "social_data",
        "signal_velocity": 8.0,
        "resolution_question": "Will Valentino sustain 3x+ elevated popularity levels versus its pre-spike baseline through Q3 2026, confirming a durable brand moment rather than a short-cycle spike?",
    },
    {
        "name": "Loewe Sentiment Leadership",
        "description": "Among tracked luxury house debut moments, Loewe's received the highest overall positive sentiment — outperforming houses with significantly higher post volume and press coverage. Positive sentiment is the metric that predicts purchasing intent and resale value more reliably than raw awareness. Social search data shows 'pose reference' at 92 normalized volume with +60% YoY growth, indicating that Loewe's highly styled, reference-rich visual language is shaping how audiences engage with fashion content broadly.",
        "ai_score": 8.5,
        "ai_thesis": "Positive sentiment is the leading indicator that converts awareness into purchasing intent. Loewe has consistently delivered intellectually resonant content that builds a loyal, purchase-driven audience — one that is more valuable per-person than brands with higher volume but lower sentiment. The brand's collaboration strategy (connecting fashion to craft, art, and pop culture) maps directly onto the surrealist movement and Neo Nostalgia directions. On resale platforms, Loewe pieces commanding premiums over retail price is the most reliable proxy for brand heat.",
        "source": "social_data",
        "signal_velocity": 7.8,
        "resolution_question": "Will Loewe rank as a top-5 most-searched brand on a major resale platform by Q4 2026, converting its sentiment leadership into measurable commercial demand?",
    },

    # ── MATERIAL & AESTHETIC DIRECTIONS ──────────────────────────────────────
    {
        "name": "Solace: Gender-Fluid Minimalism",
        "description": "Relaxed, gender-fluid, minimalist design with an emphasis on quality sustainable materials — recycled polyester, Econyl, Tencel — and indigo hues is moving from runway direction into mainstream consumer preference. The movement prioritizes conscious consumption and versatile pieces that transcend seasonal cycles. Jil Sander's recent debut at Milan received markedly more positive reception than comparable luxury debuts, directly validating this aesthetic territory.",
        "ai_score": 8.2,
        "ai_thesis": "Solace is the anti-trend trend — it grows precisely because microtrend fatigue is peaking. Consumer data showing 57% of Americans factor resale value into clothing purchases aligns directly with the Solace consumer's emphasis on materials that hold their quality and value over time. Econyl and Tencel certifications are becoming table stakes rather than premium differentiators for this audience. Brands like COS, Lemaire, and Toteme are the clearest commercial beneficiaries. Denim-adjacent social searches are structurally strong, supporting the indigo hue direction.",
        "source": "trend_intelligence",
        "signal_velocity": 7.6,
        "resolution_question": "Will gender-fluid minimalism and sustainable fabric certifications (Tencel, Econyl) become standard features in 5+ mid-market brand collections by end of 2026?",
    },
    {
        "name": "Boho Chic Suede Revival",
        "description": "Suede is re-entering fashion across footwear, bags, and outerwear at the convergence of multi-era nostalgia (strongly '70s-coded), the quality-materials consumer movement, and tactile sensory appeal following years of synthetic fabric saturation. Vintage '70s coats have emerged as top resale search terms, and the styling adjacency of boho suede to the broader Everyday Ceremony aesthetic (draped silhouettes, textured materials) gives it dual-trend support.",
        "ai_score": 7.7,
        "ai_thesis": "Boho suede is arriving at a convergence moment: the '70s component of the multi-era nostalgia cycle, the quality-materials dimension of intentional wardrobe curation, and the tactile preference for natural-feeling fabrics. Suede is authentically difficult to replicate at low price points — its texture signals craftsmanship in a way that synthetic alternatives cannot. The Everyday Ceremony consumer seeking tactile quality and the Neo Nostalgia consumer mixing '70s references are the two primary adopters, giving suede a broader market than either trend alone.",
        "source": "trend_intelligence",
        "signal_velocity": 7.3,
        "resolution_question": "Will suede appear as a featured material in major brand spring/summer 2026 campaign features across 3+ independent houses?",
    },
    {
        "name": "Aquatic Fashion Influences",
        "description": "Iridescent and pearlescent fabrics, wave-form prints, deep-sea color palettes (navy, teal, coral), and shell-inspired jewelry are gaining traction as a coherent aesthetic direction. AI-powered color and trend forecasting flagged aquatic influences as a key 2025 direction, and the broader summer aesthetic ecosystem — with social search data showing summer nail content at extraordinary growth rates — confirms the cultural mood supporting it.",
        "ai_score": 7.6,
        "ai_thesis": "Aquatic aesthetics arrive at a favorable cultural intersection: environmental consciousness around ocean health, Gen Z's documented affinity for natural-world references, and the sensory appeal of textured iridescent fabrics following synthetic fabric fatigue. The broader summer 2026 aesthetic signals are exceptionally strong — summer-specific nail and styling content is growing faster than any comparable seasonal category. Aquatic themes within this ecosystem have high organic discovery potential, particularly for accessories and nail art.",
        "source": "trend_intelligence",
        "signal_velocity": 7.4,
        "resolution_question": "Will aquatic-inspired collections (iridescent fabrics, ocean-color palettes, shell accessories) appear in 3+ major brand SS26 campaign features?",
    },

    # ── SOCIAL SEARCH BEHAVIORAL TRENDS ──────────────────────────────────────
    {
        "name": "Summer Nails 2026",
        "description": "Year-specific nail search behavior has exploded: the term 'summer nails 2026' grew 10,000%+ year-over-year in measured social search data, reaching peak normalized volume by May 2026 after starting near zero in February. Companion searches 'hottest summer nails' (+10,000% YoY) and 'fun summer nails' (+30% YoY) confirm structural demand. Nail content is the single highest-volume search category on major visual platforms.",
        "ai_score": 9.4,
        "ai_thesis": "The 10,000%+ YoY growth in year-specific nail queries reflects a new consumer behavior: audiences are searching for nail inspiration that is both seasonally and temporally coded. This creates predictable, recurring demand spikes that beauty brands can plan around with high confidence. Nail content has been the top search category on visual platforms for 12+ consecutive months — this is not a trend to track but a platform infrastructure to build on. Brands in nail care, press-on nails, and nail tools have an unusually clear signal for where to concentrate content investment.",
        "source": "social_data",
        "signal_velocity": 10.0,
        "resolution_question": "Will summer nail content maintain top-5 ranking in social platform growing trends through the full June–August 2026 window, confirming year-specific nail queries as a durable behavioral pattern?",
    },
    {
        "name": "French Tip Nail Renaissance",
        "description": "French tip nails have undergone a full aesthetic rehabilitation: from early-2000s default to unfashionable, and now back as a considered, intentional modern choice. Social search data shows french tips reaching peak all-time search volume with +90% YoY growth, and the style is prominently featured in summer nail moodboards driving the broader 10,000%+ growth in year-specific nail searches. The trend has shed its dated connotations and is repositioning as a clean, versatile base aesthetic.",
        "ai_score": 8.6,
        "ai_thesis": "French tip rehabilitation exemplifies the Neo Nostalgia mechanism: a style from the early-2000s becomes unfashionable, then re-emerges as a considered choice through the nostalgic lens rather than as a default. The +90% YoY growth on visual platforms, combined with 95–100 normalized volume consistently from March through May 2026, indicates durable mainstream arrival rather than a brief spike. The rehabilitation is complete — french tips now read as intentional rather than generic, which expands their appeal significantly.",
        "source": "social_data",
        "signal_velocity": 9.1,
        "resolution_question": "Will french tip nails maintain top-3 status in nail trend rankings through the full summer 2026 season (June–August), completing its rehabilitation from retro to perennial?",
    },
    {
        "name": "June Nails Content Wave",
        "description": "Month-specific nail content has become a distinct and predictable search behavior on visual platforms. 'June nails' reached +1,500% monthly growth and peak normalized volume in late May 2026. This follows a pattern established across multiple months: month-coded nail searches spike predictably as each month approaches. The broader nail content ecosystem is the most active single vertical on major visual platforms, with multiple subcategories simultaneously tracking at high volumes.",
        "ai_score": 7.8,
        "ai_thesis": "Month-specific nail queries represent systematized consumer behavior — not a single trend but a recurring seasonal infrastructure. Each month generates its own peak demand window, giving beauty brands an unusually predictable content calendar with built-in organic discovery. The nail content ecosystem is the single most powerful vertical on visual platforms, with nail, nail ideas, nail inspo, french tip nails, and graduation nails all tracking at high volume simultaneously. For brands in this space, monthly timing alignment is the highest-leverage marketing decision.",
        "source": "social_data",
        "signal_velocity": 8.4,
        "resolution_question": "Will month-specific nail content maintain 500%+ monthly growth on visual platforms through summer 2026, confirming the calendar-driven behavior as structural?",
    },
    {
        "name": "Graduation Fashion Surge",
        "description": "A graduation-specific fashion cluster peaks simultaneously each spring: nail designs, gift ideas, guest outfits, cap decorations, and cap-and-gown poses all spike in a synchronized April–June window. Social search data shows graduation gift ideas at +300% monthly, graduation guest outfits at +400% monthly, and graduation nail content at +200% monthly — all appearing in the same 6-week window. This is one of the most high-intent, purchase-driven seasonal clusters in fashion search behavior.",
        "ai_score": 8.5,
        "ai_thesis": "Graduation is a high-intent fashion moment with multiple distinct consumer segments: the 18–22 year old graduate building their adult wardrobe, the family member purchasing gifts, and the guest (typically a higher-income parent) buying a specific occasion outfit. The +400% monthly growth in graduation guest outfit searches specifically targets a higher-disposable-income segment than most fashion trend categories. Nine distinct graduation-related categories accelerating simultaneously in the same window is an unusually strong synchronized signal for retail planning.",
        "source": "social_data",
        "signal_velocity": 9.0,
        "resolution_question": "Will graduation-related fashion searches sustain top-20 ranking on growing trends platforms through June 2026, and will at least 5 major brands launch graduation-specific campaigns?",
    },
    {
        "name": "Patriotic Nail Art Peak",
        "description": "Patriotic nail content spikes reliably every late May through early July, driven by Memorial Day and 4th of July. Social search data shows 'patriotic nails' at +900% monthly growth, 'red white and blue nails' at +700% monthly, and patriotic french tip variations at +2,000% monthly. The pattern is consistent year over year, making this one of the most predictable high-velocity seasonal windows in beauty content.",
        "ai_score": 7.2,
        "ai_thesis": "Patriotic nail art is a reliable seasonal infrastructure rather than a trend to monitor — the data shows consistent annual spikes every Memorial Day through 4th of July window. Unlike fashion week-driven trends, this is directly actionable with a 90-day product and content lead time. It cross-pollinates with the broader nail ecosystem (the highest-volume category on visual platforms), making patriotic nail content especially strong for organic discovery during the June–July window. Beauty brands can build predictable revenue around this cycle with high confidence.",
        "source": "social_data",
        "signal_velocity": 8.8,
        "resolution_question": "Will patriotic nail art reach the #1 position in seasonal beauty trends on major visual platforms during the July 4, 2026 window?",
    },
    {
        "name": "Anime Monochrome Aesthetic",
        "description": "The anime monochrome aesthetic — applying Japanese animation's visual language (flat graphic composition, high-contrast black and white, stylized character framing) to fashion editorial and styling — has accelerated significantly, showing +200% monthly growth on major visual platforms while emerging from a near-zero baseline within the past year. It blends the mainstream penetration of anime culture (driven by global streaming) with an ongoing editorial preference for graphic black-and-white imagery.",
        "ai_score": 7.8,
        "ai_thesis": "Anime monochrome sits at the intersection of two durable forces: anime's continued mainstream cultural expansion and editorial fashion's persistent appreciation for black-and-white graphic imagery. The combination of +200% monthly growth from a new baseline — the typical profile of a trend that hasn't yet crossed from early adopters to mainstream — suggests a 6–12 month window before this reaches wider editorial recognition. Fashion brands targeting Gen Z specifically should treat this as an early signal worth acting on before it becomes obvious.",
        "source": "social_data",
        "signal_velocity": 7.2,
        "resolution_question": "Will anime monochrome aesthetic be referenced in at least 2 major fashion week SS27 collections or editorial spreads, confirming its crossover from niche to runway influence?",
    },
    {
        "name": "Tomodachi Life Fashion",
        "description": "Nintendo's Tomodachi Life relaunch has generated an unusual fashion signal: avatar-customization mechanics are driving real-world styling inspiration and personality-based dressing content. Social search data shows Tomodachi Life content at +8,500% YoY, personality chart content at +3,000% YoY, and character-based styling boards accelerating simultaneously. The game's mechanic of assigning personality types to fashion choices is proving directly translatable to real-world style exploration.",
        "ai_score": 8.0,
        "ai_thesis": "Gaming IP creating direct fashion inspiration pipelines is a documented pattern: prior Nintendo title launches drove distinct aesthetic movements that surfaced in real-world fashion. Tomodachi Life's avatar-customization mechanic is uniquely positioned to generate fashion content because it explicitly connects personality identity to clothing choices — the same psychological driver behind personal style. The 8,500% YoY spike confirms fashion-specific engagement rather than residual brand interest. Brands engaging with the bright color blocking and playful-proportions aesthetic early have a window before this saturates.",
        "source": "social_data",
        "signal_velocity": 8.5,
        "resolution_question": "Will a major streetwear or ready-to-wear brand launch a Nintendo or game-avatar-inspired collaboration before end of 2026, monetizing the gaming-to-fashion inspiration pipeline?",
    },
    {
        "name": "Reaction Pictures Economy",
        "description": "Social search data shows reaction image content growing +400% YoY on major visual platforms, with consistent high volume across all time windows from 2025 through mid-2026. Users are building libraries of fashion and pop-culture images for use as reaction content in digital communication — creating an unexpected secondary distribution channel for fashion imagery. Archival fashion photography is seeing organic resurfacing through this behavior.",
        "ai_score": 7.3,
        "ai_thesis": "Reaction picture culture has become an unofficial press distribution system for fashion: when a brand image becomes a widely-shared reaction meme, its reach multiplies by orders of magnitude without paid media. The +400% YoY growth on visual platforms indicates the behavior is accelerating and the audience is mainstream rather than niche. Second-order effects include systematic resurfacing of archival fashion photography (feeding Neo Nostalgia), engagement from non-traditional fashion audiences, and an opportunity for brands to intentionally design 'reactable' campaign imagery as a planned strategy.",
        "source": "social_data",
        "signal_velocity": 7.0,
        "resolution_question": "Will a major luxury brand intentionally create campaign imagery designed for reaction picture use by Q4 2026, formalizing reaction culture as a planned distribution strategy?",
    },
    {
        "name": "Project Hail Mary Aesthetic",
        "description": "The film adaptation of Project Hail Mary has generated a significant aesthetic signal cluster on visual platforms, with five related search terms simultaneously hitting 10,000%+ YoY growth in the April–May 2026 window. The film's visual language — utilitarian space-survival design, isolated minimalism, functional textiles — is being extracted into fashion moodboards and editorial references at a rate that suggests genuine aesthetic traction beyond typical film-promotional activity.",
        "ai_score": 7.4,
        "ai_thesis": "Five related terms from a single film all showing 10,000%+ growth simultaneously is an unusually strong cluster signal. The aesthetic itself — utilitarian minimalism with a survival-function logic — arrives at a moment when quiet luxury and normcore have already primed mainstream audiences for understated, functional design. Sci-fi film aesthetics have a documented history of surfacing in runway collections 6–12 months after peak cultural visibility. The convergence of the film's timing with the Solace/minimalism macro-movement creates a favorable environment for this aesthetic to translate into actual fashion products.",
        "source": "social_data",
        "signal_velocity": 7.0,
        "resolution_question": "Will sci-fi minimalism or utilitarian space-survival aesthetics appear in SS27 runway collections or major editorial features within 12 months of the film's peak search activity?",
    },
    {
        "name": "Hairstyles Content Surge",
        "description": "Hair content is the second most powerful vertical on major visual platforms after nail content, and it is accelerating: hairstyles overall grew +50% YoY in annual data, braided hairstyles reached near-peak normalized volume with +20% YoY growth, and half up half down hairstyles grew +200% YoY — the fastest-growing individual hair style in the measured window. These numbers represent durable structural demand, not a seasonal spike.",
        "ai_score": 8.0,
        "ai_thesis": "The +200% YoY growth of half-up styles specifically is the most actionable signal here — it outpaces prom hairstyles, braids, and curly styles, indicating a behavioral shift toward everyday-versatile styling rather than occasion-specific hair. For hair brands, this signals that content investment should shift from formal styling tutorials toward everyday versatile formats. Braids at near-peak normalized volume point to a sustained period of structured hair dominance that beauty brands should actively support through product development and content strategy.",
        "source": "social_data",
        "signal_velocity": 8.2,
        "resolution_question": "Will braided and half-up hairstyles maintain top-5 status in hair trend content on major visual platforms through Q3 2026?",
    },

    # ── TIKTOK-CONFIRMED SIGNALS (WoW growth data) ───────────────────────────
    {
        "name": "Quarter Zip Quiet Luxury",
        "description": "The quarter zip pullover has emerged as 2026's most contested fashion object — simultaneously coded as blue-collar utility, corporate aspirational, and quiet luxury depending on brand and context. A viral social media moment in late 2025 sparked +1,647% week-on-week growth in quarter zip content, with the adjacent Nike Tech hashtag reaching +1,125% WoW in the same window. The speed of adoption across all income demographics is unusually fast for a basic silhouette.",
        "ai_score": 8.1,
        "ai_thesis": "The quarter zip's viral moment was loaded with social commentary — the garment became a proxy debate about dress codes, class signaling, and assimilation. That cultural weight is exactly what turns a basic silhouette into a durable fashion object. Brands from Nike to luxury heritage houses have capitalized: the same garment reads as aspirational casual across a $50–$500 price range, making it one of the most cross-demographic fashion signals of the year. The convergence with quiet luxury aesthetics means it has staying power well beyond the original viral moment.",
        "source": "social_data",
        "signal_velocity": 8.8,
        "resolution_question": "Will the quarter zip appear in at least 3 luxury or premium brand SS27 collections, confirming its elevation from streetwear staple to cross-market fashion object by early 2027?",
    },
    {
        "name": "Corporate Girlie Office Dressing",
        "description": "Office-specific styling content has surged across social platforms — 'office outfits' content grew +811% week-on-week in January 2026, while the broader corporate girlie aesthetic has built a consistent creator class sharing commuter styling, office-appropriate GRWM content, and affordable professional wardrobing. The trend bridges the gap between post-pandemic return-to-office behavior and the everyday ceremony aesthetic direction, with creators positioning professional dressing as a form of personal expression rather than compliance.",
        "ai_score": 8.3,
        "ai_thesis": "Corporate Girlie is distinct from traditional office dressing content because its audience is seeking aspiration, not compliance. Creators are building genuine communities around professional styling — the content functions as identity-building for early-career consumers who are also the primary audience of platforms where the trend is growing fastest. The +811% WoW spike in January confirms the new-year wardrobe refresh as a reliable demand window, but the trend's underlying driver — professional identity formation — is structural and year-round. Adjacent signals: kitten heels trending in Everyday Ceremony, #WhiteDress +145% WoW for occasion dressing.",
        "source": "social_data",
        "signal_velocity": 8.5,
        "resolution_question": "Will office-specific styling content maintain a top-10 ranking in weekly growing fashion hashtags on major social platforms through Q3 2026, confirming professional dressing as a durable content category?",
    },
    {
        "name": "Coach Denim Resurgence",
        "description": "Coach emerged as one of the fastest-growing fashion hashtags on major video platforms in early 2026, driven primarily by denim — Coach denim bags, vintage Coach denim finds, outfit styling with denim accessories, and direct comparisons to more expensive luxury brands. Google Shopping data shows Coach searches up +170% in related queries. The brand is executing a successful Gen Z repositioning through denim-specific content, creating both product demand and brand discovery at scale.",
        "ai_score": 7.9,
        "ai_thesis": "Coach's denim moment is a textbook accessible luxury repositioning play — the brand is being discovered as 'cheaper luxury' by Gen Z audiences already buying into the denim-as-fashion narrative. What makes this durable is the organic creator momentum: users are generating the comparison content (Coach vs higher-price brands) independently, which is more persuasive than paid campaigns. The denim angle is structurally well-timed: jeans for women grew +350% in Google Shopping, heels +250%, and general denim demand is high across platforms. Coach is surfing multiple structural tailwinds simultaneously.",
        "source": "social_data",
        "signal_velocity": 7.8,
        "resolution_question": "Will Coach rank in the top 5 most-searched accessible luxury brands on resale platforms by Q3 2026, confirming its Gen Z repositioning converts to secondary market demand?",
    },
    {
        "name": "Graphic Tee Individuality Wave",
        "description": "The graphic tee is reasserting itself as the primary vehicle for individual expression in fashion. Social platform data shows 291,800 posts under relevant hashtags with +39% week-on-week growth, driven by creators styling single graphic pieces multiple ways — layering, accessorizing, mixing high-low. Content specifically centers on pieces that signal subcultural taste or humor rather than brand logos. Coachella 2026 confirmed the shift: the Justin Bieber band tee worn by Central Cee became the festival's defining fashion moment.",
        "ai_score": 7.7,
        "ai_thesis": "The graphic tee's resurgence is driven by an anti-uniformity impulse: as aesthetic categories flatten into algorithm-friendly similarity, the graphic tee is one of the few remaining garments that immediately communicates individual taste and reference points. The focus on styling versatility (showing one piece multiple ways) reflects the intentional wardrobe macro-trend, while the subcultural-taste angle connects to the neo-nostalgia and alt-aesthetics movements. Resale platforms are seeing vintage graphic tees commanding significant premiums — the purchase-intent signal from the resale market confirms organic consumer desire.",
        "source": "social_data",
        "signal_velocity": 7.5,
        "resolution_question": "Will graphic tees (non-logo, reference-based design) appear as a featured styling category in 3+ major editorial platforms by Q3 2026, confirming the anti-uniformity positioning?",
    },
    {
        "name": "Goth Fashion Revival",
        "description": "A documented goth and alternative aesthetics revival is building on social platforms as a direct response to cultural algorithmic flattening. The #GothFashion hashtag grew +48% week-on-week in January 2026, with adjacent alt-aesthetics content (grunge, punk, indie) simultaneously gaining traction. Creators are explicitly framing the aesthetic as resistance to the 'core-ification' of fashion — where every style becomes a sanitized, algorithm-friendly variant. TikTok's own trend report described this as users 'resisting the cultural flattening of recent years.'",
        "ai_score": 7.6,
        "ai_thesis": "Goth revival is arriving as a documented counter-reaction to the sanitization of subcultures through social media trend cycles. The explicitly oppositional framing ('resisting cultural flattening') gives it identity-formation energy that sustains beyond trend cycles — consumers building their identity around goth aesthetics are not going to abandon it when the algorithm moves on. Parallel signals in the Neo Nostalgia macro-trend confirm appetite for decade-specific references. For brands, the opportunity is in authentic subcultural engagement rather than trend-jacking: gothic-adjacent heritage brands (Vivienne Westwood, Rick Owens adjacents) have the highest organic credibility here.",
        "source": "social_data",
        "signal_velocity": 7.3,
        "resolution_question": "Will a major high-street or accessible brand launch a verified gothic or alternative aesthetic capsule collection by Q4 2026, confirming the trend's mainstream commercial arrival?",
    },

    # ── DEPOP CONFIRMED + RUNWAY VALIDATED ───────────────────────────────────
    {
        "name": "Cerulean Blue Moment",
        "description": "Cerulean blue is having its Barbie pink moment: confirmed across SS26 runways (Valentino, Chanel, Moschino), appearing as a key directional color in resale platform trend reports, and primed for a massive cultural catalyst with a major film sequel using the specific shade as its identity color. The convergence of runway presence, resale search activity, and a tentpole film release into the same summer window is the strongest multi-source color signal since pink's 2023 saturation.",
        "ai_score": 9.0,
        "ai_thesis": "The cerulean moment has three independent sources of momentum arriving simultaneously: SS26 runway validation from three major houses, documented trending status on resale platforms (purchase-intent signal), and a major film sequel that is explicitly branded around the color. The film catalyst is the wildcard — Barbie proved that a single film can saturate a color across all retail categories within weeks of release. Brands that pre-position cerulean inventory for summer 2026 have a narrow window of first-mover advantage before the color becomes unavoidable across the high street.",
        "source": "trend_intelligence",
        "signal_velocity": 9.1,
        "resolution_question": "Will cerulean blue appear in the top 5 trending color searches on Pinterest and major resale platforms between June and September 2026, tracking the film catalyst's impact on consumer demand?",
    },
    {
        "name": "Balloon Pants Breakout",
        "description": "Airy, voluminous trouser silhouettes — ranging from structured barrel-legs to full parachute proportions — are transitioning from runway novelty to commercial moment. Multiple SS26 collections featured the silhouette with designers including Zimmermann positioning it as a summer anchor, and resale platform monthly trend reports explicitly called it as an April 2026 directional item. The Coachella 2026 cycle reinforced the silhouette with real-world adoption visible at scale.",
        "ai_score": 8.4,
        "ai_thesis": "Balloon pants have cleared the most important hurdle for a runway silhouette: editorial adoption has been followed by real-world consumer uptake at festival scale. That Coachella-to-mainstream pipeline is the fastest fashion-to-consumer pathway available — when a silhouette works visually in festival photography, it spreads organically. The runway-to-resale pipeline for this specific shape is now active: early buyers are already paying premiums for Zimmermann-adjacent pieces. The garment has multi-era resonance (Y2K parachute pants nostalgia + contemporary volume aesthetic), giving it both trend and nostalgia amplifiers simultaneously.",
        "source": "trend_intelligence",
        "signal_velocity": 8.6,
        "resolution_question": "Will balloon/barrel-leg trousers appear in the top 20 most-searched items on a major resale platform by July 2026, confirming the transition from runway to consumer demand?",
    },
    {
        "name": "Racy Lace Revival",
        "description": "Lace as a fashion statement has returned through an unexpected route: Sabrina Carpenter and Madonna's Coachella 2026 performance in matching lace corsets became the festival's most-reproduced styling moment. Asymmetric lace cuts and lace hemline details appeared on the SS26 Vivienne Westwood runway, providing editorial validation alongside the cultural moment. Resale platform April trend data confirms lace as a key April 2026 directional item, completing the full signal stack: viral cultural moment + runway + purchase intent.",
        "ai_score": 8.7,
        "ai_thesis": "A celebrity styling moment alone rarely sustains — but Carpenter x Madonna lace has runway backing (Vivienne Westwood SS26) and resale search activity as independent corroboration. That triple signal stack means this is a genuine trend rather than a celebrity moment with a short half-life. The lace direction fits multiple macro-trends: Everyday Ceremony's elevated-everyday aesthetic and Neo Nostalgia's early-2000s references (lace corsets were definitional in that era). Brands positioned in the lace category have a commercial window from now through late summer before the silhouette becomes fully ubiquitous.",
        "source": "trend_intelligence",
        "signal_velocity": 8.8,
        "resolution_question": "Will lace appear as a featured fabric in 5+ SS27 runway collections or major brand FW26 campaigns, sustaining its trajectory from Coachella moment to seasonal staple?",
    },
    {
        "name": "Crochet Craft Core",
        "description": "Crochet has reached its broadest fashion legitimacy in decades. The 2026 Coachella cycle delivered a wave of crochet mini dresses, bralets with cut-off denim, and head-to-toe knit looks that generated significant styling content. Social platform data shows the #CrochetersOfTikTok community growing +51% week-on-week, blending DIY knitwear with commercial styling. The craft-meets-fashion positioning elevates crochet beyond seasonal novelty into a genuine aesthetic movement with both making and buying audiences.",
        "ai_score": 8.2,
        "ai_thesis": "Crochet's longevity is supported by its dual audience: the making community (who generate ongoing organic content) and the buying community (who follow festival styling). These two groups operate on separate but reinforcing cycles — festival-season buying spikes drive discovery, which feeds into the making community, which generates content through the rest of the year. This self-sustaining content loop is what separates crochet from simpler trend cycles. The broader Craft Core aesthetic (DIY, handmade, textural) aligns with intentional consumption values, giving it philosophical backing beyond aesthetics.",
        "source": "trend_intelligence",
        "signal_velocity": 8.0,
        "resolution_question": "Will crochet garments maintain a consistent top-10 position in summer fashion searches on visual platforms through August 2026, confirming its transition from Coachella moment to full-season commercial driver?",
    },
    {
        "name": "Statement Belt Comeback",
        "description": "Wide, chain, and concho belts emerged as a defining Coachella 2026 accessory — worn over hot pants, flowy skirts, and baggy jeans alike. The styling versatility (worn by both Slayyter and FKA Twigs in contrasting looks) confirmed the accessory's broad demographic reach. The western meets Y2K energy of chain and concho belts connects directly to the Neo Nostalgia multi-era blending macro-trend, with resale platform data showing the item as an active April trending piece.",
        "ai_score": 7.8,
        "ai_thesis": "Statement belts benefit from being one of the most styling-versatile accessories available — the same belt reads differently across completely different outfit registers, making it easy to feature in styling content. The western x Y2K energy is resonant with the Neo Nostalgia multi-era framework, giving the belt genuine cultural backing. As a relatively low price-point entry item (compared to bags or footwear), statement belts convert trend awareness to purchase at a higher rate — they're accessible enough to act on immediately. Resale platform confirmation at the same cultural moment as Coachella adoption is a strong near-term signal.",
        "source": "trend_intelligence",
        "signal_velocity": 7.6,
        "resolution_question": "Will statement belts (chain, concho, or oversized western styles) appear in top-10 trending accessory searches on resale platforms by July 2026?",
    },

    # ── GOOGLE SHOPPING SIGNALS (purchase-intent search) ─────────────────────
    {
        "name": "Swatch x AP Collab Frenzy",
        "description": "The Swatch x Audemars Piguet 'MoonSwatch' collaboration has generated extraordinary sustained purchase-intent search activity across three separate Google Shopping measurement windows in 2026: individual query variants ('swatch ap', 'freeze watch', 'ap swatch collab', 'ap watch swatch', 'swatch x ap') collectively hitting between +950% and +4,150% RISING across time windows. No other single fashion object in the measured data set showed this level of purchase-search persistence across multiple months.",
        "ai_score": 8.8,
        "ai_thesis": "The MoonSwatch collaboration model has proven the most durable consumer excitement formula in watches since the Apple Watch — accessibility-priced entry into a prestige aesthetic that was previously a $20,000+ proposition. The multi-month purchase search persistence (across at least 3 separate measurement windows) means this is not a launch-spike phenomenon but ongoing replenishment demand from consumers who didn't secure the initial drop. Secondary market premiums confirm genuine scarcity. The collaboration signals a permanent strategic opening: luxury watches and accessible brands will continue this model, and each new colorway generates a fresh demand spike.",
        "source": "social_data",
        "signal_velocity": 9.2,
        "resolution_question": "Will the Swatch x AP collaboration drive a measurable sales uplift on Swatch's standard product lines by Q4 2026, confirming the halo effect extends beyond the collab SKUs?",
    },
    {
        "name": "Travis Scott Shy Pink Jordan",
        "description": "Travis Scott's 'Shy Pink' Jordan 1 Low colorway triggered 20,000+ Google searches within 24 hours of its release date on May 29, 2026 — placing it in the top-3 fashion-adjacent Google trending events for the week. The release sits within Scott's ongoing Jordan collaboration arc, with search breakdown data showing: 'travis scott shoes', 'travis scott jordan 1', 'travis scott pink', 'shy pink travis scott', and 'travis scott tropical pink' all trending simultaneously, confirming broad organic discovery rather than a single-query event.",
        "ai_score": 8.9,
        "ai_thesis": "Travis Scott Jordan drops have established a reliable demand formula: each release generates both immediate resale premium and long-tail organic search as non-hype consumers discover the collab weeks later. The pink colorway specifically enters a fashion-friendly color moment — cerulean blue is the directional color of summer 2026, but pink Jordan variants consistently outperform neutral colorways in secondary market premium and social content generation. The cross-demographic appeal (sneaker collectors + fashion consumers) makes this a uniquely wide signal. Any retailer with access to Scott collaboration adjacents has a content window of 4–8 weeks post-release.",
        "source": "social_data",
        "signal_velocity": 9.3,
        "resolution_question": "Will Travis Scott Shy Pink Jordan 1 Low maintain a 2x+ resale premium over retail on major secondary markets for 90 days post-release (through August 2026)?",
    },
    {
        "name": "Vintage Golf Aesthetic",
        "description": "Golf's cultural repositioning from exclusionary to aspirational is driving a distinct vintage-inspired golf fashion movement. Resale platform data shows increasing demand for vintage-inspired golf wear across categories. Google Shopping data captures heels and tailored separates growing in tandem with sport-leisure queries. Social platform data shows the driving range as 'one of the fastest-growing hashtags' for date-night content, with users posting aesthetic clips and beginner POVs. Performance brands and heritage houses are both repositioning: Nike and Under Armour in ergonomic styles, Ralph Lauren updating traditional polos.",
        "ai_score": 7.8,
        "ai_thesis": "Golf's aesthetic moment mirrors tennis's trajectory 3–4 years ago — a sport historically coded as exclusive and conservative is being reclaimed as aspirational through a younger demographic who finds the visual language (country club, heritage brands, tailored shorts) appealing as fashion rather than function. The resale demand for vintage golf wear specifically — archival polo shirts, classic cable knits, heritage brand pieces — places this trend at the intersection of Neo Nostalgia, Romanticized Sports, and quality-materials curation. Brands with genuine golf heritage (Ralph Lauren, Lacoste, Fred Perry) have the most authentic positioning in this moment.",
        "source": "trend_intelligence",
        "signal_velocity": 7.4,
        "resolution_question": "Will vintage or heritage-inspired golf wear appear as a named trend category in a major fashion platform's summer 2026 trend report, confirming its mainstream arrival?",
    },

    # ── REAL-TIME SEARCH SIGNALS ──────────────────────────────────────────────
    {
        "name": "Isabel Marant x Havaianas",
        "description": "The Isabel Marant x Havaianas collaboration generated 10,000+ Google searches in the week of May 23–24, 2026, entering Google's trending shopping data as a top-tier fashion event. The collaboration pairs Marant's boho-luxe brand equity with Havaianas' summer-essential market position — a pairing that crosses the fashion-consumer and summer-lifestyle consumer segments simultaneously. Flip-flop-as-fashion has been building in resale data throughout 2026.",
        "ai_score": 7.9,
        "ai_thesis": "Designer x mass-market footwear collabs generate disproportionate cross-demographic discovery: the Marant consumer discovers Havaianas as elevated and the Havaianas consumer discovers Marant as accessible. The boho-luxe aesthetic direction of the collaboration is directly aligned with 2026's festival fashion and Everyday Ceremony aesthetics. Sandal searches trending in Google Shopping (+90% for Tory Burch sandals, heels +250%) confirm the broader summer footwear opportunity. The specific collab will peak during summer, but the 'elevated sandal' and 'designer flip flop' category will sustain beyond it.",
        "source": "social_data",
        "signal_velocity": 8.0,
        "resolution_question": "Will designer x mass-market sandal collaborations (Isabel Marant x Havaianas or similar model) sell out within 72 hours of release and maintain 1.5x+ resale premium through summer 2026?",
    },

    # ── PINTEREST PREDICTS 2026 (verified Pinterest YoY data) ────────────────
    {
        "name": "Glamoratti",
        "description": "Pinterest Predicts 2026 identifies 'Glamoratti' as the defining luxury aesthetic: 1980s power dressing updated through maximalist accessories and intentionally oversized suiting. Pinterest's own data shows 80s luxury content up +225% YoY, baggy/oversized suit searches up +90% YoY, and chunky belt searches up +65% YoY. The aesthetic is a direct reaction to the preceding decade of quiet luxury minimalism — excess as rebellion, not aspiration.",
        "ai_score": 8.4,
        "ai_thesis": "Glamoratti is Pinterest's highest-conviction 2026 prediction with data backing that's unusually strong: +225% YoY for the core aesthetic, supported by adjacent signals in suiting (+90%) and accessories (+65%). When the dominant minimalism cycle reverses, it tends to overshoot in the maximalist direction — the 80s reference point is structurally correct as it was the last time this extreme a pendulum swing occurred. Brands positioned at bold silhouettes, oversized tailoring, and statement accessory hardware will benefit from the broadest audience.",
        "source": "pinterest_predicts_2026",
        "signal_velocity": 8.5,
        "resolution_question": "Will '80s inspired fashion' or 'power dressing' appear as a top editorial trend in Vogue US or BoF's trend report by Q3 2026?",
        "scoring_data": {
            "yoy_change_pct": 225,
            "monthly_change_pct": 65,
            "on_pinterest": True,
        },
    },
    {
        "name": "Poetcore",
        "description": "Romantic literary dressing — flowing fabrics, Victorian-adjacent necklines, satchel bags, and necktie accessories drawing on Romantic era and pre-Raphaelite imagery. Pinterest data: poet aesthetic searches up +175% YoY, satchel bag searches up +85% YoY, tie accessories (on women) up +85% YoY. The trend represents the softer, intellectualized counterpart to Glamoratti's power excess.",
        "ai_score": 7.9,
        "ai_thesis": "Poetcore is structurally distinct from previous cottagecore/dark academia cycles in that it's purchase-intent-driven rather than purely aspirational. Satchel bags at +85% YoY is a hard product signal — people are actually buying, not just saving. The necktie-on-women trend at +85% speaks to the gender-fluid styling thread running through 2026 fashion broadly. This is a cross-category trend that captures multiple consumer motivations: romanticism, intellectualism, and practical nostalgia. It will translate strongly into both ready-to-wear and accessories.",
        "source": "pinterest_predicts_2026",
        "signal_velocity": 7.8,
        "resolution_question": "Will satchel bag sales show measurable growth in Q2–Q3 2026 reports from luxury accessories brands?",
        "scoring_data": {
            "yoy_change_pct": 175,
            "monthly_change_pct": 55,
            "on_pinterest": True,
        },
    },
    {
        "name": "Brooched",
        "description": "The brooch has crossed from niche vintage-lover territory to mainstream fashion signal. Pinterest data shows brooch aesthetic searches up +110% YoY, maximalist accessories broadly up +105% YoY, and lapel shirt searches up +95% YoY. The lapel shirt's rise is directly adjacent — it provides the structural surface that makes a statement brooch wearable in everyday contexts. From runway to street, pins and brooches are the 2026 statement accessory equivalent of the chunky chain in 2021.",
        "ai_score": 8.1,
        "ai_thesis": "Brooched is the accessory story of 2026. The +110% YoY in brooch aesthetics is not a sampling artifact — it's corroborated by +105% maximalist accessories and +95% lapel shirts, three independent signals pointing at the same behavior. Unlike chain jewelry (which dominated 2021–23), brooches carry a stronger vintage and craft narrative that appeals to both the resale community and the sustainability-conscious buyer. The lapel shirt as a delivery vehicle will drive product development from both mass and contemporary brands within 12 months.",
        "source": "pinterest_predicts_2026",
        "signal_velocity": 7.6,
        "resolution_question": "Will 'brooch' or 'statement pin' rank in the top 20 accessory searches on Pinterest by end of Q2 2026?",
        "scoring_data": {
            "yoy_change_pct": 110,
            "monthly_change_pct": 50,
            "on_pinterest": True,
        },
    },
    {
        "name": "Khaki Coded",
        "description": "Earth-toned utilitarian dressing driven by military and field-inspired silhouettes. Pinterest data shows brown linen shirt searches up +100% YoY and field jacket searches up +65% YoY. The aesthetic sits at the intersection of quiet masculinity, heritage dressing, and the broader return to natural materials. It functions as the practical, wearable companion to the more maximalist Glamoratti aesthetic.",
        "ai_score": 7.3,
        "ai_thesis": "Khaki Coded reflects the continued strength of earth-tone neutrals as a dressing philosophy, but now inflected with utility and structure rather than the soft minimalism of 2022–24. Brown linen at +100% YoY is a manufacturing signal as much as a fashion one — brands are committing inventory to this direction. The field jacket's resurgence (+65% YoY) aligns with the broader revival of heritage work and military references running through menswear and crossing into womenswear. The trend has long legs: it supports both the sustainable materials narrative (linen) and the intentional wardrobe framework.",
        "source": "pinterest_predicts_2026",
        "signal_velocity": 7.0,
        "resolution_question": "Will field jacket and linen separate searches maintain at least +40% YoY growth through Q4 2026?",
        "scoring_data": {
            "yoy_change_pct": 100,
            "monthly_change_pct": 40,
            "on_pinterest": True,
        },
    },
    {
        "name": "Extra Celestial",
        "description": "Alien-inspired beauty and fashion — iridescent makeup, opalescent finishes, unearthly color palettes, and body-as-canvas styling. Pinterest data: alien-inspired makeup searches up +140% YoY, opalescent content up +115% YoY. The look draws from sci-fi, rave culture, and editorial beauty simultaneously, making it accessible to multiple subcultures through different entry points.",
        "ai_score": 7.7,
        "ai_thesis": "Extra Celestial is the beauty-led trend with the widest cross-category potential. Alien/opalescent aesthetics are appearing simultaneously in editorial makeup (+140%), nail art, and costume/occasion dressing. The trend is structurally friendly to brands at both price points: drugstore brands can execute iridescent pigments at scale, while luxury beauty brands can own the high-artistry opalescent narrative. The sci-fi cultural wave (accelerating AI discourse, space-adjacent popular culture) provides external reinforcement that makes this feel resonant rather than random.",
        "source": "pinterest_predicts_2026",
        "signal_velocity": 7.5,
        "resolution_question": "Will opalescent or alien-inspired makeup appear in the spring/summer 2026 collections of 5+ major beauty brands?",
        "scoring_data": {
            "yoy_change_pct": 140,
            "monthly_change_pct": 45,
            "on_pinterest": True,
        },
    },
    {
        "name": "Glitchy Glam",
        "description": "High-fashion editorial makeup taken into daily expression: mismatched nail colors, avant-garde face art, unexpected color combinations, and deliberate asymmetry. Pinterest data: avant-garde makeup editorial searches up +270% YoY, nails-different-colors searches up +125% YoY. The aesthetic normalizes what was previously reserved for runway and editorial, pushed into mainstream visibility by creator culture.",
        "ai_score": 8.6,
        "ai_thesis": "Glitchy Glam has the highest YoY growth rate of all Pinterest Predicts 2026 beauty trends at +270% for the core aesthetic. The +125% in mismatched nails is particularly significant because nail art is a high-frequency purchase behavior — it converts to product sales faster than any other beauty category. This is not a theoretical aesthetic story; it is a formula and palette purchasing driver happening right now. The trend has strong TikTok and Instagram crossover (mismatched nails are inherently photogenic) that makes it self-amplifying through organic content creation.",
        "source": "pinterest_predicts_2026",
        "signal_velocity": 8.8,
        "resolution_question": "Will mismatched nail or avant-garde makeup tutorials rank in the top 10 beauty content categories on TikTok or Pinterest by Q3 2026?",
        "scoring_data": {
            "yoy_change_pct": 270,
            "monthly_change_pct": 80,
            "on_pinterest": True,
        },
    },
    {
        "name": "Cool Blue",
        "description": "Icy, frosted blue as the defining color story of 2026 — across makeup, nails, clothing, and accessories. Pinterest data: frosted makeup searches up +150% YoY, icy blue content up +50% YoY. The palette is a chromatic evolution from the white/silver minimalism of previous seasons, adding cool temperature and an almost digital quality to everyday styling.",
        "ai_score": 7.8,
        "ai_thesis": "Cool Blue is Pinterest's clearest color prediction for 2026 with strong underlying data. Frosted makeup at +150% YoY is the leading signal — beauty typically precedes fashion by 1–2 seasons as a color direction indicator. Icy blue at +50% YoY is still early-stage, meaning the trend is in the discovery phase rather than saturation. The color is cosmetically accessible (blue-toned products are easy to produce), culturally legible (references both Y2K and futurism), and visually striking on social media. Nail and eye makeup will be the primary product activation points.",
        "source": "pinterest_predicts_2026",
        "signal_velocity": 7.2,
        "resolution_question": "Will icy/frosted blue appear in the Pantone Fashion Color Report or equivalent trend forecasting systems' 2026 season highlights?",
        "scoring_data": {
            "yoy_change_pct": 150,
            "monthly_change_pct": 45,
            "on_pinterest": True,
        },
    },

    # ── LEGACY TRENDS ─────────────────────────────────────────────────────────
    {
        "name": "Guardian Design",
        "description": "Security-forward design is moving from niche travel gear into mainstream fashion, with anti-theft hardware — tunnel zippers, carabiner clips, RFID-blocking pockets — becoming viable aesthetic differentiators for urban commuter collections. The visibility of security features is shifting from something to hide into something to signal.",
        "ai_score": 8.5,
        "ai_thesis": "Guardian Design sits at the intersection of rising urban practicality and consumer demand for functional streetwear that carries design intention. Brands that embed visible security features into their silhouettes gain dual signal value: practical credibility and a design language that reads as deliberate and modern. The crossover from travel accessories into everyday apparel points to a durable category shift rather than a seasonal novelty — the consumer making this purchase is solving a real problem while also making a style statement.",
        "source": "trend_intelligence",
        "signal_velocity": 4.2,
        "resolution_question": "Will anti-theft design features (RFID pockets, carabiner clips, tunnel zippers) appear in 3+ major high-street brand collections by end of 2026?",
    },
]


def run():
    db = SessionLocal()
    added = 0
    skipped = 0
    try:
        for t in TRENDS:
            exists = db.query(Trend).filter(Trend.name == t["name"]).first()
            if exists:
                skipped += 1
                continue
            trend = Trend(
                id=str(uuid.uuid4()),
                name=t["name"],
                description=t["description"],
                ai_score=t["ai_score"],
                ai_thesis=t["ai_thesis"],
                source=t["source"],
                signal_velocity=t["signal_velocity"],
                status=TrendStatus.active,
            )
            db.add(trend)
            db.flush()

            market = Market(
                id=str(uuid.uuid4()),
                trend_id=trend.id,
                question=t["resolution_question"],
                resolution_date=datetime.utcnow() + timedelta(days=180),
                resolution_criteria=t["resolution_question"],
                yes_price=0.50,
                no_price=0.50,
                liquidity_param=100.0,
                total_volume=0.0,
                status=MarketStatus.open,
            )
            db.add(market)
            added += 1

        db.commit()
        print(f"✅  Added {added} trends+markets, skipped {skipped} duplicates.")
    except Exception as e:
        db.rollback()
        print(f"❌  Error: {e}")
        raise
    finally:
        db.close()


def update_descriptions():
    """Patch existing DB records with updated descriptions/theses by name match."""
    db = SessionLocal()
    updated = 0
    try:
        for t in TRENDS:
            trend = db.query(Trend).filter(Trend.name == t["name"]).first()
            if trend:
                trend.description = t["description"]
                trend.ai_thesis = t["ai_thesis"]
                trend.ai_score = t["ai_score"]
                trend.signal_velocity = t["signal_velocity"]
                updated += 1
        db.commit()
        print(f"✅  Updated {updated} existing trends.")
    except Exception as e:
        db.rollback()
        print(f"❌  Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "update":
        update_descriptions()
    else:
        run()
