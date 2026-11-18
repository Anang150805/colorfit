"""Script Pembangkit Dataset ColorFit: data/colors.csv dan data/outfits.csv.

Aturan dan Teori:
1. data/colors.csv:
   - Berdasarkan teori Color Analysis (Seasonal Color Analysis & Undertone Matching).
   - Warm undertone cocok dengan warna bernuansa earthy, hangat, keemasan (terracotta, bata, mustard, olive, coral).
   - Cool undertone cocok dengan jewel tone bernuansa dingin, keperakan (navy, emerald, royal blue, plum, magenta).
   - Neutral undertone fleksibel dan paling anggun dengan warna muted, dusty, dan seimbang (dusty rose, soft sage, taupe, mauve).
   - Nilai Hue (0-360), Saturation (0-1), dan Value (0-1) dihitung matematis dari HEX melalui modul services.color_features.
   - Distribusi ketiga label ("Sangat Cocok", "Cocok", "Kurang Cocok") dijaga seimbang per undertone.
   - Meliputi 9 rumpun warna: merah, kuning, hijau, biru, ungu, oranye, pink, coklat, netral.

2. data/outfits.csv:
   - Berdasarkan prinsip padu-padan fashion styling dan harmoni warna Itten (Monochromatic, Analogous, Complementary, Neutral Balance).
   - Pasangan atasan dan bawahan serasi untuk berbagai warna dasar pakaian populer.
   - Nilai CIELAB (L*, a*, b*) dihitung matematis dari HEX menggunakan standar D65 illuminant.
"""

import os
import sys
import pandas as pd

# Tambahkan direktori root backend ke sys.path agar modul services dapat diimpor
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from services.color_features import hex_to_hsv, hex_to_lab

DATA_DIR = os.path.join(BACKEND_DIR, "data")


# ==============================================================================
# 1. DEFINISI DATA WARNA UNTUK colors.csv
# ==============================================================================
# Format: (name, hex, undertone, family, label)

