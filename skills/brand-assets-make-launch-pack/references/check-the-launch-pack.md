# Check The Launch Pack

Give every item a result: `pass`, `draft`, or `needs-review`.

## One story

- The subject, canonical URL, and CTA are the same everywhere.
- Every factual claim points to an approved source-fact ID.
- Fictional examples are visibly labeled.
- Copy says only what the source facts support.

## One family

- All files match three approved visual anchors.
- Type, color, materials, illustration style, edge treatment, and spacing feel related.
- A thumbnail view still makes the brand and main idea recognizable.
- Each shape is recomposed for its surface. Nothing important is stretched or awkwardly cropped.
- Every raster receipt names the clean background master in `background_source`.
- Every typed asset names the approved portable font file, family, license, weight, width, and applied variation settings. There is no silent default-font fallback.
- The focal cluster stays outside the protected negative space at the final crop.
- No background is enlarged. Crop-to-fill keeps at least 75% of the selected master; otherwise a separate master is used.

## Every file works

- Pixel size, format, color mode, page count, and safe area match the placement record.
- The generated background has no text. The local overlay is readable at normal feed size and stays out of interface-covered areas.
- The type has enough weight and character to feel intentional at feed size. It is not a generic placeholder or a thin default face.
- `overlay_word_count` is present and is an integer from 0 through 14.
- The observed text bounds stay inside both the protected copy box and the placement `safe_area`.
- Contrast is measured from the actual background pixels under the rendered glyph mask, not inferred from declared palette colors.
- Profile art survives a circular crop.
- Carousel pages work alone, in order, and as a complete document.
- Alt text explains the useful visual information without repeating the caption.
- Links use HTTPS and contain the campaign's UTM values.

## Safe to share

- The manifest digest matches each saved file.
- Paths are relative and stay inside the launch-pack folder.
- The pack contains no secrets, cookies, account IDs, provider IDs, private filesystem paths, customer data, or fake publication results.
- Publication remains a separate, explicitly authorized action.
