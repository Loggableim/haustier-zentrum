#!/usr/bin/env python3
"""Generate ALL hero images for haustier-zentrum via MiniMax image-01 with furry pop-art style."""
import json, os, sys, time, urllib.request, urllib.error, ssl, re
from PIL import Image

from _minimax_key import API_KEY
API_BASE = "https://api.minimax.io/v1/image_generation"
MODEL = "image-01"

STYLE = "furry pop-art, anthropomorphic animal characters, editorial illustration, bold black contour lines, clean vector art, kawaii, cute, vibrant orange/violet color palette, halftone comic textures, graphic novel aesthetic, modern advertising illustration, dynamic composition, highly detailed, professional magazine artwork, sharp linework, colorful background"
NEGATIVE = "text, watermark, signature, blurry, low quality, distorted, photograph, realistic, 3d render"

IMG_DIR = r"C:\HermesPortable\home\spaces\haustier-zentrum\images"

# ============================================================
# ALL article hero images to generate
# Each entry: (slug_filename, subject_description)
# ============================================================
IMAGES = [
    # --- HUNDE RASSEN ---
    ("beagle-rasseguide_00001_", "anthropomorphic Beagle dog character with floppy ears and tricolor fur, happy expression, pop-art style"),
    ("berner-sennenhund-rasseguide_00001_", "anthropomorphic Bernese Mountain Dog character with tricolor fur, strong and friendly, pop-art portrait"),
    ("boxer-rasseguide_00001_", "anthropomorphic Boxer dog character with muscular build, short brown fur, friendly face, pop-art style"),
    ("cocker-spaniel-rasseguide_00001_", "anthropomorphic Cocker Spaniel character with long floppy ears and silky golden fur, pop-art portrait"),
    ("dalmatiner-rasseguide_00001_", "anthropomorphic Dalmatian dog character with black spots on white fur, elegant pose, pop-art style"),
    ("deutscher-schaeferhund_00001_", "anthropomorphic German Shepherd character with alert upright ears and black-brown fur, pop-art portrait"),
    ("deutscher-schaeferhund-rasseguide_00001_", "anthropomorphic German Shepherd dog character standing proud, strong noble pose, pop-art style"),
    ("franzoesische-bulldogge-rasseguide_00001_", "anthropomorphic French Bulldog character with bat ears, squishy face, cute expression, pop-art style"),
    ("golden-retriever-rasseguide_00001_", "anthropomorphic Golden Retriever character with golden fur, happy smiling face, pop-art portrait"),
    ("havaneser-rasseguide_00001_", "anthropomorphic Havanese dog character with long silky cream fur, cute playful eyes, pop-art style"),
    ("hero-mops-rasseguide", "anthropomorphic Pug dog character with wrinkled face, big round eyes, cute snorty expression, pop-art style"),
    ("hero-sibirischer-husky-rasseguide", "anthropomorphic Siberian Husky character with striking blue eyes and gray-white fur, pop-art portrait"),
    ("labrador-retriever_00001_", "anthropomorphic Labrador Retriever character with friendly face and wagging tail, pop-art style"),
    ("malteser-rasseguide_00001_", "anthropomorphic Maltese dog character with pure white flowing fur, elegant cute pose, pop-art style"),
    ("mops-rasseguide_00001_", "anthropomorphic Pug dog character with big round eyes, wrinkles, silly cute face, pop-art portrait"),
    ("pudel-rasseguide_00001_", "anthropomorphic Poodle character with fluffy styled fur, elegant sophisticated pose, pop-art style"),
    ("rottweiler-rasseguide_00001_", "anthropomorphic Rottweiler character with black fur and brown markings, loyal strong pose, pop-art style"),
    ("shiba-inu-rasseguide_00001_", "anthropomorphic Shiba Inu character with fox-like face and reddish fur, cute sassy attitude, pop-art style"),
    ("shih-tzu-rasseguide_00001_", "anthropomorphic Shih Tzu character with long flowing fur, cute lion-like face, pop-art portrait"),
    ("sibirischer-husky-rasseguide_00001_", "anthropomorphic Siberian Husky character with beautiful blue eyes and thick fur, pop-art style"),
    ("westie-west-highland-white-terrier-rasseguide_00001_", "anthropomorphic West Highland White Terrier character with white fluffy fur, cute dark eyes, pop-art style"),
    ("zwergspitz-pomeranian-rasseguide_00001_", "anthropomorphic Pomeranian character with fluffy orange fur, tiny foxy face, cute pose, pop-art style"),

    # --- KATZEN ---
    ("bengal-cat-rasseguide_00001_", "anthropomorphic Bengal cat character with leopard-spotted wild fur, exotic elegant pose, pop-art style"),
    ("britisch-kurzhaar-rasseguide_00001_", "anthropomorphic British Shorthair cat character with round face and plush gray fur, pop-art portrait"),
    ("chihuahua-rasseguide_00001_", "anthropomorphic Chihuahua dog character tiny cute, big ears, sassy attitude, pop-art style"),
    ("hero-ragdoll-katze-rasseguide", "anthropomorphic Ragdoll cat character with stunning blue eyes and silky seal point fur, pop-art portrait"),
    ("katzen-balkon-sichern_00001_", "anthropomorphic cat character lounging on a safe balcony, vibrant city background, pop-art summer scene"),
    ("katzen-beschaeftigung_00001_", "anthropomorphic cat character playing with colorful toys and scratching post, active fun, pop-art style"),
    ("katzen-beschaeftigung_00003", "anthropomorphic cat character jumping for a feather wand toy, dynamic playful action, pop-art style"),
    ("katzen-clickertraining-intelligenzspielzeug_00001_", "anthropomorphic cat character solving a puzzle toy, bright focused eyes, pop-art intelligence scene"),
    ("katzen-ernaehrung_00001_", "anthropomorphic cat character looking at food bowls, cute hungry expression, pop-art dining scene"),
    ("katzen-freigaenger_00001_", "anthropomorphic cat character exploring a garden with butterflies, outdoor adventure, pop-art style"),
    ("katzen-impfungen-vorsorge_00001_", "anthropomorphic cat character at vet with bandage, brave cute expression, pop-art health scene"),
    ("katzen-kastration-sterilisation_00001_", "anthropomorphic cat character recovering with a tiny bandage, cozy blanket, pop-art healing scene"),
    ("katzen-krankheiten_hero", "anthropomorphic cat character with stethoscope at vet checkup, concerned cute face, pop-art medical scene"),
    ("katzen-kratzbaum_00001_", "anthropomorphic cat character climbing a tall cat tree tower, playful energy, pop-art style"),
    ("katzen-verhalten-koerpersprache-kommunikation_00001_", "anthropomorphic cat character making different expressive poses, communication series, pop-art style"),
    ("katzen-wohnung_00001_", "anthropomorphic cat character relaxing in a cozy apartment, purring happy, pop-art indoor scene"),
    ("katzen-zahnpflege_00001_", "anthropomorphic cat character brushing teeth with a giant toothbrush, funny cute, pop-art dental scene"),
    ("katzenbeschaeftigung_00001_", "anthropomorphic cat character batting at colorful hanging toys, energetic play, pop-art style"),
    ("katzenfutter-selber-machen_00001_", "anthropomorphic cat character surrounded by fresh ingredients and bowls, cooking scene, pop-art style"),
    ("katzenfutter-vergleich-2026_00001_", "anthropomorphic cat character comparing two food bowls, curious picky expression, pop-art taste test"),
    ("katzenhaltung-wohnung_00001_", "anthropomorphic cat character in cozy apartment with window view, happy indoor life, pop-art style"),
    ("katzenkrankheiten-erkennen_00001_", "anthropomorphic cat character with thermometer, sneezing into tissue, pop-art sick scene"),
    ("katzenrassen-vergleich_00001_", "three anthropomorphic cat characters of different breeds lined up, pop-art comparison portrait"),
    ("katzenrassen-vergleich_00002_", "anthropomorphic longhair and shorthair cat characters being groomed, pop-art grooming scene"),
    ("katzenrassen-vergleich_00003_", "anthropomorphic cat character being brushed with sparkles, happy grooming time, pop-art style"),
    ("katzentoilette-geruch-vermeiden_00001_", "anthropomorphic cat character with sparkly clean litter box, fresh minty vibes, pop-art cleaning scene"),
    ("maine-coon-katze_00001_", "anthropomorphic Maine Coon cat character with huge fluffy tail and tufted ears, pop-art portrait"),
    ("maine-coon-katze-rasseguide_00001_", "anthropomorphic Maine Coon cat character majestic large size, friendly giant cat, pop-art style"),
    ("perserkatze-rasseguide_00001_", "anthropomorphic Persian cat character with luxurious flat face and flowing fur, pop-art royal portrait"),
    ("ragdoll-katze-rasseguide_00001_", "anthropomorphic Ragdoll cat character flopped on back, relaxed silly pose, pop-art style"),
    ("seniorkatzen-pflege-ernaehrung-gesundheit_00001_", "anthropomorphic elderly cat character with glasses and cozy blanket, pop-art senior portrait"),
    ("siamkatze-rasseguide_00001_", "anthropomorphic Siamese cat character with striking blue eyes and dark points, pop-art elegant portrait"),

    # --- KLEINTIERE ---
    ("chinchilla-haltung-pflege_00001_", "anthropomorphic Chinchilla character with huge round ears and fluffy gray fur, pop-art portrait"),
    ("degus-haltung-pflege_00001_", "anthropomorphic Degu characters taking a sand bath, cute brush tails, pop-art small pet scene"),
    ("hamster-haltung_00001_", "anthropomorphic Hamster character with chubby cheeks in a colorful cage with wheel, pop-art style"),
    ("kaninchenhaltung_00001_", "anthropomorphic Rabbit character with long ears and fluffy tail in a cozy hutch, pop-art style"),
    ("kaninchen-ernaehrung-gesundheit_00001_", "anthropomorphic Rabbit character surrounded by fresh vegetables and hay, pop-art healthy eating scene"),
    ("kleintier-gehege_00001_", "anthropomorphic guinea pig and rabbit characters together in a colorful enclosure, pop-art style"),
    ("kleintiere_00001_", "anthropomorphic hamster and guinea pig characters together, cute tiny pets, pop-art group portrait"),
    ("meerschweinchen-ernaehrung-vitamin-c_00001_", "anthropomorphic Guinea Pig character with vitamin C fruits and veggies, pop-art nutrition scene"),
    ("meerschweinchen-haltung_00001_", "anthropomorphic Guinea Pig character popcorning with joy, cute happy pet, pop-art style"),
    ("frettchen-haustier-haltung_00001_", "anthropomorphic Ferret character doing the weasel war dance, long silly body, pop-art playful scene"),

    # --- VÖGEL ---
    ("wellensittich-ernaehrung-futter_00001_", "anthropomorphic Budgie character with colorful feathers eating seeds, pop-art bird portrait"),
    ("wellensittich-ernaehrung-gesundheit_00001_", "anthropomorphic Budgie character with fresh greens and vitamins, pop-art healthy bird scene"),
    ("wellensittich-haltung_00001_", "anthropomorphic Budgie character perching happily in colorful cage, pop-art pet bird scene"),
    ("voegel-haustier-beste-vogelarten-einsteiger_00001_", "anthropomorphic Budgie and Canary characters together, colorful bird friends, pop-art group portrait"),
    ("vogelkaefig-voliere-vergleich_00001_", "anthropomorphic budgie character in a large colorful aviary with toys, pop-art bird home scene"),

    # --- AQUARIUM ---
    ("aquarium-einrichtung_00001_", "anthropomorphic colorful tropical fish character swimming among coral and plants, pop-art underwater scene"),
    ("aquarium-fische-einsteiger_00001_", "anthropomorphic neon tetra fish character group swimming in planted aquarium, pop-art underwater party"),

    # --- ALLGEMEIN / RATGEBER ---
    ("allergiker-haustiere_00001_", "anthropomorphic hypoallergenic pets: poodle cat and fish together, pop-art allergy-friendly group"),
    ("erste-hilfe-haustiere-notfall-ratgeber_00001_", "anthropomorphic dog and cat characters with first aid kit and bandages, pop-art emergency scene"),
    ("haustier-anschaffung_00001_", "group of anthropomorphic pets: dog cat hamster bird together, pop-art family portrait"),
    ("haustierfreundliche-wohnung-einrichten_00001_", "anthropomorphic cat and dog characters in a colorful pet-friendly apartment, pop-art interior scene"),
    ("haustiere-kinder_00001_", "anthropomorphic pet characters playing happily with a child, pop-art family fun scene"),
    ("tierarztkosten_00001_", "anthropomorphic dog character at vet with piggy bank, medical chart, pop-art cost scene"),

    # --- HUNDE PFLEGE & GESUNDHEIT ---
    ("hunde-ernaehrung-barf-trocken-nass_00001_", "anthropomorphic dog character comparing food bowls with meat and kibble, pop-art nutrition scene"),
    ("hunde-erstausstattung-checkliste_00001_", "anthropomorphic puppy character surrounded by new equipment: leash bowl bed toys, pop-art shopping scene"),
    ("hunde-fellpflege-buersten-baden-krallen_00001_", "anthropomorphic dog character getting pampered with brush and bubbles, pop-art spa scene"),
    ("hunde-gesundheit_00001_", "anthropomorphic dog character with medical cross and healthy glow, pop-art health check scene"),
    ("hunde-hausmittel_00001_", "anthropomorphic dog character surrounded by natural herbs and healing remedies, pop-art wellness scene"),
    ("hunde-krankheiten-symptome-erste-hilfe_00001_", "anthropomorphic dog character with thermometer and first aid, pop-art medical emergency scene"),
    ("hunde-reisen_00001_", "anthropomorphic dog character with suitcase and travel accessories, pop-art adventure scene"),
    ("hunde-uebergewicht_00001_", "anthropomorphic chubby dog character exercising with a ball, pop-art fitness journey scene"),
    ("hunde-zahnpflege_00001_", "anthropomorphic dog character brushing teeth with giant toothbrush, pop-art dental care scene"),
    ("hundeallergien_00001_", "anthropomorphic dog character sneezing surrounded by flowers, pop-art allergy awareness scene"),
    ("hundeernaehrung_00001_", "anthropomorphic dog character drooling over healthy food bowls, pop-art nutrition scene"),
    ("hundeerziehung-grundlagen_00001_", "anthropomorphic dog character sitting pretty learning commands with treats, pop-art training scene"),
    ("hundeerziehung_00001_", "anthropomorphic dog character doing tricks for treats, proud happy face, pop-art training scene"),
    ("hunderassen-anfaenger_00001_", "group of anthropomorphic beginner-friendly dog breeds together, pop-art guide portrait"),
    ("hundepension-tagesbetreuung-ratgeber_00001_", "anthropomorphic dogs playing together in colorful daycare facility, pop-art pet hotel scene"),
    ("hundeschule-welpenschule-ratgeber_00001_", "anthropomorphic puppy character in dog school with cap and diploma, pop-art graduation scene"),
    ("hundespielzeuge-2026_00001_", "anthropomorphic dog character surrounded by colorful toys balls ropes, pop-art toy store scene"),
    ("hundeversicherung_00001_", "anthropomorphic dog character with insurance documents and protective shield, pop-art safety scene"),
    ("leinenfuehrigkeit_00001_", "anthropomorphic dog character walking nicely on a colorful leash, pop-art walking training scene"),
    ("pferdehaltung-einsteiger_00001_", "anthropomorphic horse character galloping through colorful meadow, pop-art equestrian scene"),
    ("welpen-eingewoehnung_00001_", "anthropomorphic puppy character exploring new home with wonder, pop-art moving in scene"),
    ("zeckenschutz-flohschutz-hund_00001_", "anthropomorphic dog character protected by shield against ticks and fleas, pop-art pest protection scene"),
]