RAW_COLORS = [
    # ----------------- WARM UNDERTONE (54 Warna) -----------------
    # Sangat Cocok: Earthy, warm, golden, terracotta tones (18)
    ("Merah Bata", "#B7410E", "warm", "merah", "Sangat Cocok"),
    ("Merah Karang Hangat", "#D74826", "warm", "merah", "Sangat Cocok"),
    ("Kuning Mustard", "#E1AD01", "warm", "kuning", "Sangat Cocok"),
    ("Kuning Emas Tua", "#DAA520", "warm", "kuning", "Sangat Cocok"),
    ("Hijau Olive", "#556B2F", "warm", "hijau", "Sangat Cocok"),
    ("Hijau Sage Hangat", "#8A9A5B", "warm", "hijau", "Sangat Cocok"),
    ("Hijau Lumut", "#4A5D23", "warm", "hijau", "Sangat Cocok"),
    ("Oranye Terakota", "#CC4E2A", "warm", "oranye", "Sangat Cocok"),
    ("Oranye Karamel", "#C67129", "warm", "oranye", "Sangat Cocok"),
    ("Oranye Labu Hangat", "#D96924", "warm", "oranye", "Sangat Cocok"),
    ("Pink Coral", "#F88379", "warm", "pink", "Sangat Cocok"),
    ("Pink Salmon", "#FA8072", "warm", "pink", "Sangat Cocok"),
    ("Coklat Karamel", "#8B4513", "warm", "coklat", "Sangat Cocok"),
    ("Coklat Camel", "#C19A6B", "warm", "coklat", "Sangat Cocok"),
    ("Coklat Tan", "#D2B48C", "warm", "coklat", "Sangat Cocok"),
    ("Coklat Tembaga", "#B87333", "warm", "coklat", "Sangat Cocok"),
    ("Krem Hangat", "#F5F5DC", "warm", "netral", "Sangat Cocok"),
    ("Putih Gading (Ivory)", "#FFF8DC", "warm", "netral", "Sangat Cocok"),

    # Cocok: Netral hangat, hijau teduh, oranye lembut (18)
    ("Merah Cabai", "#C41E3A", "warm", "merah", "Cocok"),
    ("Merah Marun Hangat", "#801818", "warm", "merah", "Cocok"),
    ("Kuning Mentega", "#F6E07E", "warm", "kuning", "Cocok"),
    ("Kuning Jagung", "#FBEC5D", "warm", "kuning", "Cocok"),
    ("Hijau Khaki", "#6B8E23", "warm", "hijau", "Cocok"),
    ("Hijau Apel Hangat", "#8DB600", "warm", "hijau", "Cocok"),
    ("Biru Teal Hangat", "#008080", "warm", "biru", "Cocok"),
    ("Biru Denim Hangat", "#2C5D88", "warm", "biru", "Cocok"),
    ("Biru Pirus (Turquoise)", "#40E0D0", "warm", "biru", "Cocok"),
    ("Ungu Terong Hangat", "#4D1A39", "warm", "ungu", "Cocok"),
    ("Ungu Plum Hangat", "#701C3C", "warm", "ungu", "Cocok"),
    ("Oranye Aprikot", "#FBCEB1", "warm", "oranye", "Cocok"),
    ("Oranye Peach", "#FFE5B4", "warm", "oranye", "Cocok"),
    ("Pink Pastel Hangat", "#F4C2C2", "warm", "pink", "Cocok"),
    ("Coklat Espresso", "#362217", "warm", "coklat", "Cocok"),
    ("Coklat Mahoni", "#4C1C13", "warm", "coklat", "Cocok"),
    ("Abu-abu Hangat (Warm Taupe)", "#9E978E", "warm", "netral", "Cocok"),
    ("Beige Klasik", "#E6DBBF", "warm", "netral", "Cocok"),

    # Kurang Cocok: Warna icy, keperakan, biru/ungu dingin tajam (18)
    ("Merah Crimson Dingin", "#990000", "warm", "merah", "Kurang Cocok"),
    ("Merah Rubi Dingin", "#9B111E", "warm", "merah", "Kurang Cocok"),
    ("Kuning Lemon Icy", "#FFF44F", "warm", "kuning", "Kurang Cocok"),
    ("Kuning Neon Dingin", "#FFFF33", "warm", "kuning", "Kurang Cocok"),
    ("Hijau Zamrud Dingin", "#004B49", "warm", "hijau", "Kurang Cocok"),
    ("Hijau Pinus Dingin", "#014421", "warm", "hijau", "Kurang Cocok"),
    ("Biru Icy", "#AFDBF5", "warm", "biru", "Kurang Cocok"),
    ("Biru Elektrik", "#0000FF", "warm", "biru", "Kurang Cocok"),
    ("Biru Kobalt", "#0047AB", "warm", "biru", "Kurang Cocok"),
    ("Biru Royal", "#4169E1", "warm", "biru", "Kurang Cocok"),
    ("Ungu Lavender Dingin", "#967BB6", "warm", "ungu", "Kurang Cocok"),
    ("Ungu Dingin Royal", "#431C53", "warm", "ungu", "Kurang Cocok"),
    ("Ungu Amethyst Dingin", "#9966CC", "warm", "ungu", "Kurang Cocok"),
    ("Oranye Neon", "#FF5F1F", "warm", "oranye", "Kurang Cocok"),
    ("Pink Fuschia Tajam", "#C71585", "warm", "pink", "Kurang Cocok"),
    ("Pink Magenta Tajam", "#FF007F", "warm", "pink", "Kurang Cocok"),
    ("Abu-abu Silver Dingin", "#C0C0C0", "warm", "netral", "Kurang Cocok"),
    ("Hitam Pekat Dingin", "#0A0A0A", "warm", "netral", "Kurang Cocok"),

    # ----------------- COOL UNDERTONE (54 Warna) -----------------
    # Sangat Cocok: Jewel tones, deep cool blues, icy emeralds, plums, magentas (18)
    ("Biru Navy Klasik", "#000080", "cool", "biru", "Sangat Cocok"),
    ("Biru Royal Dingin", "#4169E1", "cool", "biru", "Sangat Cocok"),
    ("Biru Safir", "#0F52BA", "cool", "biru", "Sangat Cocok"),
    ("Hijau Zamrud (Emerald)", "#008055", "cool", "hijau", "Sangat Cocok"),
    ("Hijau Pinus Dingin", "#004225", "cool", "hijau", "Sangat Cocok"),
    ("Hijau Forest Dingin", "#1B4D3E", "cool", "hijau", "Sangat Cocok"),
    ("Ungu Plum Dingin", "#701C3C", "cool", "ungu", "Sangat Cocok"),
    ("Ungu Royal Dingin", "#6B2D5C", "cool", "ungu", "Sangat Cocok"),
    ("Ungu Deep Amethyst", "#5B2C6F", "cool", "ungu", "Sangat Cocok"),
    ("Merah Burgundy Dingin", "#800020", "cool", "merah", "Sangat Cocok"),
    ("Merah Rubi Klasik", "#9B111E", "cool", "merah", "Sangat Cocok"),
    ("Merah Cranberry", "#9E1B32", "cool", "merah", "Sangat Cocok"),
    ("Pink Magenta", "#FF007F", "cool", "pink", "Sangat Cocok"),
    ("Pink Fuschia", "#D9027D", "cool", "pink", "Sangat Cocok"),
    ("Pink Deep Rose", "#C2185B", "cool", "pink", "Sangat Cocok"),
    ("Abu-abu Dingin (Slate)", "#708090", "cool", "netral", "Sangat Cocok"),
    ("Putih Bersih (Pure White)", "#F8F9FA", "cool", "netral", "Sangat Cocok"),
    ("Hitam Elegan", "#1A1A1A", "cool", "netral", "Sangat Cocok"),

    # Cocok: Pastel dingin, ice blue, mint, lilac, slate (18)
    ("Biru Baby Blue", "#89CFF0", "cool", "biru", "Cocok"),
    ("Biru Ice Blue", "#A5F2F3", "cool", "biru", "Cocok"),
    ("Biru Cornflower", "#6495ED", "cool", "biru", "Cocok"),
    ("Hijau Mint Dingin", "#98FF98", "cool", "hijau", "Cocok"),
    ("Hijau Seafoam", "#71BC78", "cool", "hijau", "Cocok"),
    ("Hijau Celadon Dingin", "#ACE1AF", "cool", "hijau", "Cocok"),
    ("Ungu Lavender", "#B57EDC", "cool", "ungu", "Cocok"),
    ("Ungu Lilac", "#C8A2C8", "cool", "ungu", "Cocok"),
    ("Ungu Periwinkle", "#CCCCFF", "cool", "ungu", "Cocok"),
    ("Pink Pastel Dingin", "#FFD1DC", "cool", "pink", "Cocok"),
    ("Pink Dusty Rose Dingin", "#DCAE96", "cool", "pink", "Cocok"),
    ("Kuning Lemon Dingin", "#FAFA33", "cool", "kuning", "Cocok"),
    ("Merah Mawar Raspberry", "#E30B5C", "cool", "merah", "Cocok"),
    ("Coklat Rosy Brown", "#BC8F8F", "cool", "coklat", "Cocok"),
    ("Coklat Cocoa Dingin", "#533D35", "cool", "coklat", "Cocok"),
    ("Abu-abu Perak (Silver)", "#B0B7C6", "cool", "netral", "Cocok"),
    ("Abu-abu Charcoal", "#36454F", "cool", "netral", "Cocok"),
    ("Putih Salju", "#F0F8FF", "cool", "netral", "Cocok"),

    # Kurang Cocok: Warna earthy hangat pekat, oranye bata, camel (18)
    ("Kuning Mustard Hangat", "#E1AD01", "cool", "kuning", "Kurang Cocok"),
    ("Kuning Kunyit", "#FFBF00", "cool", "kuning", "Kurang Cocok"),
    ("Kuning Emas Hangat", "#DAA520", "cool", "kuning", "Kurang Cocok"),
    ("Oranye Terakota", "#CC4E2A", "cool", "oranye", "Kurang Cocok"),
    ("Oranye Labu Hangat", "#D96924", "cool", "oranye", "Kurang Cocok"),
    ("Oranye Karamel Hangat", "#C67129", "cool", "oranye", "Kurang Cocok"),
    ("Oranye Aprikot Hangat", "#FBCEB1", "cool", "oranye", "Kurang Cocok"),
    ("Coklat Camel Hangat", "#C19A6B", "cool", "coklat", "Kurang Cocok"),
    ("Coklat Karamel", "#8B4513", "cool", "coklat", "Kurang Cocok"),
    ("Coklat Karat Hangat", "#8B3A22", "cool", "coklat", "Kurang Cocok"),
    ("Coklat Tan Hangat", "#D2B48C", "cool", "coklat", "Kurang Cocok"),
    ("Hijau Olive Hangat", "#556B2F", "cool", "hijau", "Kurang Cocok"),
    ("Hijau Lumut Hangat", "#4A5D23", "cool", "hijau", "Kurang Cocok"),
    ("Hijau Chartreuse Hangat", "#7FFF00", "cool", "hijau", "Kurang Cocok"),
    ("Merah Bata Hangat", "#B7410E", "cool", "merah", "Kurang Cocok"),
    ("Pink Coral Hangat", "#F88379", "cool", "pink", "Kurang Cocok"),
    ("Krem Kuning Hangat", "#F5F5DC", "cool", "netral", "Kurang Cocok"),
    ("Beige Kuning Hangat", "#E6DBBF", "cool", "netral", "Kurang Cocok"),

    # ----------------- NEUTRAL UNDERTONE (54 Warna) -----------------
    # Sangat Cocok: Muted, dusty, soft, and balanced tones (18)
    ("Pink Dusty Rose Muted", "#DCAE96", "neutral", "pink", "Sangat Cocok"),
    ("Ungu Mauve Seimbang", "#915F6D", "neutral", "ungu", "Sangat Cocok"),
    ("Hijau Soft Sage", "#9CAF88", "neutral", "hijau", "Sangat Cocok"),
    ("Biru Muted Teal", "#3B7A85", "neutral", "biru", "Sangat Cocok"),
    ("Biru Muted Navy", "#2C3E50", "neutral", "biru", "Sangat Cocok"),
    ("Coklat Taupe Lembut", "#B38B6D", "neutral", "coklat", "Sangat Cocok"),
    ("Coklat Rose Taupe", "#905D5D", "neutral", "coklat", "Sangat Cocok"),
    ("Abu-abu Charcoal Muted", "#36454F", "neutral", "netral", "Sangat Cocok"),
    ("Krem Soft Cream", "#E8E4C9", "neutral", "netral", "Sangat Cocok"),
    ("Ungu Dusty Lavender", "#9A8C98", "neutral", "ungu", "Sangat Cocok"),
    ("Hijau Muted Olive", "#6B7B58", "neutral", "hijau", "Sangat Cocok"),
    ("Oranye Soft Peach Muted", "#FAD5A5", "neutral", "oranye", "Sangat Cocok"),
    ("Merah Muted Burgundy", "#6A2E35", "neutral", "merah", "Sangat Cocok"),
    ("Ungu Dusty Plum", "#5E3A4D", "neutral", "ungu", "Sangat Cocok"),
    ("Coklat Khaki Muted", "#A39B7B", "neutral", "coklat", "Sangat Cocok"),
    ("Abu-abu Heather Gray", "#9AA0A6", "neutral", "netral", "Sangat Cocok"),
    ("Kuning Muted Ochre", "#C29B38", "neutral", "kuning", "Sangat Cocok"),
    ("Merah Soft Terracotta", "#B85D43", "neutral", "merah", "Sangat Cocok"),

    # Cocok: Deep balanced neutrals, classic rich shades (18)
    ("Biru Deep Navy", "#1B263B", "neutral", "biru", "Cocok"),
    ("Hijau Forest Green Seimbang", "#2D5A27", "neutral", "hijau", "Cocok"),
    ("Merah Classic Wine", "#722F37", "neutral", "merah", "Cocok"),
    ("Biru Denim Muted", "#4A6FA5", "neutral", "biru", "Cocok"),
    ("Kuning Pasir (Sand)", "#D8C99B", "neutral", "kuning", "Cocok"),
    ("Coklat Cocoa Muted", "#4E3629", "neutral", "coklat", "Cocok"),
    ("Ungu Plum Muted", "#603F63", "neutral", "ungu", "Cocok"),
    ("Biru Slate Blue", "#5B758D", "neutral", "biru", "Cocok"),
    ("Hijau Soft Mint Muted", "#88B2AC", "neutral", "hijau", "Cocok"),
    ("Krem Warm Oatmeal", "#D1C7BD", "neutral", "netral", "Cocok"),
    ("Hijau Olive Muted", "#556644", "neutral", "hijau", "Cocok"),
    ("Oranye Coral Muted", "#D97D64", "neutral", "oranye", "Cocok"),
    ("Abu-abu Ash Gray", "#B2BEB5", "neutral", "netral", "Cocok"),
    ("Biru Midnight Muted", "#191970", "neutral", "biru", "Cocok"),
    ("Coklat Warm Taupe", "#7A6A58", "neutral", "coklat", "Cocok"),
    ("Coklat Camel Muted", "#B08D57", "neutral", "coklat", "Cocok"),
    ("Merah Soft Brick", "#A24836", "neutral", "merah", "Cocok"),
    ("Biru Dusty Turquoise", "#53888F", "neutral", "biru", "Cocok"),

    # Kurang Cocok: Warna neon sangat mencolok atau saturasi ekstrem silau (18)
    ("Oranye Neon Menyala", "#FF5F1F", "neutral", "oranye", "Kurang Cocok"),
    ("Kuning Neon Stabilo", "#FFFF33", "neutral", "kuning", "Kurang Cocok"),
    ("Hijau Neon Menyala", "#39FF14", "neutral", "hijau", "Kurang Cocok"),
    ("Pink Neon Menyala", "#FF1493", "neutral", "pink", "Kurang Cocok"),
    ("Biru Elektrik Tajam", "#0000FF", "neutral", "biru", "Kurang Cocok"),
    ("Kuning Terang Tajam", "#FFEF00", "neutral", "kuning", "Kurang Cocok"),
    ("Oranye Terang Tajam", "#FF6600", "neutral", "oranye", "Kurang Cocok"),
    ("Merah Menyala Tajam", "#FF0000", "neutral", "merah", "Kurang Cocok"),
    ("Hijau Terang Tajam", "#00FF00", "neutral", "hijau", "Kurang Cocok"),
    ("Ungu Elektrik Tajam", "#8A2BE2", "neutral", "ungu", "Kurang Cocok"),
    ("Pink Fuschia Silau", "#FF00FF", "neutral", "pink", "Kurang Cocok"),
    ("Biru Cyan Murni Silau", "#00FFFF", "neutral", "biru", "Kurang Cocok"),
    ("Hijau Chartreuse Silau", "#7FFF00", "neutral", "hijau", "Kurang Cocok"),
    ("Kuning Stabilo Silau", "#CCFF00", "neutral", "kuning", "Kurang Cocok"),
    ("Oranye Lava Silau", "#FF4500", "neutral", "oranye", "Kurang Cocok"),
    ("Merah Scarlet Tajam", "#FF2400", "neutral", "merah", "Kurang Cocok"),
    ("Biru Kobalt Tajam", "#0047AB", "neutral", "biru", "Kurang Cocok"),
    ("Pink Magenta Silau", "#FF0090", "neutral", "pink", "Kurang Cocok"),
]


