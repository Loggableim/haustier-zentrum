#!/usr/bin/env python3
"""Generate ALL hero images for ALL haustier-zentrum articles via MiniMax image-01.
Reads which images each article references and regenerates every single one."""
import json, os, sys, time, urllib.request, urllib.error, ssl, re
from PIL import Image

API_KEY = open(os.path.join(os.path.dirname(__file__), '_minimax_key.py')).read().split('"')[1]
API_BASE = "https://api.minimax.io/v1/image_generation"
MODEL = "image-01"

STYLE = "furry pop-art, anthropomorphic animal characters, editorial illustration, bold black contour lines, clean vector art, kawaii, cute, vibrant orange/violet color palette, halftone comic textures, graphic novel aesthetic, modern advertising illustration, dynamic composition, highly detailed, professional magazine artwork, sharp linework, colorful background"
NEGATIVE = "text, watermark, signature, blurry, low quality, distorted, photograph, realistic, 3d render"

IMG_DIR = r"C:\HermesPortable\home\spaces\haustier-zentrum\images"
ARTICLE_DIR = r"C:\HermesPortable\home\spaces\haustier-zentrum\artikel"

# ─── Read ALL article hero images + build subject prompts ───

# Map image filenames → subject descriptions for the prompt
SUBJECT_MAP = {
    # Hunde
    "beagle-rasseguide_00001_": "anthropomorphic Beagle dog character with floppy ears and tricolor fur, happy expression",
    "berner-sennenhund-rasseguide_00001_": "anthropomorphic Bernese Mountain Dog character with tricolor fur, strong and friendly",
    "boxer-rasseguide_00001_": "anthropomorphic Boxer dog character with muscular build, short brown fur, friendly face",
    "cocker-spaniel-rasseguide_00001_": "anthropomorphic Cocker Spaniel character with long floppy ears and silky golden fur",
    "dalmatiner-rasseguide_00001_": "anthropomorphic Dalmatian dog character with black spots on white fur, elegant pose",
    "deutscher-schaeferhund_00001_": "anthropomorphic German Shepherd character with alert upright ears and black-brown fur",
    "deutscher-schaeferhund_00002": "anthropomorphic German Shepherd dog character, strong loyal working dog pose",
    "deutscher-schaeferhund_00003": "anthropomorphic German Shepherd puppy character, cute and playful",
    "deutscher-schaeferhund-rasseguide_00001_": "anthropomorphic German Shepherd dog character standing proud, strong noble pose",
    "franzoesische-bulldogge-rasseguide_00001_": "anthropomorphic French Bulldog character with bat ears, squishy face, cute expression",
    "franzoesische-bulldogge_00001_": "anthropomorphic French Bulldog dog character with bat ears and wrinkly face, cute pose",
    "golden-retriever-rasseguide_00001_": "anthropomorphic Golden Retriever character with golden fur, happy smiling face",
    "golden-retriever_00002": "anthropomorphic Golden Retriever dog character, friendly happy pose, wagging tail",
    "golden-retriever_00003": "anthropomorphic Golden Retriever puppy character, cute and playful",
    "havaneser-rasseguide_00001_": "anthropomorphic Havanese dog character with long silky cream fur, cute playful eyes",
    "hero-mops-rasseguide": "anthropomorphic Pug dog character with wrinkled face, big round eyes, cute expression",
    "hero-sibirischer-husky-rasseguide": "anthropomorphic Siberian Husky character with striking blue eyes and gray-white fur",
    "hero-beagle-rasseguide-verspielt-neugierig-jagdlich-veranlagt": "anthropomorphic Beagle dog character with tricolor fur, floppy ears, curious playful expression",
    "hero-berner-sennenhund-rasseguide-sanfter-riese-mit-familiensinn": "anthropomorphic Bernese Mountain Dog character, giant fluffy tricolor fur, gentle giant",
    "hero-cocker-spaniel-rasseguide-frohlicher-jagdhund-mit-samtpfoten": "anthropomorphic Cocker Spaniel character with long floppy ears, silky fur, gentle expression",
    "hero-dalmatiner-rasseguide-eleganter-begleiter-mit-energie": "anthropomorphic Dalmatian character with black spots on white fur, elegant athletic pose",
    "hero-havaneser-rasseguide-verspielt-anhanglich-ideal-fur-die-wohnung": "anthropomorphic Havanese dog character with long silky cream fur, cute playful expression",
    "hero-malteser-rasseguide-eleganter-begleiter-mit-edlem-fell": "anthropomorphic Maltese dog character with pure white silky fur, elegant cute pose",
    "hero-ragdoll-katze-rasseguide": "anthropomorphic Ragdoll cat character with stunning blue eyes and silky seal point fur",
    "hero-west-highland-white-terrier-westie-rasseguide": "anthropomorphic West Highland White Terrier character with white fluffy fur, cute dark eyes",
    "hero-zwergspitz-pomeranian-rasseguide-kleiner-hund-grosser-charakter": "anthropomorphic Pomeranian dog character with fluffy orange fur, tiny foxy face, big personality",
    "hund-buerohund-arbeitsplatz_00001_": "anthropomorphic dog character in an office workplace, wearing a tiny tie, working at a desk",
    "hunde-erstausstattung-checkliste_00001_": "anthropomorphic puppy character surrounded by new equipment: leash bowl bed toys",
    "hunde-gesundheit_00001_": "anthropomorphic dog character with medical cross, healthy glow, checking health",
    "hunde-hausmittel_00001_": "anthropomorphic dog character surrounded by natural herbs and home remedies, wellness",
    "hunde-hausmittel_00002_": "anthropomorphic dog character with chamomile and healing plants around, natural care",
    "hunde-reisen_00001_": "anthropomorphic dog character with suitcase and travel accessories, ready for adventure",
    "hunde-reisen_00002_": "anthropomorphic dog character in a car with travel gear, road trip adventure scene",
    "hunde-reisen_00003_": "anthropomorphic dog character at a travel destination, exploring with joy",
    "hunde-zahnpflege_00001_": "anthropomorphic dog character brushing teeth with giant toothbrush, dental care",
    "hundeallergien_00001_": "anthropomorphic dog character sneezing surrounded by flowers, allergy season",
    "hundeernaehrung_00001_": "anthropomorphic dog character drooling over healthy food bowls, nutrition",
    "hundeerziehung_00001_": "anthropomorphic dog character doing tricks for treats, proud happy face",
    "hundeerziehung-grundlagen_00001_": "anthropomorphic dog character sitting pretty learning commands with treats",
    "hundepension-tagesbetreuung-ratgeber_00001_": "anthropomorphic dogs playing together in colorful daycare facility, pet hotel scene",
    "hunderassen-anfaenger_00001_": "group of anthropomorphic beginner-friendly dog breeds together, diverse group portrait",
    "hunderassen-anfaenger_00002_": "anthropomorphic golden retriever and labrador dogs playing together happily",
    "hunderassen-anfaenger_00003_": "anthropomorphic small breed dog character sitting on a comfortable couch at home",
    "hundeschule-welpenschule-ratgeber_00001_": "anthropomorphic puppy character in dog school with cap and diploma, graduation",
    "hundespielzeuge-2026_00001_": "anthropomorphic dog character surrounded by colorful toys balls ropes, playing",
    "hundeversicherung_00001_": "anthropomorphic dog character with insurance documents and protective shield, safety",
    "leinenfuehrigkeit_00001_": "anthropomorphic dog character walking nicely on a colorful leash, training scene",
    "leinenfuehrigkeit_00002_": "anthropomorphic dog character walking calmly on loose leash with person, training",
    "pferdehaltung-einsteiger_00001_": "anthropomorphic horse character galloping through colorful meadow, equestrian scene",
    "welpen-eingewoehnung_00001_": "anthropomorphic puppy character exploring new home with wonder and excitement",
    "welpen-eingewoehnung_00002_": "anthropomorphic puppy character sleeping cozy in a comfortable dog bed",
    "welpen-eingewoehnung_00003_": "anthropomorphic puppy character playing with a toy in a colorful living room",
    "welpenkauf-zuuechter-tierheim-checkliste_00001_": "anthropomorphic puppy character with adoption papers and checklist, choosing a pet",
    "zeckenschutz-flohschutz-hund_00001_": "anthropomorphic dog character protected by shield against ticks and fleas",
    "yorkshire-terrier-rasseguide_00001_": "anthropomorphic Yorkshire Terrier character with long silky steel-blue fur, tiny cute pose",
    "australian-shepherd-rasseguide_00001_": "anthropomorphic Australian Shepherd character with merle coat, heterochromia eyes, energetic pose",
    "border-collie-rasseguide_00001_": "anthropomorphic Border Collie character with black and white fur, intelligent alert expression",
    "chihuahua-rasseguide_00001_": "anthropomorphic tiny Chihuahua dog character with big ears and sassy confident attitude",
    "chihuahua_00002": "anthropomorphic Chihuahua dog character, tiny size, big personality, cute pose",
    "chihuahua_00003": "anthropomorphic Chihuahua puppy character, extra tiny and cute, big eyes",
    "dackel-rasseguide_00001_": "anthropomorphic Dachshund character with long body and short legs, cute wiener dog pose",
    "labrador-retriever_00001_": "anthropomorphic Labrador Retriever character with friendly face and wagging tail",
    "mops-rasseguide_00001_": "anthropomorphic Pug dog character with big round eyes, wrinkles, silly cute face",
    "pudel-rasseguide_00001_": "anthropomorphic Poodle character with fluffy styled fur, elegant sophisticated pose",
    "rottweiler-rasseguide_00001_": "anthropomorphic Rottweiler character with black fur and brown markings, loyal strong pose",
    "shiba-inu-rasseguide_00001_": "anthropomorphic Shiba Inu character with fox-like face and reddish fur, cute sassy attitude",
    "shih-tzu-rasseguide_00001_": "anthropomorphic Shih Tzu character with long flowing fur, cute lion-like face",
    "sibirischer-husky-rasseguide_00001_": "anthropomorphic Siberian Husky character with beautiful blue eyes and thick fur",
    "westie-west-highland-white-terrier-rasseguide_00001_": "anthropomorphic West Highland White Terrier character with white fluffy fur, cute dark eyes",
    "zwergspitz-pomeranian-rasseguide_00001_": "anthropomorphic Pomeranian character with fluffy orange fur, tiny foxy face, cute pose",
    "malteser-rasseguide_00001_": "anthropomorphic Maltese dog character with pure white flowing fur, elegant cute pose",
    
    # Katzen
    "bengal-cat-rasseguide_00001_": "anthropomorphic Bengal cat character with leopard-spotted wild fur, exotic elegant pose",
    "britisch-kurzhaar-rasseguide_00001_": "anthropomorphic British Shorthair cat character with round face and plush gray fur",
    "katzen-balkon-sichern_00001_": "anthropomorphic cat character lounging on a safe balcony, vibrant city background",
    "katzen-beschaeftigung_00001_": "anthropomorphic cat character playing with colorful toys and scratching post, active fun",
    "katzen-beschaeftigung_00002": "anthropomorphic cat character chasing a laser pointer dot, dynamic playful action",
    "katzen-beschaeftigung_00003": "anthropomorphic cat character jumping for a feather wand toy, dynamic action",
    "katzen-clickertraining-intelligenzspielzeug_00001_": "anthropomorphic cat character solving a puzzle toy, bright focused eyes",
    "katzen-ernaehrung_00001_": "anthropomorphic cat character looking at food bowls, cute hungry expression",
    "katzen-freigaenger_00001_": "anthropomorphic cat character exploring a garden with butterflies, outdoor adventure",
    "katzen-impfungen-vorsorge_00001_": "anthropomorphic cat character at vet with bandage, brave cute expression",
    "katzen-kastration-sterilisation_00001_": "anthropomorphic cat character recovering with a tiny bandage, cozy blanket",
    "katzen-krankheiten_hero": "anthropomorphic cat character with stethoscope at vet checkup, concerned cute face",
    "katzen-kratzbaum_00001_": "anthropomorphic cat character climbing a tall cat tree tower, playful energy",
    "katzen-verhalten-koerpersprache-kommunikation_00001_": "anthropomorphic cat character making different expressive poses, communication series",
    "katzen-wohnung_00001_": "anthropomorphic cat character relaxing in a cozy apartment, purring happy indoor cat",
    "katzen-zahnpflege_00001_": "anthropomorphic cat character brushing teeth with a giant toothbrush, funny cute",
    "katzenbeschaeftigung_00001_": "anthropomorphic cat character batting at colorful hanging toys, energetic play",
    "katzenfutter-selber-machen_00001_": "anthropomorphic cat character surrounded by fresh ingredients and bowls, cooking scene",
    "katzenfutter-vergleich-2026_00001_": "anthropomorphic cat character comparing two food bowls, curious picky expression",
    "katzenhaltung-wohnung_00001_": "anthropomorphic cat character in cozy apartment with window view, happy indoor life",
    "katzenkrankheiten-erkennen_00001_": "anthropomorphic cat character with thermometer, being checked by vet",
    "katzenrassen-vergleich_00001_": "three anthropomorphic cat characters of different breeds lined up together",
    "katzenrassen-vergleich_00002_": "anthropomorphic longhair and shorthair cat characters being groomed side by side",
    "katzenrassen-vergleich_00003_": "anthropomorphic cat character being brushed with sparkles, happy grooming time",
    "katzentoilette-geruch-vermeiden_00001_": "anthropomorphic cat character with sparkly clean litter box, fresh clean scene",
    "maine-coon-katze_00001_": "anthropomorphic Maine Coon cat character with huge fluffy tail and tufted ears",
    "maine-coon-katze-rasseguide_00001_": "anthropomorphic Maine Coon cat character, majestic large size, friendly giant cat",
    "perserkatze-rasseguide_00001_": "anthropomorphic Persian cat character with luxurious flat face and flowing fur",
    "ragdoll-katze-rasseguide_00001_": "anthropomorphic Ragdoll cat character flopped on back, relaxed silly pose",
    "seniorkatzen-pflege-ernaehrung-gesundheit_00001_": "anthropomorphic elderly cat character with glasses and cozy blanket, senior portrait",
    "siamkatze-rasseguide_00001_": "anthropomorphic Siamese cat character with striking blue eyes and dark points",
    
    # Kleintiere
    "chinchilla-haltung-pflege_00001_": "anthropomorphic Chinchilla character with huge round ears and fluffy gray fur",
    "degus-haltung-pflege_00001_": "anthropomorphic Degu characters taking a sand bath, cute brush tails",
    "hamster-haltung_00001_": "anthropomorphic Hamster character with chubby cheeks in colorful cage with wheel",
    "kaninchenhaltung_00001_": "anthropomorphic Rabbit character with long ears and fluffy tail in cozy hutch",
    "kaninchen-ernaehrung-gesundheit_00001_": "anthropomorphic Rabbit character surrounded by fresh vegetables and hay",
    "kleintier-gehege_00001_": "anthropomorphic guinea pig and rabbit characters together in colorful enclosure",
    "kleintiere_00001_": "anthropomorphic hamster and guinea pig characters together, cute tiny pets",
    "meerschweinchen-ernaehrung-vitamin-c_00001_": "anthropomorphic Guinea Pig character with vitamin C fruits and veggies",
    "meerschweinchen-haltung_00001_": "anthropomorphic Guinea Pig character popcorning with joy, cute happy pet",
    "frettchen-haustier-haltung_00001_": "anthropomorphic Ferret character doing the weasel war dance, long silly body",
    
    # Vögel
    "wellensittich-ernaehrung-futter_00001_": "anthropomorphic Budgie character with colorful feathers eating seeds",
    "wellensittich-ernaehrung-gesundheit_00001_": "anthropomorphic Budgie character with fresh greens and vitamins",
    "wellensittich-haltung_00001_": "anthropomorphic Budgie character perching happily in colorful cage",
    "voegel-haustier-beste-vogelarten-einsteiger_00001_": "anthropomorphic Budgie and Canary characters together, colorful bird friends",
    "vogelkaefig-voliere-vergleich_00001_": "anthropomorphic budgie character in large colorful aviary with toys",
    
    # Aquarium
    "aquarium-einrichtung_00001_": "anthropomorphic colorful tropical fish character swimming among coral and plants",
    "aquarium-fische-einsteiger_00001_": "anthropomorphic neon tetra fish group swimming in planted aquarium",
    
    # Allgemein
    "allergiker-haustiere_00001_": "anthropomorphic hypoallergenic pets: poodle cat and fish together, allergy-friendly group",
    "erste-hilfe-haustiere-notfall-ratgeber_00001_": "anthropomorphic dog and cat characters with first aid kit and bandages, emergency scene",
    "haustier-anschaffung_00001_": "group of anthropomorphic pets: dog cat hamster bird together, family portrait",
    "haustierfreundliche-wohnung-einrichten_00001_": "anthropomorphic cat and dog characters in colorful pet-friendly apartment, interior scene",
    "haustiere-kinder_00001_": "anthropomorphic pet characters playing happily with a child, family fun scene",
    "tierarztkosten_00001_": "anthropomorphic dog character at vet with piggy bank and medical chart, cost scene",
    "hunde-ernaehrung-barf-trocken-nass_00001_": "anthropomorphic dog character comparing food bowls with meat and kibble, nutrition",
    "hunde-fellpflege-buersten-baden-krallen_00001_": "anthropomorphic dog character getting pampered with brush and bubbles, spa scene",
    "hunde-krankheiten-symptome-erste-hilfe_00001_": "anthropomorphic dog character with thermometer and first aid, medical scene",
    "hunde-uebergewicht_00001_": "anthropomorphic chubby dog character exercising with a ball, fitness journey",
    "reptilien-haustier-anfaenger-vergleich-2026_00001_": "anthropomorphic friendly lizard and turtle characters as beginner pets, reptile scene",
    "katzen-kratzbaum_00001_": "anthropomorphic cat character climbing a tall cat tree, playful active energy",
}

