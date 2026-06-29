## ADDED Requirements

### Requirement: Describe mode activation

When configured with `MOCKLM_MODE=describe`, the server SHALL return a structured description of the image in the last user message, including dimensions, format, orientation, and top-3 dominant colors.

#### Scenario: Describe mode selected

- **WHEN** `MOCKLM_MODE` is set to `describe`
- **THEN** the server SHALL start in describe mode

### Requirement: Image metadata extraction

The describe mode SHALL extract and report the image dimensions (width × height) and format (JPEG or PNG) from the decoded image data.

#### Scenario: JPEG image metadata

- **WHEN** a request contains a 1920×1080 JPEG image
- **THEN** the response SHALL include "1920x1080" and "JPEG"

#### Scenario: PNG image metadata

- **WHEN** a request contains a 800×600 PNG image
- **THEN** the response SHALL include "800x600" and "PNG"

### Requirement: Orientation detection

The describe mode SHALL determine image orientation based on aspect ratio: "landscape" when width > height, "portrait" when height > width, and "square" when width equals height.

#### Scenario: Landscape image

- **WHEN** a request contains a 1920×1080 image
- **THEN** the response SHALL include "landscape"

#### Scenario: Portrait image

- **WHEN** a request contains a 1080×1920 image
- **THEN** the response SHALL include "portrait"

#### Scenario: Square image

- **WHEN** a request contains a 500×500 image
- **THEN** the response SHALL include "square"

### Requirement: Top-3 dominant colors via grid sampling

The describe mode SHALL compute top-3 dominant colors by dividing the image into a 3×3 grid (9 regions), averaging the RGB values in each region, and selecting the 3 most distinct colors by Euclidean RGB distance. Each color SHALL be reported as its nearest CSS/X11 named color with hex value.

#### Scenario: Uniform image

- **WHEN** a request contains a solid blue image
- **THEN** all 9 grid regions SHALL average to the same blue, and the top-3 colors SHALL include that blue (the remaining colors may repeat or be near-identical)

#### Scenario: Multi-color image

- **WHEN** a request contains an image with distinct color regions
- **THEN** the top-3 colors SHALL represent the 3 most visually distinct colors found across the 9 grid regions

### Requirement: Describe mode response format

The describe mode SHALL return a response in the format: `This is a <width>x<height> <format> image in <orientation> orientation. The dominant colors are <color1> (<hex1>), <color2> (<hex2>), and <color3> (<hex3>).`

#### Scenario: Full description response

- **WHEN** a 1920×1080 JPEG image is processed in describe mode
- **THEN** the response SHALL match the format `This is a 1920x1080 JPEG image in landscape orientation. The dominant colors are coral (#FF7F50), steel blue (#4682B4), and white (#FFFFFF).`

### Requirement: Describe mode without image

The describe mode SHALL handle requests with no image content gracefully.

#### Scenario: Text-only request in describe mode

- **WHEN** a text-only request is sent while in describe mode
- **THEN** the response SHALL indicate that no image was provided