def call_minimax(prompt, retries=5):
    payload = json.dumps({
        "model": MODEL,
        "prompt": f"{prompt}, {STYLE}",
        "negative_prompt": NEGATIVE
    }).encode('utf-8')
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    ctx = ssl.create_default_context()
    req = urllib.request.Request(API_BASE, data=payload, headers=headers, method="POST")
    
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=180) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                if result.get("base_resp", {}).get("status_code") != 0:
                    err = result.get("base_resp", {}).get("status_msg", "unknown")
                    print(f"  ⚠️  API Error: {err}")
                    if attempt < retries - 1:
                        time.sleep(5 * (attempt + 1))
                        continue
                    return None
                
                urls = result.get("data", {}).get("image_urls", [])
                if urls:
                    return urls[0]
                print(f"  ⚠️  No image_urls in response")
                return None
        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8')
            print(f"  ❌ HTTP {e.code}: {body[:200]}")
            if "2056" in body:
                print("  ⏸  Token Plan limit reached! Stopping.")
                return "TOKEN_LIMIT"
            if attempt < retries - 1:
                time.sleep(10 * (attempt + 1))
        except Exception as e:
            print(f"  ❌ {e}")
            if attempt < retries - 1:
                time.sleep(5)
    return None

def download_and_save(url, slug):
    """Download image from MiniMax URL and save as webp."""
    try:
        ctx = ssl.create_default_context()
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
            img_data = resp.read()
        
        # Save temp, then convert to webp
        temp_path = os.path.join(IMG_DIR, f"{slug}_temp.jpg")
        with open(temp_path, 'wb') as f:
            f.write(img_data)
        
        img = Image.open(temp_path)
        if img.mode == "RGBA":
            bg = Image.new("RGB", img.size, (255, 255, 255))
            bg.paste(img, mask=img.split()[3])
            img = bg
        
        img = img.resize((1216, 832), Image.LANCZOS)
        dst = os.path.join(IMG_DIR, f"{slug}.webp")
        img.save(dst, "WEBP", quality=92)
        kb = os.path.getsize(dst) // 1024
        
        os.remove(temp_path)
        return kb
    except Exception as e:
        print(f"  ❌ Download error: {e}")
        return None