# ─── Collect ALL images from articles ───

def get_article_images():
    """Scan all articles, return dict of {filename: slug} for hero images."""
    images = {}
    for fn in sorted(os.listdir(ARTICLE_DIR)):
        if not fn.endswith('.html') or fn == 'index.html':
            continue
        path = os.path.join(ARTICLE_DIR, fn)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        # Find hero images (first img that references images/)
        hero_matches = re.findall(r'<img[^>]+src="\.\./images/([^"]+\.webp)"', content)
        hero_matches += re.findall(r'<img[^>]+src="\.\./images/([^"]+\.png)"', content)
        hero_matches += re.findall(r'content=".*?/images/([^"]+\.webp)"', content)
        
        for img_file in hero_matches:
            if img_file not in images:
                # Detect slug from filename (strip _00001_, .webp, .png)
                slug = img_file.replace('.webp', '').replace('.png', '')
                images[img_file] = slug
    return images

# ─── API Call ───

def call_minimax(subject, retries=5):
    prompt = f"{subject}, {STYLE}"
    payload = json.dumps({
        "model": MODEL,
        "prompt": prompt,
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
                    if "rate limit" in err.lower() or "RPM" in err:
                        print(f"  ⏸ RPM limit, warte 30s...")
                        time.sleep(30)
                        continue
                    if "2056" in err:
                        print(f"  ⛔ Token limit!")
                        return "TOKEN_LIMIT"
                    print(f"  ⚠️  {err[:100]}")
                    if attempt < retries - 1:
                        time.sleep(10 * (attempt + 1))
                        continue
                    return None
                urls = result.get("data", {}).get("image_urls", [])
                if urls:
                    return urls[0]
                return None
        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8')
            if "2056" in body:
                return "TOKEN_LIMIT"
            if "RPM" in body or "rate" in body.lower():
                time.sleep(30)
                continue
            print(f"  ❌ HTTP {e.code}: {body[:150]}")
            if attempt < retries - 1:
                time.sleep(10 * (attempt + 1))
        except Exception as e:
            print(f"  ❌ {e}")
            if attempt < retries - 1:
                time.sleep(5)
    return None

def download_and_save(url, img_file):
    try:
        ctx = ssl.create_default_context()
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
            img_data = resp.read()
        
        temp_path = os.path.join(IMG_DIR, img_file + '.tmp')
        with open(temp_path, 'wb') as f:
            f.write(img_data)
        
        img = Image.open(temp_path)
        if img.mode == "RGBA":
            bg = Image.new("RGB", img.size, (255, 255, 255))
            bg.paste(img, mask=img.split()[3])
            img = bg
        
        dst = os.path.join(IMG_DIR, img_file)
        img = img.resize((1216, 832), Image.LANCZOS)
        img.save(dst, "WEBP", quality=92)
        kb = os.path.getsize(dst) // 1024
        
        os.remove(temp_path)
        return kb
    except Exception as e:
        print(f"  ❌ Download error: {e}")
        return None

# ─── Main ───

all_images = get_article_images()
items = sorted(all_images.items())  # (img_file, slug)

# Filter: only images we have a subject for
items = [(img, slug) for img, slug in items if slug in SUBJECT_MAP]

print(f"🎯 {len(items)} article hero images to regenerate via MiniMax image-01")
print(f"   Style: furry pop-art, orange/violet palette")
print(f"={'='*60}\n")

os.makedirs(IMG_DIR, exist_ok=True)

success = 0
skipped = 0
failed = 0
rate_limited = False

for idx, (img_file, slug) in enumerate(items, 1):
    dst = os.path.join(IMG_DIR, img_file)
    
    # Skip if already MiniMax (modified in last 30 min AND >200KB)
    if os.path.exists(dst):
        mtime = os.path.getmtime(dst)
        kb = os.path.getsize(dst) // 1024
        if mtime > time.time() - 1800 and kb > 200:
            print(f"[{idx}/{len(items)}] ⏭ {img_file} ({kb}KB, bereits MiniMax)")
            skipped += 1
            continue
    
    subject = SUBJECT_MAP[slug]
    print(f"[{idx}/{len(items)}] {img_file}... ", end="", flush=True)
    
    url = call_minimax(subject)
    
    if url == "TOKEN_LIMIT":
        print(f"⛔ Token Limit erreicht nach {success} Erfolgen")
        rate_limited = True
        break
    
    if url:
        print(f"URL... ", end="", flush=True)
        result_kb = download_and_save(url, img_file)
        if result_kb and result_kb > 100:
            print(f"✅ {result_kb}KB")
            success += 1
        elif result_kb:
            print(f"⚠️  nur {result_kb}KB")
            failed += 1
        else:
            print(f"❌ Download fehlgeschlagen")
            failed += 1
    else:
        print(f"❌ Keine URL (Rate Limit?)")
        failed += 1
        time.sleep(5)
    
    time.sleep(3)

print(f"\n{'='*50}")
print(f"✅ Fertig: {success} neu / {skipped} übersprungen / {failed} fehlgeschlagen")
if rate_limited:
    print(f"⛔ Token Limit erreicht - Rest später fortsetzen")
print(f"{'='*50}")
