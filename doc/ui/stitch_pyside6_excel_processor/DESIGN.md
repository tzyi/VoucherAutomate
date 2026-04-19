# Design System Strategy: The Precision Architect

## 1. Overview & Creative North Star
The "Creative North Star" for this design system is **The Precision Architect**. 

In the realm of data processing and technical frameworks like PySide6, there is a tendency to fall into "gray-box" industrialism—interfaces that are functional but sterile. This design system rejects that sterility. Instead, it treats data as a high-end editorial subject. We leverage the stability of the Qt framework's logic but wrap it in a signature aesthetic of **Technical Sophistication**. 

The goal is to move beyond a "template" look by using intentional asymmetry in sidebars, deep tonal layering, and high-contrast typography scales. We are not just building a tool; we are building a professional instrument that feels as stable as a mainframe but as refined as a luxury timepiece.

---

## 2. Colors
Our palette is anchored in deep, atmospheric neutrals (`#131317`) and a luminous primary blue (`#a3c9ff`). This creates a high-performance environment where focus is directed, not scattered.

*   **The "No-Line" Rule:** We explicitly prohibit the use of 1px solid borders for sectioning. Structural boundaries must be defined solely through background color shifts. For example, a sidebar using `surface-container-low` sits directly against a `background` workspace. The eye perceives the edge through the change in value, resulting in a cleaner, more modern interface.
*   **Surface Hierarchy & Nesting:** We treat the UI as a series of nested physical layers. 
    *   **Base:** `background` (#131317).
    *   **Primary Containers:** `surface-container` (#1f1f23) for main content areas.
    *   **Utility Layers:** `surface-container-high` (#2a2a2e) for cards or tool-bars.
    *   **Interactive Elements:** `surface-container-highest` (#353439) for hovered states or active selection.
*   **The "Glass & Gradient" Rule:** To avoid a flat "out-of-the-box" feel, floating modals or dropdowns should utilize a backdrop-blur (12px–20px) combined with a semi-transparent `surface-tint`. Main action buttons should use a subtle linear gradient from `primary` (#a3c9ff) to `primary_container` (#0061ad) to provide a sense of "tactile soul."

---

## 3. Typography
We utilize **Inter** across the entire system to maintain a technical, clean, and highly legible profile suitable for data density.

*   **Display & Headline:** Use `display-md` and `headline-sm` for dashboard summaries and major section titles. These should be set with tighter letter-spacing (-0.02em) to feel authoritative and "editorial."
*   **Data Points:** Use `title-lg` for primary data metrics. The high contrast between the `on_surface` color and the deep `background` ensures these figures are the first thing a user sees.
*   **Labels & Metadata:** `label-md` and `label-sm` are the workhorses of this system. They should be used for table headers and input labels, often in `on_surface_variant` (#c1c6d4) to maintain hierarchy without cluttering the visual field.

---

## 4. Elevation & Depth
In this system, depth is a function of light and tone, not shadows and lines.

*   **The Layering Principle:** Rather than using a shadow to lift a card, place a `surface-container-lowest` card inside a `surface-container-high` section. This "inverted" depth creates a sophisticated, recessed look that feels integrated into the application's architecture.
*   **Ambient Shadows:** If a component must float (e.g., a context menu), use a shadow with a 24px–32px blur at 6% opacity. The shadow color must be a tinted version of `surface_container_lowest` rather than pure black, ensuring the "glow" feels like natural ambient occlusion.
*   **The "Ghost Border" Fallback:** For accessibility in high-density data tables, use a "Ghost Border": the `outline-variant` token at 15% opacity. This provides a visual guide without the "grid-prison" feel of standard UI kits.

---

## 5. Components

### Buttons
*   **Primary:** Roundedness `md` (0.375rem). Use the `primary` to `primary_container` gradient. Text is `on_primary`. 
*   **Secondary:** No background. Use a `ghost-border` (outline-variant at 20%) and `on_surface` text.
*   **Tertiary:** Flat. Only visible via `on_surface_variant` text, shifting to `surface_container_high` on hover.

### Input Fields
*   **Style:** Inputs should use `surface_container_low`. No borders.
*   **States:** On focus, the background transitions to `surface_container_high`, and a 2px bottom-bar of `primary` appears. This mimics a professional terminal feel.
*   **Error:** Use the `error` token (#ffb4ab) for the bottom-bar and `on_error_container` for the helper text.

### Data Chips
*   **Visuals:** Roundedness `full`. Use `secondary_container` for the background and `on_secondary_container` for text. These should feel like small, tactile pebbles within the interface.

### Cards & Lists
*   **The No-Divider Mandate:** Horizontal lines are forbidden. Use 24px of vertical whitespace or a subtle background shift (from `surface` to `surface_container_low`) to separate list items. This forces a more "breathable" and premium layout.

### Data Visualization (Specific for Data Tools)
*   **Trend Lines:** Use `tertiary` (#ffb68f) for secondary data trends to provide a sophisticated warm/cool contrast against the primary blue.

---

## 6. Do's and Don'ts

### Do
*   **Do** use asymmetrical layouts. A wide main content area paired with a very slim, icon-only sidebar creates a custom, "pro-tool" feel.
*   **Do** use `surface-bright` for very small, high-frequency interaction points to make them "pop" against the dark UI.
*   **Do** prioritize vertical rhythm. Ensure all components align to a 4px or 8px grid to maintain the "Architect" precision.

### Don't
*   **Don't** use 100% white text on the #131317 background. Always use `on_surface` or `on_surface_variant` to prevent eye strain and "haloing."
*   **Don't** use standard "drop shadows" on cards. Stick to Tonal Layering.
*   **Don't** use sharp corners. Always use at least the `sm` (0.125rem) or `md` (0.375rem) roundedness to keep the interface feeling modern and approachable.