# ============================================================
# MAIN
# ============================================================
total = len(IMAGES)
print(f"🎯 Generate {total} hero images via MiniMax image-01")
print(f"   Style: furry pop-art, orange/violet palette")
print(f"={'='*60}\n")

os.makedirs(IMG_DIR, exist_ok=True)

success = 0
skipped = 0
failed = 0

for idx, (slug, subject) in enumerate(IMAGES, 1):
    dst = os.path.join(IMG_DIR, f"{slug}.webp")
    
    # Skip if already has a good image (>50KB = real image)
    # ALL images >5KB are treated as needing replacement 
    if os.path.exists(dst) and os.path.getsize(dst) > 50000 and os.path.getmtime(dst) > 1749600000:
        print(f"[{idx}/{total}] ⏭ {slug}.webp ({os.path.getsize(dst)//1024}KB) existiert (kürzlich erneuert)")
        skipped += 1
        continue
    
    print(f"[{idx}/{total}] {slug}... ", end="", flush=True)
    
    prompt = f"{subject}"
    url = call_minimax(prompt)
    
    if url == "TOKEN_LIMIT":
        print("⏸ Token Limit erreicht. Fortsetzung später.")
        break
    
    if url:
        print(f"URL erhalten... ", end="", flush=True)
        kb = download_and_save(url, slug)
        if kb and kb > 20:
            print(f"✅ {kb}KB")
            success += 1
        else:
            print(f"⚠️  zu klein ({kb}KB)")
            failed += 1
    else:
        print(f"❌ Keine URL")
        failed += 1
    
    # 3s delay between calls (RPM limit)
    time.sleep(3)

print(f"\n{'='*50}")
print(f"✅ Fertig: {success} neu / {skipped} übersprungen / {failed} fehlgeschlagen")
print(f"{'='*50}")
