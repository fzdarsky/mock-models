## ADDED Requirements

### Requirement: Color mode activation

When configured with `MOCKLM_MODE=color`, the server SHALL compute the dominant color of the image in the last user message and return the nearest CSS/X11 named color.

#### Scenario: Color mode selected

- **WHEN** `MOCKLM_MODE` is set to `color`
- **THEN** the server SHALL start in color mode and process image requests using dominant color detection

### Requirement: Average color computation

The color mode SHALL compute the dominant color by averaging the RGB values of all pixels in the image.

#### Scenario: Solid color image

- **WHEN** a request contains a solid red image (all pixels RGB 255, 0, 0)
- **THEN** the computed average color SHALL be (255, 0, 0) and the response SHALL include the color name "red"

#### Scenario: Mixed color image

- **WHEN** a request contains an image with varying pixel colors
- **THEN** the server SHALL compute the arithmetic mean of all pixel R, G, and B values independently

### Requirement: CSS/X11 named color matching

The color mode SHALL match the computed average color to the nearest color in the CSS/X11 named color table (~140 colors) using Euclidean distance in RGB space.

#### Scenario: Exact match

- **WHEN** the average color is exactly (255, 127, 80)
- **THEN** the matched color name SHALL be "coral"

#### Scenario: Nearest match

- **WHEN** the average color does not exactly match any named color
- **THEN** the server SHALL return the named color with the smallest Euclidean distance in RGB space

### Requirement: Color mode response format

The color mode SHALL return a response in the format: `The dominant color in this image is '<color-name>' (RGB: <r>, <g>, <b>).` where `<color-name>` is the matched CSS/X11 color name and `<r>, <g>, <b>` are the RGB values of the named color.

#### Scenario: Response format

- **WHEN** a request with a base64-encoded image is processed in color mode
- **THEN** the response SHALL match the format `The dominant color in this image is 'coral' (RGB: 255, 127, 80).`

### Requirement: Color mode without image

The color mode SHALL handle requests with no image content gracefully.

#### Scenario: Text-only request in color mode

- **WHEN** a text-only request is sent while in color mode
- **THEN** the response SHALL indicate that no image was provided (e.g., "No image provided.")