# ==============================================================================
# 2. DEFINISI DATA PASANGAN OUTFIT UNTUK outfits.csv
# ==============================================================================
# Format: (base_name, base_hex, combo_name, combo_hex)
# Berisi minimal 150 pasangan atasan-bawahan pakaian serasi

RAW_OUTFITS = [
    # --- Base: Biru Navy Klasik (#000080 / #1B263B) ---
    ("Kemeja Navy", "#000080", "Celana Chino Camel", "#C19A6B"),
    ("Kemeja Navy", "#000080", "Celana Khaki Krem", "#D2B48C"),
    ("Kemeja Navy", "#000080", "Celana Putih Bersih", "#F8F9FA"),
    ("Kemeja Navy", "#000080", "Celana Abu-abu Terang", "#B0B7C6"),
    ("Blazer Navy", "#000080", "Rok Plisket Mustard", "#E1AD01"),
    ("Kaos Navy", "#000080", "Celana Jeans Denim Terang", "#6495ED"),
    ("Sweater Navy", "#000080", "Celana Chino Olive", "#556B2F"),
    ("Jaket Navy", "#000080", "Celana Terracotta", "#CC4E2A"),

    # --- Base: Putih Bersih / Putih Gading (#F8F9FA / #FFF8DC) ---
    ("Kemeja Putih", "#F8F9FA", "Celana Denim Navy", "#1B263B"),
    ("Kemeja Putih", "#F8F9FA", "Celana Chino Hitam", "#1A1A1A"),
    ("Kemeja Putih", "#F8F9FA", "Celana Chino Olive", "#556B2F"),
    ("Kemeja Putih", "#F8F9FA", "Rok Plisket Terracotta", "#B85D43"),
    ("Kaos Putih", "#F8F9FA", "Celana Jeans Biru Klasik", "#2C5D88"),
    ("Blus Putih", "#F8F9FA", "Celana Chino Camel", "#C19A6B"),
    ("Kemeja Linen Putih", "#F8F9FA", "Celana Sage Green", "#8A9A5B"),
    ("Tunik Putih Gading", "#FFF8DC", "Celana Coklat Espresso", "#362217"),
    ("Blus Putih Gading", "#FFF8DC", "Celana Kulot Navy", "#000080"),

    # --- Base: Hitam Elegan (#1A1A1A) ---
    ("Kaos Hitam", "#1A1A1A", "Celana Jeans Denim Biru", "#4A6FA5"),
    ("Kaos Hitam", "#1A1A1A", "Celana Chino Khaki", "#D2B48C"),
    ("Kemeja Hitam", "#1A1A1A", "Celana Chino Abu-abu", "#708090"),
    ("Kemeja Hitam", "#1A1A1A", "Celana Putih Off-White", "#F8F9FA"),
    ("Blazer Hitam", "#1A1A1A", "Rok Plisket Emerald Green", "#008055"),
    ("Sweater Hitam", "#1A1A1A", "Celana Chino Camel", "#C19A6B"),
    ("Jaket Hitam", "#1A1A1A", "Celana Denim Hitam Charcoal", "#36454F"),
    ("Cardigan Hitam", "#1A1A1A", "Rok Merah Marun", "#800020"),

    # --- Base: Hijau Olive (#556B2F) ---
    ("Kemeja Olive", "#556B2F", "Celana Chino Hitam", "#1A1A1A"),
    ("Kemeja Olive", "#556B2F", "Celana Chino Khaki Krem", "#D2B48C"),
    ("Kemeja Olive", "#556B2F", "Celana Denim Navy", "#000080"),
    ("Jaket Parka Olive", "#556B2F", "Celana Putih Gading", "#FFF8DC"),
    ("Kaos Olive", "#556B2F", "Celana Chino Terracotta", "#CC4E2A"),
    ("Sweater Olive", "#556B2F", "Celana Jeans Abu-abu Charcoal", "#36454F"),
    ("Kemeja Linen Olive", "#556B2F", "Celana Chino Beige", "#E6DBBF"),

    # --- Base: Hijau Sage (#8A9A5B / #9CAF88) ---
    ("Kemeja Sage", "#8A9A5B", "Celana Putih Bersih", "#F8F9FA"),
    ("Kemeja Sage", "#8A9A5B", "Celana Chino Krem", "#F5F5DC"),
    ("Blus Sage", "#8A9A5B", "Rok Plisket Dusty Rose", "#DCAE96"),
    ("Kaos Sage", "#8A9A5B", "Celana Denim Biru Terang", "#6495ED"),
    ("Cardigan Sage", "#8A9A5B", "Celana Chino Hitam", "#1A1A1A"),
    ("Sweater Sage", "#9CAF88", "Celana Chino Navy", "#1B263B"),
    ("Tunik Sage", "#9CAF88", "Celana Kulot Taupe", "#B38B6D"),

    # --- Base: Merah Bata / Terracotta (#B7410E / #CC4E2A) ---
    ("Kemeja Merah Bata", "#B7410E", "Celana Chino Krem", "#D2B48C"),
    ("Kemeja Merah Bata", "#B7410E", "Celana Denim Navy", "#000080"),
    ("Kaos Terracotta", "#CC4E2A", "Celana Chino Hitam", "#1A1A1A"),
    ("Kaos Terracotta", "#CC4E2A", "Celana Chino Olive", "#556B2F"),
    ("Sweater Terracotta", "#CC4E2A", "Celana Jeans Denim Biru", "#2C5D88"),
    ("Blus Terracotta", "#CC4E2A", "Rok Putih Gading", "#FFF8DC"),
    ("Kemeja Terracotta", "#CC4E2A", "Celana Chino Charcoal", "#36454F"),
    ("Jaket Merah Bata", "#B7410E", "Celana Jeans Abu-abu Terang", "#B0B7C6"),

    # --- Base: Kuning Mustard (#E1AD01) ---
    ("Kaos Mustard", "#E1AD01", "Celana Denim Navy Gelap", "#000080"),
    ("Kemeja Mustard", "#E1AD01", "Celana Chino Hitam", "#1A1A1A"),
    ("Kemeja Mustard", "#E1AD01", "Celana Chino Abu-abu Charcoal", "#36454F"),
    ("Sweater Mustard", "#E1AD01", "Celana Chino Olive", "#556B2F"),
    ("Cardigan Mustard", "#E1AD01", "Rok Plisket Burgundy", "#800020"),
    ("Blus Mustard", "#E1AD01", "Celana Jeans Biru Terang", "#6495ED"),
    ("Tunik Mustard", "#E1AD01", "Celana Chino Putih Gading", "#FFF8DC"),

    # --- Base: Coklat Camel (#C19A6B) ---
    ("Kemeja Camel", "#C19A6B", "Celana Denim Navy Klasik", "#000080"),
    ("Blazer Camel", "#C19A6B", "Celana Putih Bersih", "#F8F9FA"),
    ("Sweater Camel", "#C19A6B", "Celana Chino Hitam", "#1A1A1A"),
    ("Cardigan Camel", "#C19A6B", "Rok Plisket Hijau Forest", "#1B4D3E"),
    ("Kaos Camel", "#C19A6B", "Celana Chino Olive", "#556B2F"),
    ("Jaket Camel", "#C19A6B", "Celana Merah Burgundy", "#800020"),
    ("Kemeja Linen Camel", "#C19A6B", "Celana Jeans Denim Terang", "#89CFF0"),

    # --- Base: Merah Burgundy / Marun (#800020) ---
    ("Kemeja Burgundy", "#800020", "Celana Chino Khaki Krem", "#D2B48C"),
    ("Kemeja Burgundy", "#800020", "Celana Hitam Elegan", "#1A1A1A"),
    ("Sweater Burgundy", "#800020", "Celana Denim Biru Navy", "#000080"),
    ("Kaos Marun", "#800020", "Celana Chino Abu-abu", "#708090"),
    ("Blazer Burgundy", "#800020", "Celana Chino Camel", "#C19A6B"),
    ("Blus Burgundy", "#800020", "Rok Plisket Putih Gading", "#FFF8DC"),
    ("Cardigan Marun", "#800020", "Celana Chino Olive", "#556B2F"),

    # --- Base: Hijau Zamrud (Emerald) (#008055) ---
    ("Kemeja Emerald", "#008055", "Celana Chino Hitam", "#1A1A1A"),
    ("Kemeja Emerald", "#008055", "Celana Putih Bersih", "#F8F9FA"),
    ("Blus Emerald", "#008055", "Celana Chino Abu-abu Charcoal", "#36454F"),
    ("Sweater Emerald", "#008055", "Celana Denim Navy", "#000080"),
    ("Cardigan Emerald", "#008055", "Rok Plisket Khaki", "#D2B48C"),
    ("Blazer Emerald", "#008055", "Celana Chino Camel", "#C19A6B"),

    # --- Base: Pink Dusty Rose (#DCAE96) ---
    ("Blus Dusty Rose", "#DCAE96", "Celana Chino Putih Bersih", "#F8F9FA"),
    ("Blus Dusty Rose", "#DCAE96", "Celana Denim Navy Gelap", "#1B263B"),
    ("Sweater Dusty Rose", "#DCAE96", "Celana Chino Abu-abu Terang", "#B0B7C6"),
    ("Kaos Dusty Rose", "#DCAE96", "Celana Chino Hitam", "#1A1A1A"),
    ("Kemeja Dusty Rose", "#DCAE96", "Celana Chino Olive Lembut", "#9CAF88"),
    ("Cardigan Dusty Rose", "#DCAE96", "Rok Plisket Taupe", "#B38B6D"),

    # --- Base: Ungu Lavender / Lilac (#B57EDC / #C8A2C8) ---
    ("Kaos Lavender", "#B57EDC", "Celana Putih Bersih", "#F8F9FA"),
    ("Kemeja Lavender", "#B57EDC", "Celana Chino Abu-abu Charcoal", "#36454F"),
    ("Sweater Lavender", "#B57EDC", "Celana Denim Biru Navy", "#000080"),
    ("Cardigan Lilac", "#C8A2C8", "Rok Plisket Putih Gading", "#FFF8DC"),
    ("Blus Lavender", "#B57EDC", "Celana Chino Khaki Krem", "#D2B48C"),
    ("Kaos Lilac", "#C8A2C8", "Celana Chino Hitam", "#1A1A1A"),

    # --- Base: Biru Denim Klasik (#2C5D88 / #4A6FA5) ---
    ("Kemeja Denim", "#2C5D88", "Celana Chino Khaki Krem", "#D2B48C"),
    ("Kemeja Denim", "#2C5D88", "Celana Chino Hitam", "#1A1A1A"),
    ("Kemeja Denim", "#2C5D88", "Celana Chino Olive", "#556B2F"),
    ("Jaket Denim", "#2C5D88", "Celana Chino Putih", "#F8F9FA"),
    ("Jaket Denim", "#2C5D88", "Celana Chino Terracotta", "#CC4E2A"),
    ("Kemeja Denim Biru", "#4A6FA5", "Celana Chino Camel", "#C19A6B"),
    ("Kaos Biru Denim", "#4A6FA5", "Celana Chino Abu-abu", "#708090"),

    # --- Base: Abu-abu Heather / Charcoal (#9AA0A6 / #36454F) ---
    ("Kaos Abu-abu Heather", "#9AA0A6", "Celana Chino Hitam", "#1A1A1A"),
    ("Kaos Abu-abu Heather", "#9AA0A6", "Celana Denim Navy", "#000080"),
    ("Sweater Abu-abu Heather", "#9AA0A6", "Celana Chino Terracotta", "#CC4E2A"),
    ("Kemeja Abu-abu", "#9AA0A6", "Celana Chino Burgundy", "#800020"),
    ("Cardigan Abu-abu", "#9AA0A6", "Rok Plisket Hijau Olive", "#556B2F"),
    ("Blazer Charcoal", "#36454F", "Celana Chino Krem Khaki", "#D2B48C"),
    ("Kemeja Charcoal", "#36454F", "Celana Putih Bersih", "#F8F9FA"),
    ("Sweater Charcoal", "#36454F", "Celana Jeans Denim Biru", "#6495ED"),

    # --- Base: Coklat Espresso Tua (#362217) ---
    ("Kemeja Espresso", "#362217", "Celana Chino Krem", "#F5F5DC"),
    ("Sweater Espresso", "#362217", "Celana Chino Khaki", "#D2B48C"),
    ("Jaket Espresso", "#362217", "Celana Denim Biru Navy", "#000080"),
    ("Cardigan Espresso", "#362217", "Celana Chino Sage Green", "#8A9A5B"),
    ("Kaos Espresso", "#362217", "Celana Putih Off-White", "#F8F9FA"),
    ("Blus Espresso", "#362217", "Rok Plisket Terracotta", "#B85D43"),

    # --- Base: Pink Coral (#F88379) ---
    ("Blus Coral", "#F88379", "Celana Chino Putih Bersih", "#F8F9FA"),
    ("Kaos Coral", "#F88379", "Celana Denim Biru Navy", "#000080"),
    ("Kemeja Coral", "#F88379", "Celana Chino Khaki", "#D2B48C"),
    ("Cardigan Coral", "#F88379", "Celana Chino Olive", "#556B2F"),
    ("Tunik Coral", "#F88379", "Rok Plisket Hitam", "#1A1A1A"),
    ("Sweater Coral", "#F88379", "Celana Jeans Abu-abu Terang", "#B0B7C6"),

    # --- Base: Ungu Plum Tua (#701C3C) ---
    ("Kemeja Plum", "#701C3C", "Celana Chino Khaki Krem", "#D2B48C"),
    ("Sweater Plum", "#701C3C", "Celana Chino Abu-abu Slate", "#708090"),
    ("Blus Plum", "#701C3C", "Celana Hitam Elegan", "#1A1A1A"),
    ("Cardigan Plum", "#701C3C", "Rok Plisket Putih Gading", "#FFF8DC"),
    ("Kaos Plum", "#701C3C", "Celana Denim Navy", "#000080"),

    # --- Base: Biru Royal (#4169E1) ---
    ("Kemeja Royal Blue", "#4169E1", "Celana Chino Putih Bersih", "#F8F9FA"),
    ("Kaos Royal Blue", "#4169E1", "Celana Chino Hitam", "#1A1A1A"),
    ("Sweater Royal Blue", "#4169E1", "Celana Chino Abu-abu Terang", "#B0B7C6"),
    ("Blus Royal Blue", "#4169E1", "Celana Chino Khaki", "#D2B48C"),
    ("Jaket Royal Blue", "#4169E1", "Celana Denim Navy Gelap", "#000080"),

    # --- Base: Coklat Tan (#D2B48C) ---
    ("Kemeja Tan", "#D2B48C", "Celana Denim Navy Klasik", "#000080"),
    ("Kaos Tan", "#D2B48C", "Celana Hitam Elegan", "#1A1A1A"),
    ("Sweater Tan", "#D2B48C", "Celana Chino Olive Green", "#556B2F"),
    ("Cardigan Tan", "#D2B48C", "Celana Merah Burgundy", "#800020"),
    ("Blus Tan", "#D2B48C", "Rok Plisket Hijau Forest", "#1B4D3E"),
    ("Jaket Tan", "#D2B48C", "Celana Putih Off-White", "#F8F9FA"),

    # --- Base: Biru Baby Blue (#89CFF0) ---
    ("Kemeja Baby Blue", "#89CFF0", "Celana Chino Putih Bersih", "#F8F9FA"),
    ("Kemeja Baby Blue", "#89CFF0", "Celana Chino Khaki Krem", "#D2B48C"),
    ("Kaos Baby Blue", "#89CFF0", "Celana Chino Navy Gelap", "#000080"),
    ("Sweater Baby Blue", "#89CFF0", "Celana Chino Abu-abu Charcoal", "#36454F"),
    ("Blus Baby Blue", "#89CFF0", "Rok Plisket Hitam", "#1A1A1A"),

    # --- Base: Hijau Forest Deep (#1B4D3E) ---
    ("Kemeja Forest Green", "#1B4D3E", "Celana Chino Camel", "#C19A6B"),
    ("Sweater Forest Green", "#1B4D3E", "Celana Chino Khaki", "#D2B48C"),
    ("Kaos Forest Green", "#1B4D3E", "Celana Hitam Elegan", "#1A1A1A"),
    ("Jaket Forest Green", "#1B4D3E", "Celana Putih Bersih", "#F8F9FA"),
    ("Cardigan Forest Green", "#1B4D3E", "Celana Denim Navy", "#000080"),
    ("Blus Forest Green", "#1B4D3E", "Rok Plisket Abu-abu Terang", "#B0B7C6"),

    # --- Base: Coklat Taupe (#B38B6D) ---
    ("Kemeja Taupe", "#B38B6D", "Celana Denim Navy", "#1B263B"),
    ("Sweater Taupe", "#B38B6D", "Celana Putih Bersih", "#F8F9FA"),
    ("Kaos Taupe", "#B38B6D", "Celana Hitam Elegan", "#1A1A1A"),
    ("Cardigan Taupe", "#B38B6D", "Celana Hijau Olive", "#556B2F"),
    ("Blus Taupe", "#B38B6D", "Rok Plisket Burgundy", "#800020"),

    # --- Base: Krem Hangat / Beige (#F5F5DC / #E6DBBF) ---
    ("Kemeja Krem", "#F5F5DC", "Celana Denim Navy Klasik", "#000080"),
    ("Kaos Krem", "#F5F5DC", "Celana Chino Olive", "#556B2F"),
    ("Sweater Krem", "#F5F5DC", "Celana Chino Terracotta", "#CC4E2A"),
    ("Cardigan Krem", "#F5F5DC", "Celana Chino Coklat Espresso", "#362217"),
    ("Blus Krem", "#F5F5DC", "Rok Plisket Hitam", "#1A1A1A"),
    ("Kemeja Linen Beige", "#E6DBBF", "Celana Chino Khaki Gelap", "#A39B7B"),
    ("Kaos Beige", "#E6DBBF", "Celana Denim Biru Terang", "#6495ED"),

    # --- Base: Oranye Aprikot / Peach (#FBCEB1) ---
    ("Blus Peach", "#FBCEB1", "Celana Putih Bersih", "#F8F9FA"),
    ("Kaos Peach", "#FBCEB1", "Celana Denim Navy Gelap", "#000080"),
    ("Sweater Peach", "#FBCEB1", "Celana Chino Abu-abu Slate", "#708090"),
    ("Cardigan Peach", "#FBCEB1", "Celana Chino Olive Muted", "#6B7B58"),
    ("Kemeja Peach", "#FBCEB1", "Celana Chino Khaki Krem", "#D2B48C"),
]


