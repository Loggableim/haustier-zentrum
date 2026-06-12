#!/usr/bin/env python3
"""Regenerate ALL hero images with CORRECT Haustierzentrum style: colored pencil sketch on cream paper."""
import json, os, sys, time, urllib.request, subprocess
from PIL import Image

QUEUE = "http://127.0.0.1:8283"
IMG_DIR = r"C:\HermesPortable\home\spaces\haustier-zentrum\images"
os.makedirs(IMG_DIR, exist_ok=True)

POSITIVE_TEMPLATE = "Colored pencil sketch drawing on cream paper of {subject}, hand-drawn illustration style, soft pastel colors, warm tones, gentle strokes, children's book illustration, cute friendly animals, detailed fur, cozy atmosphere"
NEGATIVE = "photorealistic, 3d render, photograph, realistic texture, hyperrealistic, cinematic lighting, shadows, gradient, oil painting, digital art, smooth shading, dark mood, scary, pop art, comic style, warhol, halftone dots, bold outlines, high contrast"

IMAGES = [
    # Batch 1
    ("westie-west-highland-white-terrier-rasseguide_00001_", "a cute West Highland White Terrier dog with white fur, dark eyes, small upright ears, friendly expression"),
    ("beagle-rasseguide_00001_", "a happy Beagle dog with tricolor fur, brown floppy ears, big brown eyes, curious expression"),
    ("malteser-rasseguide_00001_", "a cute Maltese dog with pure white silky long fur, dark button eyes, elegant appearance"),
    ("havaneser-rasseguide_00001_", "a Havanese dog with long silky cream-colored fur, big dark eyes, playful expression"),
    ("dalmatiner-rasseguide_00001_", "a Dalmatian dog with white fur and black spots, alert brown eyes, elegant body"),
    ("zwergspitz-pomeranian-rasseguide_00001_", "a cute Pomeranian dog with fluffy orange-brown fur, small pointy ears, fox-like face"),
    ("cocker-spaniel-rasseguide_00001_", "a Cocker Spaniel with long floppy ears, silky golden fur, big dark eyes, gentle expression"),
    ("berner-sennenhund-rasseguide_00001_", "a Bernese Mountain Dog with tricolor fur, strong body, friendly gentle expression"),
    ("hero-mops-rasseguide", "a cute Pug dog with beige fur, black mask, short snout, big round eyes, deep wrinkles, friendly"),
    ("hero-ragdoll-katze-rasseguide", "a beautiful Ragdoll cat with big blue eyes, silky medium-long seal point fur, relaxed pose"),
    ("hero-sibirischer-husky-rasseguide", "a majestic Siberian Husky with striking blue eyes, gray-white-black fur, upright triangular ears"),
    ("katzen-krankheiten_hero", "a friendly house cat at the vet with a stethoscope, health checkup scene"),
    # Batch 2
    ("deutscher-schaeferhund_00001_", "a German Shepherd dog with strong build, black and brown fur, large upright ears, alert expression"),
    ("katzen-kastration-sterilisation_00001_", "a cute house cat with a small bandage after surgery, resting comfortably"),
    ("hundepension-tagesbetreuung-ratgeber_00001_", "happy dogs playing together in a dog daycare facility, outdoor play area"),
    ("katzen-clickertraining-intelligenzspielzeug_00001_", "an attentive cat doing clicker training with interactive puzzle toys"),
    ("wellensittich-ernaehrung-futter_00001_", "a colorful budgie parrot with seed mix and fresh food, cage with food bowl"),
    ("hundeschule-welpenschule-ratgeber_00001_", "a cute puppy learning commands at dog school with treats and toys"),
    ("hunde-erstausstattung-checkliste_00001_", "puppy essentials: food bowl, leash, bed, toys, a complete first equipment set"),
    ("katzen-beschaeftigung_00003", "a playful cat with a feather wand and scratching post, active indoor cat"),
    # Batch 3
    ("rottweiler-rasseguide_00001_", "a strong Rottweiler dog with black fur and brown markings, muscular body, loyal expression"),
    ("boxer-rasseguide_00001_", "an athletic Boxer dog with short brown fur, white chest, muscular build, friendly face"),
    ("frettchen-haustier-haltung_00001_", "a playful ferret with long slender body, light brown fur, dark mask, curious nose"),
    ("bengal-cat-rasseguide_00001_", "an exotic Bengal cat with leopard-spotted golden fur, wild appearance, elegant posture"),
    ("degus-haltung-pflege_00001_", "cute degus taking a sand bath, with brush tails, big round eyes, brown-gray fur"),
    ("erste-hilfe-haustiere-notfall-ratgeber_00001_", "pet first aid kit with bandage, scissors, and a dog or cat, emergency scene"),
    ("katzen-balkon-sichern_00001_", "a cat on a balcony with safety netting, secure outdoor access, happy cat"),
    ("chinchilla-haltung-pflege_00001_", "a cute chinchilla with big round ears, fluffy gray fur, taking a dust bath"),
    ("pferdehaltung-einsteiger_00001_", "a beautiful horse on a green meadow, mane flowing in wind, gentle expression"),
    ("shiba-inu-rasseguide_00001_", "a distinctive Shiba Inu with fox-like face, reddish-brown fur, triangular ears"),
    ("aquarium-fische-einsteiger_00001_", "colorful tropical aquarium fish swimming among green water plants, freshwater tank"),
    ("haustierfreundliche-wohnung-einrichten_00001_", "a cozy pet-friendly apartment with cat tree and dog bed, animals and humans living together"),
    ("vogelkaefig-voliere-vergleich_00001_", "a large bird aviary with colorful budgies and parakeets, species-appropriate bird keeping"),
    ("wellensittich-ernaehrung-gesundheit_00001_", "a colorful budgie with seed mix, fresh greens, and vitamins for healthy nutrition"),
]

