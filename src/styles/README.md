# Cyberpunk/Premium Theme Documentation

## Overview
This theme transforms your NextStep Streamlit app with a futuristic, cyberpunk aesthetic featuring glassmorphism effects, neon accents, and animated backgrounds.

## Theme Features

### 1. **Animated Gradient Background**
- Smooth, animated gradient that shifts between dark blues and purples
- Creates a dynamic, living background effect
- 15-second animation cycle for subtle movement

### 2. **Glassmorphism Cards**
- All metrics and containers use semi-transparent backgrounds (`rgba(255, 255, 255, 0.05)`)
- 10px backdrop blur filter for the "frosted glass" effect
- Thin white borders with low opacity
- Elevated hover states with neon green glow

### 3. **Neon Accents**
- **Primary Colors:**
  - Neon Green: `#00FF94`
  - Cyber Blue: `#00E5FF`
- Applied to:
  - Buttons (gradient from green to blue)
  - Metric values (green with glow effect)
  - Active tabs
  - Sliders and progress bars
  - Scrollbar thumbs

### 4. **Rounded Corners**
- Consistent 15px border-radius across:
  - Input fields
  - Cards and containers
  - Buttons
  - Tabs
  - Expanders

### 5. **Hidden Streamlit Elements**
- Removed top header decoration
- Hidden footer and "Deploy" button
- Cleaner, more professional appearance

### 6. **Interactive Effects**
- Hover states with color transitions
- Glow effects on interactive elements
- Smooth transitions (0.3s ease)
- Button lift effect on hover

### 7. **Custom Components**

#### Metric Cards
- Large value display with neon green glow
- Hover effect with upward translation
- Delta values in cyber blue

#### Buttons
- Gradient background (green → blue)
- Text in dark color for contrast
- Glowing shadow effect
- Uppercase text with letter spacing

#### Tabs
- Glassmorphism when inactive
- Gradient fill when active
- Smooth color transitions

#### Sidebar
- Semi-transparent dark background
- Neon green border accent
- Backdrop blur for depth

#### Scrollbars
- Custom gradient thumbs
- Transparent tracks
- Smooth hover effects

## File Structure

```
src/
└── styles/
    ├── __init__.py
    └── custom_css.py
```

## Usage

The theme is automatically applied in `app.py`:

```python
from src.styles.custom_css import get_custom_css

# Apply theme
st.markdown(get_custom_css(), unsafe_allow_html=True)
```

## Color Palette

| Color Name | Hex Code | Usage |
|------------|----------|-------|
| Neon Green | #00FF94 | Primary accent, buttons, metrics |
| Cyber Blue | #00E5FF | Secondary accent, gradients |
| Dark Base | #0a0e27 | Background, button text |
| Dark Purple | #1a1f3a | Gradient background |
| Dark Gray | #0f1419 | Gradient background |

## Customization

To modify the theme, edit `src/styles/custom_css.py`:

- **Change primary color**: Update `#00FF94` throughout
- **Adjust blur amount**: Modify `backdrop-filter: blur(10px)`
- **Change border radius**: Update all `border-radius: 15px`
- **Animation speed**: Modify `animation: gradientShift 15s`

## Browser Compatibility

- Best viewed in modern browsers (Chrome, Firefox, Edge, Safari)
- Backdrop filter requires `-webkit-backdrop-filter` for Safari
- All major browsers support the animation and gradient features
