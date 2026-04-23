import pdfplumber
import re
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

pdf_path = r"D:\MM\litjvpc.pdf"

# Product ID validation (already fixed earlier)
def is_valid_product_id(text):
    return (
        re.match(r"^[A-Z]{1,3}-[A-Z0-9\-]+$", text)
        and any(char.isdigit() for char in text)
    )

all_products = []

# =========================
# STEP 1: Extract products
# =========================
with pdfplumber.open(pdf_path) as pdf:

    for page_index in range(9, 145):   # page 10 to 145
        page = pdf.pages[page_index]
        words = page.extract_words()

        lines = {}
        for w in words:
            y = round(w['top'], 0)
            lines.setdefault(y, []).append(w)

        sorted_lines = sorted(lines.items())

        processed_lines = []
        for y, ws in sorted_lines:
            ws_sorted = sorted(ws, key=lambda x: x['x0'])
            text = " ".join([w['text'] for w in ws_sorted])
            x_positions = [w['x0'] for w in ws_sorted]
            avg_x = sum(x_positions) / len(x_positions)
            processed_lines.append((text, avg_x))

        i = 0
        while i < len(processed_lines):
            text, x = processed_lines[i]

            if is_valid_product_id(text):
                product_id = text
                description = ""
                bullets = []

                j = i + 1

                # Extract description
                while j < len(processed_lines):
                    t, x_pos = processed_lines[j]

                    if is_valid_product_id(t):
                        break
                    if t.startswith("•"):
                        break

                    if x_pos < 300 and not re.match(r"^\d{3}-", t):
                        description += " " + t

                    j += 1

                # =========================
                # BULLET FIX (ONLY CHANGE)
                # =========================
                while j < len(processed_lines):
                    t, x_pos = processed_lines[j]

                    if is_valid_product_id(t):
                        break

                    if t.startswith("•") and x_pos > 250:
                        bullet = t

                        k = j + 1
                        while k < len(processed_lines):
                            next_t, next_x = processed_lines[k]

                            # stop if next bullet or new product
                            if next_t.startswith("•") or is_valid_product_id(next_t):
                                break

                            # merge continuation line (same right side)
                            if next_x > 250:
                                bullet += " " + next_t
                                k += 1
                            else:
                                break

                        bullets.append(bullet)
                        j = k
                    else:
                        j += 1

                search_text = f"{product_id} {description} {' '.join(bullets)}"

                all_products.append({
                    "product_id": product_id,
                    "description": description.strip(),
                    "bullets": bullets,
                    "text": search_text,
                    "page": page_index + 1
                })

                i = j
            else:
                i += 1

print("Total products extracted:", len(all_products))


# =========================
# STEP 2: Embeddings
# =========================
model = SentenceTransformer('all-MiniLM-L6-v2')

texts = [p["text"] for p in all_products]
embeddings = np.array(model.encode(texts), dtype=np.float32)
faiss.normalize_L2(embeddings)

# =========================
# STEP 3: FAISS
# =========================
dimension = embeddings.shape[1]
index = faiss.IndexFlatIP(dimension)
index.add(embeddings)

print("FAISS index created!")


# =========================
# STEP 4: SEARCH
# =========================
while True:
    query = input("\nEnter product description (or type 'exit'): ")

    query = query.strip()

    if query.lower() == "exit":
        break

    exact_product = next(
        (p for p in all_products if p["product_id"].strip().upper() == query.upper()),
        None
    )
    if exact_product:
        print("\n--- Search Results ---\n")
        print("Product ID:", exact_product["product_id"])
        print("Page:", exact_product["page"])
        print("Description:", exact_product["description"])

        print("\nFeatures:")
        for b in exact_product["bullets"]:
            print(" ", b)

        print("-" * 60)
        continue

    query_vec = np.array(model.encode([query]), dtype=np.float32)
    faiss.normalize_L2(query_vec)
    similarities, indices = index.search(query_vec, k=10)
    print(f"Debug: returned {len(indices[0])} results")

    print("\n--- Search Results ---\n")

    found_match = False
    for i, idx in enumerate(indices[0]):
        product = all_products[idx]
        score = similarities[0][i]

        if score < 0.5:
            continue

        found_match = True

        print(f"Rank {i+1}")
        print("Product ID:", product["product_id"])
        print("Page:", product["page"])
        print("Similarity (higher = better):", round(score, 3))
        print("Confidence:", f"{round(score * 100, 1)}%")
        print("Description:", product["description"])

        print("\nFeatures:")
        for b in product["bullets"]:
            print(" ", b)

        print("-" * 60)

    if not found_match:
        print("No match found")