def submit(prompt, neg):
    data = json.dumps({
        "model": "sdxl-lightning", "prompt": prompt, "negative": neg,
        "steps": 8, "width": 1216, "height": 832,
    }).encode()
    req = urllib.request.Request(f"{QUEUE}/generate", data=data, headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=30).read()).get("job_id")

def wait_for(job_id, timeout=300):
    for i in range(timeout // 3):
        time.sleep(3)
        try:
            resp = json.loads(urllib.request.urlopen(f"{QUEUE}/status/{job_id}", timeout=10).read())
            if resp.get("status") == "done" and resp.get("output_path"):
                return resp["output_path"]
            if resp.get("status") == "failed":
                return None
        except: pass
    return None

total = len(IMAGES)
print(f"🎯 Regeneriere {total} Bilder mit RICHTIGEM Style\n")

failed = []
for idx, (slug, subject) in enumerate(IMAGES, 1):
    prompt = POSITIVE_TEMPLATE.replace("{subject}", subject)
    print(f"[{idx}/{total}] {slug}... ", end="", flush=True)
    try:
        job_id = submit(prompt, NEGATIVE)
        if not job_id:
            print("❌ submit fail")
            failed.append(slug)
            continue
        out_path = wait_for(job_id)
        if out_path:
            img = Image.open(out_path.replace("\\", "/"))
            if img.mode == "RGBA":
                bg = Image.new("RGB", img.size, (255, 255, 255))
                bg.paste(img, mask=img.split()[3])
                img = bg
            img = img.resize((1216, 832), Image.LANCZOS)
            img.save(os.path.join(IMG_DIR, f"{slug}.webp"), "WEBP", quality=92)
            kb = os.path.getsize(os.path.join(IMG_DIR, f"{slug}.webp")) // 1024
            print(f"✅ {kb}KB")
        else:
            print("❌ failed/timeout")
            failed.append(slug)
    except Exception as e:
        print(f"❌ {e}")
        failed.append(slug)
    time.sleep(1)

print(f"\n{'='*50}")
print(f"✅ Done! {total - len(failed)}/{total} regenerated")
if failed:
    print(f"❌ Failed: {', '.join(failed)}")

r = subprocess.run(["curl", "-s", "http://127.0.0.1:8283/health"], capture_output=True, text=True)
d = json.loads(r.stdout)
print(f"Queue total: {d['completed']} done / {d['failed']} failed")
