# Storage & Asset Management Architecture (`storage/`)

**Domain Owner**: Nidiya (Database and Cloud Developer)

## Overview
This module outlines Supabase Storage bucket configurations, access policies, file naming conventions, and local asset staging directories for Inteliedu.

---

## Storage Buckets

| Bucket Name | Purpose | Public / Private | Allowed MIME Types | Max File Size |
| :--- | :--- | :--- | :--- | :--- |
| `documents` | Course notes, PDFs, DOCX, lesson attachments | Authenticated Read | `application/pdf`, `text/*`, `application/vnd.openxmlformats-officedocument.*` | 50 MB |
| `3d-models` | GLTF/GLB binaries, DRACO buffers, textures | Public / CDN | `model/gltf-binary`, `model/gltf+json`, `image/png`, `image/webp` | 100 MB |
| `images` | Lesson diagrams, quiz illustrations, slide graphics | Public / CDN | `image/jpeg`, `image/png`, `image/webp`, `image/svg+xml` | 10 MB |
| `avatars` | User profile profile pictures | Public / CDN | `image/jpeg`, `image/png`, `image/webp` | 5 MB |

---

## Directory Organization

```
storage/
├── documents/          # Staging & sample course documents
├── 3d-models/          # Staging & low-poly sample GLB/GLTF assets
├── images/             # Staging & sample illustration assets
├── avatars/            # Staging & sample profile avatar assets
└── README.md
```