def build_colors_dataframe() -> pd.DataFrame:
    """Membangun dataframe colors dengan nilai HSV dihitung matematis dari HEX."""
    rows = []
    for item in RAW_COLORS:
        name, hex_code, undertone, family, label = item
        h, s, v = hex_to_hsv(hex_code)
        rows.append({
            "name": name,
            "hex": hex_code.upper(),
            "undertone": undertone.lower(),
            "family": family.lower(),
            "hue": h,
            "saturation": s,
            "value": v,
            "label": label
        })
    df = pd.DataFrame(rows)
    return df


def build_outfits_dataframe() -> pd.DataFrame:
    """Membangun dataframe outfits dengan nilai CIELAB (D65) dihitung matematis dari HEX."""
    rows = []
    for item in RAW_OUTFITS:
        base_name, base_hex, combo_name, combo_hex = item
        L, a_val, b_val = hex_to_lab(base_hex)
        rows.append({
            "base_name": base_name,
            "base_hex": base_hex.upper(),
            "base_L": L,
            "base_a": a_val,
            "base_b": b_val,
            "combo_name": combo_name,
            "combo_hex": combo_hex.upper()
        })
    df = pd.DataFrame(rows)
    return df


def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    print("=== MEMBANGUN DATASET COLORFIT ===")
    
    # 1. Colors Dataset
    colors_df = build_colors_dataframe()
    colors_path = os.path.join(DATA_DIR, "colors.csv")
    colors_df.to_csv(colors_path, index=False)
    print(f"[OK] data/colors.csv tersimpan ({len(colors_df)} baris)")
    print("Distribusi per undertone dan label:")
    print(pd.crosstab(colors_df['undertone'], colors_df['label']))
    print("\nDistribusi family warna:")
    print(colors_df['family'].value_counts())

    # 2. Outfits Dataset
    outfits_df = build_outfits_dataframe()
    outfits_path = os.path.join(DATA_DIR, "outfits.csv")
    outfits_df.to_csv(outfits_path, index=False)
    print(f"\n[OK] data/outfits.csv tersimpan ({len(outfits_df)} baris)")
    print("Contoh 5 baris pertama outfits.csv:")
    print(outfits_df.head())


if __name__ == "__main__":
    main()
