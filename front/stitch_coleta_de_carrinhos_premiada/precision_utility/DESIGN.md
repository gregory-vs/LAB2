---
name: Precision Utility
colors:
  surface: '#f7f9fb'
  surface-dim: '#d8dadc'
  surface-bright: '#f7f9fb'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f4f6'
  surface-container: '#eceef0'
  surface-container-high: '#e6e8ea'
  surface-container-highest: '#e0e3e5'
  on-surface: '#191c1e'
  on-surface-variant: '#414754'
  inverse-surface: '#2d3133'
  inverse-on-surface: '#eff1f3'
  outline: '#727785'
  outline-variant: '#c1c6d6'
  surface-tint: '#005bc0'
  primary: '#005bbf'
  on-primary: '#ffffff'
  primary-container: '#1a73e8'
  on-primary-container: '#ffffff'
  inverse-primary: '#adc7ff'
  secondary: '#515f74'
  on-secondary: '#ffffff'
  secondary-container: '#d5e3fc'
  on-secondary-container: '#57657a'
  tertiary: '#565e74'
  on-tertiary: '#ffffff'
  tertiary-container: '#6f768d'
  on-tertiary-container: '#ffffff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#d8e2ff'
  primary-fixed-dim: '#adc7ff'
  on-primary-fixed: '#001a41'
  on-primary-fixed-variant: '#004493'
  secondary-fixed: '#d5e3fc'
  secondary-fixed-dim: '#b9c7df'
  on-secondary-fixed: '#0d1c2e'
  on-secondary-fixed-variant: '#3a485b'
  tertiary-fixed: '#dae2fd'
  tertiary-fixed-dim: '#bec6e0'
  on-tertiary-fixed: '#131b2e'
  on-tertiary-fixed-variant: '#3f465c'
  background: '#f7f9fb'
  on-background: '#191c1e'
  surface-variant: '#e0e3e5'
typography:
  h1:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '700'
    lineHeight: '1.2'
    letterSpacing: -0.02em
  h2:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.3'
    letterSpacing: -0.01em
  h3:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: '1.4'
    letterSpacing: '0'
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
    letterSpacing: '0'
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
    letterSpacing: '0'
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: '1.2'
    letterSpacing: 0.02em
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: '1.2'
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  gutter: 16px
  margin-mobile: 16px
  margin-desktop: 48px
---

## Brand & Style

The brand personality for this design system is centered on **Efficiency, Reliability, and Clarity**. Designed for the high-stakes, fast-paced environment of an airport, the UI prioritizes immediate comprehension and task completion. The visual language follows a **Corporate / Modern** aesthetic, drawing inspiration from high-end logistics and transportation interfaces.

The target audience includes both travelers and service personnel, requiring a UI that feels authoritative yet accessible. The emotional response should be one of "controlled calm"—reducing the stress of transit through structured information and predictable interaction patterns.

## Colors

The palette is anchored by **Airport Blue**, a high-visibility primary color that denotes action and trust. **Slate Gray** is utilized for secondary elements and secondary navigation, providing a grounded, professional contrast to the vibrant blue.

- **Primary (#1a73e8):** Reserved for primary actions, active states, and brand-critical identifiers.
- **Secondary (#475569):** Used for iconography, supporting text, and UI borders to maintain a sophisticated hierarchy.
- **Surface/Neutral (#f8fafc):** A clean, off-white background that reduces screen glare and separates content modules clearly.
- **Success/Warning/Error:** Standard utility colors should be tinted with slate to maintain harmony with the core palette.

## Typography

This design system utilizes **Inter** for all typographic levels to ensure maximum legibility across various device densities. The scale is built on a modular rhythm, emphasizing vertical rhythm and clear information density.

- **Headlines:** Use tighter letter-spacing and heavier weights to create a strong visual anchor.
- **Body Text:** Optimized for long-form reading of terms or instructions, using a generous line height.
- **Labels:** Set in medium to semi-bold weights, often in all-caps for utility-style identifiers (e.g., Gate Numbers, Cart IDs) to distinguish them from prose.

## Layout & Spacing

The design system employs a **Fluid Grid** system based on an 8pt grid (4px increments). This ensures consistency across mobile and desktop breakpoints.

- **Mobile:** 4-column grid with 16px margins. Content is primarily stacked to facilitate one-handed operation.
- **Desktop:** 12-column grid with a maximum content width of 1280px. Gutters are fixed at 24px to maintain breathability in data-heavy views.
- **Rhythm:** Vertical spacing between components should follow the `lg` (24px) or `xl` (32px) tokens to prevent the UI from feeling cramped during stressful transit moments.

## Elevation & Depth

To maintain a professional and "app-like" feel, this design system uses **Tonal Layers** combined with **Ambient Shadows**. 

- **Level 0 (Base):** The neutral background color (#f8fafc).
- **Level 1 (Cards/Containers):** Pure white (#ffffff) surfaces with a subtle 1px border (#e2e8f0) and a soft, low-opacity shadow (Y: 2, Blur: 4, Opacity: 0.05).
- **Level 2 (Modals/Popovers):** Higher elevation with a more pronounced shadow (Y: 8, Blur: 16, Opacity: 0.1) to focus user attention.
- **Interaction:** Buttons utilize a slight "lift" effect on hover, increasing shadow depth rather than changing color drastically, mimicking a tactile physical response.

## Shapes

The shape language is defined as **Rounded**, striking a balance between the friendliness of consumer apps and the structure of professional utilities. 

- **Standard Elements:** Buttons, input fields, and small cards use a 0.5rem (8px) corner radius.
- **Large Containers:** Content blocks and major sections use a 1rem (16px) corner radius to create a distinct "shell" appearance.
- **Icons:** Should follow a consistent 2px stroke weight with slightly rounded terminals to match the container language.

## Components

The components within the design system are built for high affordance and rapid interaction.

- **Buttons:** Primary buttons use the Airport Blue background with white text. They must have a minimum touch target of 44px for mobile accessibility.
- **Input Fields:** Use a white background with a Slate Gray border. On focus, the border transitions to Airport Blue with a 2px outer glow.
- **Chips/Badges:** Used for status indicators (e.g., "In Transit", "Available"). These use low-saturation background tints of the status color with high-saturation text for readability.
- **Cards:** The primary vehicle for information. They feature a white fill, soft shadow, and clear padding. For "CartCollect" specific needs, cards should include a distinct "Action Zone" at the bottom for primary task buttons.
- **Lists:** Use subtle horizontal dividers and chevron indicators to suggest drill-down navigation.
- **Utility Indicators:** High-contrast progress bars and step-indicators are essential for tracking logistics and service flows.